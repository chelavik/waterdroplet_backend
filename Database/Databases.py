import asyncio, aiomysql, pymysql
from typing import Any
from databases import Database
from Utils import Hasher
from Utils.Env import EnvClass
import config


# -----------------------ERRORS------------------------
class DatabaseError(Exception): pass


class DatabaseConnectionError(DatabaseError): pass


class DatabaseTransactionError(DatabaseError): pass


class BadUserError(DatabaseError): pass


# -----------------MYSQL_CONNECTIONS-----------------------
users_conn = pymysql.connect(
    host=config.host,
    port=config.port,
    user=config.user_users,
    password=config.users_password,
    db=config.db_users,
    cursorclass=pymysql.cursors.DictCursor
)

trans_conn = pymysql.connect(
    host=config.host,  # Local IP address
    port=config.port,  # Local port
    user=config.user_trans,  # MySQL server username
    password=config.trans_password,  # MySQL server password
    db=config.db_trans,  # MySQL database name
    cursorclass=pymysql.cursors.DictCursor
)


# -----------------------------MYSQL-----------------------
class SQLDatabase:
    def __init__(self):
        self.users_conn = users_conn
        self.trans_conn = trans_conn

    # ---------------------------USERS-----------------------------------------------
    async def change_password(self, new_password, username, user_type):
        user_c = self.users_conn.cursor()
        user_c.execute(f"UPDATE {user_type} set hashed_password='{new_password}' WHERE login = '{username}'")
        users_conn.commit()
        user_c.close()

    async def change_email(self, new_email, username, user_type):
        user_c = self.users_conn.cursor()
        user_c.execute(f"UPDATE {user_type} set email='{new_email}' WHERE login = '{username}'")
        users_conn.commit()
        user_c.close()

    async def get_user(self, username, user_type):
        if user_type == 'physic':
            user_c = self.users_conn.cursor()
            user_c.execute(f"SELECT id_physic, login, full_name, email, address, id_business"
                           f" from physic WHERE login='{username}'")
            data = user_c.fetchone()
        elif user_type == 'sotrudnik':
            user_c = self.users_conn.cursor()
            user_c.execute(f"SELECT id_sotrudnik, id_business, login from sotrudnik WHERE login='{username}'")
            data = user_c.fetchone()
        else:
            raise BadUserError
        user_c.close()
        return data

    async def get_business(self, username, user_type):
        if user_type == 'business':
            user_c = self.users_conn.cursor()
            user_c.execute(f"SELECT id_business, login, email, apitoken, tariff from business "
                           f"WHERE login='{username}'")
            data = user_c.fetchone()
            user_c.close()
            return data
        else:
            raise BadUserError

    async def create_user(self, username, password, email, user_type, full_name):
        if user_type == 'physic':
            user_c = self.users_conn.cursor()
            user_c.execute(f"INSERT INTO {user_type} (login, email, hashed_password, full_name)"
                           f" VALUES ('{username}', '{email}', '{password}', '{full_name}')")
            self.users_conn.commit()
            user_c.close()
        elif user_type == 'business':
            user_c = self.users_conn.cursor()
            user_c.execute(
                f"INSERT INTO {user_type} (login, email, hashed_password)"
                f" VALUES ('{username}', '{email}', '{password}')")
            self.users_conn.commit()
            user_c.close()
        else:
            raise BadUserError

    async def get_ipus(self, username, user_type):
        try:
            if user_type != 'physic':
                raise BadUserError
            user_c = self.users_conn.cursor()
            validate_c = self.trans_conn.cursor()
            user_id, tariff = await self.get_user_id_tariff(username)
            data = {}
            user_c.execute(f"SELECT ipus from physic WHERE login='{username}'")
            ipus = (user_c.fetchone())['ipus'].split()
            for i in ipus:
                try:
                    validate_c.execute(f"SELECT date from transactions WHERE id_physic={user_id} AND ipu='{i}' "
                                   f"ORDER BY date DESC "
                                   f"LIMIT 1")
                    date = (validate_c.fetchone())['date'].strftime('%m/%d/%Y')
                    data[i] = date
                except:
                    data[i] = 'None'
            user_c.close()
            validate_c.close()
            return data
        except:
            ...

    async def get_user_id_tariff(self, username):
        user_c = self.users_conn.cursor()
        user_c.execute(f"SELECT id_physic, id_business from physic where login='{username}'")
        id = user_c.fetchone()
        user_c.execute(f"SELECT tariff from business where id_business={id['id_business']}")
        tariff = user_c.fetchone()
        user_c.close()
        return id['id_physic'], tariff['tariff']

    # -------------------------TRANSACTIONS----------------------------------

    async def get_last_number(self, user_id, ipu):
        validate_c = self.trans_conn.cursor()
        validate_c.execute(f"SELECT prev_number from transactions WHERE id_physic={user_id} AND ipu='{ipu}' "
                           f"ORDER BY date DESC "
                           f"LIMIT 1")
        prev_number = validate_c.fetchone()
        if not prev_number:
            prev_number = 0
        else:
            prev_number = prev_number['prev_number']
        validate_c.close()
        return prev_number

    async def add_transaction(self, user_id, prev_number, new_number, ipu, payment_sum):
        validate_c = self.trans_conn.cursor()
        validate_c.execute(f"INSERT INTO transactions "
                           f"(date, id_physic, ipu, prev_number, new_number, payment_sum, status) "
                           f"VALUES (NOW(), {user_id}, '{ipu}', '{prev_number}', '{new_number}', "
                           f"{payment_sum}, 1)")
        self.trans_conn.commit()
        validate_c.execute(
            f"SELECT id_transaction, payment_sum from transactions WHERE id_physic={user_id} AND ipu='{ipu}' "
            f"ORDER BY date DESC "
            f"LIMIT 1")
        data = validate_c.fetchone()
        validate_c.close()
        return data

    async def change_status(self, trans_id: int, status: int):
        validate_c = self.trans_conn.cursor()
        validate_c.execute(f"UPDATE transactions set status={status} WHERE id_transaction={trans_id}")
        self.trans_conn.commit()
        validate_c.close()


# -----------------------------SQLITE----------------------------


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
        finally:
            return self.database_inited

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

    # about_us
    getAboutUs = 'SELECT * FROM about_us'
    editAboutUs = 'UPDATE about_us SET about_text=:about_text'

    # articles
    getAllArticles = 'SELECT * FROM for_developers'
    getArticleById = 'SELECT * FROM for_developers WHERE id_article=:article_id'
    editArticle = 'UPDATE for_developers SET article_name=:article_name, article_text=:article_text WHERE id_article=:article_id'
    editArticleText = 'UPDATE for_developers SET article_text=:article_text WHERE id_article=:article_id'
    postArticle = 'INSERT INTO for_developers (article_name, article_text) VALUES (:article_name, :article_text)'
    deleteArticle = 'DELETE FROM for_developers WHERE id_article=:article_id'

    # services
    getAllServices = 'SELECT * FROM services'
    editServiceById = 'UPDATE services SET service_name=:service_name, price=:price WHERE id_service=:service_id'
    postService = 'INSERT INTO services (service_name, price) VALUES (:service_name, :price)'
    deleteService = 'DELETE FROM services WHERE id_service=:service_id'

    # -------------------------functions------------------------------

    # about_us
    async def get_about_us(self):
        return (await self.request(self.getAboutUs))[0]
        # Adajiojfokp[];

    async def edit_about_us(self, AboutUs):
        await self.request(self.editAboutUs, about_text=AboutUs.about_text)

    # articles
    async def get_all_articles(self):
        return await self.request(self.getAllArticles)

    async def get_article_by_id(self, article_id):
        return (await self.request(self.getArticleById, article_id=article_id))[0]

    async def edit_article(self, article_id, article_name, article_text):
        await self.request(self.editArticle, article_id=article_id, article_name=article_name,
                           article_text=article_text)

    async def edit_article_text(self, article_id, article_text):
        await self.request(self.editArticleText, article_id=article_id, article_text=article_text)

    async def post_article(self, Article):
        await self.request(self.postArticle, article_name=Article.article_name, article_text=Article.article_text)

    async def delete_article(self, article_id):
        await self.request(self.deleteArticle, article_id=article_id)

    # services
    async def get_all_services(self):
        return await self.request(self.getAllServices)

    async def edit_service_by_id(self, service_id, Service):
        await self.request(self.editServiceById, service_id=service_id, service_name=Service.service_name,
                           price=Service.price)

    async def post_service(self, Service):
        await self.request(self.postService, service_name=Service.service_name, price=Service.price)

    async def delete_service(self, service_id):
        await self.request(self.deleteService, service_id=service_id)
