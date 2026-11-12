#!/usr/bin/env bash
# Rebuild the patched DISC 2 image from the original + all translations.
set -euo pipefail
cd "$(dirname "$0")/.."
ORIG="disc2/Metal Gear Solid - Integral (Japan) (En,Ja) (Disc 2).bin"
OUT="patched/MGS Integral PT-BR (Disc 2).bin"
F=disc2/files/MGS
L=legendas/disc2
W=work/disc2
mkdir -p $W patched
[ -f $F/DEMO.DAT ] || python3 -I tools/psxiso.py "$ORIG" extract disc2/files MGS/DEMO.DAT MGS/RADIO.DAT MGS/VOX.DAT MGS/SLPM_862.48 > /dev/null
[ -f $L/demo_all.json ] || python3 -I tools/demosubs.py extract $F/DEMO.DAT $L/demo_all.json
[ -f $L/vox_all.json ] || python3 -I tools/demosubs.py extract $F/VOX.DAT $L/vox_all.json
[ -f $L/radio_all.json ] || python3 -I tools/radio.py extract $F/RADIO.DAT $L/radio_all.json
[ -f $L/movie_all.json ] || MGS_ZMOVIE=234052,142098432 python3 -I tools/movie.py extract "$ORIG" $L/movie_all.json
[ -f legendas/radio_pt.json ] || { echo "monte o disco 1 primeiro (tools/montar.sh)"; exit 1; }
python3 -I tools/disco2.py textos

python3 -I tools/disco2.py aplicar
python3 -I tools/demosubs.py insert $F/DEMO.DAT $L/demo_pt.json $W/DEMO.DAT > $W/demo.log
python3 -I tools/radio.py insert $F/RADIO.DAT $L/radio_pt.json $W/RADIO.DAT > $W/radio.log
python3 -I tools/demosubs.py insert $F/VOX.DAT $L/vox_pt.json $W/VOX.DAT > $W/vox.log
python3 -I tools/exe_patch.py $F/SLPM_862.48 $W/SLPM_862.48

python3 -I tools/patchbin.py "$ORIG" "$OUT" 2820 $F/DEMO.DAT $W/DEMO.DAT
python3 -I tools/patchbin.py "$OUT" "$OUT" 99397 $F/RADIO.DAT $W/RADIO.DAT
python3 -I tools/patchbin.py "$OUT" "$OUT" 104865 $F/SLPM_862.48 $W/SLPM_862.48
python3 -I tools/patchbin.py "$OUT" "$OUT" 141864 $F/VOX.DAT $W/VOX.DAT
MGS_ZMOVIE=234052,142098432 python3 -I tools/movie.py insert "$OUT" $L/movie_pt.json

python3 -I tools/psxiso.py "$OUT" extract $W/verify MGS/DEMO.DAT MGS/RADIO.DAT MGS/VOX.DAT > /dev/null
for f in DEMO RADIO VOX; do cmp $W/verify/MGS/$f.DAT $W/$f.DAT; done
printf 'FILE "MGS Integral PT-BR (Disc 2).bin" BINARY\n  TRACK 01 MODE2/2352\n    INDEX 01 00:00:00\n' > "patched/MGS Integral PT-BR (Disc 2).cue"
printf 'MGS Integral PT-BR (Disc 1).cue\nMGS Integral PT-BR (Disc 2).cue\n' > "patched/MGS Integral PT-BR.m3u"
echo "OK -> patched/MGS Integral PT-BR (Disc 2).cue (+ .m3u)"
