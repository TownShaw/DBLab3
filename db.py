# import MySQLdb
from flask.globals import session
from sqlalchemy import Table, Column, String, Integer, MetaData, func, and_, or_
from sqlalchemy.orm.session import Session
from sqlalchemy.sql import select, insert, delete, update
from sqlalchemy.engine import reflection
from sqlalchemy.orm import sessionmaker, relationship, backref
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql.coercions import expect
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
    for key, value in insert_dict.items():
        if value == '':
            insert_dict[key] = None
    stmt = table.insert().values(**insert_dict)
    # print(str(stmt))
    try:
        connection.execute(stmt)
    except:
        pass
    # connection.execute(stmt)

def table_update(engine, tablename, search_dict, update_dict):
    connection = db_getconnection(engine)
    table = db_gettable(engine, tablename)
    clause = []
    for key, value in search_dict.items():
        clause.append(table.c[key] == value)
    # stmt = table.update().where(table.c['Client_ID'] == search_dict['Client_ID']).values(**update_dict)
    stmt = table.update().where(and_(*clause)).values(**update_dict)
    print(str(stmt))
    try:
        connection.execute(stmt)
    except:
        pass
    # stmt = table.select().where(table.c['Client_ID'] == search_dict['Client_ID'])
    stmt = table.select().where(and_(*clause))
    rows = connection.execute(stmt)
    return rows
'''
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
'''
def get_loan_status(engine, loan_id, installment):
    tablename = "Partial_Payment"
    connection = db_getconnection(engine)
    table = db_gettable(engine, tablename)
    stmt = table.select().where(table.c["Loan_ID"] == loan_id)
    rows = connection.execute(stmt).fetchall()
    if len(rows) == installment:
        status = ("已全部发放", 0)
    elif len(rows) == 0:
        status = ("未开始发放", 1)
    elif len(rows) < installment:
        status = ("发放中", 2)
    else:
        status = ("错误状态", 3)

    return status

def payments_insert(engine, tablename, insert_dict):
    connection = db_getconnection(engine)
    payment_table = db_gettable(engine, tablename)
    bank_table = db_gettable(engine, "Branch_Bank")
    loans_table = db_gettable(engine, "Loans")
    for key, value in insert_dict.items():
        if value == '':
            insert_dict[key] = None
        if key == "Payment_Amount":
            money = float(value)
        if key == "Loan_ID":
            loan_id = value
    stmt1 = payment_table.insert().values(**insert_dict)
    # print(str(stmt))
    # try:
    # search_columns = [bank_table.c["Bank_Name"], bank_table.c["Asset"], loans_table.c["Loan_ID"], loans_table.c["Bank_Name"]]
    stmt = select([loans_table.c["Bank_Name"], loans_table.c["Loan_ID"]]).where(loans_table.c["Loan_ID"] == loan_id)
    # stmt = stmt.select([loans_table.c["Bank_Name"]])
    result = connection.execute(stmt).fetchone()
    bank = result[0]
    stmt = select([bank_table.c["Bank_Name"], bank_table.c["Asset"]]).where(bank_table.c["Bank_Name"] == bank)
    result = connection.execute(stmt).fetchone()
    asset = float(result[1])

    connection.execute(stmt1)
    table_update(engine, "Branch_Bank", {"Bank_Name": bank}, {"Asset": asset - money})

def clients_delete(engine, client_id):
    clients_tablename = "Clients"
    tablename_1 = "CL_Table"
    tablename_2 = "Connection_Table"
    connection = db_getconnection(engine)
    table_1 = db_gettable(engine, tablename_1)
    stmt_1 = table_1.select().where(table_1.c["Client_ID"] == client_id)
    rows_1 = connection.execute(stmt_1).fetchall()
    table_2 = db_gettable(engine, tablename_2)
    stmt_2 = table_2.select().where(and_(table_2.c["Client_ID"] == client_id, or_(table_2.c["Checking_Account_ID"] != None, table_2.c["Saving_Account_ID"] != None)))
    rows_2 = connection.execute(stmt_2).fetchall()
    if len(rows_1) == 0 and len(rows_2) == 0:
        clients_table = db_gettable(engine, clients_tablename)
        stmt = clients_table.delete().where(clients_table.c["Client_ID"] == client_id)
        connection.execute(stmt)

def loans_delete(engine, loan_id, installment):
    loans_tablename = "Loans"
    payment_tablename = "Partial_Payment"
    status = get_loan_status(engine, loan_id, installment)
    if status[1] != 2:
        connection = db_getconnection(engine)
        loans_table = db_gettable(engine, loans_tablename)
        payment_table = db_gettable(engine, payment_tablename)
        try:
            stmt = payment_table.delete().where(payment_table.c["Loan_ID"] == loan_id)
            connection.execute(stmt)
            stmt = loans_table.delete().where(loans_table.c["Loan_ID"] == loan_id)
            connection.execute(stmt)
        except:
            pass

def checking_account_statistics(engine, time):
    connection = db_getconnection(engine)
    bank_table = db_gettable(engine, "Branch_Bank")
    connection_table = db_gettable(engine, "Connection_Table")
    checking_account_table = db_gettable(engine, "Checking_Account")

    # columns = [bank_table.c["Bank_Name"], bank_table.c["Asset"], connection_table.c["Bank_Name"], connection_table.c["Checking_Account_ID"]]
    rows = list()
    stmt = select([bank_table.c["Bank_Name"], bank_table.c["Asset"]])
    Banks = connection.execute(stmt)
    for bank in Banks:
        rows.append([])
        search_columns = [connection_table.c["Bank_Name"], connection_table.c["Checking_Account_ID"], connection_table.c["Client_ID"], checking_account_table.c["Checking_Account_ID"], checking_account_table.c["Open_Date"]]
        stmt = select(search_columns).where(and_(connection_table.c["Bank_Name"] == bank[0], \
                                                 connection_table.c["Checking_Account_ID"] != None, \
                                                 connection_table.c["Checking_Account_ID"] == checking_account_table.c["Checking_Account_ID"], \
                                                 checking_account_table.c["Open_Date"] <= time))
        results = connection.execute(stmt).fetchall()
        rows[-1].append(bank[0])
        rows[-1].append(bank[1])
        rows[-1].append(len(results))

    return rows

def saving_account_statistics(engine, time):
    connection = db_getconnection(engine)
    bank_table = db_gettable(engine, "Branch_Bank")
    connection_table = db_gettable(engine, "Connection_Table")
    saving_account_table = db_gettable(engine, "Saving_Account")

    # columns = [bank_table.c["Bank_Name"], bank_table.c["Asset"], connection_table.c["Bank_Name"], connection_table.c["Checking_Account_ID"]]
    rows = list()
    stmt = select(bank_table.c["Bank_Name"], bank_table.c["Asset"])
    Banks = connection.execute(stmt)
    for bank in Banks:
        rows.append([])
        # stmt = connection_table.select().where(and_(connection_table.c["Connection_Table"] == bank[0], connection_table.c["Saving_Account_ID"] != None))
        search_columns = [connection_table.c["Bank_Name"], connection_table.c["Saving_Account_ID"], connection_table.c["Client_ID"], saving_account_table.c["Saving_Account_ID"], saving_account_table.c["Open_Date"]]
        stmt = select(search_columns).where(and_(connection_table.c["Bank_Name"] == bank[0], \
                                                 connection_table.c["Saving_Account_ID"] != None, \
                                                 connection_table.c["Saving_Account_ID"] == saving_account_table.c["Saving_Account_ID"], \
                                                 saving_account_table.c["Open_Date"] <= time))
        results = connection.execute(stmt).fetchall()
        rows[-1].append(bank[0])
        rows[-1].append(bank[1])
        rows[-1].append(len(results))

    return rows


# def db_close(db):
    # if db is not None:
        # db.close()

# if __name__ == "__main__":
    # db = db_login("lyp1234", "1234", "127.0.0.1", "test")

    # tabs = db_showtable(db)
    
    # db_close(db)