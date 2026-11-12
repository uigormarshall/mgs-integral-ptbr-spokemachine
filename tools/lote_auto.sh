#!/usr/bin/env bash
# Translate the next codec batch with a fresh, minimal Claude Code session.
# Triggered hourly by ~/.config/systemd/user/mgs-lote.timer. Log: work/lote_auto.log
set -uo pipefail
cd "$(dirname "$0")/.."
CLAUDE=/home/spoken/.local/share/mise/installs/claude/latest/claude
MODEL="${MGS_MODEL:-sonnet}"
TIPO="${MGS_TIPO:-codec}"   # codec | vox
LOG=work/lote_auto.log
mkdir -p work

exec 9>work/lote_auto.lock
flock -n 9 || { echo "$(date -Is) ja existe um lote rodando, pulando" >> "$LOG"; exit 0; }

if python3 -I tools/$TIPO.py proximo | grep -q "todos os lotes"; then
    echo "$(date -Is) todos os lotes prontos, desligando o timer" >> "$LOG"
    systemctl --user disable --now mgs-lote.timer >> "$LOG" 2>&1
    exit 0
fi

LOTE=$(python3 -I tools/$TIPO.py proximo)
echo "$(date -Is) inicio: $LOTE (modelo $MODEL)" >> "$LOG"
"$CLAUDE" -p "traduza o próximo lote do $TIPO" \
    --model "$MODEL" \
    --allowedTools "Read" "Write" "Edit" \
        "Bash(python3 -I tools/$TIPO.py:*)" "Bash(tools/montar.sh)" "Bash(tools/montar2.sh)" \
    >> "$LOG" 2>&1
RC=$?
echo "$(date -Is) fim (rc=$RC)" >> "$LOG"
python3 -I tools/$TIPO.py status | tail -1 >> "$LOG"
echo "----" >> "$LOG"
