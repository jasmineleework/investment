#!/usr/bin/env python3
"""
grab_chat_id.py — one-shot helper to capture the chat_id for the independent
morning-update Telegram bot.

Flow:
  1. Read MORNING_BOT_TOKEN from ~/.claude/channels/morning-update/.env
  2. Call getUpdates; tell the user to send "/start" to the bot from Telegram
  3. Capture chat.id from the first message and append MORNING_CHAT_ID to .env
  4. Send a "Setup OK ✅" test message to confirm

Run ONCE during setup. Idempotent: if MORNING_CHAT_ID already set, prints it
and exits without polling.

Zero dependencies (stdlib urllib).
"""
from __future__ import annotations

import json
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

CHANNEL_DIR = Path.home() / ".claude" / "channels" / "morning-update"
ENV_FILE = CHANNEL_DIR / ".env"

POLL_INTERVAL = 3   # seconds between getUpdates calls
POLL_DURATION = 300  # give up after 5 minutes
TIMEOUT = 10


def load_env() -> dict:
    if not ENV_FILE.is_file():
        return {}
    out: dict[str, str] = {}
    for line in ENV_FILE.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        out[k.strip()] = v.strip().strip('"').strip("'")
    return out


def append_env(key: str, value: str) -> None:
    CHANNEL_DIR.mkdir(parents=True, exist_ok=True)
    text = ENV_FILE.read_text(encoding="utf-8") if ENV_FILE.is_file() else ""
    if text and not text.endswith("\n"):
        text += "\n"
    text += f"{key}={value}\n"
    ENV_FILE.write_text(text, encoding="utf-8")
    try:
        ENV_FILE.chmod(0o600)
    except OSError:
        pass


def get_updates(token: str, offset: int = 0) -> list[dict]:
    url = f"https://api.telegram.org/bot{token}/getUpdates"
    params = {"timeout": 0}
    if offset:
        params["offset"] = offset
    full = url + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(full, method="GET")
    with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
        body = resp.read().decode("utf-8", errors="replace")
    r = json.loads(body)
    if not r.get("ok"):
        raise RuntimeError(f"getUpdates failed: {r.get('description')}")
    return r.get("result", [])


def send_test(token: str, chat_id: str) -> bool:
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = urllib.parse.urlencode({
        "chat_id": chat_id,
        "text": "Setup OK ✅\n\nMorning Update bot is now configured. You will receive your first morning briefing on the next scheduled run (default: weekdays 08:00 SGT).",
        "parse_mode": "Markdown",
    }).encode("utf-8")
    req = urllib.request.Request(url, data=data, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
            r = json.loads(resp.read().decode("utf-8", errors="replace"))
        return bool(r.get("ok"))
    except (urllib.error.URLError, json.JSONDecodeError) as e:
        print(f"  test message send error: {e}", file=sys.stderr)
        return False


def main() -> int:
    env = load_env()
    token = env.get("MORNING_BOT_TOKEN", "").strip()
    if not token:
        print(f"❌ MORNING_BOT_TOKEN missing from {ENV_FILE}", file=sys.stderr)
        print("", file=sys.stderr)
        print("Setup steps:", file=sys.stderr)
        print("  1. Open Telegram → @BotFather → /newbot → follow prompts to create a NEW bot", file=sys.stderr)
        print(f"  2. Write the token to {ENV_FILE} as:", file=sys.stderr)
        print("       MORNING_BOT_TOKEN=<your-token>", file=sys.stderr)
        print("  3. chmod 600 the .env file", file=sys.stderr)
        print("  4. Re-run this script", file=sys.stderr)
        return 1

    existing_chat = env.get("MORNING_CHAT_ID", "").strip()
    if existing_chat:
        print(f"✅ MORNING_CHAT_ID already set: ...{existing_chat[-4:]}")
        print(f"   (Re-running test message)")
        if send_test(token, existing_chat):
            print("✅ Test message delivered.")
            return 0
        print("❌ Test message failed. Check the token / chat_id manually.", file=sys.stderr)
        return 1

    print(f"📡 Polling {ENV_FILE.parent.name} bot for new /start messages...")
    print(f"   👉 Open Telegram, find your new bot, and send: /start")
    print(f"   (Will give up after {POLL_DURATION}s)")
    print()

    deadline = time.time() + POLL_DURATION
    last_offset = 0
    while time.time() < deadline:
        try:
            updates = get_updates(token, offset=last_offset)
        except (urllib.error.URLError, RuntimeError, json.JSONDecodeError) as e:
            print(f"  getUpdates error: {e} — retrying...", file=sys.stderr)
            time.sleep(POLL_INTERVAL)
            continue

        for upd in updates:
            last_offset = upd["update_id"] + 1
            msg = upd.get("message") or upd.get("edited_message") or {}
            chat = msg.get("chat") or {}
            chat_id = chat.get("id")
            if not chat_id:
                continue
            chat_id = str(chat_id)
            user = (msg.get("from") or {}).get("username") or chat.get("first_name") or "unknown"
            text = msg.get("text", "")
            print(f"  Got message from {user}: {text!r} (chat_id={chat_id})")
            # Append to .env and send test
            append_env("MORNING_CHAT_ID", chat_id)
            print(f"✅ Wrote MORNING_CHAT_ID=...{chat_id[-4:]} to {ENV_FILE}")
            if send_test(token, chat_id):
                print("✅ Test message delivered. Setup complete.")
                return 0
            else:
                print("⚠️  chat_id captured but test message failed; check bot block/permissions.", file=sys.stderr)
                return 1

        time.sleep(POLL_INTERVAL)

    print(f"⏱️  Timeout after {POLL_DURATION}s — no messages received.", file=sys.stderr)
    print("   Make sure you opened the new bot in Telegram and pressed /start.", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
