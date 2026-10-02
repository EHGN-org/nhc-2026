from colorama import Fore, Style, init

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
a, b, c, d, e = guess[0:10], guess[10:20], guess[20:30], guess[30:40], guess[40:50]
if (
    len(guess) == 50
    and check(a, 'hC_Zyp{CHN')
    and cheque(b, b'N>y1!G&EF1M@2MMPgyfdNlHjYQ8ijMNL4*OJv}`=')
    and czech(c, b'\x00\xd3\x0cV5\x86\xc0;a\xf1W+P\xae@W')
    and chic(d, b'tiZ_HuNeat')
    and chech(e, 834116172812670004082183)
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
