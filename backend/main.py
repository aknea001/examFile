from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, Response
import jwt
from datetime import datetime, timedelta
from dotenv import load_dotenv
from os import getenv
from pydantic import BaseModel
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from databaseConnection import Database

load_dotenv()

def createJWT(data: str) -> str:
    encodedJWT = jwt.encode({"userID": data, "exp": datetime.now() + timedelta(hours=1)}, getenv("jwtSecret"), algorithm="HS256")
    return encodedJWT

class Credentials(BaseModel):
    username: str
    passwd: str

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.db = Database()
    yield

a2 = PasswordHasher()

app = FastAPI(lifespan=lifespan)

@app.post("/login", status_code=200)
async def index(request: Request, response: Response, body: Credentials):
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
    dek = "dek" # Not going to implement keys rn

    result = db.execute("INSERT INTO users (username, hash, dek) \
                        VALUES \
                        (%s, %s, %s)", body.username, hashed, dek)
    
    if isinstance(result, str):
        response.status_code = 500
        return {"msg": f"Database error: {result}"}
    
    return {"msg": "Success"}