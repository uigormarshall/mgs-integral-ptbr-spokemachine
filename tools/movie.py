#!/usr/bin/env python3
"""Extract / reinsert FMV subtitles in ZMOVIE.STR, working directly on the raw .bin.

Format (mgs_reversing source/game/movie.c):
  STR stream sectors (Form1): 32-byte header + 2016 bytes payload.
    header: u16 0x0160, u16 type, u16 sector_index, u16 n_sectors, u32 frame, ...
  type 0x8001 = video frame. Other types = subtitle/font "frame":
    payload concatenated over n_sectors; short @0xA = subtitle list offset,
    int @0xC = embedded font offset. Subtitle records like DEMO.DAT:
    i32 size, i32 start, i32 duration, i32 0, text NUL (pad 4), last size = 0.
  XA audio sectors (Form2) are skipped and never written.

usage:
  movie.py extract IMAGE.bin OUT.json
  movie.py insert  IMAGE.bin IN.json        (patches IMAGE.bin in place, fixes EDC/ECC)
"""
import json, os, struct, sys

sys.path.insert(0, os.path.dirname(__file__))
from patchbin import fix_form1  # noqa: E402
from demosubs import decode, encode  # noqa: E402

LBA, SIZE = map(int, os.environ.get("MGS_ZMOVIE", "269128,47517696").split(","))
RAW, HDR, PAY = 2352, 32, 2016


def scan(f):
    """Return list of subtitle frames: {lbas:[...], type, frame, data}."""
    frames = {}
    n = (SIZE + 2047) // 2048
    for i in range(n):
        f.seek((LBA + i) * RAW)
        sec = f.read(RAW)
        if sec[18] & 0x20:  # Form2 (XA audio)
            continue
        h = sec[24:24 + HDR]
        magic, typ, idx, cnt = struct.unpack_from("<HHHH", h)
        frame = struct.unpack_from("<I", h, 8)[0]
        if magic != 0x0160 or typ == 0x8001:
            continue
        key = (LBA + i - idx, typ)
        fr = frames.setdefault(key, {"type": typ, "frame": frame, "count": cnt, "parts": {}})
        fr["parts"][idx] = (LBA + i, sec[24 + HDR:24 + HDR + PAY])
    out = []
    for (start, typ), fr in sorted(frames.items()):
        if len(fr["parts"]) != fr["count"]:
            continue
        lbas = [fr["parts"][k][0] for k in range(fr["count"])]
        data = b"".join(fr["parts"][k][1] for k in range(fr["count"]))
        out.append({"lbas": lbas, "type": typ, "frame": fr["frame"], "data": data})
    return out


def parse(data):
    sub_off = struct.unpack_from("<h", data, 0xA)[0]
    font_off = struct.unpack_from("<i", data, 0xC)[0]
    recs = []
    q = sub_off
    while 0 <= q < len(data) - 16:
        size, st, dur, z = struct.unpack_from("<iiii", data, q)
        if size == 0 and st == 0 and dur == 0:
            break
        text = data[q + 16:q + (size if size else 0x400)].split(b"\x00", 1)[0]
        recs.append({"start": st, "duration": dur, "raw": text})
        if size <= 0:
            break
        q += size
    return sub_off, font_off, recs


def build(lines):
    out = bytearray()
    for i, ln in enumerate(lines):
        t = encode(ln["pt"]) if ln.get("pt") else ln["raw"]
        t += b"\x00"
        t += b"\x00" * (-len(t) % 4)
        size = 0 if i == len(lines) - 1 else 16 + len(t)
        out += struct.pack("<iiii", size, ln["start"], ln["duration"], 0) + t
    return out


def is_en(b):
    return all(c < 0x80 or c == 0x80 for c in b) and any(65 <= c <= 122 for c in b)


def main():
    cmd, img = sys.argv[1], sys.argv[2]
    if cmd == "extract":
        res = []
        with open(img, "rb") as f:
            for fr in scan(f):
                sub_off, font_off, recs = parse(fr["data"])
                if not recs or not all(is_en(r["raw"].replace(b"\x80|", b" ")) for r in recs):
                    continue
                res.append({"lbas": fr["lbas"], "type": fr["type"], "sub_off": sub_off, "font_off": font_off,
                            "lines": [{"start": r["start"], "duration": r["duration"], "en": decode(r["raw"])} for r in recs]})
        json.dump(res, open(sys.argv[3], "w"), ensure_ascii=False, indent=1)
        print(f"{len(res)} videos com legenda em ingles, {sum(len(r['lines']) for r in res)} falas")
    elif cmd == "juntar":  # movie.py juntar ALL.json TR.json OUT.json  (TR = [{lbas, pt:[...]}], no English)
        tr = {tuple(t["lbas"]): t["pt"] for t in json.load(open(sys.argv[3]))}
        res = [c for c in json.load(open(img)) if tuple(c["lbas"]) in tr]
        for c in res:
            for l, p in zip(c["lines"], tr[tuple(c["lbas"])]):
                if p:
                    l["pt"] = p
        json.dump(res, open(sys.argv[4], "w"), ensure_ascii=False, indent=1)
    elif cmd == "insert":
        tr = json.load(open(sys.argv[3]))
        with open(img, "r+b") as f:
            frames = {tuple(fr["lbas"]): fr for fr in scan(f)}
            for t in tr:
                if not any(l.get("pt") for l in t["lines"]):
                    continue
                fr = frames[tuple(t["lbas"])]
                data = bytearray(fr["data"])
                sub_off, font_off, recs = parse(bytes(data))
                for r, l in zip(recs, t["lines"]):
                    r["pt"] = l.get("pt")
                blob = build(recs)
                end = font_off if font_off > sub_off else len(data)
                room = end - sub_off
                if len(blob) > room:
                    sys.exit(f"video {t['lbas'][0]}: {len(blob)} > {room} bytes; encurtar")
                data[sub_off:sub_off + len(blob)] = blob
                data[sub_off + len(blob):end] = b"\x00" * (room - len(blob))
                for k, lba in enumerate(t["lbas"]):
                    f.seek(lba * RAW)
                    sec = bytearray(f.read(RAW))
                    assert not (sec[18] & 0x20)
                    sec[24 + HDR:24 + HDR + PAY] = data[k * PAY:(k + 1) * PAY]
                    fix_form1(sec)
                    f.seek(lba * RAW)
                    f.write(sec)
                print(f"video {t['lbas'][0]}: {len(blob)}/{room} bytes")


if __name__ == "__main__":
    main()
