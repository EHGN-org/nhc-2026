#!/usr/bin/env python3
import base64
from itertools import cycle

from Crypto.Cipher import AES
from Crypto.Util.number import long_to_bytes
from Crypto.Util.Padding import unpad
from z3 import BitVec, Solver, sat

a = "hC_Zyp{CHN"[::-1]

b = base64.b64decode(
    base64.b32decode(base64.b85decode(b"N>y1!G&EF1M@2MMPgyfdNlHjYQ8ijMNL4*OJv}`="))
).decode()

cipher = AES.new(b"The fun has only", AES.MODE_CBC, b"just begun. glhf")
c = unpad(cipher.decrypt(b"\x00\xd3\x0cV5\x86\xc0;a\xf1W+P\xae@W"), AES.block_size).decode()

KEY = "KEY"
ALPHABET = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ_abcdefghijklmnopqrstuvwxyz{}"
out = []
for ch, k in zip("tiZ_HuNeat", cycle(KEY)):
    ch = ALPHABET.index(ch)
    k = ALPHABET.index(k)
    out.append(ord(ALPHABET[(ch + (len(ALPHABET) - k)) % len(ALPHABET)]))
d = bytes(out).decode()

s = Solver()
x = BitVec("x", 10 * 8)
s.add((1337 * x + 424242) % 256**10 == 834116172812670004082183)
assert s.check() == sat
e = long_to_bytes(s.model()[x].as_long()).decode()

print([a, b, c, d, e])
print(a + b + c + d + e)
