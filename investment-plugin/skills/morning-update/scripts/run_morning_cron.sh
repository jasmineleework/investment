#!/bin/bash
# morning-update 定时执行器
# 由 launchd (com.jasmine.morning-update) 触发：每天 08:00 + 工作日 21:30（美股夏令时开盘）
# 模式对齐 双币赢/run_dcd_cron.sh：硬超时 + 重试 + 日志 + 失败 Telegram 告警

set -u

# ========= 配置 =========
WORK_DIR="$HOME/Documents/Investment"
LOG_DIR="$WORK_DIR/Research/_morning/cron_logs"
MORNING_ENV="$HOME/.claude/channels/morning-update/.env"
CLAUDE_BIN="$HOME/.local/bin/claude"
MODEL="claude-sonnet-4-6"
TIMEOUT_SEC=1800         # 30 分钟硬超时（RSS + WebFetch 摘要 + WebSearch discovery）
MAX_RETRIES=1            # 失败重试 1 次（应对 API 529）
RETRY_DELAY=600          # 重试间隔 10 分钟

# launchd 环境 PATH 很短，补齐
export PATH="$HOME/.local/bin:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin"

mkdir -p "$LOG_DIR"
TS=$(date +%Y%m%d_%H%M%S)
LOG_FILE="$LOG_DIR/morning_cron_$TS.log"

cd "$WORK_DIR" || {
    echo "[$(date)] FATAL: cannot cd to $WORK_DIR" >&2
    exit 1
}

# 加载独立 morning bot（失败告警用同一渠道）
MORNING_BOT_TOKEN=""
MORNING_CHAT_ID=""
if [ -f "$MORNING_ENV" ]; then
    # shellcheck disable=SC1090
    source "$MORNING_ENV"
fi

send_alert() {
    local text="$1"
    [ -n "$MORNING_BOT_TOKEN" ] && [ -n "$MORNING_CHAT_ID" ] || return 0
    curl -s -o /dev/null --max-time 15 \
        "https://api.telegram.org/bot${MORNING_BOT_TOKEN}/sendMessage" \
        -d chat_id="${MORNING_CHAT_ID}" \
        --data-urlencode text="$text" || true
}

PROMPT='执行 /morning --push：严格按 investment-plugin/skills/morning-update/SKILL.md 的流程生成晨报并推送 Telegram。must_push 桶文章零丢弃；Discovery 必须附来源文章并排重。'

attempt=0
while [ "$attempt" -le "$MAX_RETRIES" ]; do
    attempt=$((attempt + 1))
    echo "[$(date)] attempt $attempt starting" | tee -a "$LOG_FILE"

    # 屏幕锁定时 Claude 读 Keychain token 会 401/卡死，先解锁（对齐 DCD 配方）
    security unlock-keychain "$HOME/Library/Keychains/login.keychain-db" 2>/dev/null

    # headless 配方（已验证）：bypassPermissions + 只用 user settings，
    # 否则项目 settings.json 只放行只读工具会死锁
    if gtimeout "$TIMEOUT_SEC" "$CLAUDE_BIN" -p "$PROMPT" \
        --model "$MODEL" \
        --permission-mode bypassPermissions \
        --setting-sources user \
        >> "$LOG_FILE" 2>&1; then
        echo "[$(date)] attempt $attempt OK" | tee -a "$LOG_FILE"
        # 真实产出校验：今天的报告文件必须存在且非空（is_error 不可信，见 lessons）
        TODAY_MD="Research/_morning/$(date +%Y-%m-%d)_morning.md"
        if [ -s "$TODAY_MD" ]; then
            echo "[$(date)] report verified: $TODAY_MD" | tee -a "$LOG_FILE"
            exit 0
        fi
        echo "[$(date)] WARN: exit 0 but $TODAY_MD missing/empty" | tee -a "$LOG_FILE"
    else
        echo "[$(date)] attempt $attempt FAILED (exit=$?)" | tee -a "$LOG_FILE"
    fi

    if [ "$attempt" -le "$MAX_RETRIES" ]; then
        echo "[$(date)] retrying in ${RETRY_DELAY}s" | tee -a "$LOG_FILE"
        sleep "$RETRY_DELAY"
    fi
done

send_alert "⚠️ morning-update 定时任务失败（$(date '+%m-%d %H:%M')），已重试 $MAX_RETRIES 次。日志：$LOG_FILE"
echo "[$(date)] all attempts failed" | tee -a "$LOG_FILE"
exit 1
