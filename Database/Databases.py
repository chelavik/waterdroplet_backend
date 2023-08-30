import pymysql
from typing import Optional
import datetime
from typing import Any
from databases import Database
from Utils import Hasher
from Utils.Env import EnvClass
import config


# -----------------------ERRORS------------------------
class DatabaseError(Exception): pass


class NotFoundError(DatabaseError): pass


class DatabaseConnectionError(DatabaseError): pass


class DatabaseTransactionError(DatabaseError): pass


class BadUserError(DatabaseError): pass


class BadUsernameError(DatabaseError): pass


class BadTransactionNumberError(DatabaseError): pass


class BadIpuDeltaError(DatabaseError): pass


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

    async def get_user_by_address(self, address):
        user_c = self.users_conn.cursor()
        user_c.execute(f"SELECT full_name, contract_number, email FROM physic WHERE address='{address}'")
        info = user_c.fetchone()
        if not info:
            raise NotFoundError
        return info

    async def get_username_by_address(self, address):
        user_c = self.users_conn.cursor()
        user_c.execute(f"SELECT contract_number from physic where address='{address}'")
        info = user_c.fetchone()
        if not info:
            raise NotFoundError
        return info['contract_number']

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
            user_c.execute(f"SELECT id_physic, contract_number, full_name, email, address, id_business"
                           f" from physic WHERE contract_number='{username}'")
            data = user_c.fetchone()
        elif user_type == 'sotrudnik':
            user_c = self.users_conn.cursor()
            user_c.execute(f"SELECT id_sotrudnik, id_business, login, full_name "
                           f"from sotrudnik WHERE login='{username}'")
            data = user_c.fetchone()
        else:
            raise BadUserError
        user_c.close()
        return data

    async def get_business(self, username, user_type):
        if user_type == 'business' or user_type == 'admin':
            user_c = self.users_conn.cursor()
            user_c.execute(f"SELECT id_business, login, company_name, email, apitoken, expiration_date from business "
                           f"WHERE login='{username}'")
            data = user_c.fetchone()
            data['expiration_date'] = str(data['expiration_date'])
            user_c.close()
            return data
        else:
            raise BadUserError

    async def create_user(self, username, password, email, user_type, full_name):
        if user_type == 'physic':
            user_c = self.users_conn.cursor()
            user_c.execute(f"INSERT INTO {user_type} (contract_number, email, full_name)"
                           f" VALUES ('{username}', '{email}', '{full_name}')")
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

    async def get_last_values(self, user_id: int, ipu: str):
        validate_c = self.trans_conn.cursor()
        validate_c.execute(f'SELECT new_number, date FROM transactions WHERE id_physic = {user_id} '
                           f'AND ipu = "{ipu}" and status = 2 ORDER BY `date` DESC LIMIT 3;')
        info = validate_c.fetchall()
        validate_c.close()
        return info

    async def get_ipus(self, username, user_type):
        try:
            user_c = self.users_conn.cursor()
            validate_c = self.trans_conn.cursor()
            user_id, tariff = await self.get_user_id_tariff(username)
            data = {}
            user_c.execute(f"SELECT ipus from physic WHERE contract_number='{username}'")
            ipus = (user_c.fetchone())['ipus'].split()
            for i in ipus:
                try:
                    if user_type == 'physic':
                        validate_c.execute(f"SELECT date from transactions WHERE id_physic={user_id} AND ipu='{i}' "
                                           f"ORDER BY date DESC "
                                           f"LIMIT 1")
                        date = (validate_c.fetchone())['date'].strftime('%m/%d/%Y')
                        data[i] = date
                    elif user_type == 'sotrudnik':
                        validate_c.execute(
                            f"SELECT sotrudnik_photo_date from validate WHERE id_physic={user_id} AND ipu='{i}' ORDER BY sotrudnik_photo_date DESC LIMIT 1")
                        date = (validate_c.fetchone())['sotrudnik_photo_date'].strftime('%m/%d/%Y')
                        data[i] = date
                    else:
                        raise BadUserError
                except:
                    data[i] = 'None'
            user_c.close()
            validate_c.close()
            return data
        except:
            ...

    async def get_user_id_tariff(self, username):
        user_c = self.users_conn.cursor()
        user_c.execute(f"SELECT id_physic, id_business from physic where contract_number='{username}'")
        id = user_c.fetchone()
        user_c.execute(f"SELECT tariff from business where id_business={id['id_business']}")
        tariff = user_c.fetchone()
        user_c.close()
        return id['id_physic'], tariff['tariff']

    # -------------------------TRANSACTIONS----------------------------------

    async def get_last_number(self, user_id, ipu):
        validate_c = self.trans_conn.cursor()
        validate_c.execute(
            f"SELECT new_number from transactions WHERE id_physic={user_id} AND ipu='{ipu}' and status=2 "
            f"ORDER BY date DESC "
            f"LIMIT 1")
        prev_number = validate_c.fetchone()
        if not prev_number:
            raise NotFoundError
        prev_number = prev_number['new_number']
        validate_c.close()
        return prev_number

    async def add_transaction(self, user_id, prev_number, new_number, ipu, payment_sum, verdict):
        user_c = self.users_conn.cursor()
        user_c.execute(f"SELECT id_business from physic WHERE id_physic={user_id}")
        business_id = user_c.fetchone()['id_business']
        validate_c = self.trans_conn.cursor()
        validate_c.execute(f"INSERT INTO transactions "
                           f"(date, id_physic, id_business, ipu, prev_number, new_number, payment_sum, status, verdict)"
                           f" VALUES (NOW(), {user_id}, {business_id}, '{ipu}', '{prev_number}', '{new_number}', "
                           f"{payment_sum}, 2, '{verdict}')")
        self.trans_conn.commit()
        validate_c.execute(
            f"SELECT id_transaction, payment_sum, new_number from transactions "
            f"WHERE id_physic={user_id} AND ipu='{ipu}' "
            f"ORDER BY date DESC "
            f"LIMIT 1")
        data = validate_c.fetchone()
        data['number'] = data['new_number']
        del data['new_number']
        validate_c.close()
        return data

    async def change_status(self, trans_id: int, status: int):
        validate_c = self.trans_conn.cursor()
        validate_c.execute(f"UPDATE transactions set status={status}, date=NOW() WHERE id_transaction={trans_id}")
        self.trans_conn.commit()
        validate_c.close()

    async def first_value(self, username, ipu, new_number):
        validate_c = self.trans_conn.cursor()
        user_id, tariff = await self.get_user_id_tariff(username)
        validate_c.execute(
            f"INSERT INTO transactions (date, id_physic, ipu, prev_number, new_number, payment_sum, status, verdict) VALUES "
            f"(NOW(), {user_id}, '{ipu}', '00000000', '{new_number}', 0, 2, 'Не подозрительно')")
        trans_conn.commit()
        validate_c.execute(
            f"SELECT id_transaction, payment_sum, new_number from transactions "
            f"WHERE id_physic={user_id} AND ipu='{ipu}' "
            f"ORDER BY date DESC "
            f"LIMIT 1")
        data = validate_c.fetchone()
        data['number'] = data['new_number']
        del data['new_number']
        validate_c.close()
        return data

    async def get_validation_logs(self, username, validation_id):
        user_id = await self.get_business_id(username)
        validate_c = self.trans_conn.cursor()
        user_c = self.users_conn.cursor()
        validate_c.execute(f"SELECT sotrudnik_id, sotrudnik_photo_date, sotrudnik_number, "
                           f"id_physic, physic_photo_date, physic_number, verdict from validate"
                           f" WHERE id_business={user_id} AND id_validation={validation_id}")
        data = validate_c.fetchone()
        if not data:
            raise NotFoundError
        user_c.execute(f"SELECT full_name from physic where id_physic={data['id_physic']}")
        data['physic_name'] = (user_c.fetchone())['full_name']
        user_c.execute(f"SELECT full_name from sotrudnik where id_sotrudnik={data['sotrudnik_id']}")
        data['sotrudnik_name'] = (user_c.fetchone())['full_name']
        data['sotrudnik_photo_date'] = str(data['sotrudnik_photo_date'])
        data['physic_photo_date'] = str(data['physic_photo_date'])
        del data['sotrudnik_id'], data['id_physic']
        return data

    # ----------------------WORKERS-------------------------------------

    async def get_business_id(self, username):
        user_c = self.users_conn.cursor()
        user_c.execute(f"SELECT id_business FROM business WHERE login='{username}'")
        id = user_c.fetchone()
        user_c.close()
        return id['id_business']

    async def get_sotr_business(self, username):
        user_c = self.users_conn.cursor()
        user_c.execute(f'SELECT id_business FROM sotrudnik WHERE login="{username}"')
        id = user_c.fetchone()
        user_c.close()
        if id:
            return id['id_business']
        else:
            return False

    async def get_all_workers(self, username):
        business_id = await self.get_business_id(username)
        user_c = self.users_conn.cursor()
        user_c.execute(f"SELECT id_sotrudnik, full_name FROM sotrudnik WHERE id_business={business_id}")
        data = user_c.fetchall()
        user_c.close()
        return data

    async def get_worker_info(self, username, sotrudnik_id):
        business_id = await self.get_business_id(username)
        user_c = self.users_conn.cursor()
        user_c.execute(f"SELECT * FROM sotrudnik WHERE id_business={business_id} AND id_sotrudnik={sotrudnik_id}")
        info = user_c.fetchone()
        user_c.close()
        if not info:
            user_c.close()
            raise NotFoundError
        return info

    async def delete_worker(self, username, sotrudnik_id):
        business_id = await self.get_business_id(username)
        user_c = self.users_conn.cursor()
        user_c.execute(f'DELETE FROM sotrudnik WHERE id_sotrudnik={sotrudnik_id} and id_business={business_id} LIMIT 1')
        self.users_conn.commit()
        user_c.close()

    async def create_worker(self, business_name, full_name, login, phone, password):
        if not await self.check_login(login):
            raise BadUsernameError
        business_id = await self.get_business_id(business_name)
        if not business_id:
            raise NotFoundError
        user_c = self.users_conn.cursor()
        user_c.execute(f'INSERT INTO sotrudnik '
                       f'(id_business, login, phone, hashed_password, full_name) '
                       f'VALUES ({business_id}, "{login}", "{phone}", "{password}", "{full_name}")')
        self.users_conn.commit()
        user_c.close()

    async def check_login(self, login):
        user_c = self.users_conn.cursor()
        user_c.execute(f"SELECT id_business from business where login='{login}'")
        if not user_c.fetchone():
            user_c.execute(f"SELECT id_physic from physic where contract_number='{login}'")
            if not user_c.fetchone():
                user_c.execute(f"SELECT id_sotrudnik from sotrudnik where login='{login}'")
                if not user_c.fetchone():
                    user_c.close()
                    return True
        user_c.close()
        return False

    async def edit_worker(self, username, worker_id, login, phone, password, full_name):
        business_id = await self.get_business_id(username)
        user_c = self.users_conn.cursor()
        user_c.execute(f'SELECT id_sotrudnik from sotrudnik '
                       f'WHERE id_sotrudnik={worker_id} '
                       f'AND id_business={business_id}')
        if user_c.fetchone():
            user_c.execute(f'UPDATE sotrudnik set hashed_password="{password}", login="{login}", phone="{phone}", '
                           f'full_name="{full_name}" '
                           f'WHERE id_sotrudnik={worker_id} AND id_business = {business_id}')
            self.users_conn.commit()
        else:
            raise NotFoundError

    # ---------------------------Business-----------------------------

    async def get_related_physics(self, username):
        business_id = await self.get_business_id(username)
        user_c = self.users_conn.cursor()
        user_c.execute(f'SELECT id_physic, contract_number, full_name, email, ipus, address from physic '
                       f'WHERE id_business={business_id}')
        info = user_c.fetchall()
        user_c.close()
        return info

    async def get_address_by_contract_number(self, contract_number: str):
        user_c = self.users_conn.cursor()
        user_c.execute(f'SELECT address from physic WHERE contract_number="{contract_number}" LIMIT 1;')
        address = user_c.fetchone()
        user_c.close()
        return address['address']

    async def get_hundred_physics(self, username, hundred: int, search: Optional[str] = None):
        business_id = await self.get_business_id(username)
        user_c = self.users_conn.cursor()
        count_query = f"SELECT COUNT(*) as total_rows from physic " \
                      f"WHERE id_business={business_id} "
        query = f'SELECT id_physic, contract_number, full_name, email, ipus, address from physic ' \
                f'WHERE id_business={business_id} '
        if search is not None:
            query += f"and (contract_number like '%{search}%' or email like '%{search}%' or ipus like '%{search}%'" \
                     f"or address like '%{search}%' or full_name like '%{search}%')"
            count_query += f"and (contract_number like '%{search}%' or email like '%{search}%' or ipus like '%{search}%'" \
                           f"or address like '%{search}%' or full_name like '%{search}%')"
        query += f"LIMIT 15 OFFSET {hundred * 15}"
        user_c.execute(query)
        info = user_c.fetchall()
        user_c.execute(count_query)
        amount = user_c.fetchone()
        user_c.close()
        return info, amount

    async def get_suspicious_validations(self, username, hundred, first_date: Optional[str] = None,
                                         second_date: Optional[str] = None, search: Optional[str] = None):
        business_id = await self.get_business_id(username)
        user_c = self.users_conn.cursor()
        validate_c = self.trans_conn.cursor()
        count_query = f"select COUNT(*) as total_rows from waterdroplet_model.physic as ph " \
                      f"JOIN transactions.validate as val on val.id_physic = ph.id_physic " \
                      f"JOIN waterdroplet_model.sotrudnik as sotr on val.sotrudnik_id = sotr.id_sotrudnik " \
                      f"WHERE val.id_business={business_id} and verdict = 'Подозрительно' "
        query = f"select val.id_validation, val.id_physic, val.sotrudnik_photo_date, ph.contract_number, " \
                f"ph.full_name, ph.address from waterdroplet_model.physic as ph " \
                f"JOIN transactions.validate as val on val.id_physic = ph.id_physic " \
                f"JOIN waterdroplet_model.sotrudnik as sotr on val.sotrudnik_id = sotr.id_sotrudnik " \
                f"WHERE val.id_business={business_id} and verdict = 'Подозрительно' "
        if search is not None:
            query += f"and (sotr.full_name like '%{search}%' or ph.full_name like '%{search}%' or " \
                     f"val.physic_number like '%{search}%' or val.sotrudnik_number like '%{search}%') "
            count_query += f"and (sotr.full_name like '%{search}%' or ph.full_name like '%{search}%' or " \
                           f"val.physic_number like '%{search}%' or val.sotrudnik_number like '%{search}%') "
        if first_date is None and second_date is None:
            pass
        elif first_date is not None and second_date is not None:
            query += f'AND sotrudnik_photo_date ' \
                     f'BETWEEN "{first_date} 00:00:00" AND "{second_date} 23:59:59" '
            count_query += f'AND sotrudnik_photo_date ' \
                           f'BETWEEN "{first_date} 00:00:00" AND "{second_date} 23:59:59" '
        elif first_date is not None and second_date is None:
            current_date = datetime.datetime.now().strftime('%Y-%m-%d')
            query += f'AND sotrudnik_photo_date ' \
                     f'BETWEEN "{first_date} 00:00:00" AND "{current_date} 23:59:59" '
            count_query += f'AND sotrudnik_photo_date ' \
                           f'BETWEEN "{first_date} 00:00:00" AND "{current_date} 23:59:59" '
        else:
            query += f'AND sotrudnik_photo_date <= "{second_date} 23:59:59" '
            count_query += f'AND sotrudnik_photo_date <= "{second_date} 23:59:59" '
        query += f'ORDER BY val.id_validation DESC LIMIT 15 OFFSET {hundred * 15};'
        validate_c.execute(query)
        info = validate_c.fetchall()
        validate_c.execute(count_query)
        amount = validate_c.fetchone()
        user_info = []
        for validation in info:
            user_c.execute(f'SELECT full_name from physic WHERE id_physic={validation["id_physic"]}')
            result = user_c.fetchone()
            user_dict = {'validation_id': validation["id_validation"],
                         'validation_date': str(validation["sotrudnik_photo_date"]), 'full_name': result["full_name"]}
            user_info.append(user_dict)
        validate_c.close()
        user_c.close()
        return user_info, amount

    async def get_all_validations(self, username, hundred, first_date: Optional[str] = None,
                                  second_date: Optional[str] = None, search: Optional[str] = None):
        business_id = await self.get_business_id(username)
        user_c = self.users_conn.cursor()
        validate_c = self.trans_conn.cursor()
        count_query = f"select COUNT(*) as total_rows from waterdroplet_model.physic as ph " \
                      f"JOIN transactions.validate as val on val.id_physic = ph.id_physic " \
                      f"JOIN waterdroplet_model.sotrudnik as sotr on val.sotrudnik_id = sotr.id_sotrudnik " \
                      f"WHERE val.id_business={business_id} "
        query = f"select val.id_validation, val.id_physic, val.sotrudnik_photo_date, ph.contract_number, " \
                f"sotr.id_sotrudnik, ph.full_name, ph.address from waterdroplet_model.physic as ph " \
                f"JOIN transactions.validate as val on val.id_physic = ph.id_physic " \
                f"JOIN waterdroplet_model.sotrudnik as sotr on val.sotrudnik_id = sotr.id_sotrudnik " \
                f"WHERE val.id_business={business_id} "
        if search is not None:
            query += f"and (sotr.full_name like '%{search}%' or ph.full_name like '%{search}%' or " \
                     f"val.physic_number like '%{search}%' or val.sotrudnik_number like '%{search}%') "
            count_query += f"and (sotr.full_name like '%{search}%' or ph.full_name like '%{search}%' or " \
                           f"val.physic_number like '%{search}%' or val.sotrudnik_number like '%{search}%') "
        if first_date is None and second_date is None:
            pass
        elif first_date is not None and second_date is not None:
            query += f"AND sotrudnik_photo_date " \
                     f"BETWEEN '{first_date} 00:00:00' AND '{second_date} 23:59:59' "
            count_query += f"AND sotrudnik_photo_date " \
                           f"BETWEEN '{first_date} 00:00:00' AND '{second_date} 23:59:59' "
        elif first_date is not None and second_date is None:
            current_date = datetime.datetime.now().strftime('%Y-%m-%d')
            query += f"AND sotrudnik_photo_date " \
                     f"BETWEEN '{first_date} 00:00:00' AND '{current_date} 23:59:59' "
            count_query += f"AND sotrudnik_photo_date " \
                           f"BETWEEN '{first_date} 00:00:00' AND '{current_date} 23:59:59' "
        else:
            query += f"AND sotrudnik_photo_date <= '{second_date} 23:59:59' "
            count_query += f"AND sotrudnik_photo_date <= '{second_date} 23:59:59' "
        query += f"ORDER BY val.id_validation DESC LIMIT 15 OFFSET {hundred * 15};"
        validate_c.execute(query)
        info = validate_c.fetchall()
        validate_c.execute(count_query)
        amount = validate_c.fetchone()
        user_info = []
        for validation in info:
            user_c.execute(f'SELECT full_name from physic WHERE id_physic={validation["id_physic"]}')
            result = user_c.fetchone()
            user_dict = {'validation_id': validation["id_validation"],
                         'validation_date': str(validation["sotrudnik_photo_date"]), 'full_name': result["full_name"]}
            user_info.append(user_dict)
        validate_c.close()
        user_c.close()
        return user_info, amount

    async def get_transactions_logs(self, username, hundred, first_date: Optional[str] = None,
                                    second_date: Optional[str] = None, search: Optional[str] = None):
        business_id = await self.get_business_id(username)
        user_c = self.users_conn.cursor()
        validate_c = self.trans_conn.cursor()
        count_query = f"select COUNT(*) as total_rows " \
                      f"from waterdroplet_model.physic as ph " \
                      f"JOIN transactions.transactions as val on val.id_physic = ph.id_physic " \
                      f"WHERE val.id_business={business_id} and status=2 "
        query = f"select val.id_transaction, val.id_physic, val.prev_number, val.new_number, val.date, val.ipu, " \
                f"val.payment_sum, val.verdict, ph.contract_number, ph.full_name, ph.address " \
                f"from waterdroplet_model.physic as ph " \
                f"JOIN transactions.transactions as val on val.id_physic = ph.id_physic " \
                f"WHERE val.id_business={business_id} and status=2 "
        if search is not None:
            query += f"and (val.new_number like '%{search}%' or ph.full_name like '%{search}%' or " \
                     f"val.id_transaction like '%{search}%') "
            count_query += f"and (val.new_number like '%{search}%' or ph.full_name like '%{search}%' or " \
                           f"val.id_transaction like '%{search}%') "
        if first_date is None and second_date is None:
            pass
        elif first_date is not None and second_date is not None:
            count_query += f"AND date BETWEEN '{first_date} 00:00:00' AND '{second_date} 23:59:59' "
            query += f"AND date BETWEEN '{first_date} 00:00:00' AND '{second_date} 23:59:59' "

        elif first_date is not None and second_date is None:
            current_date = datetime.datetime.now().strftime('%Y-%m-%d')
            query += f"AND date BETWEEN '{first_date} 00:00:00' AND '{current_date} 23:59:59' "
            count_query += f"AND date BETWEEN '{first_date} 00:00:00' AND '{current_date} 23:59:59' "
        else:
            query += f"AND date <= '{second_date} 23:59:59' "
            count_query += f"AND date <= '{second_date} 23:59:59' "
        query += f"ORDER BY val.id_transaction DESC LIMIT 15 OFFSET {hundred * 15};"
        validate_c.execute(query)
        info = validate_c.fetchall()
        validate_c.execute(count_query)
        amount = validate_c.fetchone()
        user_info = []
        for transaction in info:
            user_c.execute(f'SELECT full_name from physic WHERE id_physic={transaction["id_physic"]}')
            result = user_c.fetchone()
            user_dict = {'transaction_id': transaction["id_transaction"], 'full_name': result["full_name"],
                         'transaction_date': str(transaction["date"]), 'ipu': transaction['ipu'],
                         'prev_number': transaction["prev_number"], 'new_number': transaction["new_number"],
                         'payment_sum': transaction["payment_sum"], 'verdict': transaction["verdict"]
                         }
            user_info.append(user_dict)
        validate_c.close()
        user_c.close()
        return user_info, amount

    async def get_sus_transactions_logs(self, username, hundred, first_date: Optional[str] = None,
                                        second_date: Optional[str] = None, search: Optional[str] = None):
        business_id = await self.get_business_id(username)
        user_c = self.users_conn.cursor()
        validate_c = self.trans_conn.cursor()
        count_query = f"select COUNT(*) as total_rows " \
                      f"from waterdroplet_model.physic as ph " \
                      f"JOIN transactions.transactions as val on val.id_physic = ph.id_physic " \
                      f"WHERE val.id_business={business_id} and status=2 and verdict='Подозрительно' "
        query = f"select val.id_transaction, val.id_physic, val.prev_number, val.new_number, val.date, val.ipu, " \
                f"val.payment_sum, val.verdict, ph.contract_number, ph.full_name, ph.address " \
                f"from waterdroplet_model.physic as ph " \
                f"JOIN transactions.transactions as val on val.id_physic = ph.id_physic " \
                f"WHERE val.id_business={business_id} and status=2 and verdict='Подозрительно' "
        if search is not None:
            query += f"and (val.new_number like '%{search}%' or ph.full_name like '%{search}%' or " \
                     f"val.id_transaction like '%{search}%') "
            count_query += f"and (val.new_number like '%{search}%' or ph.full_name like '%{search}%' or " \
                           f"val.id_transaction like '%{search}%') "
        if first_date is None and second_date is None:
            pass
        elif first_date is not None and second_date is not None:
            query += f"AND date BETWEEN '{first_date} 00:00:00' AND '{second_date} 23:59:59' "
            count_query += f"AND date BETWEEN '{first_date} 00:00:00' AND '{second_date} 23:59:59' "
        elif first_date is not None and second_date is None:
            current_date = datetime.datetime.now().strftime('%Y-%m-%d')
            query += f"and date BETWEEN '{first_date} 00:00:00' AND '{current_date} 23:59:59' "
            count_query += f"and date BETWEEN '{first_date} 00:00:00' AND '{current_date} 23:59:59' "
        else:
            query += f"and date <= '{second_date} 23:59:59' "
            count_query += f"and date <= '{second_date} 23:59:59' "
        query += f"ORDER BY val.id_transaction DESC LIMIT 15 OFFSET {hundred * 15};"
        validate_c.execute(query)
        info = validate_c.fetchall()
        validate_c.execute(count_query)
        amount = validate_c.fetchone()
        user_info = []
        for transaction in info:
            user_c.execute(f'SELECT full_name from physic WHERE id_physic={transaction["id_physic"]}')
            result = user_c.fetchone()
            user_dict = {'transaction_id': transaction["id_transaction"], 'full_name': result["full_name"],
                         'transaction_date': str(transaction["date"]), 'ipu': transaction['ipu'],
                         'prev_number': transaction["prev_number"], 'new_number': transaction["new_number"],
                         'payment_sum': transaction["payment_sum"], 'verdict': transaction["verdict"]
                         }
            user_info.append(user_dict)
        validate_c.close()
        user_c.close()
        return user_info, amount

    async def get_all_addresses(self, username, user_type):
        if user_type == 'sotrudnik':
            business_id = await self.get_sotr_business(username)
        else:
            business_id = await self.get_business_id(username)
        user_c = self.users_conn.cursor()
        user_c.execute(f'SELECT address from physic WHERE id_business={business_id}')
        info = user_c.fetchall()
        user_c.close()
        return info

    async def get_addresses(self, username, hundred, user_type):
        if user_type == 'sotrudnik':
            business_id = await self.get_sotr_business(username)
        else:
            business_id = await self.get_business_id(username)
        user_c = self.users_conn.cursor()
        user_c.execute(f'SELECT address from physic WHERE id_business={business_id} '
                       f'LIMIT 15 OFFSET {hundred * 15}')
        info = user_c.fetchall()
        user_c.close()
        return info

    async def get_ipus_by_address(self, address):
        user_c = self.users_conn.cursor()
        user_c.execute(f'SELECT ipus, id_physic from physic WHERE address="{address}"')
        info = user_c.fetchone()
        user_c.close()
        return info

    async def add_validation(self, username, sotr_number, ipu, address):
        validate_c = self.trans_conn.cursor()
        user_c = self.users_conn.cursor()
        user_c.execute(f'SELECT id_physic, id_business, ipus from physic where address="{address}"')
        data = user_c.fetchone()
        if not data:
            raise NotFoundError
        ipus = data['ipus'].split()
        if ipu not in ipus:
            raise NotFoundError
        id_physic, id_business = data['id_physic'], data['id_business']
        validate_c.execute(f'SELECT date, new_number from transactions WHERE id_physic={id_physic} AND ipu="{ipu}" '
                           f'ORDER BY date DESC LIMIT 1')
        data = validate_c.fetchone()
        user_c.execute(f'SELECT id_sotrudnik, id_business from sotrudnik WHERE login="{username}"')
        info = user_c.fetchone()
        id_sotr, sotr_id_business = info['id_sotrudnik'], info['id_business']
        if sotr_id_business != id_business:
            raise BadUserError
        if not data:
            validate_c.execute(f'INSERT INTO validate (id_physic, id_business, ipu, '
                               f'sotrudnik_id, sotrudnik_photo_date, sotrudnik_number, verdict) '
                               f'VALUES ({id_physic}, {id_business}, "{ipu}", '
                               f'{id_sotr}, NOW(), "{sotr_number}", "Не подозрительно")')
        else:
            physic_photo_date, physic_number = data['date'], data['new_number']
            if (int(sotr_number) - int(physic_number) > (config.VALIDATION_CONST *
                                                         int((datetime.datetime.now() - physic_photo_date).days))) or (
                    int(sotr_number) - int(physic_number) < 0):
                verdict = 'Подозрительно'
            else:
                verdict = 'Не подозрительно'
            validate_c.execute(f'INSERT INTO validate (id_physic, id_business, ipu, physic_photo_date, physic_number, '
                               f'sotrudnik_id, sotrudnik_photo_date, sotrudnik_number, verdict) '
                               f'VALUES ({id_physic}, {id_business}, "{ipu}", "{physic_photo_date}", "{physic_number}",'
                               f' {id_sotr}, NOW(), "{sotr_number}", "{verdict}")')
        trans_conn.commit()
        user_c.close()
        validate_c.close()

    async def save_form(self, name, phone, message):
        user_c = self.users_conn.cursor()
        user_c.execute(f'INSERT INTO forms (person_name, phone, message) '
                       f'VALUES ("{name}", "{phone}", "{message}")')
        self.users_conn.commit()
        user_c.close()


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
