#!/usr/bin/env python3
"""Extract / reinsert codec dialogue in MGS Integral RADIO.DAT.

Format (mgs_reversing source/menu/radiomes.c):
  Each call fragment starts on a 2048-byte sector:
    u16 freq, u32 BE faces(sectors<<24|start), u16 flags, then a BLOCK, then font data.
  BLOCK   = 0x80, u16 BE size, children..., 0x00      (total bytes = size + 1)
  COMMAND = 0xFF, code, u16 BE size, payload           (total bytes = size + 2)
  TALK (code 0x01) payload = u32 chara, u16 flags, text NUL.
  Font offset = block size + 1 (font follows the block), so growing text just shifts
  the font forward into the zero padding at the end of the fragment's sectors.
  Line break inside codec text: b"\\x80#\\x80N" (shown as "\\n" in JSON).

usage:
  radio.py extract RADIO.DAT OUT.json
  radio.py insert  RADIO.DAT IN.json OUT_RADIO.DAT
"""
import json, struct, sys, unicodedata

SECTOR = 2048
NL = b"\x80#\x80N"
TALK = 0x01


def be16(d, p):
    return (d[p] << 8) | d[p + 1]


class ParseError(Exception):
    pass


def parse_block(d, p, limit, chain, talks):
    """Parse BLOCK at p. chain = list of size-field offsets of ancestors."""
    if p + 3 > limit or d[p] != 0x80:
        raise ParseError
    size = be16(d, p + 1)
    end = p + size + 1
    if end > limit or size < 3:
        raise ParseError
    my = chain + [(p + 1, "block")]
    q = p + 3
    while True:
        if q >= end:
            raise ParseError
        if d[q] == 0x00:
            if q != end - 1:
                raise ParseError
            return end
        if d[q] != 0xFF:
            raise ParseError
        q = parse_cmd(d, q, end - 1, my, talks)


def parse_cmd(d, q, limit, chain, talks):
    code = d[q + 1]
    size = be16(d, q + 2)
    nxt = q + 2 + size
    if size < 2 or nxt > limit:
        raise ParseError
    my = chain + [(q + 2, "cmd")]
    pay, pend = q + 4, nxt
    if code == TALK:
        t0 = pay + 6
        z = d.index(b"\x00", t0, pend)
        talks.append({"pos": t0, "len": z - t0, "chain": my, "end": pend})
    else:
        # nested blocks may appear anywhere inside other commands' payloads
        i = pay
        while i < pend:
            if d[i] == 0x80:
                try:
                    sub = []
                    e = parse_block(d, i, pend, my, sub)
                    talks.extend(sub)
                    i = e
                    continue
                except (ParseError, ValueError):
                    pass
            i += 1
    return nxt


def fragments(d):
    for s in range(0, len(d), SECTOR):
        if d[s + 8] != 0x80:
            continue
        talks = []
        try:
            end = parse_block(d, s + 8, len(d), [], talks)
        except (ParseError, ValueError):
            continue
        if talks:
            yield s, end, talks


def decode(b):
    return b.replace(NL, b"\n").decode("latin-1")


def encode(s):
    s = "".join(ch for ch in unicodedata.normalize("NFKD", s) if not unicodedata.combining(ch))
    return s.encode("ascii").replace(b"\n", NL)


def frag_alloc_end(d, s, block_end):
    """End of this fragment's sector run: last non-zero byte after block, rounded up."""
    e = block_end
    nxt = ((block_end + SECTOR - 1) // SECTOR) * SECTOR
    return nxt, e


def main():
    cmd = sys.argv[1]
    d = open(sys.argv[2], "rb").read()
    if cmd == "extract":
        out = []
        for s, end, talks in fragments(d):
            out.append({
                "offset": s,
                "freq": be16(d, s),
                "lines": [{"pos": t["pos"], "en": decode(d[t["pos"]:t["pos"] + t["len"]])} for t in talks],
            })
        json.dump(out, open(sys.argv[3], "w"), ensure_ascii=False, indent=1)
        print(f"{len(out)} chamadas, {sum(len(f['lines']) for f in out)} falas")
    elif cmd == "insert":
        tr = json.load(open(sys.argv[3]))
        want = {f["offset"]: {l["pos"]: l["pt"] for l in f["lines"] if l.get("pt")} for f in tr}
        out = bytearray(d)
        for s, end, talks in fragments(d):
            reps = want.get(s)
            if not reps:
                continue
            # tail = everything after the block up to the end of the fragment's sectors
            alloc = ((end + SECTOR - 1) // SECTOR) * SECTOR
            frag = bytearray(d[s:alloc])
            base = s
            # apply from last talk to first so earlier offsets stay valid
            for t in sorted(talks, key=lambda t: -t["pos"]):
                if t["pos"] not in reps:
                    continue
                new = encode(reps[t["pos"]])
                delta = len(new) - t["len"]
                a = t["pos"] - base
                frag[a:a + t["len"]] = new
                for off, _kind in t["chain"]:
                    o = off - base
                    v = ((frag[o] << 8) | frag[o + 1]) + delta
                    if not 0 < v < 0x10000:
                        sys.exit("size overflow")
                    frag[o:o + 2] = v.to_bytes(2, "big")
            grow = len(frag) - (alloc - s)
            if grow > 0:
                tail = frag[-grow:]
                if any(tail):
                    room = (alloc - s) - len(bytes(frag).rstrip(b"\x00")) + grow
                    sys.exit(f"chamada @0x{s:x}: passou {grow} bytes do espaco (folga {room - grow})")
                frag = frag[:alloc - s]
            elif grow < 0:
                frag += b"\x00" * (-grow)
            # sanity: reparse
            chk = []
            parse_block(bytes(frag), 8, len(frag), [], chk)
            out[s:alloc] = frag
            used = len(bytes(frag).rstrip(b"\x00"))
            print(f"chamada @0x{s:x}: {used}/{alloc - s} bytes, {len(reps)} falas")
        open(sys.argv[4], "wb").write(out)


if __name__ == "__main__":
    main()
