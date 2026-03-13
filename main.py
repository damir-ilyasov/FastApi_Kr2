from fastapi import FastAPI, Response, Cookie, HTTPException
from pydantic import BaseModel
from typing import Optional
import uuid
app = FastAPI()
sessions: dict = {}

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


class LoginData(BaseModel):
    username: str
    password: str


@app.post("/login")
def login(data: LoginData, response: Response):
    user = USERS.get(data.username)

    if not user or user["password"] != data.password:
        raise HTTPException(status_code=401, detail="Неверный логин или пароль")

    token = str(uuid.uuid4())

    sessions[token] = {
        "username": data.username,
        "name": user["name"],
        "email": user["email"],
        "age": user["age"]
    }

    response.set_cookie(
        key="session_token",
        value=token,
        httponly=True,
        secure=False,
        samesite="lax"
    )

    return {"message": "Вход выполнен успешно"}


@app.get("/user")
def get_user(session_token: Optional[str] = Cookie(default=None)):
    if not session_token or session_token not in sessions:
        raise HTTPException(status_code=401, detail={"message": "Unauthorized"})

    return sessions[session_token]


@app.post("/logout")
def logout(response: Response, session_token: Optional[str] = Cookie(default=None)):
    if session_token and session_token in sessions:
        del sessions[session_token]

    response.delete_cookie("session_token")
    return {"message": "Выход выполнен"}