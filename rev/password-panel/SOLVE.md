Need to use python3.12 pyinsxtractor to make sure modules are decompiled:

```sh
docker run --rm -v "$PWD":/pwd -w /pwd python:3.12-slim bash -c 'pip
install pyinstxtractor-ng && pyinstxtractor-ng main.exe'
```

Start with entrypoint:

```sh
pylingual main.exe_extracted/main.pyc
```

```py
from colorama import Fore, Style, init
from check import check
from cheque import cheque
from czech import czech
from chic import chic
from chech import chech
init()
print()
print(Fore.CYAN + Style.BRIGHT + '  +----------------------------------+')
print('  |       CONTROL PANEL v2.4         |')
print('  |     authorization required       |')
print('  +----------------------------------+' + Style.RESET_ALL)
print()
print(Fore.YELLOW + '  Enter password to continue.' + Style.RESET_ALL)
guess = input(Fore.CYAN + Style.BRIGHT + '  Password> ' + Style.RESET_ALL)
a, b, c, d, e = (guess[0:10], guess[10:20], guess[20:30], guess[30:40], guess[40:50])
if len(guess) == 50 and check(a, 'hC_Zyp{CHN') and cheque(b, b'N>y1!G&EF1M@2MMPgyfdNlHjYQ8ijMNL4*OJv}`=') and czech(c, b'\x00\xd3\x0cV5\x86\xc0;a\xf1W+P\xae@W') and chic(d, b'tiZ_HuNeat') and chech(e, 834116172812670004082183):
    print()
    print(Fore.GREEN + Style.BRIGHT + '  [+] ACCESS GRANTED' + Style.RESET_ALL)
    print(Fore.GREEN + '      Welcome to the control panel.' + Style.RESET_ALL)
    print()
else:
    print()
    print(Fore.RED + Style.BRIGHT + '  [-] ACCESS DENIED' + Style.RESET_ALL)
    print(Fore.RED + '      Invalid password.' + Style.RESET_ALL)
    print()
```

checks:

1. `check(a, 'hC_Zyp{CHN')`
2. `` cheque(b, b'N>y1!G&EF1M@2MMPgyfdNlHjYQ8ijMNL4*OJv}`=') ``
3. `czech(c, b'\x00\xd3\x0cV5\x86\xc0;a\xf1W+P\xae@W')`
4. `chic(d, b'tiZ_HuNeat')`
5. `chech(e, 834116172812670004082183)`

```sh
pylingual main.exe_extracted/PYZ-00.pyz_extracted/{check,cheque,czech,chic,chech}.pyc
```

### 1. check

```py
def check(piece, target):
    return piece[::-1] == target
```

Simple reverse of `'hC_Zyp{CHN'` is `NHC{pyZ_Ch`

### 2. cheque

```py
import base64
def cheque(piece, target):
    return base64.b85encode(base64.b32encode(base64.b64encode(piece.encode()))) == target
```

Run inverse functions in python:

```py
>>> import base64
>>> base64.b64decode(base64.b32decode(base64.b85decode(b'N>y1!G&EF1M@2MMPgyfdNlHjYQ8ijMNL4*OJv}`=')))
b'3Cks_Fr0M_'
```

### 3. czech

```py
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
def czech(piece, target):
    cipher = AES.new(b'The fun has only', AES.MODE_CBC, b'just begun. glhf')
    return cipher.encrypt(pad(piece.encode(), AES.block_size)) == target
```

Just decrypt the string:

```py
>>> from Crypto.Cipher import AES
>>> from Crypto.Util.Padding import unpad
>>> cipher = AES.new(b'The fun has only', AES.MODE_CBC, b'just begun. glhf')
>>> unpad(cipher.decrypt(b'\x00\xd3\x0cV5\x86\xc0;a\xf1W+P\xae@W'), AES.block_size)
b'1Nv3Rs3_T0'
```

### 4. chic

```py
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
```

Recognize it is just ROT with a key. Inverse:

```py
>>> from itertools import cycle
>>> KEY = 'KEY'
>>> ALPHABET = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ_abcdefghijklmnopqrstuvwxyz{}'
>>> out = []
>>> for c, k in zip('tiZ_HuNeat', cycle(KEY)):
...     c = ALPHABET.index(c)
...     k = ALPHABET.index(k)
...     out.append(ord(ALPHABET[(c + (len(ALPHABET) - k)) % len(ALPHABET)]))
>>> bytes(out)
b'_V1G3N3R3_'
```

### 5. chech

```py
def chech(piece, target):
    raw = piece.encode()
    x = int.from_bytes(raw, 'big')
    return (1337 * x + 424242) % (256 ** len(raw)) == target
```

We know it is 10 long from `e=guess[40:50]`. use z3 to solve:

```py
>>> from z3 import *
>>> s = Solver()
>>> x = BitVec("x", 10*8)  # 10 bytes
>>> s.add((1337 * x + 424242) % 256 ** 10 == 834116172812670004082183)
>>> s.check()
sat
>>> s.model()
[x = 397571092732711202467965]
>>> long_to_bytes(s.model()[x].as_long())
b'T0_Crypt0}'
```

Together: `NHC{pyZ_Ch3Cks_Fr0M_1Nv3Rs3_T0_V1G3N3R3_T0_Crypt0}`
