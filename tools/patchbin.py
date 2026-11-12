#!/usr/bin/env python3
"""Write a modified file back into a raw MODE2/2352 image at its original LBA,
recomputing EDC/ECC for every changed Form1 sector. File size must not change.

usage: patchbin.py ORIG.bin OUT.bin LBA ORIG_FILE NEW_FILE
"""
import shutil, sys

SECTOR = 2352


def _tables():
    ecc_f = [0] * 256
    ecc_b = [0] * 256
    edc = [0] * 256
    for i in range(256):
        j = (i << 1) ^ (0x11D if i & 0x80 else 0)
        ecc_f[i] = j & 0xFF
        ecc_b[i ^ j] = i
        e = i
        for _ in range(8):
            e = (e >> 1) ^ (0xD8018001 if e & 1 else 0)
        edc[i] = e
    return ecc_f, ecc_b, edc


ECC_F, ECC_B, EDC_T = _tables()


def edc_compute(data):
    e = 0
    for b in data:
        e = (e >> 8) ^ EDC_T[(e ^ b) & 0xFF]
    return e


def ecc_part(sec, major_count, minor_count, major_mult, minor_inc, out_off):
    size = major_count * minor_count
    for major in range(major_count):
        index = (major >> 1) * major_mult + (major & 1)
        a = b = 0
        for _ in range(minor_count):
            t = sec[12 + index]
            index += minor_inc
            if index >= size:
                index -= size
            a ^= t
            b ^= t
            a = ECC_F[a]
        a = ECC_B[ECC_F[a] ^ b]
        sec[out_off + major] = a
        sec[out_off + major + major_count] = a ^ b


def fix_form1(sec):
    sec[0x818:0x81C] = edc_compute(sec[16:0x818]).to_bytes(4, "little")
    saved = bytes(sec[12:16])
    sec[12:16] = b"\x00\x00\x00\x00"  # Mode2: header excluded from ECC
    ecc_part(sec, 86, 24, 2, 86, 0x81C)   # P
    ecc_part(sec, 52, 43, 86, 88, 0x8C8)  # Q
    sec[12:16] = saved


def main():
    orig_bin, out_bin, lba, orig_f, new_f = sys.argv[1], sys.argv[2], int(sys.argv[3]), sys.argv[4], sys.argv[5]
    a = open(orig_f, "rb").read()
    b = open(new_f, "rb").read()
    assert len(a) == len(b), "file size changed"
    if orig_bin != out_bin:
        shutil.copyfile(orig_bin, out_bin)
    changed = 0
    with open(out_bin, "r+b") as f:
        for i in range(0, len(a), 2048):
            if a[i:i + 2048] == b[i:i + 2048]:
                continue
            pos = (lba + i // 2048) * SECTOR
            f.seek(pos)
            sec = bytearray(f.read(SECTOR))
            assert not (sec[18] & 0x20), "Form2 sector, refusing"
            sec[24:24 + 2048] = b[i:i + 2048].ljust(2048, b"\x00")
            fix_form1(sec)
            f.seek(pos)
            f.write(sec)
            changed += 1
    print(f"{changed} sectors rewritten")


if __name__ == "__main__":
    main()
