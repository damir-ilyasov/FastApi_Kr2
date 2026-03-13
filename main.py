from fastapi import FastAPI, Response, Cookie
from pydantic import BaseModel
from typing import Optional
from itsdangerous import URLSafeSerializer, BadSignature
import uuid
import time
app = FastAPI()

SECRET_KEY = "SyperSecretPuperKey"
serializer = URLSafeSerializer(SECRET_KEY)

SESSION_LIFETIME = 300
RENEW_THRESHOLD  = 180

USERS = {
    "user123": {"password": "password123", "name": "Alice", "email": "alice@example.com", "age": 30},
    "admin":   {"password": "admin123",    "name": "Admin", "email": "admin@example.com", "age": 25},
}

user_id_map: dict = {}


class LoginData(BaseModel):
    username: str
    password: str


def build_token(user_id: str, timestamp: float) -> str:
    payload = f"{user_id}.{int(timestamp)}"
    return serializer.dumps(payload)


def parse_token(token: str) -> tuple[str, int]:
    payload = serializer.loads(token)
    parts = payload.split(".", 1)
    if len(parts) != 2:
        raise ValueError("Bad payload format")
    user_id, ts_str = parts
    return user_id, int(ts_str)


def set_session_cookie(response: Response, user_id: str, timestamp: float):
    token = build_token(user_id, timestamp)
    response.set_cookie(
        key="session_token",
        value=token,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=SESSION_LIFETIME,
    )


@app.post("/login")
def login(data: LoginData, response: Response):
    user = USERS.get(data.username)
    if not user or user["password"] != data.password:
        response.status_code = 401
        return {"message": "Неверный логин или пароль"}

    user_id = str(uuid.uuid4())
    user_id_map[user_id] = data.username

    set_session_cookie(response, user_id, time.time())
    return {"message": "Вход выполнен успешно", "user_id": user_id}


@app.get("/profile")
def get_profile(
    response: Response,
    session_token: Optional[str] = Cookie(default=None),
):
    if not session_token:
        response.status_code = 401
        return {"message": "Unauthorized"}

    try:
        user_id, last_active = parse_token(session_token)
    except (BadSignature, ValueError):
        response.status_code = 401
        return {"message": "Invalid session"}

    now = time.time()
    elapsed = now - last_active

    if elapsed >= SESSION_LIFETIME:
        response.delete_cookie("session_token")
        response.status_code = 401
        return {"message": "Session expired"}

    username = user_id_map.get(user_id)
    if not username:
        response.status_code = 401
        return {"message": "Invalid session"}

    if elapsed >= RENEW_THRESHOLD:
        set_session_cookie(response, user_id, now)

    user = USERS[username]
    return {
        "user_id":  user_id,
        "username": username,
        "name":     user["name"],
        "email":    user["email"],
        "age":      user["age"],
        "session_info": {
            "last_active_ago_sec": int(elapsed),
            "cookie_renewed":      elapsed >= RENEW_THRESHOLD,
        }
    }


@app.post("/logout")
def logout(
    response: Response,
    session_token: Optional[str] = Cookie(default=None),
):
    if session_token:
        try:
            user_id, _ = parse_token(session_token)
            user_id_map.pop(user_id, None)
        except (BadSignature, ValueError):
            pass
    response.delete_cookie("session_token")
    return {"message": "Выход выполнен"}