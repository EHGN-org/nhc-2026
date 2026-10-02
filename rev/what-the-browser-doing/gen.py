import hashlib
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

def encrypt_data(password: str, secret_text: str):
    password_bytes = password.encode('utf-8')
    plaintext_bytes = secret_text.encode('utf-8')

    # 1. Generate the SHA-256 hash (EXPECTED_HASH_HEX in JS)
    hash_hex = hashlib.sha256(password_bytes).hexdigest()

    # 2. Define key derivation parameters (matching JS setup)
    salt = bytes([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16])
    iv = bytes(12)  # 96-bit zero-initialized IV matching JS code

    # 3. Derive 256-bit (32-byte) AES key using PBKDF2
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
    )
    aes_key = kdf.derive(password_bytes)

    # 4. Encrypt with AES-GCM (automatically appends 16-byte tag required by Web Crypto)
    aesgcm = AESGCM(aes_key)
    ciphertext = aesgcm.encrypt(iv, plaintext_bytes, associated_data=None)

    return hash_hex, str(list(ciphertext))

