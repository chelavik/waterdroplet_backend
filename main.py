from fastapi import HTTPException, Depends, FastAPI, APIRouter, status
from fastapi.middleware.cors import CORSMiddleware
from Utils.Hasher import HasherClass
from Database import Databases
from Database.Databases import users_conn, trans_conn
from Routes import *
from fastapi_limiter import FastAPILimiter
import uvicorn

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
        users_conn.close()
        trans_conn.close()
        await database.database_uninit()
    except:
        print('closing connections failed')


# ---------------------------------ROUTERS---------------------------
app.include_router(Info_CRUD.router)
app.include_router(Authorization.router)
app.include_router(UserInfo_update.router)
app.include_router(Transactions.router)
app.include_router(sotrudniki.router)
app.include_router(validations.router)

if __name__ == '__main__':
    uvicorn.run("main:app",
                host="waterdroplet.ru",
                port=5502,
                reload=True,
                ssl_keyfile='/etc/letsencrypt/live/waterdroplet.ru/privkey.pem',
                ssl_certfile='/etc/letsencrypt/live/waterdroplet.ru/fullchain.pem'
                )