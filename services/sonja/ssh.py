import base64
import bcrypt

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization


def generate_rsa_key():
    key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=4096,
        backend=default_backend()
    )
    private = key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption()
    ).decode("utf-8")
    public = key.public_key().public_bytes(
        encoding=serialization.Encoding.OpenSSH,
        format=serialization.PublicFormat.OpenSSH,
    ).decode("utf-8")
    return (private, public)


def encode(raw):
    if not raw:
        return ""
    return str(base64.b64encode(raw.encode("utf-8")), "utf-8")


def decode(encoded):
    if not encoded:
        return ""

    return str(base64.b64decode(encoded), "utf-8")


def hash_password(password):
    return str(bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()), "utf-8")


def test_password(password, hashed):
    return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))
