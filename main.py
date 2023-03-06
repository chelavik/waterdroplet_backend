from fastapi import HTTPException, Depends, FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from Utils.Hasher import HasherClass
from Database import Databases
from Routes import *

database = Databases.DatabaseBaseClass()
HasherObject = HasherClass()
app = FastAPI()


# -------------CURSORS-------------------


async def create_validate_cursor():
    app.state.mysql_conn = await aiomysql.connect(
        host='185.185.70.161',  # Local IP address
        port=3333,  # Local port
        user='admin_backend',  # MySQL server username
        password='BacKend_paSSword123331',  # MySQL server password
        db='transactions',  # MySQL database name
        loop=asyncio.get_event_loop(),
        charset='utf8mb4'
    )


async def create_users_cursor():
    app.state.mysql_conn1 = await aiomysql.connect(
        host='185.185.70.161',  # Local IP address
        port=3333,  # Local port
        user='admin_backend',  # MySQL server username
        password='BacKend_paSSword123331',  # MySQL server password
        db='waterdroplet_model',  # MySQL database name
        loop=asyncio.get_event_loop(),
        charset='utf8mb4'
    )


# -----------------------ROUTES-------------------------


@app.on_event('startup')
async def startup_event():
    if await database.database_init():
        raise Databases.DatabaseConnectionError()


@app.on_event('shutdown')
async def shutdown_event():
    try:
        await database.database_uninit()
    except:
        ...

app.include_router(Authorization.router)
app.include_router(Info_CRUD.router)
