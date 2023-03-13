from fastapi import APIRouter, HTTPException
from Models.Models import CheckToken, AboutUs, Article, Service
from Utils.Hasher import HasherClass
from Database.Databases import DatabaseClass
from typing import Optional

database = DatabaseClass()
HasherObject = HasherClass()
router = APIRouter()


# ---------------------------------ABOUT US---------------------------------------------

# get
@router.get('/get-about-us', tags=['site_info'])
async def get_about_us():
    try:
        return await database.get_about_us()
    except:
        raise HTTPException(status_code=500, detail='Database Error')


# put
@router.put('/edit-about-us', tags=['site_info'])
async def edit_about_us(AboutUs: AboutUs):  # auth is required
    try:
        return await database.edit_about_us(AboutUs)
    except:
        raise HTTPException(status_code=500, detail='Database Error')


# -------------------------------articles(for developers)--------------------------------

# get all
@router.get('/get-all-articles', tags=['site_info'])
async def get_all_articles():
    try:
        return await database.get_all_articles()
    except:
        raise HTTPException(status_code=500, detail='Database Error')


# get
@router.get('/get-article-by-id/{article_id}', tags=['site_info'])
async def get_article_by_id(article_id: int):
    try:
        return await database.get_article_by_id(article_id)
    except:
        raise HTTPException(status_code=500, detail='Database Error')


# put
@router.put('/edit-article/{article_id}', tags=['site_info'])
async def edit_article(article_id: int, article_text: str, article_name: Optional[str] = None):
    try:
        if article_name != None:
            return await database.edit_article(article_id, article_name, article_text)
        return await database.edit_article_text(article_id, article_text)
    except:
        raise HTTPException(status_code=500, detail='Database Error')


# post
@router.post('/post-article', tags=['site_info'])
async def post_article(Article: Article):  # auth is required
    try:
        return await database.post_article(Article)
    except:
        raise HTTPException(status_code=500, detail='Database Error')


# delete
@router.delete('/delete-article/{article_id}', tags=['site_info'])
async def delete_article(article_id: int):  # auth is required
    try:
        return await database.delete_article(article_id)
    except:
        raise HTTPException(status_code=500, detail='Database Error')


# ---------------------------------------services--------------------------------------

# get all
@router.get('/get-all-services', tags=['site_info'])
async def get_all_services():
    try:
        return await database.get_all_services()
    except:
        raise HTTPException(status_code=500, detail='Database Error')


# put
@router.put('/edit-service-by-id/{service_id}', tags=['site_info'])
async def edit_service_by_id(service_id: int, Service: Service):  # auth is required
    try:
        return await database.edit_service_by_id(service_id, Service)
    except:
        raise HTTPException(status_code=500, detail='Database Error')


# post
@router.post('/post-service', tags=['site_info'])
async def post_service(Service: Service):  # auth is required
    try:
        return await database.post_service(Service)
    except:
        raise HTTPException(status_code=500, detail='Database Error')


# delete
@router.delete('/delete-service/{service_id}', tags=['site_info'])
async def delete_service(service_id: int):  # auth is required
    try:
        return await database.delete_service(service_id)
    except:
        raise HTTPException(status_code=500, detail='Database Error')
