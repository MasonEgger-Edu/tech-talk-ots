from fastapi import FastAPI, HTTPException
from typing import Optional
from pydantic import BaseModel  # pylint: disable=no-name-in-module
from datetime import timedelta
import os
import redis
import crypto_utils

app = FastAPI()

r = redis.Redis(
    host=os.getenv("DB_HOST", "localhost"),
    port=os.getenv("DB_PORT", 6379),
    password=os.getenv("DB_PASSWORD", None),
    ssl=os.getenv("REDIS_SSL", "True") == "True",
)


class Secret(BaseModel):
    message: str
    passphrase: str
    expire_seconds: Optional[int] = 3600


@app.post("/secrets")
def create_secret(secret: Secret):
    id = crypto_utils.get_uuid()
    sha = crypto_utils.get_sha(secret.passphrase)
    ciphertext = crypto_utils.encrypt(secret.passphrase, secret.message)
    r.setex(id, timedelta(seconds=secret.expire_seconds), f"{sha}\n{ciphertext}")
    return {"success": "True", "id": id}


class Passphrase(BaseModel):
    passphrase: str


@app.post("/secrets/{secret_id}")
def read_secret(secret_id: str, passphrase: Passphrase):
    data = r.get(secret_id)
    passphrase = passphrase.passphrase
    if data is None:
        return HTTPException(
            404, detail="This secret wither never existed or it was already read"
        )

    data = data.decode("utf-8")

    stored_sha, ciphertext = data.split("\n")
    sha = crypto_utils.get_sha(passphrase)

    if stored_sha != sha:
        return HTTPException(
            404, detail="This secret wither never existed or it was already read"
        )

    r.delete(secret_id)
    plaintext = crypto_utils.decrypt(passphrase, ciphertext)
    return {"success": "True", "message": plaintext}
