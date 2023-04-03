from fastapi import HTTPException, Depends, FastAPI, APIRouter, status
from fastapi.middleware.cors import CORSMiddleware
from Utils.Hasher import HasherClass
from Database import Databases
from Routes import *
from fastapi_limiter import FastAPILimiter

database = Databases.DatabaseBaseClass()
db = Databases.DatabaseClass()
Hasher = HasherClass()
app = FastAPI()

origins = [
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# -----------------------ROUTES----------------------------

@app.on_event('startup')
async def startup_event():
    if not await database.database_init():
        raise Databases.DatabaseConnectionError()


@app.on_event('shutdown')
async def shutdown_event():
    try:
        await database.database_uninit()
    except:
        ...


# ---------------------------------ROUTERS---------------------------
app.include_router(Info_CRUD.router)
app.include_router(Authorization.router)
app.include_router(UserInfo_update.router)
app.include_router(Transactions.router)
app.include_router(sotrudniki.router)
app.include_router(validations.router)
