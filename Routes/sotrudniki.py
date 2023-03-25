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


# -----------------ROUTES--------------------

@router.post('/get_all_workers')
async def get_all_workers(token: Token):
    try:
        username, user_type = unpack_token(token.access_token)
        if user_type == "business":
            info = await SQLDatabase.get_all_workers(username)
            return JSONResponse({'info': info})
        else:
            return HTTPException(status_code=400, detail="bad user_type")
    except ExpiredSignatureError:
        return HTTPException(status_code=400, detail='token expired')
    except BadTokenError:
        return HTTPException(status_code=400, detail='bad token')