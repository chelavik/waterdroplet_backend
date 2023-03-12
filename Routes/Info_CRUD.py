from fastapi import APIRouter, HTTPException
from Models.Models import CheckToken, AboutUs, FullArticle, ArticleText, Service
from Utils.Hasher import HasherClass
from Database.Databases import DatabaseClass


database = DatabaseClass()
HasherObject = HasherClass()
router = APIRouter()

# ---------------------------------ABOUT US---------------------------------------------

#get
@router.get('/get-about-us')
async def get_about_us():
    try:
        return await database.get_about_us()
    except:
        raise HTTPException(status_code=500, detail='Database Error')

#put
@router.put('/edit-about-us')
async def edit_about_us(AboutUs: AboutUs): #auth is required
    try:
        return await database.edit_about_us(AboutUs)
    except:
        raise HTTPException(status_code=500, detail='Database Error')

#-------------------------------articles(for developers)--------------------------------

#get all
@router.get('/get-all-articles')
async def get_all_articles():
    try:
        return await database.get_all_articles()
    except:
        raise HTTPException(status_code=500, detail='Database Error')

#get by id
@router.get('/get-article-by-id/{article_id}')
async def get_article_by_id(article_id: int):
    try:
        return await database.get_article_by_id(article_id)
    except:
        raise HTTPException(status_code=500, detail='Database Error')

#get by name
@router.get('/get-article-by-name/{article_name}')
async def get_article_by_name(article_name: str):
    try:
        return await database.get_article_by_name(article_name)
    except:
        raise HTTPException(status_code=500, detail='Database Error')

#put by id(whole article)
@router.put('/edit-article-by-id/{article_id}')
async def edit_article_by_id(article_id: int, Article: FullArticle): #auth is required
    try:
        return await database.edit_article_by_id(article_id, Article)
    except:
        raise HTTPException(status_code=500, detail='Database Error')

#put by name(text only)
@router.put('/edit-article-by-name/{article_name}')
async def edit_article_by_name(article_name: str, Article: ArticleText): #auth is required
    try:
        return await database.edit_article_by_name(article_name, Article)
    except:
        raise HTTPException(status_code=500, detail='Database Error')

@router.post('/post-article')
async def post_article(Article: FullArticle):
    try:
        return await database.post_article(Article)
    except:
        raise HTTPException(status_code=500, detail='Database Error')

#crud

#---------------------------------------services--------------------------------------

#get all
@router.get('/get-all-services')
async def get_all_services():
    try:
        return await database.get_all_services()
    except:
        raise HTTPException(status_code=500, detail='Database Error')

#put by id
@router.put('/edit-service-by-id/{service_id}')
async def edit_service_by_id(service_id: int, Service: Service): #auth is required
    try:
        return await database.edit_service_by_id(service_id, Service)
    except:
        raise HTTPException(status_code=500, detail='Database Error')

#post
@router.post('/post-service')
async def post_service(Service: Service): #auth is required
    try:
        return await database.post_service(Service)
    except:
        raise HTTPException(status_code=500, detail='Database Error')

#crud
