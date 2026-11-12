#!/usr/bin/env bash
# Run codec batches back to back until done; stop on error or no progress.
cd "$(dirname "$0")/.."
LOG=work/lote_auto.log
count() { python3 -I tools/${MGS_TIPO:-codec}.py status | tail -1 | grep -oE '^total: [0-9]+' | grep -oE '[0-9]+'; }
while ! python3 -I tools/${MGS_TIPO:-codec}.py proximo | grep -q "todos os lotes"; do
    before=$(count)
    tools/lote_auto.sh
    after=$(count)
    if [ "$after" -le "$before" ]; then
        echo "$(date -Is) LOOP PARADO: lote sem progresso ($before -> $after). Veja o log acima (limite de uso?)." >> "$LOG"
        exit 1
    fi
done
echo "$(date -Is) LOOP CONCLUIDO: todos os lotes traduzidos." >> "$LOG"
