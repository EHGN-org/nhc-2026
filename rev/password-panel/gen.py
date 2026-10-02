#!/usr/bin/env python3
import base64
from itertools import cycle
from pathlib import Path

from Crypto.Cipher import AES
from Crypto.Util.Padding import pad

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
FLAG = ROOT.joinpath("flag.txt").read_text().strip()

if not (FLAG.startswith("NHC{") and FLAG.endswith("}") and len(FLAG) > 5):
    raise SystemExit("flag.txt must be NHC{...}")

N_CHUNKS = 5
AES_KEY = b"The fun has only"
AES_IV = b"just begun. glhf"
VIGENERE_KEY = "KEY"
VIGENERE_ALPH = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ_abcdefghijklmnopqrstuvwxyz{}"
if any(ch not in VIGENERE_ALPH for ch in FLAG):
    raise SystemExit("flag contains characters outside the vigenere alphabet")


def split_slices(text, n):
    q, r = divmod(len(text), n)
    sizes = [q + (1 if i < r else 0) for i in range(n)]
    if any(size == 0 for size in sizes):
        raise SystemExit("flag too short to split into 5 chunks")
    slices = []
    pos = 0
    for size in sizes:
        slices.append((pos, pos + size))
        pos += size
    return slices


def vigenere(piece, key, alph):
    out = []
    for c, k in zip(piece, cycle(key)):
        c = alph.index(chr(c))
        k = alph.index(k)
        out.append(ord(alph[(c + k) % len(alph)]))
    return bytes(out)


def write(name, text):
    SRC.mkdir(parents=True, exist_ok=True)
    SRC.joinpath(name).write_text(text)
    print(f"wrote src/{name}")


slices = split_slices(FLAG, N_CHUNKS)
pieces = [FLAG[start:end].encode("utf-8") for start, end in slices]
a0, a1 = slices[0]
b0, b1 = slices[1]
c0, c1 = slices[2]
d0, d1 = slices[3]
e0, e1 = slices[4]

exp_a = pieces[0][::-1].decode("ascii")
exp_b = base64.b85encode(base64.b32encode(base64.b64encode(pieces[1])))
exp_c = AES.new(AES_KEY, AES.MODE_CBC, AES_IV).encrypt(pad(pieces[2], AES.block_size))
exp_d = vigenere(pieces[3], VIGENERE_KEY, VIGENERE_ALPH)

e = pieces[4]
e_len = len(e)
e_a = 1337
e_b = 424242
e_target = (int.from_bytes(e, "big") * e_a + e_b) % (256 ** e_len)

write(
    "check.py",
    """def check(piece, target):
    return piece[::-1] == target
""",
)

write(
    "cheque.py",
    """import base64


def cheque(piece, target):
    return base64.b85encode(base64.b32encode(base64.b64encode(piece.encode()))) == target
""",
)

write(
    "czech.py",
    f"""from Crypto.Cipher import AES
from Crypto.Util.Padding import pad


def czech(piece, target):
    cipher = AES.new({AES_KEY!r}, AES.MODE_CBC, {AES_IV!r})
    return cipher.encrypt(pad(piece.encode(), AES.block_size)) == target
""",
)

write(
    "chic.py",
    f"""from itertools import cycle

KEY = {VIGENERE_KEY!r}
ALPHABET = {VIGENERE_ALPH!r}


def chic(piece, target):
    out = []
    for c, k in zip(piece, cycle(KEY)):
        c = ALPHABET.index(c)
        k = ALPHABET.index(k)
        out.append(ord(ALPHABET[(c + k) % len(ALPHABET)]))
    return bytes(out) == target
""",
)

write(
    "chech.py",
    f"""def chech(piece, target):
    raw = piece.encode()
    x = int.from_bytes(raw, "big")
    return ({e_a} * x + {e_b}) % (256 ** len(raw)) == target
""",
)

write(
    "main.py",
    f"""from colorama import Fore, Style, init

from check import check
from cheque import cheque
from czech import czech
from chic import chic
from chech import chech

init()
print()
print(Fore.CYAN + Style.BRIGHT + "  +----------------------------------+")
print("  |       CONTROL PANEL v2.4         |")
print("  |     authorization required       |")
print("  +----------------------------------+" + Style.RESET_ALL)
print()
print(Fore.YELLOW + "  Enter password to continue." + Style.RESET_ALL)
guess = input(Fore.CYAN + Style.BRIGHT + "  Password> " + Style.RESET_ALL)
a, b, c, d, e = guess[{a0}:{a1}], guess[{b0}:{b1}], guess[{c0}:{c1}], guess[{d0}:{d1}], guess[{e0}:{e1}]
if (
    len(guess) == {e1}
    and check(a, {exp_a!r})
    and cheque(b, {exp_b!r})
    and czech(c, {exp_c!r})
    and chic(d, {exp_d!r})
    and chech(e, {e_target})
):
    print()
    print(Fore.GREEN + Style.BRIGHT + "  [+] ACCESS GRANTED" + Style.RESET_ALL)
    print(Fore.GREEN + "      Welcome to the control panel." + Style.RESET_ALL)
    print()
else:
    print()
    print(Fore.RED + Style.BRIGHT + "  [-] ACCESS DENIED" + Style.RESET_ALL)
    print(Fore.RED + "      Invalid password." + Style.RESET_ALL)
    print()
""",
)
