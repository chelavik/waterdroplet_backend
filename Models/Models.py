from typing import Optional
from pydantic import BaseModel


class User(BaseModel):
    id_business: Optional[int] = None
    id_physic: Optional[int] = None
    id_sotrudnik: Optional[int] = None
    login: str
    email: Optional[str] = None
    apitoken: Optional[str] = None
    tariff: Optional[str] = None


class CheckToken(BaseModel):
    token: str


class reg_user(BaseModel):
    username: str
    password: str
    email: Optional[str] = None
    full_name: Optional[str] = None


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


class Worker(BaseModel):
    login: str
    full_name: str
    phone: str
    password: str


class Secret_key(BaseModel):
    key: str