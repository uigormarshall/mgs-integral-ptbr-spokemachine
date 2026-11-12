#!/usr/bin/env python3
"""Merge translations (demo_cena1.json + legendas/lote*.py) into legendas/demo_pt.json
and report byte usage per chunk.

usage: aplicar.py BASE_DIR
"""
import glob, json, os, sys

sys.path.insert(0, os.path.dirname(__file__))
from demosubs import build_records  # noqa: E402

base = sys.argv[1]
leg = os.path.join(base, "legendas")
chunks = json.load(open(os.path.join(leg, "demo_all.json")))
by_off = {c["offset"]: c for c in chunks}

for c in json.load(open(os.path.join(leg, "demo_cena1.json"))):
    for dst, src in zip(by_off[c["offset"]]["lines"], c["lines"]):
        dst["pt"] = src["pt"]

ok = True
for path in sorted(glob.glob(os.path.join(leg, "lote*.py"))):
    ns = {}
    exec(open(path, encoding="utf-8").read(), ns)
    for idx, lines in ns["T"].items():
        ch = chunks[idx]
        if len(lines) != len(ch["lines"]):
            print(f"{os.path.basename(path)} #{idx}: {len(lines)} falas, esperado {len(ch['lines'])}")
            ok = False
            continue
        for l, t in zip(ch["lines"], lines):
            l["pt"] = t.replace(" / ", "\n").strip()

over = 0
done = 0
for i, ch in enumerate(chunks):
    if not any(l.get("pt") for l in ch["lines"]):
        continue
    done += 1
    room = ch["font_off"] - ch["sub_off"]
    used = len(build_records(ch["lines"]))
    if used > room:
        over += 1
        print(f"#{i}: {used}/{room} (+{used - room} bytes)")

json.dump(chunks, open(os.path.join(leg, "demo_pt.json"), "w"), ensure_ascii=False, indent=1)
print(f"{done}/{len(chunks)} blocos traduzidos, {over} estourando")
sys.exit(0 if ok and not over else 1)
