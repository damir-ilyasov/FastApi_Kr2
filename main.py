from fastapi import FastAPI, Header, HTTPException
from typing import Optional
import re
app = FastAPI()

def validate_accept_language(value: str) -> bool:
    pattern = r'^([a-zA-Z]{1,8}(-[a-zA-Z0-9]{1,8})*(;q=0(\.\d{1,3})?)?)(,\s*[a-zA-Z]{1,8}(-[a-zA-Z0-9]{1,8})*(;q=0(\.\d{1,3})?)?)*$'
    return bool(re.match(pattern, value))

@app.get("/headers")
def get_headers(
    user_agent: Optional[str] = Header(default=None),
    accept_language: Optional[str] = Header(default=None),
):
    if not user_agent:
        raise HTTPException(status_code=400, detail="Заголовок User-Agent отсутствует")

    if not accept_language:
        raise HTTPException(status_code=400, detail="Заголовок Accept-Language отсутствует")

    if not validate_accept_language(accept_language):
        raise HTTPException(status_code=400, detail="Неверный формат заголовка Accept-Language")

    return {
        "User-Agent": user_agent,
        "Accept-Language": accept_language,
    }