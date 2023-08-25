from fastapi import APIRouter, HTTPException
from Models.Models import Token, AboutUs, Article, Service
from Utils.Hasher import HasherClass
from Database.Databases import DatabaseClass
from typing import Optional
from Routes.Authorization import BadTokenError, unpack_token
from starlette.responses import JSONResponse
from jose.exceptions import ExpiredSignatureError

database = DatabaseClass()
HasherObject = HasherClass()
router = APIRouter()


# ---------------------------------ABOUT US---------------------------------------------

# get
@router.get('/get-about-us', tags=['site_info'])
async def get_about_us():
    try:
        return JSONResponse(await database.get_about_us())
    except:
        raise HTTPException(status_code=500, detail='Database Error')


# put
@router.put('/edit-about-us', tags=['site_info'])
async def edit_about_us(token: Token, AboutUs: AboutUs):
    try:
        username, user_type = unpack_token(token.access_token)
        if username == 'admin' and user_type == 'admin':
            await database.edit_about_us(AboutUs)
            return HTTPException(status_code=200, detail='Success')
        else:
            raise HTTPException(status_code=400, detail='No permission')
    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail='token expired')
    except BadTokenError:
        raise HTTPException(status_code=400, detail='bad token')
    except:
        raise HTTPException(status_code=500, detail='Database Error')


# -------------------------------articles(for developers)--------------------------------

# get all
@router.get('/get-all-articles', tags=['site_info'])
async def get_all_articles():
    try:
        return JSONResponse(await database.get_all_articles())
    except:
        raise HTTPException(status_code=500, detail='Database Error')


# get
@router.get('/get-article-by-id/{article_id}', tags=['site_info'])
async def get_article_by_id(article_id: int):
    try:
        return JSONResponse(await database.get_article_by_id(article_id))
    except:
        raise HTTPException(status_code=500, detail='Database Error')


# put
@router.put('/edit-article/{article_id}', tags=['site_info'])
async def edit_article(token: Token, article_id: int, article_text: str, article_name: Optional[str] = None):
    try:
        username, user_type = unpack_token(token.access_token)
        if username == 'admin' and user_type == 'admin':
            if article_name is not None:
                await database.edit_article(article_id, article_name, article_text)
            await database.edit_article_text(article_id, article_text)
            return HTTPException(status_code=200, detail='Success')
        else:
            return HTTPException(status_code=400, detail='No permission')
    except ExpiredSignatureError:
        return HTTPException(status_code=401, detail='token expired')
    except BadTokenError:
        return HTTPException(status_code=400, detail='bad token')
    except:
        raise HTTPException(status_code=500, detail='Database Error')


# post
@router.post('/post-article', tags=['site_info'])
async def post_article(token: Token, Article: Article):
    try:
        username, user_type = unpack_token(token.access_token)
        if username == 'admin' and user_type == 'admin':
            await database.post_article(Article)
            return HTTPException(status_code=200, detail='Success')
        else:
            return HTTPException(status_code=400, detail='No permission')
    except ExpiredSignatureError:
        return HTTPException(status_code=401, detail='token expired')
    except BadTokenError:
        return HTTPException(status_code=400, detail='bad token')
    except:
        raise HTTPException(status_code=500, detail='Database Error')


# delete
@router.delete('/delete-article/{article_id}', tags=['site_info'])
async def delete_article(token: Token, article_id: int):
    try:
        username, user_type = unpack_token(token.access_token)
        if username == 'admin' and user_type == 'admin':
            await database.delete_article(article_id)
            return HTTPException(status_code=200, detail='Success')
        else:
            return HTTPException(status_code=400, detail='No permission')
    except ExpiredSignatureError:
        return HTTPException(status_code=401, detail='token expired')
    except BadTokenError:
        return HTTPException(status_code=400, detail='bad token')
    except:
        raise HTTPException(status_code=500, detail='Database Error')


# ---------------------------------------services--------------------------------------

# get all
@router.get('/get-all-services', tags=['site_info'])
async def get_all_services():
    try:
        return JSONResponse(await database.get_all_services())
    except:
        raise HTTPException(status_code=500, detail='Database Error')


# put
@router.put('/edit-service-by-id/{service_id}', tags=['site_info'])
async def edit_service_by_id(token: Token, Service: Service, service_id: int):
    try:
        username, user_type = unpack_token(token.access_token)
        if username == 'admin' and user_type == 'admin':
            await database.edit_service_by_id(service_id, Service)
            return HTTPException(status_code=200, detail='Success')
        else:
            return HTTPException(status_code=400, detail='No permission')
    except ExpiredSignatureError:
        return HTTPException(status_code=401, detail='token expired')
    except BadTokenError:
        return HTTPException(status_code=400, detail='bad token')
    except:
        raise HTTPException(status_code=500, detail='Database Error')


# post
@router.post('/post-service', tags=['site_info'])
async def post_service(token: Token, Service: Service):
    try:
        username, user_type = unpack_token(token.access_token)
        if username == 'admin' and user_type == 'admin':
            await database.post_service(Service)
            return HTTPException(status_code=200, detail='Success')
        else:
            return HTTPException(status_code=400, detail='No permission')
    except ExpiredSignatureError:
        return HTTPException(status_code=401, detail='token expired')
    except BadTokenError:
        return HTTPException(status_code=400, detail='bad token')
    except:
        raise HTTPException(status_code=500, detail='Database Error')


# delete
@router.delete('/delete-service/{service_id}', tags=['site_info'])
async def delete_service(token: Token, service_id: int):
    try:
        username, user_type = unpack_token(token.access_token)
        if username == 'admin' and user_type == 'admin':
            await database.delete_service(service_id)
            return HTTPException(status_code=200, detail='Success')
        else:
            return HTTPException(status_code=400, detail='No permission')
    except ExpiredSignatureError:
        return HTTPException(status_code=401, detail='token expired')
    except BadTokenError:
        return HTTPException(status_code=400, detail='bad token')
    except:
        raise HTTPException(status_code=500, detail='Database Error')
