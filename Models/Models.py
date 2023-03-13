from typing import Optional
from pydantic import BaseModel


class User(BaseModel):
    id_business: Optional[int] = None
    id_physic: Optional[int] = None
    id_sotrudnik: Optional[int] = None
    login: str
    email: str
    apitoken: str
    tariff: int


class CheckToken(BaseModel):
    token: str

class reg_user(BaseModel):
    username: str
    password: str
    email: str

class UserInDB(User):
    hashed_password: str
    user_type: str


class Token(BaseModel):
    access_token: str



class auth(BaseModel):
    username: str
    password: str


class AboutUs(BaseModel):
    about_text: str


class Article(BaseModel):
    article_name: str
    article_text: str


class Service(BaseModel):
    service_name: str
    price: str
