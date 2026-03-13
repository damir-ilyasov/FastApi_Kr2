from fastapi import FastAPI, Response, Cookie, HTTPException
from pydantic import BaseModel
from typing import Optional
from itsdangerous import URLSafeSerializer, BadSignature
import uuid
app = FastAPI()

SECRET_KEY = "SyperSecretPuperKey"
serializer = URLSafeSerializer(SECRET_KEY)

USERS = {
    "user123": {
        "password": "password123",
        "name": "Alice",
        "email": "alice@example.com",
        "age": 30
    },
    "admin": {
        "password": "admin123",
        "name": "Admin",
        "email": "admin@example.com",
        "age": 25
    }
}
user_id_map: dict = {}


class LoginData(BaseModel):
    username: str
    password: str


@app.post("/login")
def login(data: LoginData, response: Response):
    user = USERS.get(data.username)

    if not user or user["password"] != data.password:
        raise HTTPException(status_code=401, detail="Неверный логин или пароль")

    user_id = str(uuid.uuid4())

    user_id_map[user_id] = data.username

    session_token = serializer.dumps(user_id)

    response.set_cookie(
        key="session_token",
        value=session_token,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=3600
    )

    return {"message": "Вход выполнен успешно", "user_id": user_id}


@app.get("/profile")
def get_profile(session_token: Optional[str] = Cookie(default=None)):
    if not session_token:
        raise HTTPException(status_code=401, detail={"message": "Unauthorized"})

    try:
        user_id = serializer.loads(session_token)
    except BadSignature:
        raise HTTPException(status_code=401, detail={"message": "Unauthorized"})

    username = user_id_map.get(user_id)
    if not username:
        raise HTTPException(status_code=401, detail={"message": "Unauthorized"})

    user = USERS[username]
    return {
        "user_id": user_id,
        "username": username,
        "name": user["name"],
        "email": user["email"],
        "age": user["age"]
    }