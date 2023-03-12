import asyncio, aiomysql
from typing import Any
import asyncssh
from databases import Database
from Utils import Hasher
from Utils.Env import EnvClass


# -----------------------ERRORS------------------------
class DatabaseError(Exception): pass


class DatabaseConnectionError(DatabaseError): pass


class DatabaseTransactionError(DatabaseError): pass


# -----------------------MYSQL-------------------------

async def ssh_connect():
    ssh_client = await asyncssh.connect(
        '185.185.70.161',  # SSH server IP address
        username='chelavik',  # SSH server username
        password='chel123',  # SSH server password
        known_hosts=None
    )
    await ssh_client.forward_local_port(
        '185.185.70.161',  # Local IP address
        3333,  # Local port
        '127.0.0.1',  # Remote MySQL server hostname
        3306  # Remote MySQL server port
    )


# -----------------------------SQLITE---------------------------


class DatabaseBaseClass:
    def __init__(self):
        self.path_to_database = "database.db"
        self.database_inited: bool = False
        self.Hasher = Hasher.HasherClass()
        self.database: Database | None = None
        self.Env = EnvClass()

    async def database_init(self):
        self.database = Database(self.Env.env["DATABASE_URL"])
        await self.database.connect()
        self.database_inited = True
        try:
            await self.request(
                'CREATE TABLE IF NOT EXISTS about_us(' \
                'about_text TEXT PRIMARY KEY);'
            )
            await self.request(
                'CREATE TABLE IF NOT EXISTS for_developers(' \
                '    id_article INTEGER PRIMARY KEY AUTOINCREMENT,' \
                '    article_name TEXT,' \
                '    article_text TEXT);'
            )
            await self.request(
                'CREATE TABLE IF NOT EXISTS services(' \
                '    id_service INTEGER PRIMARY KEY AUTOINCREMENT,' \
                '    service_name TEXT,' \
                '    price TEXT);'
            )
        except Exception as e:
            print(f"Request error - {e}")
            raise DatabaseTransactionError()

    async def database_uninit(self):
        if self.database: await self.database.disconnect()

    async def request(self, request: str, *args: dict[str, str | int], **other: str | int):
        if not self.database_inited or self.database is None:
            if not await self.database_init():
                raise DatabaseConnectionError()
        try:
            common_dict = {key: value for dict in [*args, other] for key, value in dict.items()}
            if "select" not in request.lower():
                await self.database.execute(request, common_dict)  # type: ignore
                return None
            else:
                response: list[dict[str, Any]] = \
                    list(map(
                        lambda x: dict(x),  # type: ignore
                        await self.database.fetch_all(request, common_dict)  # type: ignore
                    ))
                return response
        except Exception as e:
            print(f"Request error - {e}")
            raise DatabaseTransactionError()



class DatabaseClass(DatabaseBaseClass):
    # -----------------------requests----------------------------


    #about_us
    getAboutUs = 'SELECT * FROM about_us'
    editAboutUs = 'UPDATE about_us SET about_text=:about_text'


    #articles
    getAllArticles = 'SELECT * FROM for_developers'
    getArticleById = 'SELECT * FROM for_developers WHERE id_article=:article_id'
    getArticleByName = 'SELECT * FROM for_developers WHERE article_name=:article_name'
    editArticleById = 'UPDATE for_developers SET article_name=:article_name, article_text=:article_text WHERE id_article=:article_id'
    editArticleByName = 'UPDATE for_developers SET article_text=:article_text WHERE article_name=:article_name'
    postArticle = 'INSERT INTO for_developers (article_name, article_text) VALUES (:article_name, :article_text)'
    deleteArticle = 'DELETE FROM for_developers WHERE id_article=:article_id'


    #services
    getAllServices = 'SELECT * FROM services'
    editServiceById = 'UPDATE services SET service_name=:service_name, price=:price WHERE id_service=:service_id'
    postService = 'INSERT INTO services (service_name, price) VALUES (:service_name, :price)'
    deleteService = 'DELETE FROM services WHERE id_service=:service_id'


    #-------------------------functions------------------------------
    

    #about_us
    async def get_about_us(self):
        return await self.request(self.getAboutUs)

    async def edit_about_us(self, AboutUs):
        await self.request(self.editAboutUs, about_text=AboutUs.about_text)
        return {'Edited':'successfully'}


    #articles
    async def get_all_articles(self):
        return await self.request(self.getAllArticles)

    async def get_article_by_id(self, article_id):
        return await self.request(self.getArticleById, article_id=article_id)

    async def get_article_by_name(self, article_name):
        return await self.request(self.getArticleByName, article_name=article_name)

    async def edit_article_by_id(self, article_id, Article):
        await self.request(self.editArticleById, article_id=article_id, article_name=Article.article_name, article_text=Article.article_text)
        return {'Edited':'successfully'}

    async def edit_article_by_name(self, article_name, Article):
        await self.request(self.editArticleByName, article_name=article_name, article_text=Article.article_text)
        return {'Edited':'successfully'}

    async def post_article(self, Article):
        await self.request(self.postArticle, article_name=Article.article_name, article_text=Article.article_text)
        return {'Posted':'successfully'}

    async def delete_article(self, article_id):
        await self.request(self.deleteArticle, article_id=article_id)
        return {'Deleted':'successfully'}


    #services
    async def get_all_services(self):
        return await self.request(self.getAllServices)

    async def edit_service_by_id(self, service_id, Service):
        await self.request(self.editServiceById, service_id=service_id, service_name=Service.service_name, price=Service.price)
        return {'Edited':'successfully'}

    async def post_service(self, Service):
        await self.request(self.postService, service_name=Service.service_name, price=Service.price)
        return {'Posted':'successfully'}

    async def delete_service(self, service_id):
        await self.request(self.deleteService, service_id=service_id)
        return {'Deleted':'successfully'}
