#!/usr/bin/env python3
"""Minimal ISO9660 reader for raw MODE2/2352 PS1 images.
usage: psxiso.py IMAGE.bin list
       psxiso.py IMAGE.bin extract OUTDIR [NAME ...]   (no names = all files)
"""
import os, struct, sys

SECTOR = 2352
DATA_OFF = 24  # MODE2 Form1: 12 sync + 4 header + 8 subheader


def read_sectors(f, lba, count):
    out = bytearray()
    for i in range(count):
        f.seek((lba + i) * SECTOR + DATA_OFF)
        out += f.read(2048)
    return bytes(out)


def walk(f, lba, size, path=""):
    data = read_sectors(f, lba, (size + 2047) // 2048)
    pos = 0
    while pos < len(data):
        ln = data[pos]
        if ln == 0:
            pos = (pos // 2048 + 1) * 2048
            continue
        rec = data[pos:pos + ln]
        elba = struct.unpack_from("<I", rec, 2)[0]
        esize = struct.unpack_from("<I", rec, 10)[0]
        flags = rec[25]
        nlen = rec[32]
        name = rec[33:33 + nlen]
        pos += ln
        if name in (b"\x00", b"\x01"):
            continue
        name = name.decode("ascii", "replace").split(";")[0]
        full = f"{path}/{name}"
        if flags & 2:
            yield from walk(f, elba, esize, full)
        else:
            yield full, elba, esize


def main():
    img, cmd = sys.argv[1], sys.argv[2]
    with open(img, "rb") as f:
        pvd = read_sectors(f, 16, 1)
        assert pvd[1:6] == b"CD001", "not ISO9660"
        root = pvd[156:156 + 34]
        rlba = struct.unpack_from("<I", root, 2)[0]
        rsize = struct.unpack_from("<I", root, 10)[0]
        files = list(walk(f, rlba, rsize))
        if cmd == "list":
            for p, lba, size in files:
                print(f"{lba:8d} {size:12d} {p}")
        elif cmd == "extract":
            outdir = sys.argv[3]
            want = set(sys.argv[4:])
            for p, lba, size in files:
                if want and p.lstrip("/") not in want:
                    continue
                dst = os.path.join(outdir, p.lstrip("/"))
                os.makedirs(os.path.dirname(dst), exist_ok=True)
                with open(dst, "wb") as o:
                    o.write(read_sectors(f, lba, (size + 2047) // 2048)[:size])
                print("extracted", p, size)


if __name__ == "__main__":
    main()
