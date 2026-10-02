from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
import os

KEY = os.urandom(16)
FLAG = os.environ.get("FLAG", "CTF{f4k3_fl4g_f0r_t3st1ng}").encode()


def encrypt(mode, data):
    print(f"Encrypting {len(data)} bytes with {mode} mode...")
    if mode == "ECB":
        cipher = AES.new(KEY, AES.MODE_ECB)
        return cipher.encrypt(pad(data, AES.block_size))
    if mode == "CBC":
        cipher = AES.new(KEY, AES.MODE_CBC)
        return cipher.iv + cipher.encrypt(pad(data, AES.block_size))
    if mode == "CTR":
        cipher = AES.new(KEY, AES.MODE_CTR)
        return cipher.nonce + cipher.encrypt(data)


print("[MODUS OPERANDI]\n", flush=True)

while True:
    mode = input("Mode [ECB/CBC/CTR]: ").strip().upper()
    if mode not in ["ECB", "CBC", "CTR"]:
        raise ValueError(f"unknown mode {mode!r}")
    what = input("Encrypt [flag/custom]: ").strip().lower()
    if what == "flag":
        data = FLAG
    elif what == "custom":
        data = bytes.fromhex(input("Custom text (hex): "))
    else:
        raise ValueError(f"unknown choice {what!r}")

    print(encrypt(mode, data).hex())
