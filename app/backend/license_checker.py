import base64
from pathlib import Path

SALT = "SnIpEr"

def xor_decrypt(encoded: str, salt: str) -> str:
    decoded = base64.b64decode(encoded)
    decrypted = bytearray()
    for i, b in enumerate(decoded):
        decrypted.append(b ^ ord(salt[i % len(salt)]))
    return decrypted.decode()

def read_license_and_get_id(path) -> int:
    try:
        path = Path(path)
        if not path.exists():
            return -2
        with open(path, "r") as f:
            encrypted = f.read().strip()
        user_id_str = xor_decrypt(encrypted, SALT)
        return int(user_id_str)
    except Exception as e:
        return None