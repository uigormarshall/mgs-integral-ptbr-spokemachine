#!/usr/bin/env python3
"""Force English (GM_CONFIG_ENGLISH = 0x100) every frame in SLPM_862.47,
keeping the original vibration logic intact.

gamed.c Act(), original:
  8002adf8 lhu  v0,4(v1)        ; DualShock path
  8002adfc j    8002ae14
  8002ae00 andi v0,v0,0xfbff    ;   clear VIBRATION_OFF
  8002ae04 addiu v1,v1,0x4d98   ; other pads
  8002ae08 lhu  v0,4(v1)
  8002ae0c nop
  8002ae10 ori  v0,v0,0x400     ;   set VIBRATION_OFF
  8002ae14 sh   v0,4(v1)
patched:
  8002adfc j    8002ae10        ; DualShock path also gets the English ori
  8002ae04 lhu  v0,0x4d9c(v1)   ; same address, loaded before v1 is adjusted
  8002ae08 addiu v1,v1,0x4d98   ;   (fills the load delay slot)
  8002ae0c ori  v0,v0,0x400     ; other pads: VIBRATION_OFF as before
  8002ae10 ori  v0,v0,0x100     ; everyone: ENGLISH
v1 = 0x800b0000 from the lui in the branch delay slot (8002adf0).

usage: exe_patch.py ORIG_SLPM OUT_SLPM
"""
import struct, sys

PATCHES = [  # file offset, original word, new word
    (0x1B5FC, 0x0800AB85, 0x0800AB84),
    (0x1B604, 0x24634D98, 0x94624D9C),
    (0x1B608, 0x94620004, 0x24634D98),
    (0x1B60C, 0x00000000, 0x34420400),
    (0x1B610, 0x34420400, 0x34420100),
]

d = bytearray(open(sys.argv[1], "rb").read())
for off, old, new in PATCHES:
    cur = struct.unpack_from("<I", d, off)[0]
    if cur != old:
        sys.exit(f"0x{off:x}: esperado {old:08x}, achado {cur:08x}")
    struct.pack_into("<I", d, off, new)
open(sys.argv[2], "wb").write(d)
print("executavel: ingles forcado")
