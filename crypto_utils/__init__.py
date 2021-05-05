import base64, os, hashlib, uuid
from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


def get_uuid():
    return uuid.uuid4().hex


def get_sha(text):
    m = hashlib.sha256()
    m.update(text.encode("utf-8"))
    sha = m.hexdigest()

    return sha


def encrypt(passphrase, plaintext):
    # setup a Fernet key based on our passphrase
    password = passphrase.encode()  # Convert to type bytes
    salt = str.encode(os.getenv("SALT"))
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
        backend=default_backend(),
    )
    key = base64.urlsafe_b64encode(kdf.derive(password))  # Can only use kdf once
    f = Fernet(key)

    # encrypt the message
    ciphertext = f.encrypt(plaintext.encode("utf-8"))

    return ciphertext.decode("utf-8")


def decrypt(passphrase, ciphertext):
    password = passphrase.encode()  # Convert to type bytes
    salt = str.encode(os.getenv("SALT"))
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
        backend=default_backend(),
    )
    key = base64.urlsafe_b64encode(kdf.derive(password))  # Can only use kdf once
    f = Fernet(key)
    decrypted_message = f.decrypt(ciphertext.encode("utf-8"))
    return decrypted_message.decode("utf-8")
