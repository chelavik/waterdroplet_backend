from pydantic import BaseModel


class User(BaseModel):
    username: str
    password: str


class CheckToken(BaseModel):
    token: str
