from datetime import timedelta, datetime
from Database import Databases
from Models.Models import UserInDB
from Utils.Hasher import HasherClass, SECRET_KEY, ALGORITHM
from jose import jwt
from jose.exceptions import ExpiredSignatureError
from Models.Models import *
from fastapi import HTTPException, Depends, APIRouter, status


class BadTokenError(Exception): pass


db = Databases.SQLDatabase()
Database = Databases.DatabaseBaseClass()
router = APIRouter()
Hasher = HasherClass()
ACCESS_TOKEN_EXPIRE_MINUTES = 300


# --------------------------FUNCTIONS-------------------------------
def unpack_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, ALGORITHM)
        username = payload.get('login')
        user_type = payload.get('type')
        return username, user_type
    except ExpiredSignatureError:
        raise ExpiredSignatureError
    except:
        raise BadTokenError


def get_user(login: str):
    c = Databases.users_conn.cursor()
    c.execute(f"SELECT * FROM business WHERE login='{login}'")
    user = c.fetchone()

    if not user:
        c.execute(f"SELECT * FROM physic WHERE login='{login}'")
        user = c.fetchone()
        if not user:
            c.execute(f"SELECT * FROM sotrudnik WHERE login='{login}'")
            user = c.fetchone()
            if not user:
                return False
            user['user_type'] = 'sotrudnik'
            return UserInDB(**user)
        user['user_type'] = 'physic'
        return UserInDB(**user)
    user['user_type'] = 'business'
    return UserInDB(**user)


def authenticate_user(login: str, password: str):
    user = get_user(login)
    if not user:
        return False
    if not Hasher.verify_password(password, user.hashed_password):
        return False
    return user


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def get_user_id_tariff(username):
    db.user_c.execute(f"SELECT id_physic, id_business from physic where login='{username}'")
    id = db.user_c.fetchone()
    db.user_c.execute(f"SELECT tariff from business where id_business={id['id_business']}")
    tariff = db.user_c.fetchone()
    return id['id_physic'], tariff['tariff']

# --------------------------ROUTES-------------------------------


@router.post("/login", tags=['user'])
async def login_for_access_token(user: auth):
    user = authenticate_user(user.username, user.password)
    print(user)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"login": user.login, "type": user.user_type}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.post('/register', tags=['user'])
async def create_user(user: reg_user, user_type: str):
    is_user = get_user(user.username)
    if is_user:
        return HTTPException(status_code=400, detail="personal account occupied")
    hashed_password = Hasher.get_password_hash(user.password)
    return await db.create_user(username=user.username, password=hashed_password,
                                email=user.email, user_type=user_type, full_name=user.full_name)
