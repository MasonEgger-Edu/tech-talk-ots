from fastapi import FastAPI, HTTPException, Form, Request, Depends
from typing import Optional
from pydantic import BaseModel  # pylint: disable=no-name-in-module
from datetime import timedelta
import os
import redis
import crypto_utils
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import requests
from jinja2.filters import FILTERS


app = FastAPI()

templates = Jinja2Templates(directory="templates")

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

    @classmethod
    def as_form(cls, message: str = Form(...), passphrase: str = Form(...), expire_seconds: Optional[int] = Form(None)) -> 'Secret':
        return cls(message=message, passphrase=passphrase, expire_seconds=expire_seconds)


# @app.post('/secretsform', response_model=Secret)
# def endpoint(secret: Secret = Depends(Secret)):
#     print("got item =", repr(secret))
#     id = crypto_utils.get_uuid()
#     sha = crypto_utils.get_sha(secret.passphrase)
#     print(f"id is {id}")
#     data = {
#             "page": "Secrets Page",
#     }
#     return templates.TemplateResponse("page.html", {"data": data})


@app.post("/secretsform", response_model=Secret, response_class=HTMLResponse)
async def web_create_secret(request: Request, secret: Secret = Depends(Secret.as_form)):
    """
    Web form data passwd from index.html - store secret and render secret UUID via template page.html

    - **secret*: refers to pydantic model Secret
    - **secret_id**: each secret must have a UUID
    - **passphrase**: each secret must have a passphrase
    - **expire_seconds**: optional value - number of seconds secret is kept in redis db
    """
    print("got item =", repr(secret))
    id = crypto_utils.get_uuid()
    sha = crypto_utils.get_sha(secret.passphrase)
    ciphertext = crypto_utils.encrypt(secret.passphrase, secret.message)
    r.setex(id, timedelta(seconds=secret.expire_seconds), f"{sha}\n{ciphertext}")
    data = {
            "id": id
    }
    return templates.TemplateResponse("page.html", {"request": request, "data": data})


@app.post("/secrets")
def api_create_secret(secret: Secret):
    """
    API to create a secret

    - **secret*: refers to pydantic model Secret
    - **secret_id**: each secret must have a UUID
    - **passphrase**: each secret must have a passphrase
    - **expire_seconds**: optional value - number of seconds secret is kept in redis db
    """
    id = crypto_utils.get_uuid()
    sha = crypto_utils.get_sha(secret.passphrase)
    ciphertext = crypto_utils.encrypt(secret.passphrase, secret.message)
    r.setex(id, timedelta(seconds=secret.expire_seconds), f"{sha}\n{ciphertext}")
    return {"success": "True", "id": id}

# @app.post("/secretsforma")
# async def create_secret(req: Request, secret: Secret = Depends(Secret.as_form)):
#     print("got item =", repr(secret))
#     id = crypto_utils.get_uuid()
#     sha = crypto_utils.get_sha(secret.passphrase)
#     ciphertext = crypto_utils.encrypt(secret.passphrase, secret.message)
#     r.setex(id, timedelta(seconds=secret.expire_seconds), f"{sha}\n{ciphertext}")
#     return {"success": "True", "id": id}


class Passphrase(BaseModel):
    passphrase: str


@app.post("/secrets/{secret_id}")
def api_read_secret(secret_id: str, passphrase: Passphrase):
    """
    API to retrieve a secret

    - **secret_id**: each secret must have a UUID
    """
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


@app.get("/", response_class=HTMLResponse)
def index_page(request: Request):
    """
    Index web page via template index.html

    """
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/secrets/{id}", response_class=HTMLResponse)
def web_read_secret(request: Request, id: str):
    """
    Web form to retrieve a secret - will render web form via template websecret.html

    - **id**: each secret must have a UUID
    """
    print("got item =", repr(id))
    data = r.get(id)
    # if data is None:
    #     return templates.TemplateResponse("secret404.html", {"request": request, "data": data})
    return templates.TemplateResponse("websecret.html", {"request": request, "id": id})


@app.post("/getsecret", response_class=HTMLResponse)
def web_get_secret(request: Request, id: str = Form(...), passphrase: str = Form(...)):
    """
    Retrieve a secret - called from web form route @app.get("/secrets/{id}"):

    - **id**: each secret must have a UUID
    - **passphrase**: a passphrase 
    - **plaintext**: if the sha for passphrase matches stored sha, then retrieve message to be displayed
    """
    print("got item =", repr(id))
    print("got item =", repr(passphrase))
    data = r.get(id)
    passphrase = passphrase
    if data is None:
        return templates.TemplateResponse("secret404.html", {"request": request, "data": data})
    data = data.decode("utf-8")
    stored_sha, ciphertext = data.split("\n")
    sha = crypto_utils.get_sha(passphrase)
    if stored_sha != sha:
        return templates.TemplateResponse("secret404.html", {"request": request, "data": data})
    r.delete(id)
    plaintext = crypto_utils.decrypt(passphrase, ciphertext)
    data = {
        "plaintext": plaintext
    }
    return templates.TemplateResponse("showsecret.html", {"request": request, "data": data})
