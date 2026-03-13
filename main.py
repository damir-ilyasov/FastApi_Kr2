from fastapi import FastAPI, Response
from pydantic import BaseModel, field_validator
from typing import Annotated
from fastapi.params import Header
import re
import datetime
app = FastAPI()

class CommonHeaders(BaseModel):
    user_agent: str = Header(alias="user-agent")
    accept_language: str = Header(alias="accept-language")

    model_config = {"populate_by_name": True}

    @field_validator("accept_language")
    @classmethod
    def validate_accept_language(cls, v):
        pattern = r'^([a-zA-Z]{1,8}(-[a-zA-Z0-9]{1,8})*(;q=0(\.\d{1,3})?)?)(,\s*[a-zA-Z]{1,8}(-[a-zA-Z0-9]{1,8})*(;q=0(\.\d{1,3})?)?)*$'
        if not re.match(pattern, v):
            raise ValueError("Неверный формат заголовка Accept-Language")
        return v

@app.get("/headers")
def get_headers(headers: Annotated[CommonHeaders, Header()]):
    return {
        "User-Agent": headers.user_agent,
        "Accept-Language": headers.accept_language,
    }

@app.get("/info")
def get_info(headers: Annotated[CommonHeaders, Header()], response: Response):
    response.headers["X-Server-Time"] = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

    return {
        "message": "Добро пожаловать! Ваши заголовки успешно обработаны.",
        "headers": {
            "User-Agent": headers.user_agent,
            "Accept-Language": headers.accept_language,
        }
    }