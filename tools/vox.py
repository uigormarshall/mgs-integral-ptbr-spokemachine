#!/usr/bin/env python3
"""VOX.DAT subtitles (voice streams: opening talk, briefing...). Same chunk format as DEMO.DAT.
Lines already translated in cutscenes/codec are reused; the rest goes to batches like the codec.

usage (run from ~/Downloads/MGS-Integral):
  vox.py preparar [--tamanho 150]   create legendas/vox/lote_NN_en.txt (once)
  vox.py status | proximo           same as codec.py
  vox.py curto                      batch lote_99: shorter versions for chunks that overflow
  vox.py aplicar                    reused + batches -> legendas/vox_pt.json (chunks that
                                    don't fit stay in English and are listed)
"""
import glob, json, os, re, sys

sys.path.insert(0, os.path.dirname(__file__))
import codec  # noqa: E402
from demosubs import build_records  # noqa: E402

LEG = codec.LEG
ALL = os.path.join(LEG, "vox_all.json")
codec.DIR = os.path.join(LEG, "vox")


def norm(s):
    return re.sub(r"\W+", " ", s).strip().lower()


def known():
    k = {}
    for c in json.load(open(os.path.join(LEG, "demo_pt.json"))):
        for l in c["lines"]:
            if l.get("pt"):
                k.setdefault(norm(l["en"]), l["pt"])
    for f in json.load(open(os.path.join(LEG, "radio_pt.json"))):
        for l in f["lines"]:
            if l.get("pt"):
                k.setdefault(norm(l["en"]), l["pt"])
    return k


def en(l):
    return l["en"].replace("\r", "\n")


def preparar(size):
    os.makedirs(codec.DIR, exist_ok=True)
    if glob.glob(os.path.join(codec.DIR, "lote_*.txt")):
        sys.exit("lotes ja existem")
    k = known()
    seen, order = set(), []
    for c in json.load(open(ALL)):
        for l in c["lines"]:
            t = en(l)
            if codec.is_en(t) and codec.needs_translation(t) and norm(t) not in k and t not in seen:
                seen.add(t)
                order.append(t)
    ids = {t: i + 1 for i, t in enumerate(order)}
    json.dump({"ids": {codec.h(t): i for t, i in ids.items()}}, open(os.path.join(codec.DIR, "ids.json"), "w"), indent=0)
    for n in range(0, len(order), size):
        with open(os.path.join(codec.DIR, f"lote_{n // size + 1:02d}_en.txt"), "w") as o:
            for t in order[n:n + size]:
                o.write(f"{ids[t]}\t{codec.flat(t)}\n")
    print(f"{len(order)} falas novas em {(len(order) + size - 1) // size} lotes")


def fill(chunks):
    """Apply translations; returns list of (chunk, overflow_bytes)."""
    k = known()
    j = json.load(open(os.path.join(codec.DIR, "ids.json")))
    ids, curto = j["ids"], j.get("curto", {})
    pt = codec.load_pt()
    mf = os.path.join(codec.DIR, "manual.json")  # {codec.h(english with \\n): pt} for lines with special codes
    manual = json.load(open(mf)) if os.path.exists(mf) else {}
    res = []
    for c in chunks:
        for l in c["lines"]:
            t = en(l)
            i = ids.get(codec.h(t))
            p = manual.get(codec.h(t)) or pt.get(curto.get(codec.h(t))) or (pt.get(i) if i else k.get(norm(t)))
            if p:
                l["pt"] = p
        if any(l.get("pt") for l in c["lines"]):
            room = (c["font_off"] or c["chunk_size"] - 4) - c["sub_off"]
            res.append((c, len(build_records(c["lines"])) - room))
    return res


def curto():
    """Batch lote_99: for each overflowing chunk, ask a shorter version of its longest line(s)."""
    path = os.path.join(codec.DIR, "ids.json")
    j = json.load(open(path))
    cur = j.setdefault("curto", {})
    want = {}
    for c, over in fill(json.load(open(ALL))):
        if over <= 0:
            continue
        ls = sorted((l for l in c["lines"] if l.get("pt")), key=lambda l: -len(l["pt"]))
        pick = ls[:1] if len(ls[0]["pt"]) - over - 4 >= len(ls[0]["pt"]) * 0.65 else ls[:2]
        cut = over // len(pick) + 4
        for l in pick:
            t = en(l)
            mx = len(l["pt"]) - cut
            if t not in want or mx < want[t][1]:
                want[t] = (l["pt"], mx)
    with open(os.path.join(codec.DIR, "lote_99_en.txt"), "w") as o:
        for t, (p, mx) in want.items():
            i = cur.setdefault(codec.h(t), 100000 + len(cur) + 1)
            o.write(f"{i}\t{codec.flat(t)}   [atual: {codec.flat(p)}]   [max {mx} letras]\n")
    json.dump(j, open(path, "w"), ensure_ascii=False, indent=0)
    print(f"{len(want)} falas para encurtar -> legendas/vox/lote_99_en.txt")


def aplicar():
    chunks = json.load(open(ALL))
    out, over, n = [], [], 0
    for c, ov in fill(chunks):
        if ov > 0:
            over.append(f"@0x{c['offset']:x} +{ov}")
            continue
        n += sum(1 for l in c["lines"] if l.get("pt"))
        out.append(c)
    json.dump(out, open(os.path.join(LEG, "vox_pt.json"), "w"), ensure_ascii=False, indent=1)
    print(f"{n} falas em {len(out)}/{len(chunks)} blocos -> legendas/vox_pt.json")
    if over:
        print(f"{len(over)} blocos nao couberam (ficam em ingles): {' '.join(over[:20])}")


if __name__ == "__main__":
    c = sys.argv[1]
    if c == "preparar":
        preparar(int(sys.argv[sys.argv.index("--tamanho") + 1]) if "--tamanho" in sys.argv else 150)
    elif c == "status":
        codec.status()
    elif c == "proximo":
        codec.proximo()
    elif c == "curto":
        curto()
    elif c == "aplicar":
        aplicar()
    elif c == "textos":
        codec.textos((codec.h(en(l)), en(l)) for c in json.load(open(ALL)) for l in c["lines"])
