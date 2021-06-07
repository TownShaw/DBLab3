import MySQLdb
from MySQLdb._exceptions import OperationalError, ProgrammingError

def db_login(user, passwd, server_addr, dbname):
    try:
        db = MySQLdb.connect(server_addr, user, passwd, dbname, charset = "utf8")
    except OperationalError:
        db = None

    return db

def db_showtable(db):
    cursor = db.cursor()

    cursor.execute("show tables")
    tabs = cursor.fetchall()

    res = list()

    for tab in tabs:
        cursor.execute("select count(*) from " + tab[0])
        row_cnt = cursor.fetchone()

        res.append((tab[0], row_cnt[0]))
    
    cursor.close()

    return res

def table_showlines(db, table, search_conf):     # 显示 db table 的所有表项
    cursor = db.cursor()

    cursor.execute("describe " + table)
    table_head = cursor.fetchall()
    columns = []
    for i in range(len(table_head)):
        columns.append(table_head[i][0])
    if search_conf == None or search_conf == {}:     # if search_conf 为空
        try:
            cursor.execute("SELECT * FROM " + table)
        except OperationalError:
            print("Not Such Table, Error!")
            return [], []
        result = cursor.fetchall()
    else:
        try:
            WHERE_Clause = ''
            for key, value in search_conf.items():
                WHERE_Clause = WHERE_Clause + key + value + " AND "
            WHERE_Clause = WHERE_Clause[:-5]            # 去掉最后的 and
            cursor.execute("SELECT * FROM " + table + " WHERE " + WHERE_Clause)
        except OperationalError or ProgrammingError:
            print("Search Clause Error!")
            return [], []
        result = cursor.fetchall()

    cursor.close()

    return columns, result

def table_insert(db, table, insert_list):
    # TODO
    pass

def table_update(db, table, search_list, update_dict):
    cursor = db.cursor()

    cursor.execute("describe " + table)
    table_head = cursor.fetchall()
    columns = []
    result = []
    search_dict = dict()
    for i in range(len(table_head)):
        columns.append(table_head[i][0])
        search_dict[columns[i]] = str(search_list[i])
    if update_dict == None or update_dict == {}:     # if search_conf 为空
        WHERE_Clause = ''
        for key, value in search_dict.items():
            WHERE_Clause = WHERE_Clause + str(key) + "='" + value + "' AND "
        WHERE_Clause = WHERE_Clause[:-5]            # 去掉最后的 and
        cursor.execute("SELECT * FROM " + table + " WHERE " + WHERE_Clause)
        result = cursor.fetchall()
    else:
        WHERE_Clause = ''
        for key, value in search_dict.items():
            WHERE_Clause = WHERE_Clause + key + "='" + value + "' AND "
        WHERE_Clause = WHERE_Clause[:-5]            # 去掉最后的 and
        UPDATE_Clause = ''
        for key, value in update_dict.items():
            UPDATE_Clause = UPDATE_Clause + key + "='" + value + "', "
        UPDATE_Clause = UPDATE_Clause[:-2]            # 去掉最后的 and
        try:
            cursor.execute("UPDATE " + table + " SET " + UPDATE_Clause + " WHERE " + WHERE_Clause)
            db.commit()
            for key, value in update_dict.items():
                search_dict[key] = str(value)
            WHERE_Clause = ''
            for key, value in search_dict.items():
                WHERE_Clause = WHERE_Clause + key + "='" + value + "' AND "
            WHERE_Clause = WHERE_Clause[:-5]            # 去掉最后的 and
            cursor.execute("SELECT * FROM " + table + " WHERE " + WHERE_Clause)
        except OperationalError or ProgrammingError:
            print("Update Clause Error!")
            db.rollback()
            return [], []
        result = cursor.fetchall()
# UPDATE Course SET cno='000011', type='0' WHERE cno='000001' AND cname='大学生心理学' AND type='1' AND credit='3.0'
    cursor.close()

    return columns, result

def table_delete(db, table, delete_dict):
    cursor = db.cursor()

    cursor.execute("describe " + table)
    table_head = cursor.fetchall()
    columns = []
    result = []
    for i in range(len(table_head)):
        columns.append(table_head[i][0])
    if delete_dict == {} or delete_dict == None:
        try:
            cursor.execute("SELECT * FROM " + table)
        except OperationalError:
            print("Not Such Table, Error!")
            return [], []
        result = cursor.fetchall()
    else:
        WHERE_Clause = ''
        for key, value in delete_dict.items():
            WHERE_Clause = WHERE_Clause + key + "='" + value + "' AND "
        WHERE_Clause = WHERE_Clause[:-5]            # 去掉最后的 and
        try:
            cursor.execute("DELETE FROM " + table + " WHERE " + WHERE_Clause)
            db.commit()
            cursor.execute("SELECT * FROM " + table)
        except OperationalError or ProgrammingError:
            print("Search Clause Error!")
            return [], []
        result = cursor.fetchall()

    return columns, result

def db_close(db):
    if db is not None:
        db.close()

if __name__ == "__main__":
    db = db_login("lyp1234", "1234", "127.0.0.1", "test")

    tabs = db_showtable(db)
    
    db_close(db)