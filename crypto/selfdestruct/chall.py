from Crypto.Util.number import getPrime, bytes_to_long, long_to_bytes
from colorama import Back, Fore, Style
import os

FLAG = os.environ.get("FLAG", "CTF{f4k3_fl4g_f0r_t3st1ng}")

p, q = getPrime(1024), getPrime(1024)
N, e = p * q, 65537
d = pow(e, -1, (p - 1) * (q - 1))

BLOCKED = b"selfdestruct"


def is_ascii(msg: bytes) -> bool:
    return all(0x20 <= b <= 0x7E for b in msg)


Y = Back.RESET + Fore.YELLOW + Style.BRIGHT
R = Back.RESET + Fore.RED + Style.BRIGHT
C = Back.RESET + Fore.CYAN + Style.BRIGHT
RB = Back.RED + Fore.WHITE + Style.BRIGHT
_ = Style.RESET_ALL

print(f"{R}╔══════════════════════════╗")
print(f"{R}║ ░ {RB} TERMINATOR CONTROL {R} ░ ║")
print(f"{R}╚══════════════════════════╝")
print(_)
print(f"{Y}[!] NOTICE ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓")
print(f"{Y} ┃ {_}The {R}selfdestruct{_} command is currently{Y} ┃")
print(f"{Y} ┃ {_}disabled for security reasons.{Y}        ┃")
print(f"{Y} ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛")
print(_)
while True:
    choice = input(f"{C}[sign/verify]: {_}").strip().lower()
    if choice == "sign":
        command = input(f"{C}Message: {_}").encode()
        if command == BLOCKED:
            print(f"{R}Message is blocked{_}")
            continue
        if not is_ascii(command):
            print(f"{R}Message is not ASCII{_}")
            continue
        sig = pow(bytes_to_long(command), d, N)
        print(long_to_bytes(sig).hex())
    elif choice == "verify":
        sig = int(input(f"{C}Signature (hex): {_}"), 16)
        command = long_to_bytes(pow(sig, e, N))
        if command == BLOCKED:
            print()
            print(f"{R}\033[5m[ INITIATING SELF-DESTRUCTION SEQUENCE... ]{_}")
            print(FLAG)
            break
        else:
            raise ValueError(f"Unrecognized command {command!r}")
    else:
        print(f"{R}Unknown choice {choice!r}{_}")
