from fastapi import FastAPI
from pydantic import BaseModel, EmailStr, field_validator

app = FastAPI()
class UserCreate(BaseModel):
    name: str
    email: EmailStr
    age: int
    is_subscribed: bool
    
    @field_validator("age")
    @classmethod
    def age_validate(cls, v):
        if v is not None and v <= 0:
            raise ValueError("Возраст не мможет быть меньше 0")
        return v

@app.post('/create_users')
async def create_users(user: UserCreate):
    return user