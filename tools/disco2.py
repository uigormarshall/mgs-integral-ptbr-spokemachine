#!/usr/bin/env python3
"""Disc 2: reuse every disc-1 translation (by English text) and batch only the new lines.

usage (run from ~/Downloads/MGS-Integral):
  disco2.py preparar     new unique lines (cutscenes+voices+videos) -> legendas/disc2/lotes/lote_NN_en.txt
  disco2.py status | proximo
  disco2.py curto        lote_99: shorter versions for cutscene/voice chunks that overflow
  disco2.py aplicar      -> legendas/disc2/{demo,radio,vox,movie}_pt.json
Batch format = codec (ID<TAB>text, " / " = line break).
"""
import glob, json, os, re, sys

sys.path.insert(0, os.path.dirname(__file__))
import codec  # noqa: E402
from demosubs import build_records  # noqa: E402

LEG1 = codec.LEG
LEG = os.path.join(LEG1, "disc2")
codec.DIR = os.path.join(LEG, "lotes")
IDS = os.path.join(codec.DIR, "ids.json")
KINDS = ["demo", "vox", "movie"]  # chunk-style subtitle files with fixed space


def norm(s):
    return re.sub(r"\W+", " ", s.replace("\r", "\n")).strip().lower()


def key(t):
    return codec.h(norm(t))


def en(l):
    return l["en"].replace("\r", "\n")


def ok(t):
    return codec.is_en(t) and codec.needs_translation(t)


def disc1():
    k = {}
    for f in ["demo_pt.json", "vox_pt.json", "movie_pt.json", "radio_pt.json"]:
        for c in json.load(open(os.path.join(LEG1, f))):
            for l in c["lines"]:
                if l.get("pt"):
                    k.setdefault(norm(l["en"]), l["pt"])
    mf = os.path.join(LEG1, "vox", "manual.json")  # keyed by codec.h(english)
    man = json.load(open(mf)) if os.path.exists(mf) else {}
    for c in json.load(open(os.path.join(LEG1, "vox_all.json"))):
        for l in c["lines"]:
            if codec.h(en(l)) in man:
                k[norm(en(l))] = man[codec.h(en(l))]
    return k


def load(kind):
    return json.load(open(os.path.join(LEG, f"{kind}_all.json")))


def preparar(size):
    os.makedirs(codec.DIR, exist_ok=True)
    if glob.glob(os.path.join(codec.DIR, "lote_*.txt")):
        sys.exit("lotes ja existem")
    k = disc1()
    seen, order = set(), []
    for kind in KINDS:
        for c in load(kind):
            for l in c["lines"]:
                t = en(l)
                if ok(t) and norm(t) not in k and norm(t) not in seen:
                    seen.add(norm(t))
                    order.append(t)
    ids = {t: i + 1 for i, t in enumerate(order)}
    json.dump({"ids": {key(t): i for t, i in ids.items()}}, open(IDS, "w"), indent=0)
    for n in range(0, len(order), size):
        with open(os.path.join(codec.DIR, f"lote_{n // size + 1:02d}_en.txt"), "w") as o:
            for t in order[n:n + size]:
                o.write(f"{ids[t]}\t{codec.flat(t)}\n")
    print(f"{len(order)} falas novas em {(len(order) + size - 1) // size} lotes")


def lookup():
    k = disc1()
    j = json.load(open(IDS))
    pt = codec.load_pt()
    curto = {t: pt[i] for t, i in j.get("curto", {}).items() if i in pt}
    new = {t: pt[i] for t, i in j["ids"].items() if i in pt}
    af = os.path.join(codec.DIR, "ajustes.json")  # {current pt (" / " breaks): shorter pt}
    aj = {a.replace(" / ", "\n"): b.replace(" / ", "\n") for a, b in (json.load(open(af)).items() if os.path.exists(af) else [])}

    def get(t):
        p = curto.get(key(t)) or new.get(key(t)) or k.get(norm(t))
        return aj.get(p, p)
    return get


def fill(kind, get):
    res = []
    for c in load(kind):
        for l in c["lines"]:
            p = get(en(l))
            if p:
                l["pt"] = p
        if any(l.get("pt") for l in c["lines"]):
            if kind == "movie":
                res.append((c, 0))  # movie.py checks space itself
                continue
            room = (c["font_off"] or c["chunk_size"] - 4) - c["sub_off"]
            res.append((c, len(build_records(c["lines"])) - room))
    return res


def curto():
    j = json.load(open(IDS))
    cur = j.setdefault("curto", {})
    get = lookup()
    want = {}
    for kind in ["demo", "vox"]:
        for c, over in fill(kind, get):
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
    have = set()
    p99 = os.path.join(codec.DIR, "lote_99_pt.txt")
    if os.path.exists(p99):
        have = {int(x.split("\t")[0]) for x in open(p99) if "\t" in x}
    with open(os.path.join(codec.DIR, "lote_99_en.txt"), "a") as o:
        for t, (p, mx) in want.items():
            i = cur.setdefault(key(t), 100000 + len(cur) + 1)
            if i in have:  # already shortened once and still too long: ask again
                lines = [x for x in open(p99) if not x.startswith(f"{i}\t")]
                open(p99, "w").writelines(lines)
            o.write(f"{i}\t{codec.flat(t)}   [atual: {codec.flat(p)}]   [max {mx} letras]\n")
    json.dump(j, open(IDS, "w"), indent=0)
    print(f"{len(want)} falas para encurtar -> {codec.DIR}/lote_99_en.txt")


def aplicar():
    get = lookup()
    for kind in KINDS:
        out, over, n = [], [], 0
        allc = load(kind)
        for c, ov in fill(kind, get):
            if ov > 0:
                over.append(f"@0x{c['offset']:x} +{ov}")
                continue
            n += sum(1 for l in c["lines"] if l.get("pt"))
            out.append(c)
        json.dump(out, open(os.path.join(LEG, f"{kind}_pt.json"), "w"), ensure_ascii=False, indent=1)
        print(f"{kind}: {n} falas em {len(out)}/{len(allc)} blocos" + (f"; {len(over)} nao couberam: {' '.join(over[:15])}" if over else ""))
    calls = [f for f in json.load(open(os.path.join(LEG, "radio_all.json")))
             if sum(codec.is_en(l["en"]) for l in f["lines"]) > len(f["lines"]) * 0.8]
    n = 0
    for f in calls:
        for l in f["lines"]:
            p = get(l["en"]) if codec.is_en(l["en"]) else None
            if p:
                l["pt"] = p
                n += 1
    calls = [f for f in calls if any(l.get("pt") for l in f["lines"])]
    json.dump(calls, open(os.path.join(LEG, "radio_pt.json"), "w"), ensure_ascii=False, indent=1)
    print(f"codec: {n} falas em {len(calls)} chamadas")


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
        codec.textos((key(en(l)), en(l)) for k in KINDS for c in load(k) for l in c["lines"])
