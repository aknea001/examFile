from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, Response, Depends, Query, Body
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

def decodeJWT(token: str) -> int:
    payload = jwt.decode(token, getenv("jwtSecret"), algorithms=["HS256"], require=["exp"], verify_exp=True)
    identity = payload.get("userID")
    
    return int(identity)

def getDEK(db, userID: int | str, passwd: bytes) -> bytes:
    try:
        data = db.execute("SELECT dek, salt, nonce, tag FROM users WHERE id = %s", userID)
    except ConnectionError as e:
        raise ConnectionError(e)

    b64encryptedDek, b64dekSalt, b64dekNonce, b64dekTag = data

    encryptedDek, dekSalt, dekNonce, dekTag = [base64.b64decode(i) for i in (b64encryptedDek, b64dekSalt, b64dekNonce, b64dekTag)]

    dek = decryptDEK(encryptedDek, passwd, dekSalt, dekNonce, dekTag)

    return dek

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

def decompress(compressed: bytes) -> bytes:
    dctx = zstd.ZstdDecompressor()
    decompressed = dctx.decompress(compressed)

    return decompressed

class Credentials(BaseModel):
    username: str
    passwd: str

class File(BaseModel):
    b64bytes: str
    name: str

class FileID(BaseModel):
    id: int

class DekDerivation(BaseModel):
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
    try:
        data = db.execute("SELECT hash, id FROM users WHERE username = %s", body.username)
    except ConnectionError as e:
        response.status_code = 500
        return {"msg": f"Database error: {e}"}

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

    try:
        result = db.execute("INSERT INTO users (username, hash, dek, salt, nonce, tag) \
                            VALUES \
                            (%s, %s, %s, %s, %s, %s)", body.username, hashed, b64ciphertext, b64salt, b64nonce, b64tag)
    except ConnectionError as e:
        response.status_code = 500
        return {"msg": f"Database error: {e}"}
    
    return {"msg": "Success"}

@app.post("/upload", status_code=201)
async def upload(request: Request, response: Response, token: Annotated[str, Depends(oauth2Scheme)], dekDerivation: DekDerivation = Body(embed=True), file: File = Body(embed=True)):
    db = request.app.state.db

    try:
        userID = decodeJWT(token)
    except jwt.exceptions.InvalidTokenError:
        response.status_code = 401
        return {"msg": "Invalid token"}

    fileBytes = base64.b64decode(file.b64bytes)

    compressed = compress(fileBytes)

    try:
        dek = getDEK(db, userID, dekDerivation.passwd.encode())
    except ConnectionError as e:
        response.status_code = 500
        return {"msg": f"Database error: {e}"}

    nonce = get_random_bytes(24)
    cipher = ChaCha20_Poly1305.new(key=dek, nonce=nonce)
    ciphertext, tag = cipher.encrypt_and_digest(compressed["data"])

    b64ciphertext, b64nonce, b64tag = [base64.b64encode(i).decode() for i in (ciphertext, nonce, tag)]

    fileNameLst = file.name.split(".")
    fileName = "".join(fileNameLst[:-1])

    try:
        result = db.execute("INSERT INTO files (cipherText, nonce, tag, compressed, name, extension, userID) \
                            VALUES \
                            (%s, %s, %s, %s, %s, %s, %s)", b64ciphertext, b64nonce, b64tag, "t" if compressed["compressed"] else "f", fileName, fileNameLst[-1], userID)
    except ConnectionError as e:
        response.status_code = 500
        return {"msg": f"Database error: {e}"}
    
    return {"msg": "Success"}

@app.post("/download", status_code=200)
async def download(request: Request, response: Response, token: Annotated[str, Depends(oauth2Scheme)], dekDerivation: DekDerivation = Body(embed=True), fileID: FileID = Body(embed=True)):
    db = request.app.state.db

    try:
        userID = decodeJWT(token)
    except jwt.exceptions.InvalidTokenError:
        response.status_code = 401
        return {"msg": "Invalid token"}
    
    fileID = fileID.id

    try:
        data = db.execute("SELECT cipherText, nonce, tag, compressed, name, extension \
                    FROM files \
                    WHERE userID = %s LIMIT %s,1", userID, fileID)
    except ConnectionError as e:
        response.status_code = 500
        return {"msg": f"Database error: {e}"}

    if not data:
        response.status_code = 404
        return {"msg": "Found no file on that fileID", "userID": userID, "fileID": fileID}
    
    try:
        dek = getDEK(db, userID, dekDerivation.passwd.encode())
    except ConnectionError as e:
        response.status_code = 500
        return {"msg": f"Database error: {e}"}
    
    b64ciphertext, b64nonce, b64tag, compressed, name, extension = data

    ciphertext, nonce, tag = [base64.b64decode(i) for i in (b64ciphertext, b64nonce, b64tag)]

    cipher = ChaCha20_Poly1305.new(key=dek, nonce=nonce)
    compressedFile = cipher.decrypt_and_verify(ciphertext, tag)

    if compressed == "t":
        plaintext = decompress(compressedFile)
    else:
        plaintext = compressedFile

    b64Plaintext = base64.b64encode(plaintext).decode()

    return {"msg": "Success", "data": b64Plaintext, "name": name, "extension": extension}

@app.delete("/delete", status_code=204)
async def delete(request: Request, response: Response, token: Annotated[str, Depends(oauth2Scheme)], fileID: int = Query()):
    db = request.app.state.db

    try:
        userID = decodeJWT(token)
    except jwt.exceptions.InvalidTokenError:
        response.status_code = 401
        return {"msg": "Invalid token"}

    try:
        x = db.execute("SELECT id FROM files WHERE userID = %s LIMIT %s,1", userID, fileID)[0]
        db.execute("DELETE FROM files WHERE userID = %s AND id = %s", userID, x)
    except ConnectionError as e:
        response.status_code =  500
        return {"msg": f"Database error: {e}"}
    
    return {"msg": "Success"}

@app.get("/tableInfo", status_code=200)
async def tableInfo(request: Request, response: Response, token: Annotated[str, Depends(oauth2Scheme)]):
    db = request.app.state.db

    try:
        userID = decodeJWT(token)
    except jwt.exceptions.InvalidTokenError:
        response.status_code = 401
        return {"msg": "Invalid token"}

    try:
        data = db.execute("SELECT name, extension FROM files WHERE userID = %s", userID, a=2)
    except ConnectionError as e:
        response.status_code =  500
        return {"msg": f"Database error: {e}"}
    
    parsedData = []

    for entry in data:
        dic = {
            "fileName": entry[0],
            "fileExtension": entry[1]
        }

        parsedData.append(dic)

    return parsedData