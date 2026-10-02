from hashlib import sha256
import hmac
import os

KEY = b"This key is actually the same on production if you can believe it"
MSG = b"Give me the flag pleeeeeaaase"
HASH = hmac.new(KEY, MSG, sha256).hexdigest()

seen = set()

print("Hi there locksmith! I need you to make 32 copies of this key for me:")
print(KEY.hex())

for i in range(32):
    key = bytes.fromhex(input(f"Copy of key {i+1} (hex): "))
    if key == KEY:
        raise Exception("You cannot send the original key!")
    if key in seen:
        raise Exception(f"You already sent {key!r} before!")
    seen.add(key)

    hash = hmac.new(key, MSG, sha256).hexdigest()
    if hash != HASH:
        raise Exception(f"{hash!r} != {HASH!r}")

print("Thanks for your help! Here is the flag:")
print(os.environ["FLAG"])
