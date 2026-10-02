#!/usr/bin/env python3
from Crypto.Util.number import bytes_to_long, long_to_bytes
import itertools
from gmpy2 import mpz, gcd, c_div
import gmpy2
from pwn import *

# p = process(["python3", "chall.py"])
p = remote("localhost", 1337)

TARGET = b"selfdestruct"
e = 65537


def sign(msg: bytes) -> int:
    p.sendlineafter(b"[sign/verify]: ", b"sign")
    p.sendlineafter(b"Message: \x1b[0m", msg)
    return int(p.recvline().decode(), 16)


def verify(sig: int):
    p.sendlineafter(b"[sign/verify]: ", b"verify")
    p.sendlineafter(b"Signature (hex): ", hex(sig)[2:].encode())


def is_ascii(m: int) -> bool:
    return all(0x20 <= b <= 0x7E for b in long_to_bytes(m))


def find_r(m: int):
    for i in range(4):
        for chars in itertools.product(range(0x20, 0x7E), repeat=i + 1):
            factor = bytes_to_long(bytes(chars))
            m_blind = m * factor
            if is_ascii(m_blind):
                return m_blind, factor
    raise ValueError("No ASCII message found")


def remove_small_factors(n: mpz, limit: int = 1000) -> mpz:
    p = mpz(2)

    while p < limit:
        while gmpy2.is_divisible(n, p):
            n //= p
        p = gmpy2.next_prime(p)

    return n

def sig2n(s1, s2, m1, m2) -> mpz:
    s1, s2, m1, m2 = mpz(s1), mpz(s2), mpz(m1), mpz(m2)
    # https://crypto.stackexchange.com/questions/30289/is-it-possible-to-recover-an-rsa-modulus-from-its-signatures/30301#30301
    gcd_res = gcd(pow(s1, e) - m1, pow(s2, e) - m2)
    return remove_small_factors(gcd_res)


"""
Basic idea: "RSA Blind Signatures" but with ASCII constraint on the factor and combined message. Brute force to find working factor

m_blind = m * r
c_blind = c * c_r
c = c_blind * pow(c_r, -1, N)

can easily iterate r until m_blind is ASCII
"""

m = bytes_to_long(TARGET)
m_blind, r = find_r(m)
print("Found ASCII messages:")
print(f"m_blind={long_to_bytes(m_blind)!r}")
print(f"r={long_to_bytes(r)!r}")

sig_blind = sign(long_to_bytes(m_blind))
sig_r = sign(long_to_bytes(r))
print("Signatures:")
print(f"{sig_blind=}")
print(f"{sig_r=}")

# Recover n from 2 signatures
print("Recovering n...")
n = sig2n(sig_blind, sig_r, m_blind, r)
print(f"n={n}")

sig = (sig_blind * pow(sig_r, -1, n)) % n
verify(sig)
print(p.clean(0.5).decode())
