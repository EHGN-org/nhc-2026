from itertools import cycle

KEY = 'KEY'
ALPHABET = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ_abcdefghijklmnopqrstuvwxyz{}'


def chic(piece, target):
    out = []
    for c, k in zip(piece, cycle(KEY)):
        c = ALPHABET.index(c)
        k = ALPHABET.index(k)
        out.append(ord(ALPHABET[(c + k) % len(ALPHABET)]))
    return bytes(out) == target
