from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, Response, Depends
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from typing import Annotated
import jwt
from datetime import datetime, timedelta
from dotenv import load_dotenv
from os import getenv
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from Crypto.Cipher import ChaCha20_Poly1305
from Crypto.Random import get_random_bytes
import base64
import zstandard as zstd
from databaseConnection import Database
from hh import HardwareHash

load_dotenv()

def createJWT(data: str) -> str:
    encodedJWT = jwt.encode({"userID": data, "exp": datetime.now() + timedelta(hours=1)}, getenv("jwtSecret"), algorithm="HS256")
    return encodedJWT

def decodeJWT(token: str) -> dict:
    try:
        payload = jwt.decode(token, getenv("jwtSecret"), algorithms=["HS256"], require=["exp"], verify_exp=True)
        identity = payload.get("userID")
    except jwt.exceptions.InvalidTokenError:
        return {"success": False}
    
    return {"success": True, "id": int(identity)}

def decryptDEK(ciphertext: bytes, passwd: bytes, salt: bytes, nonce: bytes, tag: bytes) -> bytes:
    kek = hh.getKEK(passwd, salt)

    cipher = ChaCha20_Poly1305.new(key=kek, nonce=nonce)

    try:
        plaintext = cipher.decrypt_and_verify(ciphertext, tag)
    except ValueError as e:
        print(f"Error during decrypting: {e}")
        return b""
    
    return plaintext

def compress(plaintext: bytes) -> dict:
    cctx = zstd.ZstdCompressor()
    compressed = cctx.compress(plaintext)

    if len(compressed) > len(plaintext):
        return {"data": plaintext, "compressed": False}
    
    return {"data": compressed, "compressed": True}

class Credentials(BaseModel):
    username: str
    passwd: str

class File(BaseModel):
    fileB64bytes: str
    fileName: str
    passwd: str

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.db = Database()
    yield

a2 = PasswordHasher()
hh = HardwareHash()

app = FastAPI(lifespan=lifespan)

oauth2Scheme = OAuth2PasswordBearer(tokenUrl="login")

@app.post("/login", status_code=200)
async def login(request: Request, response: Response, body: Credentials):
    db = request.app.state.db
    data = db.execute("SELECT hash, id FROM users WHERE username = %s", body.username)

    if not data:
        response.status_code = 401
        return {"msg": "Wrong username or password.."}
    
    try:
        a2.verify(data[0], body.passwd)
    except VerifyMismatchError:
        response.status_code = 401
        return {"msg": "Wrong username or password.."}

    encodedJWT = createJWT(str(data[1]))
    return {"token": encodedJWT}

@app.post("/register", status_code=201)
async def register(request: Request, response: Response, body: Credentials):
    db = request.app.state.db

    hashed = a2.hash(body.passwd)
    dek = get_random_bytes(32)

    salt = get_random_bytes(16)
    kek = hh.getKEK(body.passwd.encode(), salt)
    nonce = get_random_bytes(24)

    cipher = ChaCha20_Poly1305.new(key=kek, nonce=nonce)
    ciphertext, tag = cipher.encrypt_and_digest(dek)

    b64ciphertext, b64salt, b64nonce, b64tag = [base64.b64encode(i).decode() for i in (ciphertext, salt, nonce, tag)]

    result = db.execute("INSERT INTO users (username, hash, dek, salt, nonce, tag) \
                        VALUES \
                        (%s, %s, %s, %s, %s, %s)", body.username, hashed, b64ciphertext, b64salt, b64nonce, b64tag)
    
    if isinstance(result, str):
        response.status_code = 500
        return {"msg": f"Database error: {result}"}
    
    return {"msg": "Success"}

@app.post("/upload", status_code=201)
async def upload(request: Request, response: Response, token: Annotated[str, Depends(oauth2Scheme)], body: File):
    db = request.app.state.db

    identity = decodeJWT(token)

    if not identity["success"]:
        response.status_code = 401
        return {"msg": "Invalid token"}
    
    userID = identity["id"]

    fileBytes = base64.b64decode(body.fileB64bytes)

    compressed = compress(fileBytes)

    b64encryptedDek, b64dekSalt, b64dekNonce, b64dekTag = db.execute("SELECT dek, salt, nonce, tag FROM users WHERE id = %s", userID)
    encryptedDek, dekSalt, dekNonce, dekTag = [base64.b64decode(i) for i in (b64encryptedDek, b64dekSalt, b64dekNonce, b64dekTag)]

    dek = decryptDEK(encryptedDek, body.passwd.encode(), dekSalt, dekNonce, dekTag)

    nonce = get_random_bytes(24)
    cipher = ChaCha20_Poly1305.new(key=dek, nonce=nonce)
    ciphertext, tag = cipher.encrypt_and_digest(compressed["data"])

    b64ciphertext, b64nonce, b64tag = [base64.b64encode(i).decode() for i in (ciphertext, nonce, tag)]

    fileNameLst = body.fileName.split(".")
    fileName = "".join(fileNameLst[:-1])

    result = db.execute("INSERT INTO files (cipherText, nonce, tag, compressed, name, extension, userID) \
                        VALUES \
                        (%s, %s, %s, %s, %s, %s, %s)", b64ciphertext, b64nonce, b64tag, "t" if compressed["compressed"] else "f", fileName, fileNameLst[-1], userID)
    
    if isinstance(result, str):
        response.status_code = 500
        return {"msg": f"Database error: {result}"}
    
    return {"msg": "Success"}