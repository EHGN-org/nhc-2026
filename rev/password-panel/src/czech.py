from Crypto.Cipher import AES
from Crypto.Util.Padding import pad


def czech(piece, target):
    cipher = AES.new(b'The fun has only', AES.MODE_CBC, b'just begun. glhf')
    return cipher.encrypt(pad(piece.encode(), AES.block_size)) == target
