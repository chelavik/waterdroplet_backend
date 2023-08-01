from cryptography.fernet import InvalidToken
import requests

from Database import Databases
from Database.Databases import NotFoundError
from Routes.Transactions import Encrypter
from Utils.Hasher import HasherClass
from jose.exceptions import ExpiredSignatureError
from Models.Models import *
from fastapi import HTTPException, APIRouter, UploadFile, File, Form
from starlette.responses import JSONResponse
from Routes.Authorization import unpack_token, BadTokenError
from Utils.QRscanner import scanQR
from config import SECRET_KEY, iputoken

router = APIRouter()
Hasher = HasherClass()
SQLDatabase = Databases.SQLDatabase()


@router.post('/get_related_physics', tags=['business'])
async def get_related_physics(token: Token):
    try:
        username, user_type = unpack_token(token.access_token)
        if user_type == "business":
            info = await SQLDatabase.get_related_physics(username)
            return JSONResponse(info)
        else:
            raise HTTPException(status_code=400, detail="bad user_type")
    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail='token expired')
    except BadTokenError:
        raise HTTPException(status_code=401, detail='bad token')


@router.post('/get_related_physics/{page_id}', tags=['business'])
async def get_hundred_physics(token: Token, page_id: int):
    try:
        username, user_type = unpack_token(token.access_token)
        if user_type == "business":
            page_id -= 1
            info = await SQLDatabase.get_hundred_physics(username, page_id)
            return JSONResponse(info)
        else:
            raise HTTPException(status_code=400, detail="bad user_type")
    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail='token expired')
    except BadTokenError:
        raise HTTPException(status_code=401, detail='bad token')


@router.post('/get_all_validations/{page_id}', tags=['business'])
async def get_all_validations(token: Token, page_id: int):
    try:
        username, user_type = unpack_token(token.access_token)
        if user_type == "business":
            page_id -= 1
            info = await SQLDatabase.get_all_validations(username, page_id)
            for dictionary in info:
                dictionary['validation_date'] = str(dictionary['validation_date'])
            return JSONResponse(info)
        else:
            raise HTTPException(status_code=400, detail="bad user_type")
    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail='token expired')
    except BadTokenError:
        raise HTTPException(status_code=401, detail='bad token')



@router.post('/suspicious_validations/{page_id}', tags=['business'])
async def get_suspicious_validations(token: Token, page_id: int):
    try:
        username, user_type = unpack_token(token.access_token)
        if user_type == "business":
            page_id -= 1
            info = await SQLDatabase.get_suspicious_validations(username, page_id)
            for dictionary in info:
                dictionary['validation_date'] = str(dictionary['validation_date'])
            return JSONResponse(info)
        else:
            raise HTTPException(status_code=400, detail="bad user_type")
    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail='token expired')
    except BadTokenError:
        raise HTTPException(status_code=401, detail='bad token')


@router.post('/get_all_related_addresses', tags=['sotrudnik'])
async def get_all_related_addresses(token: Token):
    try:
        username, user_type = unpack_token(token.access_token)
        if user_type == "sotrudnik" or user_type == 'business':
            info = await SQLDatabase.get_all_addresses(username, user_type)
            return JSONResponse(info)
        else:
            raise HTTPException(status_code=400, detail="bad user_type")
    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail='token expired')
    except BadTokenError:
        raise HTTPException(status_code=401, detail='bad token')


@router.post('/get_related_address/{page_id}', tags=['sotrudnik'])
async def get_related_address(token: Token, page_id: int):
    try:
        username, user_type = unpack_token(token.access_token)
        if user_type == "sotrudnik" or user_type == "business":
            page_id -= 1
            info = await SQLDatabase.get_addresses(username, page_id, user_type)
            return JSONResponse(info)
        else:
            raise HTTPException(status_code=400, detail="bad user_type")
    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail='token expired')
    except BadTokenError:
        raise HTTPException(status_code=401, detail='bad token')


@router.post('/get_ipus_by_address', tags=['sotrudnik'])
async def get_ipus_by_address(token: Token, address: str):
    try:
        username, user_type = unpack_token(token.access_token)
        if user_type == "sotrudnik":
            username = await SQLDatabase.get_username_by_address(address)
            info = await SQLDatabase.get_ipus(username, 'sotrudnik')
            return JSONResponse(info)
        else:
            raise HTTPException(status_code=400, detail="bad user_type")
    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail='token expired')
    except BadTokenError:
        raise HTTPException(status_code=401, detail='bad token')
    except NotFoundError:
        raise HTTPException(status_code=404, detail='user by address not found')


@router.post('/scan_validation_photo', tags=['sotrudnik'])
async def scan_validation_photo(photo: UploadFile = File(...), key: str = Form()):
    try:
        if not Hasher.verify_password(key, SECRET_KEY):
            raise HTTPException(status_code=403, detail='bad secret key')
        content = await photo.read()
        qr_info = scanQR(content)
        if qr_info == '':
            raise HTTPException(status_code=404, detail='QR-code not found on photo')
        try:
            Encrypter.decrypt_qrinfo(qr_info).split(sep=';')  # договор, счетчик
        except InvalidToken:
            raise HTTPException(status_code=404, detail='QR-code wrong info')
        data = {"token": iputoken}
        files = {"upload_image": (photo.filename, content)}
        number_result = requests.post(url='https://api.waterdroplet.ru/get_number',
                                      data=data, files=files)
        if number_result.status_code == 200:
            res = number_result.json()  # цифры на счетчике
            if res == "":
                raise HTTPException(status_code=417, detail='number not found on photo')
            info = {'qr_string': qr_info, 'number': res['number']}
            return info
        else:
            raise HTTPException(status_code=500, detail='API service Error')
    except:
        ...


@router.post('/new_validation', tags=['sotrudnik'])
async def new_validation(token: Token, sotr_number: str, qr_string: str):
    try:
        username, user_type = unpack_token(token.access_token)
        try:
            qr_info = Encrypter.decrypt_qrinfo(qr_string).split(sep=';')
        except InvalidToken:
            raise HTTPException(status_code=404, detail='QR-info issues')
        address = await SQLDatabase.get_address_by_contract_number(qr_info[0])
        if not user_type == "sotrudnik":
            raise HTTPException(status_code=400, detail="bad user_type")
        await SQLDatabase.add_validation(username, sotr_number, qr_info[1], address)
        return HTTPException(status_code=200, detail="success")
    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail='token expired')
    except BadTokenError:
        raise HTTPException(status_code=401, detail='bad token')


@router.post('/get_validation_logs', tags=['transactions'])
async def get_validation_logs(token: Token, validation_id: int):
    try:
        username, user_type = unpack_token(token.access_token)
        if user_type != 'business':
            raise HTTPException(status_code=403, detail='bad user_type')
        data = await SQLDatabase.get_validation_logs(username, validation_id)
        return JSONResponse(data)
    except ExpiredSignatureError:
        raise HTTPException(status_code=400, detail='token expired')
    except BadTokenError:
        raise HTTPException(status_code=400, detail='bad token')
    except NotFoundError:
        raise HTTPException(status_code=404, detail='validation not found')
