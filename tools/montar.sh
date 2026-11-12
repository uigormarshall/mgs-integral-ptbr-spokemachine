#!/usr/bin/env bash
# Rebuild the patched disc image from the original + all translations.
# usage: tools/montar.sh   (run from anywhere)
set -euo pipefail
cd "$(dirname "$0")/.."
ORIG="disc1/Metal Gear Solid - Integral (Japan) (En,Ja) (Disc 1).bin"
OUT="patched/MGS Integral PT-BR (Disc 1).bin"
F=disc1/files/MGS
mkdir -p work patched
[ -f $F/SLPM_862.47 ] || python3 -I tools/psxiso.py "$ORIG" extract disc1/files MGS/DEMO.DAT MGS/RADIO.DAT MGS/VOX.DAT MGS/SLPM_862.47 > /dev/null
[ -f legendas/demo_all.json ] || python3 -I tools/demosubs.py extract $F/DEMO.DAT legendas/demo_all.json
[ -f legendas/vox_all.json ] || python3 -I tools/demosubs.py extract $F/VOX.DAT legendas/vox_all.json
[ -f legendas/radio_all.json ] || python3 -I tools/radio.py extract $F/RADIO.DAT legendas/radio_all.json
[ -f legendas/movie_all.json ] || python3 -I tools/movie.py extract "$ORIG" legendas/movie_all.json > /dev/null
python3 -I tools/movie.py juntar legendas/movie_all.json legendas/movie_tr.json legendas/movie_pt.json
# English reference for translators (lote_NN_en.txt), rebuilt from your disc; not versioned
python3 -I tools/codec.py textos
python3 -I tools/vox.py textos

echo "== cutscenes (DEMO.DAT)"
python3 -I tools/aplicar.py .
python3 -I tools/demosubs.py insert $F/DEMO.DAT legendas/demo_pt.json work/DEMO.DAT > work/demo_insert.log

echo "== codec (RADIO.DAT)"
python3 -I tools/codec.py aplicar
python3 -I tools/radio.py insert $F/RADIO.DAT legendas/radio_pt.json work/RADIO.DAT > work/radio_insert.log
grep -c "chamada" work/radio_insert.log | xargs echo "chamadas gravadas:"

echo "== vozes (VOX.DAT)"
python3 -I tools/vox.py aplicar
python3 -I tools/demosubs.py insert $F/VOX.DAT legendas/vox_pt.json work/VOX.DAT > work/vox_insert.log

echo "== imagem"
python3 -I tools/patchbin.py "$ORIG" "$OUT" 2820 $F/DEMO.DAT work/DEMO.DAT
python3 -I tools/patchbin.py "$OUT" "$OUT" 130873 $F/RADIO.DAT work/RADIO.DAT
python3 -I tools/patchbin.py "$OUT" "$OUT" 173340 $F/VOX.DAT work/VOX.DAT
echo "== executavel (ingles por padrao)"
python3 -I tools/exe_patch.py $F/SLPM_862.47 work/SLPM_862.47
python3 -I tools/patchbin.py "$OUT" "$OUT" 136341 $F/SLPM_862.47 work/SLPM_862.47

echo "== videos (ZMOVIE.STR, direto na imagem)"
python3 -I tools/movie.py insert "$OUT" legendas/movie_pt.json
python3 -I tools/psxiso.py "$OUT" extract work/verify MGS/DEMO.DAT MGS/RADIO.DAT MGS/VOX.DAT > /dev/null
cmp work/verify/MGS/DEMO.DAT work/DEMO.DAT
cmp work/verify/MGS/RADIO.DAT work/RADIO.DAT
cmp work/verify/MGS/VOX.DAT work/VOX.DAT
printf 'FILE "MGS Integral PT-BR (Disc 1).bin" BINARY\n  TRACK 01 MODE2/2352\n    INDEX 01 00:00:00\n' > "patched/MGS Integral PT-BR (Disc 1).cue"
echo "OK -> patched/MGS Integral PT-BR (Disc 1).cue"
