#!/usr/bin/env python3
"""Codec translation in batches (unique English lines of RADIO.DAT).

usage (run from ~/Downloads/MGS-Integral):
  codec.py preparar [--tamanho 150]   create legendas/codec/lote_NN_en.txt (once)
  codec.py status                     progress per batch
  codec.py proximo                    print next untranslated batch file name
  codec.py aplicar                    merge lote_NN_pt.txt -> legendas/radio_pt.json + fit report

Batch files:
  lote_NN_en.txt : "ID<TAB>English" (line breaks as " / ")
  lote_NN_pt.txt : "ID<TAB>Portuguese" (same IDs; " / " = line break). Accents OK (stripped on insert).
"""
import glob, hashlib, json, os, re, sys

BASE = os.getcwd()
LEG = os.path.join(BASE, "legendas")
DIR = os.path.join(LEG, "codec")
ALL = os.path.join(LEG, "radio_all.json")
DICT = os.path.join(DIR, "dicionario.json")


def h(t):
    """Key for an English line. The repo stores only this hash, never the game's text."""
    return hashlib.sha1(t.encode("utf-8")).hexdigest()[:16]


def textos(pairs):
    """Rebuild lote_NN_en.txt (English reference, not versioned) from (key, English) pairs read off the disc."""
    j = json.load(open(os.path.join(DIR, "ids.json")))
    idk = {i: k for k, i in list(j["ids"].items()) + list(j.get("curto", {}).items())}
    en = dict(pairs)
    for p in sorted(glob.glob(os.path.join(DIR, "lote_*_pt.txt"))):
        q = p[:-7] + "_en.txt"
        if os.path.exists(q):
            continue
        with open(q, "w") as o:
            for ln in open(p, encoding="utf-8"):
                i = ln.split("\t", 1)[0].strip()
                if i.isdigit():
                    o.write(f"{i}\t{flat(en.get(idk.get(int(i)), '?'))}\n")


def is_en(t):
    return all(ord(c) < 0x80 for c in t) and any(c.isalpha() for c in t)


def english_calls():
    r = json.load(open(ALL))
    return [f for f in r if sum(is_en(l["en"]) for l in f["lines"]) > len(f["lines"]) * 0.8]


def needs_translation(t):
    return bool(re.search(r"[A-Za-z]{2,}", t))


def flat(t):
    return t.replace("\n", " / ")


def preparar(size):
    os.makedirs(DIR, exist_ok=True)
    if glob.glob(os.path.join(DIR, "lote_*.txt")):
        sys.exit("lotes ja existem")
    seen, order = set(), []
    for f in english_calls():
        for l in f["lines"]:
            t = l["en"]
            if is_en(t) and needs_translation(t) and t not in seen:
                seen.add(t)
                order.append(t)
    ids = {t: i + 1 for i, t in enumerate(order)}
    json.dump({"ids": {h(t): i for t, i in ids.items()}}, open(os.path.join(DIR, "ids.json"), "w"), indent=0)
    for n in range(0, len(order), size):
        part = order[n:n + size]
        with open(os.path.join(DIR, f"lote_{n // size + 1:02d}_en.txt"), "w") as o:
            for t in part:
                o.write(f"{ids[t]}\t{flat(t)}\n")
    print(f"{len(order)} falas unicas em {(len(order) + size - 1) // size} lotes de ate {size}")


def load_pt():
    pt = {}
    for p in sorted(glob.glob(os.path.join(DIR, "lote_*_pt.txt"))):
        for ln in open(p, encoding="utf-8"):
            ln = ln.rstrip("\n")
            if not ln.strip():
                continue
            i, _, t = ln.partition("\t")
            pt[int(i)] = t.replace(" / ", "\n").strip()
    return pt


def lotes():
    out = []
    for p in sorted(glob.glob(os.path.join(DIR, "lote_*_en.txt"))):
        ids = [int(l.split("\t", 1)[0]) for l in open(p) if l.strip()]
        out.append((os.path.basename(p)[:7], ids, p))
    return out


def status():
    pt = load_pt()
    tot = done = 0
    for name, ids, _ in lotes():
        d = sum(i in pt for i in ids)
        tot += len(ids)
        done += d
        mark = "OK" if d == len(ids) else ("parcial" if d else "")
        print(f"{name}: {d:4d}/{len(ids):4d} {mark}")
    print(f"total: {done}/{tot} falas ({100 * done // max(tot, 1)}%)")


def proximo():
    pt = load_pt()
    for name, ids, p in lotes():
        if not all(i in pt for i in ids):
            print(p)
            return
    print("todos os lotes traduzidos")


def aplicar():
    ids = json.load(open(os.path.join(DIR, "ids.json")))["ids"]
    pt = load_pt()
    calls = english_calls()
    n = 0
    for f in calls:
        for l in f["lines"]:
            i = ids.get(h(l["en"]))
            if i and i in pt:
                l["pt"] = pt[i]
                n += 1
    calls = [f for f in calls if any(l.get("pt") for l in f["lines"])]
    json.dump(calls, open(os.path.join(LEG, "radio_pt.json"), "w"), ensure_ascii=False, indent=1)
    print(f"{n} ocorrencias traduzidas em {len(calls)} chamadas -> legendas/radio_pt.json")


if __name__ == "__main__":
    c = sys.argv[1]
    if c == "preparar":
        preparar(int(sys.argv[sys.argv.index("--tamanho") + 1]) if "--tamanho" in sys.argv else 150)
    elif c == "status":
        status()
    elif c == "proximo":
        proximo()
    elif c == "aplicar":
        aplicar()
    elif c == "textos":
        textos((h(l["en"]), l["en"]) for f in english_calls() for l in f["lines"])
