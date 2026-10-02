#!/usr/bin/env python3
from pwn import *

# r = process(["python", "chall.py"])
r = remote("localhost", 1337)


def encrypt(mode, plaintext=None):
    r.sendlineafter(b"Mode [ECB/CBC/CTR]: ", mode.encode())
    r.sendlineafter(
        b"Encrypt [flag/custom]: ", b"flag" if plaintext is None else b"custom"
    )
    if plaintext is not None:
        r.sendlineafter(b"Custom text (hex): ", plaintext.hex().encode())
    r.recvline()
    return bytes.fromhex(r.recvline().decode())


# CTR mode = pt ^ aes(nonce + counter)
flag_ct = encrypt("CTR")
nonce, flag_ct = flag_ct[:8], flag_ct[8:]

# Recreate counter with ECB
keystream = b""
for i in range(len(flag_ct) // 16 + 1):
    # Need [:16] here to cut off padding
    keystream += encrypt("ECB", nonce + i.to_bytes(8, byteorder="big"))[:16]

flag = xor(flag_ct, keystream)
print(flag)
