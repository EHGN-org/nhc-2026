#!/usr/bin/env python3
from hashlib import sha256
from pwn import *
import hmac

KEY = b"This key is actually the same on production if you can believe it"
msg = b"Give me the flag pleeeeeaaase"

hash = hmac.new(KEY, msg, sha256).hexdigest()
print(hash)

keys = []
key_sha256 = sha256(KEY).digest()
for i in range(1, 64 - len(key_sha256)+1):
    key = key_sha256 + b"\x00"*i
    keys.append(key)

print(len(keys))

# r = process(["python3", "chall.py"])
r = remote("localhost", 1337)
for key in keys:
    assert hash == hmac.new(key, msg, sha256).hexdigest(), key
    r.sendlineafter(b"(hex): ", key.hex().encode())

print(r.clean(0.5).decode())
