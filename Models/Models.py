from pydantic import BaseModel


class User(BaseModel):
    username: str
    password: str


class CheckToken(BaseModel):
    token: str


class AboutUs(BaseModel):
    about_text: str


class FullArticle(BaseModel):
    article_name: str
    article_text: str


class ArticleText(BaseModel):
    article_text: str


class Service(BaseModel):
    service_name: str
    price: str
