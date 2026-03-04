# Simple symmetric encryption helpers (placeholder - use real crypto in production)
from cryptography.fernet import Fernet
import json
import os

VAULT_PATH = os.path.join(os.path.dirname(__file__), 'vault.enc')
KEY_PATH = os.path.join(os.path.dirname(__file__), 'vault_key.txt')


def load_key():
    if not os.path.exists(KEY_PATH):
        key = Fernet.generate_key()
        with open(KEY_PATH, 'wb') as f:
            f.write(key)
        return key
    with open(KEY_PATH, 'rb') as f:
        return f.read()


def get_cipher():
    return Fernet(load_key())


def encrypt_vault(data: dict):
    cipher = get_cipher()
    token = cipher.encrypt(json.dumps(data).encode())
    with open(VAULT_PATH, 'wb') as f:
        f.write(token)


def decrypt_vault():
    if not os.path.exists(VAULT_PATH):
        return {}
    cipher = get_cipher()
    with open(VAULT_PATH, 'rb') as f:
        token = f.read()
    try:
        return json.loads(cipher.decrypt(token).decode())
    except Exception:
        return {}
