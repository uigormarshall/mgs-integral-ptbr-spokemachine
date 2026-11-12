#!/usr/bin/env python3
"""Extract / reinsert English cutscene subtitles (stream chunk type 6) in MGS Integral DEMO.DAT.

Chunk layout (libfs/stream.c): u32 header = type | (size << 8), size includes header.
Subtitle chunk payload (game/jimctrl.c SubtitleHeader):
  i32 start, i32 end, i16 data_offset, i16 subtitle_offset, i32 font_offset
  records at subtitle_offset: i32 size, i32 start, i32 duration, i32 0, char text[] (NUL, pad 4)
  last record has size 0. Line break inside text = b"\\x80|".

usage:
  demosubs.py extract DEMO.DAT OUT.json [--max-chunks N]
  demosubs.py insert  DEMO.DAT IN.json OUT_DEMO.DAT
"""
import json, struct, sys

SUB_TYPE = 6
NL = b"\x80|"


def iter_chunks(d):
    p = 0
    n = len(d)
    while p + 4 <= n:
        h = struct.unpack_from("<I", d, p)[0]
        t, s = h & 0xFF, h >> 8
        if t == 0xFF or s == 0 or p + s > n:
            p = (p // 0x800 + 1) * 0x800  # padding to next sector
            continue
        yield p, t, s
        p += s


def decode(b):
    return b.replace(NL, b"\n").decode("latin-1")


def encode(s):
    # Game font has no accented glyphs yet: strip diacritics (ã->a, ç->c).
    import unicodedata
    s = "".join(ch for ch in unicodedata.normalize("NFKD", s) if not unicodedata.combining(ch))
    # {9C01} = raw game bytes (quotes / button icon codes)
    import re
    out = b""
    for part in re.split(r"(\{[0-9A-Fa-f]{2,}\})", s):
        out += bytes.fromhex(part[1:-1]) if part.startswith("{") else part.encode("ascii")
    return out.replace(b"\n", NL)


def parse_chunk(d, p, s):
    base = p + 4
    start, end, data_off, sub_off, font_off = struct.unpack_from("<iihhi", d, base)
    recs = []
    q = base + sub_off
    while True:
        size, rs, dur, zero = struct.unpack_from("<iiii", d, q)
        if size == 0 and rs == 0 and dur == 0:
            break
        raw = d[q + 16:q + (size if size else 0x1000)]
        text = raw.split(b"\x00", 1)[0]
        recs.append({"start": rs, "duration": dur, "en": decode(text)})
        if size == 0:
            break
        q += size
    return {"offset": p, "chunk_size": s, "sub_off": sub_off, "font_off": font_off, "lines": recs}


def build_records(lines):
    out = bytearray()
    for i, ln in enumerate(lines):
        text = encode(ln["pt"]) if ln.get("pt") else ln["en"].encode("latin-1").replace(b"\n", NL)
        text += b"\x00"
        text += b"\x00" * (-len(text) % 4)
        size = 0 if i == len(lines) - 1 else 16 + len(text)
        out += struct.pack("<iiii", size, ln["start"], ln["duration"], 0) + text
    return out


def main():
    cmd = sys.argv[1]
    if cmd == "extract":
        d = open(sys.argv[2], "rb").read()
        maxc = int(sys.argv[sys.argv.index("--max-chunks") + 1]) if "--max-chunks" in sys.argv else None
        chunks = []
        for p, t, s in iter_chunks(d):
            if t == SUB_TYPE:
                c = parse_chunk(d, p, s)
                if c["lines"]:
                    chunks.append(c)
                    if maxc and len(chunks) >= maxc:
                        break
        json.dump(chunks, open(sys.argv[3], "w"), ensure_ascii=False, indent=1)
        print(f"{len(chunks)} chunks, {sum(len(c['lines']) for c in chunks)} lines")
    elif cmd == "insert":
        d = bytearray(open(sys.argv[2], "rb").read())
        chunks = json.load(open(sys.argv[3]))
        for c in chunks:
            if not any(l.get("pt") for l in c["lines"]):
                continue
            p = c["offset"]
            rec_start = p + 4 + c["sub_off"]
            # space available: up to the embedded font (or chunk end)
            limit = p + 4 + c["font_off"] if c["font_off"] else p + c["chunk_size"]
            limit = min(limit, p + c["chunk_size"])
            blob = build_records(c["lines"])
            room = limit - rec_start
            if len(blob) > room:
                sys.exit(f"chunk @0x{p:x}: {len(blob)} bytes > {room} available; shorten text")
            d[rec_start:rec_start + len(blob)] = blob
            d[rec_start + len(blob):limit] = b"\x00" * (room - len(blob))
            print(f"chunk @0x{p:x}: {len(blob)}/{room} bytes")
        open(sys.argv[4], "wb").write(d)


if __name__ == "__main__":
    main()
