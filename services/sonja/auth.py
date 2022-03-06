import bcrypt
import os

from datetime import datetime, timedelta
from jose import jwt, ExpiredSignatureError

secret_key = os.environ.get('SONJA_SECRET_KEY', '1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef')


def hash_password(password):
    return str(bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()), "utf-8")


def test_password(password, hashed):
    return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))


def create_access_token(data: str, expires_delta: timedelta):
    expire = datetime.utcnow() + expires_delta
    to_encode = {
        "sub": data,
        "exp": expire
    }
    return jwt.encode(to_encode, secret_key, algorithm="HS256")


def decode_access_token(token: str):
    payload = jwt.decode(token, secret_key, algorithms=["HS256"])
    return payload.get("sub")