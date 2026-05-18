#!/usr/bin/env python3
"""
push_telegram.py — push morning-update markdown to an INDEPENDENT Telegram bot.

Reads stdin markdown; splits at Part 1 / Part 2 / Part 3 headers; sends each
section as a separate Telegram message (mobile-friendly). If a section exceeds
3900 chars, further split by ticker bullet ("- **TICKER** ...").

Credentials read from ~/.claude/channels/morning-update/.env :
    MORNING_BOT_TOKEN=<from BotFather>
    MORNING_CHAT_ID=<from grab_chat_id.py>

Zero dependencies (stdlib urllib). Never logs the token.

Exit codes:
  0  — all messages sent successfully
  1  — config missing / parse error / send failed after retry
"""
from __future__ import annotations

import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime
from pathlib import Path

CHANNEL_DIR = Path.home() / ".claude" / "channels" / "morning-update"
ENV_FILE = CHANNEL_DIR / ".env"
LOG_FILE = CHANNEL_DIR / "_push.log"

MAX_MSG_CHARS = 3900     # Telegram hard limit is 4096; leave headroom for formatting
INTER_SEND_SLEEP = 0.5   # avoid Telegram flood control
TIMEOUT = 15


def load_env() -> dict:
    if not ENV_FILE.is_file():
        return {}
    out: dict[str, str] = {}
    for line in ENV_FILE.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        k, v = line.split("=", 1)
        out[k.strip()] = v.strip().strip('"').strip("'")
    return out


def mask_chat(chat_id: str) -> str:
    """Mask all but last 4 digits for logging."""
    s = str(chat_id)
    return ("*" * max(0, len(s) - 4)) + s[-4:] if len(s) >= 4 else "****"


def log_event(level: str, event: str, **fields) -> None:
    """Append a JSON line to _push.log. NEVER include the bot token."""
    safe_fields = {k: v for k, v in fields.items() if "token" not in k.lower()}
    if "chat_id" in safe_fields:
        safe_fields["chat_id"] = mask_chat(safe_fields["chat_id"])
    entry = {
        "ts": datetime.now().isoformat(timespec="seconds"),
        "level": level,
        "event": event,
        **safe_fields,
    }
    try:
        CHANNEL_DIR.mkdir(parents=True, exist_ok=True)
        with LOG_FILE.open("a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except OSError:
        pass


def split_into_sections(md: str) -> list[tuple[str, str]]:
    """Return [(label, text), ...] split at top-level Part / Top Call markers.

    Result order roughly:
      ("HEAD", "<header + Top Call>")   — always present
      ("Part 1", "<Part 1 markdown>")
      ("Part 2", "<Part 2 markdown>")
      ("Part 3", "<Part 3 markdown>")
      ("FOOT", "<footer>")              — merged into Part 3 if short
    """
    lines = md.splitlines()
    sections: list[tuple[str, list[str]]] = []
    current_label = "HEAD"
    current_lines: list[str] = []

    for ln in lines:
        if ln.startswith("## Part 1"):
            sections.append((current_label, current_lines))
            current_label, current_lines = "Part 1", [ln]
        elif ln.startswith("## Part 2"):
            sections.append((current_label, current_lines))
            current_label, current_lines = "Part 2", [ln]
        elif ln.startswith("## Part 3"):
            sections.append((current_label, current_lines))
            current_label, current_lines = "Part 3", [ln]
        else:
            current_lines.append(ln)
    sections.append((current_label, current_lines))

    # Drop empty / pure-separator sections; merge HEAD + Part 1 into one message
    out: list[tuple[str, str]] = []
    head_text: str = ""
    for label, ls in sections:
        text = "\n".join(ls).strip()
        if not text:
            continue
        if label == "HEAD":
            head_text = text
        else:
            if head_text and label == "Part 1":
                out.append(("Part 1", head_text + "\n\n---\n\n" + text))
                head_text = ""
            else:
                out.append((label, text))
    if head_text:
        # No Part 1 — keep HEAD alone
        out.append(("HEAD", head_text))
    return out


def split_long(text: str, max_chars: int = MAX_MSG_CHARS) -> list[str]:
    """Split a single section by ticker bullet boundaries if too long."""
    if len(text) <= max_chars:
        return [text]
    chunks: list[str] = []
    current: list[str] = []
    current_len = 0
    for line in text.splitlines(keepends=True):
        # Start a new chunk before a ticker bullet if we're getting too long
        is_bullet = line.lstrip().startswith("- **")
        if is_bullet and current_len + len(line) > max_chars and current:
            chunks.append("".join(current).rstrip() + "\n\n_… (续)_")
            current = ["_(续) Morning Update_\n\n"]
            current_len = len(current[0])
        current.append(line)
        current_len += len(line)
    if current:
        chunks.append("".join(current).rstrip())
    return chunks


def telegram_send(token: str, chat_id: str, text: str) -> tuple[bool, str]:
    """Send one message. Returns (ok, error_msg)."""
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = urllib.parse.urlencode({
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "Markdown",
        "disable_web_page_preview": "true",
    }).encode("utf-8")
    req = urllib.request.Request(url, data=data, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
            body = resp.read().decode("utf-8", errors="replace")
            r = json.loads(body)
            if r.get("ok"):
                return True, ""
            return False, f"Telegram returned ok=false: {r.get('description', body[:200])}"
    except urllib.error.HTTPError as e:
        # 429: handle Retry-After
        try:
            err_body = e.read().decode("utf-8", errors="replace")
        except Exception:
            err_body = ""
        return False, f"HTTP {e.code}: {err_body[:200]}"
    except urllib.error.URLError as e:
        return False, f"URLError: {e.reason}"
    except (json.JSONDecodeError, OSError) as e:
        return False, f"{type(e).__name__}: {e}"


def send_with_retry(token: str, chat_id: str, text: str) -> bool:
    ok, err = telegram_send(token, chat_id, text)
    if ok:
        return True
    log_event("warn", "send_failed_attempt1", chat_id=chat_id, error=err)
    time.sleep(2.0)
    ok, err = telegram_send(token, chat_id, text)
    if ok:
        log_event("info", "send_ok_after_retry", chat_id=chat_id)
        return True
    log_event("error", "send_failed_final", chat_id=chat_id, error=err)
    print(f"[push_telegram] send failed after retry: {err}", file=sys.stderr)
    return False


def main() -> int:
    env = load_env()
    token = env.get("MORNING_BOT_TOKEN", "").strip()
    chat_id = env.get("MORNING_CHAT_ID", "").strip()

    if not token:
        print(f"[push_telegram] MORNING_BOT_TOKEN missing from {ENV_FILE}", file=sys.stderr)
        print("  Hint: create bot via @BotFather, then write the token to this file.", file=sys.stderr)
        log_event("error", "missing_token")
        return 1
    if not chat_id:
        print(f"[push_telegram] MORNING_CHAT_ID missing from {ENV_FILE}", file=sys.stderr)
        print("  Hint: run grab_chat_id.py after /start-ing your bot in Telegram.", file=sys.stderr)
        log_event("error", "missing_chat_id")
        return 1

    md = sys.stdin.read()
    if not md.strip():
        print("[push_telegram] empty stdin — nothing to send", file=sys.stderr)
        log_event("warn", "empty_stdin")
        return 1

    sections = split_into_sections(md)
    if not sections:
        print("[push_telegram] no sections detected", file=sys.stderr)
        return 1

    sent = 0
    total_chunks = 0
    for label, text in sections:
        chunks = split_long(text)
        total_chunks += len(chunks)
        for i, chunk in enumerate(chunks, 1):
            ok = send_with_retry(token, chat_id, chunk)
            if not ok:
                log_event("error", "abort", chat_id=chat_id, sent_so_far=sent)
                return 1
            sent += 1
            time.sleep(INTER_SEND_SLEEP)

    log_event("info", "all_sent", chat_id=chat_id, messages=sent, sections=len(sections))
    print(f"[push_telegram] sent {sent} message(s) across {len(sections)} sections", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
