from Database import Databases
from Utils.Hasher import HasherClass
from jose.exceptions import ExpiredSignatureError
from Models.Models import *
from fastapi import HTTPException, APIRouter
from starlette.responses import JSONResponse
from Routes.Authorization import unpack_token, BadTokenError

router = APIRouter()
Hasher = HasherClass()
SQLDatabase = Databases.SQLDatabase()


@router.post('/get_related_physics', tags=['business'])
async def get_related_physics(token: Token):
    try:
        username, user_type = unpack_token(token.access_token)
        if user_type == "business":
            info = await SQLDatabase.get_related_physics(username)
            return JSONResponse({'physics': info})
        else:
            raise HTTPException(status_code=400, detail="bad user_type")
    except ExpiredSignatureError:
        raise HTTPException(status_code=400, detail='token expired')
    except BadTokenError:
        raise HTTPException(status_code=400, detail='bad token')


@router.post('/suspicious_validations', tags=['business'])
async def get_suspicious_validations(token: Token):
    try:
        username, user_type = unpack_token(token.access_token)
        if user_type == "business":
            info = await SQLDatabase.get_suspicious_validations(username)
            return JSONResponse({'sus': info})
        else:
            raise HTTPException(status_code=400, detail="bad user_type")
    except ExpiredSignatureError:
        raise HTTPException(status_code=400, detail='token expired')
    except BadTokenError:
        raise HTTPException(status_code=400, detail='bad token')
