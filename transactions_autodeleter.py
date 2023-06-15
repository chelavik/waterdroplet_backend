from Database import Databases
SQLDatabase = Databases.DatabaseClass()

def autodelete():
    trans_c = Databases.trans_conn.cursor()
    trans_c.execute('DELETE FROM transactions '
                    'WHERE (status = 0 OR status = 1)'
                    '  AND TIMESTAMPDIFF(MINUTE, date, NOW()) > 15;'
                    )
    Databases.trans_conn.commit()
    trans_c.close()

autodelete()