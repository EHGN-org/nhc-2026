#!/usr/bin/env python3
import sys

# ANSI fallback then RGB (truecolor overwrites; older terminals keep ANSI)
PINK = "\033[95m\033[38;2;253;121;168m"
AQUA = "\033[96m\033[38;2;129;236;236m"
RESET = "\033[0m"

print("Send Python braincode. Bytes must alternate odd/even.")

sys.stdout.write(PINK + """\
      _---~~(~~-_.
    _{        )   )
  ,   ) -~~- ( ,-' )_
(  `-,_..`., )-- '_,)
( """ + AQUA + ">>> ")
sys.stdout.flush()

code = sys.stdin.buffer.readline().rstrip(b"\r\n")
if not code:
    sys.exit(1)

print(PINK + """\
(_-  _  ~_-~~~~`,  ,' )
  `~ -^(    __;-,((()))
        ~~~~ {_ -_(())
               `\\  }
                 { }""" + RESET)

if not code.isascii():
    print("ASCII only.")
    sys.exit(1)


def odd_even(b):
    return "odd" if b & 1 else "even"


for i in range(1, len(code)):
    if (code[i] ^ code[i - 1]) & 1 == 0:
        prev, cur = code[i - 1], code[i]
        print(
            "Invalid: bytes must alternate odd/even.\n"
            f"  code[{i - 1}] = {chr(prev)!r} 0x{prev:02x} ({odd_even(prev)})\n"
            f"  code[{i}] = {chr(cur)!r} 0x{cur:02x} ({odd_even(cur)}, should be {odd_even(prev ^ 1)})"
        )
        sys.exit(1)

exec(code)
