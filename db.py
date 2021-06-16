# import MySQLdb
from flask.globals import session
from sqlalchemy import Table, Column, String, Integer, MetaData, func
from sqlalchemy.orm.session import Session
from sqlalchemy.sql import select, insert, delete, update
from sqlalchemy.engine import reflection
from sqlalchemy.orm import sessionmaker, relationship, backref
from sqlalchemy.ext.declarative import declarative_base
# from MySQLdb._exceptions import OperationalError, ProgrammingError
'''
def db_login(user, passwd, server_addr, dbname):
    try:
        db = MySQLdb.connect(server_addr, user, passwd, dbname, charset = "utf8")
    except OperationalError:
        db = None

    return db
def db_showtable(engine):
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
    Base = declarative_base()
    Base.metadata.reflect(engine)
    tables = Base.metadata.tables
    tables_name = []
    for table in tables:
        tables_name.append(table)
    return tables_name
'''
def db_getsession(engine):
    Session = sessionmaker(bind=engine)
    session = Session()
    return session

def db_getconnection(engine):
    connection = engine.connect()
    return connection

def db_gettable(engine, tablename):
    metadata = MetaData(engine)
    table = Table(tablename, metadata, autoload=True)
    return table

def table_getcolumns(engine, tablename):
    insp = reflection.Inspector.from_engine(engine)
    columns = insp.get_columns(tablename)    #这里是写的表名
    columns = [column['name'] for column in columns]
    return columns


def table_search(engine, tablename, search_dict):     # 显示 db table 中的表项
    connection = db_getconnection(engine)
    table = db_gettable(engine, tablename)
    if search_dict == None or search_dict == {}:     # if search_conf 为空
        stmt = table.select()
        rows = connection.execute(stmt).fetchall()
    else:
        key = next(iter(search_dict))
        value = next(iter(search_dict.values()))
        # table.select().where(table.c[search_dict])
        stmt = table.select().where(table.c[key].like("%{}%".format(value)))
        try:
            rows = connection.execute(stmt).fetchall()
        except:
            print("Search Clause Error!")
            return [], []
    return rows


def table_insert(engine, tablename, insert_dict):
    connection = db_getconnection(engine)
    table = db_gettable(engine, tablename)
    stmt = table.insert().values(**insert_dict)
    print(str(stmt))
    connection.execute(stmt)

def table_update(engine, connection, tablename, update_dict):
    rp = connection.execute("describe " + tablename)
    table_head = rp.fetchall()
    columns = []
    results = []
    search_dict = dict()
    for i in range(len(table_head)):
        columns.append(table_head[i][0])
        search_dict[columns[i]] = str(search_list[i])
    if update_dict == None or update_dict == {}:     # if search_conf 为空
        WHERE_Clause = ''
        for key, value in search_dict.items():
            WHERE_Clause = WHERE_Clause + str(key) + "='" + value + "' AND "
        WHERE_Clause = WHERE_Clause[:-5]            # 去掉最后的 and
        rp = connection.execute("SELECT * FROM " + tablename + " WHERE " + WHERE_Clause)
        results = rp.fetchall()
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
            rp = connection.execute("UPDATE " + tablename + " SET " + UPDATE_Clause + " WHERE " + WHERE_Clause)
            for key, value in update_dict.items():
                search_dict[key] = str(value)
            WHERE_Clause = ''
            for key, value in search_dict.items():
                WHERE_Clause = WHERE_Clause + key + "='" + value + "' AND "
            WHERE_Clause = WHERE_Clause[:-5]            # 去掉最后的 and
            rp = connection.execute("SELECT * FROM " + tablename + " WHERE " + WHERE_Clause)
            results = rp.fetchall()
        except:
            return [], []
# UPDATE Course SET cno='000011', type='0' WHERE cno='000001' AND cname='大学生心理学' AND type='1' AND credit='3.0'

    return columns, results

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

# def db_close(db):
    # if db is not None:
        # db.close()

# if __name__ == "__main__":
    # db = db_login("lyp1234", "1234", "127.0.0.1", "test")

    # tabs = db_showtable(db)
    
    # db_close(db)