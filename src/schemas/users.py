from pydantic import BaseModel, EmailStr


class UserDetail(BaseModel):
    id: int
    username: str
    email: str
    avatar: str | None


class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class RequestEmail(BaseModel):
    email: EmailStr
