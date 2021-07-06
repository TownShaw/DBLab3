import functools

from flask import Flask, session
from flask import redirect
from flask import request, make_response
from flask import render_template
from flask import url_for
from flask import flash
from sqlalchemy import create_engine
from sqlalchemy.sql.expression import column

from db import *
import jinja2
env = jinja2.Environment()
env.globals.update(zip=zip)

# 生成一个app
app = Flask(__name__, instance_relative_config=True)
app.secret_key = 'lab3'

# engine = None
# connection = None
databasename = "BankSystem"
engine = create_engine('mysql+pymysql://root:200219xiaotong@localhost:3306/{}'.format(databasename), echo=True, pool_recycle=3600)

# 对app执行请求页面地址到函数的绑定
@app.route("/", methods=(["GET"]))    # 主页, 不需要附加任何操作
@app.route("/home", methods=(["GET"]))
def home():
    return render_template("home.html")
'''
@app.route("/login", methods=("GET", "POST"))
def login():
    """Log in a registered user by adding the user id to the session."""
    if request.method == "POST":
        # 客户端在login页面发起的POST请求
        username = request.form["username"]
        password = request.form["password"]
        ipaddr   = request.form["ipaddr"]
        database = request.form["database"]
        port = 3306

        global engine
        engine = create_engine('mysql+pymysql://' + username + ':' + password + '@' + ipaddr + ':' + str(port) + '/' + database, echo=True, pool_recycle=3600)
        global connection
        connection = engine.connect()

        if engine == None:
            return render_template("login_fail.html")
        else:
            session['username'] = username
            session['password'] = password
            session['ipaddr'] = ipaddr
            session['database'] = database

            return redirect(url_for('database'))
    else :
        # 客户端GET 请求login页面时
        return render_template("login.html")
'''
@app.route("/clients", methods=['GET', 'POST'])
def clients():
    tablename = "Clients"
    columns = table_getcolumns(engine, tablename)
    # table = db_gettable(engine, tablename)
    # stmt = table.select()
    # rows = connection.execute(stmt).fetchall()
    rows = table_search(engine, tablename, None)

    if request.method == 'POST':
        if "Back" in request.form:
            return render_template("home.html")
        elif "search" in request.form:
            search_dict = dict()
            for key, value in request.form.items():
                if key == "select_type":
                    search_dict[value] = value
                elif key == "searchConf":
                    search_dict[next(iter(search_dict))] = value
            rows = table_search(engine, tablename, search_dict)
            return render_template("clients.html", columns=columns, rows=rows)
        elif "update" in request.form:
            keys, values = request.form['update'].split("&&")
            keys = keys.split("||")
            values = values.split("||")
            idx = 0
            global client_id
            for idx in range(len(keys)):
                if keys[idx] == 'Client_ID':
                    client_id = values[idx]
            return redirect(url_for("update_client"))
        elif "insert" in request.form:
            return redirect(url_for("insert_client"))
        elif "delete" in request.form:
            pass    #TODO
        elif "clear" in request.form:
            return render_template("clients.html", columns=columns, rows='')
        else:
            rows = table_search(engine, tablename, None)
            return render_template("clients.html", columns=columns, rows=rows)
    else:
        return render_template("clients.html", columns=columns, rows=rows)

@app.route("/clients/update", methods=['GET', 'POST'])
def update_client():
    tablename = "Clients"
    columns = table_getcolumns(engine, tablename)
    update_columns = columns[:]
    update_columns.remove("Client_ID")
    # table = db_gettable(engine, tablename)
    # stmt = table.select().where(table.c['Client_ID'] == client_id)
    # rows = connection.execute(stmt).fetchall()
    rows = table_search(engine, tablename, {"Client_ID": account_id})

    if request.method == 'POST':
        if "update" in request.form:
            update_dict = dict()
            for key, value in request.form.items():
                if key != "update" and key != "Client_ID" and value != '':
                    update_dict[key] = value
            rows = table_update(engine, tablename, {"Client_ID": client_id}, update_dict)
            return render_template("update.html", tablename=tablename, rows=rows, columns=columns, update_columns=update_columns)
        elif "Back" in request.form:
            return redirect(url_for("clients"))
        else:
            return render_template("update.html", tablename=tablename, rows=rows, columns=columns, update_columns=update_columns)
    else:
        return render_template("update.html", tablename=tablename, rows=rows, columns=columns, update_columns=update_columns)

@app.route("/clients/insert", methods=['GET', 'POST'])
def insert_client():
    tablename = "Clients"
    columns = table_getcolumns(engine, tablename)

    if request.method == 'POST':
        if "insert" in request.form:
            insert_dict = dict()
            for key, value in request.form.items():
                if key != "insert":
                    insert_dict[key] = value
            table_insert(engine, tablename, insert_dict)
            return render_template("insert.html", tablename=tablename, columns=columns)
        elif "Back" in request.form:
            return redirect(url_for("clients"))
        else:
            return render_template("insert.html", tablename=tablename, columns=columns)
    else:
        return render_template("insert.html", tablename=tablename, columns=columns)

@app.route("/accounts/<account_type>", methods=["GET", "POST"])
def accounts(account_type):
    tablename = account_type
    columns = table_getcolumns(engine, tablename)
    # table = db_gettable(engine, tablename)
    # stmt = table.select()
    # rows = connection.execute(stmt).fetchall()
    rows = table_search(engine, tablename, None)

    if request.method == 'POST':
        if "Back" in request.form:
            return render_template("home.html")
        elif "search" in request.form:
            search_dict = dict()
            for key, value in request.form.items():
                if key == "select_type":
                    search_dict[value] = value
                elif key == "searchConf":
                    search_dict[next(iter(search_dict))] = value
            rows = table_search(engine, tablename, search_dict)
            return render_template("accounts.html", columns=columns, rows=rows)
        elif "update" in request.form:
            keys, values = request.form['update'].split("&&")
            keys = keys.split("||")
            values = values.split("||")
            idx = 0
            global account_id
            for idx in range(len(keys)):
                if keys[idx] == account_type + '_ID':
                    account_id = values[idx]
            return redirect(url_for("update_accounts", account_type=account_type))
        elif "insert" in request.form:
            return redirect(url_for("insert_accounts", account_type=account_type))
        elif "delete" in request.form:
            pass    #TODO
        elif "clear" in request.form:
            return render_template("accounts.html", columns=columns, rows='')
        else:
            rows = table_search(engine, tablename, None)
            return render_template("accounts.html", columns=columns, rows=rows)
    else:
        return render_template("accounts.html", columns=columns, rows=rows)

@app.route("/accounts/<account_type>/update", methods=["GET", "POST"])
def update_accounts(account_type):
    tablename = account_type
    columns = table_getcolumns(engine, tablename)
    update_columns = columns[:]
    update_columns.remove(account_type + "_ID")
    # table = db_gettable(engine, tablename)
    # stmt = table.select().where(table.c[account_type + "_ID"] == account_id)
    # rows = connection.execute(stmt).fetchall()
    rows = table_search(engine, tablename, {account_type + "_ID": account_id})

    if request.method == 'POST':
        if "update" in request.form:
            update_dict = dict()
            for key, value in request.form.items():
                if key != "update" and key != account_type + "_ID" and value != '':
                    update_dict[key] = value
            rows = table_update(engine, tablename, {account_type + "_ID": account_id}, update_dict)
            return render_template("update.html", tablename=tablename, rows=rows, columns=columns, update_columns=update_columns)
        elif "Back" in request.form:
            return redirect(url_for("accounts", account_type=account_type))
        else:
            return render_template("update.html", tablename=tablename, rows=rows, columns=columns, update_columns=update_columns)
    else:
        return render_template("update.html", tablename=tablename, rows=rows, columns=columns, update_columns=update_columns)

@app.route("/accounts/<account_type>/insert", methods=["GET", "POST"])
def insert_accounts(account_type):
    tablename = account_type
    columns = table_getcolumns(engine, tablename)

    if request.method == 'POST':
        if "insert" in request.form:
            insert_dict = dict()
            for key, value in request.form.items():
                if key != "insert":
                    insert_dict[key] = value
            table_insert(engine, tablename, insert_dict)
            return render_template("insert.html", tablename=tablename, columns=columns)
        elif "Back" in request.form:
            return redirect(url_for("accounts", account_type=account_type))
        else:
            return render_template("insert.html", tablename=tablename, columns=columns)
    else:
        return render_template("insert.html", tablename=tablename, columns=columns)

@app.route("/loans", methods=["GET", "POST"])
def loans():
    tablename = "Loans"
    columns = table_getcolumns(engine, tablename)
    # table = db_gettable(engine, tablename)
    # stmt = table.select()
    # rows = connection.execute(stmt).fetchall()
    rows = table_search(engine, tablename, None)
    rows_with_status = list()
    for row in rows:
        rows_with_status.append([])
        for item in row:
            rows_with_status[-1].append(item)
        loan_id = row[0]
        installment = row[-1]
        status = get_loan_status(engine, loan_id, installment)
        rows_with_status[-1].append(status)
        


    if request.method == 'POST':
        if "Back" in request.form:
            return render_template("home.html")
        elif "search" in request.form:
            search_dict = dict()
            for key, value in request.form.items():
                if key == "select_type":
                    search_dict[value] = value
                elif key == "searchConf":
                    search_dict[next(iter(search_dict))] = value
            rows = table_search(engine, tablename, search_dict)
            return render_template("loans.html", columns=columns, rows=rows_with_status)
        elif "view" in request.form:
            keys, values = request.form['view'].split("&&")
            keys = keys.split("||")
            values = values.split("||")
            for idx in range(len(keys)):
                if keys[idx] == "Loan_ID":
                    loan_id = values[idx]
            return redirect(url_for("partial_payments", loan_id=loan_id))
        elif "insert" in request.form:
            return redirect(url_for("insert_loans"))
        elif "delete" in request.form:
            pass    #TODO
        elif "clear" in request.form:
            return render_template("loans.html", columns=columns, rows='')
        else:
            rows = table_search(engine, tablename, None)
            return render_template("loans.html", columns=columns, rows=rows_with_status)
    else:
        return render_template("loans.html", columns=columns, rows=rows_with_status)

@app.route("/loans/insert", methods=["GET", "POST"])
def insert_loans():
    tablename = "Loans"
    columns = table_getcolumns(engine, tablename)

    if request.method == 'POST':
        if "insert" in request.form:
            insert_dict = dict()
            for key, value in request.form.items():
                if key != "insert":
                    insert_dict[key] = value
            table_insert(engine, tablename, insert_dict)
            return render_template("insert.html", tablename=tablename, columns=columns)
        elif "Back" in request.form:
            return redirect(url_for("loans"))
        else:
            return render_template("insert.html", tablename=tablename, columns=columns)
    else:
        return render_template("insert.html", tablename=tablename, columns=columns)

@app.route("/loans/<loan_id>/partial_payments", methods=["GET", "POST"])
def partial_payments(loan_id):
    tablename = "Partial_Payment"
    columns = table_getcolumns(engine, tablename)
    rows = table_search(engine, tablename, {"Loan_ID": loan_id})

    if request.method == 'POST':
        if "Back" in request.form:
            return redirect(url_for("loans"))
        elif "search" in request.form:
            search_dict = dict()
            for key, value in request.form.items():
                if key == "select_type":
                    search_dict[value] = value
                elif key == "searchConf":
                    search_dict[next(iter(search_dict))] = value
            rows = table_search(engine, tablename, search_dict)
            return render_template("loans.html", columns=columns, rows=rows)
        elif "insert" in request.form:
            return redirect(url_for("insert_payments", loan_id=loan_id))
        elif "delete" in request.form:
            pass    #TODO
        elif "clear" in request.form:
            return render_template("partial_payments.html", loan_id=loan_id, columns=columns, rows='')
        else:
            rows = table_search(engine, tablename, {"Loan_ID": loan_id})
            return render_template("partial_payments.html", loan_id=loan_id, columns=columns, rows=rows)
    else:
        return render_template("partial_payments.html", loan_id=loan_id, columns=columns, rows=rows)

@app.route("/loans/<loan_id>/partial_payments/insert", methods=["GET", "POST"])
def insert_payments(loan_id):
    tablename = "Partial_Payment"
    columns = table_getcolumns(engine, tablename)
    insert_columns = columns[:]
    insert_columns.remove("Loan_ID")


    if request.method == 'POST':
        if "insert" in request.form:
            insert_dict = dict()
            for key, value in request.form.items():
                if key != "insert":
                    insert_dict[key] = value
            insert_dict["Loan_ID"] = loan_id
            table_insert(engine, tablename, insert_dict)
            return render_template("insert.html", tablename=tablename, columns=insert_columns)
        elif "Back" in request.form:
            return redirect(url_for("partial_payments", loan_id=loan_id))
        else:
            return render_template("insert.html", tablename=tablename, columns=insert_columns)
    else:
        return render_template("insert.html", tablename=tablename, columns=insert_columns)




@app.route("/database", methods=(["GET", "POST"]))
def database():
    # tablenames = db_showtable(engine)
    tablenames = engine.table_names()

    if request.method == "POST":
        if 'clear' in request.form:
            return render_template("database.html", tablenames = '', dbname=databasename)         # 调用模板, 随后参数为键值对, 将表示模板中变量对应的具体值.
        elif 'search' in request.form:
            return render_template("database.html", tablenames = tablenames, dbname=databasename)
        else:
            print("No handler, Error!")
            return render_template("database.html", tablenames = tablenames, dbname=databasename)

    else:

        return render_template("database.html", tablenames = tablenames, dbname=databasename)

@app.route("/table/<tablename>", methods=(["GET", "POST"]))
def table(tablename):
    columns, rows = table_search(engine, tablename, None)

    if request.method == "POST":
        if 'clear' in request.form:
            return render_template("table.html", columns = '', rows = '', tablename = tablename)         # 调用模板, 随后参数为键值对, 将表示模板中变量对应的具体值.
        elif 'show all' in request.form:
            return render_template("table.html", columns = columns, rows = rows, tablename = tablename)
        elif "search" in request.form:
            search_dict = dict()
            for key, value in request.form.items():
                if key != "search" and value != '':
                    search_dict[key] = value
            columns, rows = table_search(engine, tablename, search_dict)
            return render_template("table.html", columns = columns, rows = rows, tablename = tablename)
        elif "Back" in request.form:
            return redirect(url_for("database"))
        else:
            return render_template("table.html", columns = columns, rows = rows, tablename = tablename)
    else:
        return render_template("table.html", columns = columns, rows = rows, tablename = tablename)

@app.route("/update/<tablename>", methods=['GET', 'POST'])
def update(tablename):
    columns, rows = table_update(engine, tablename, None)

    if request.method == 'POST':
        if "update" in request.form:
            update_dict = dict()
            for key, value in request.form.items():
                if key != "update" and value != '':
                    update_dict[key] = value
            columns, rows = table_update(engine, tablename, update_dict=update_dict)
            return render_template("update.html", columns = columns, rows = rows, tablename = table)
        elif "Back" in request.form:
            return redirect(url_for("lines"))
        else:
            return render_template("update.html", columns = columns, rows = rows, tablename = table)
    else:
        return render_template("update.html", columns = columns, rows = rows, tablename = table)

# 测试URL下返回html page
@app.route("/insert/<tablename>", methods=['GET', 'POST'])
def insert(tablename):
    columns = table_getcolumns(engine, tablename)

    if request.method == 'POST':
        if "insert" in request.form:
            insert_dict = dict()
            for key, value in request.form.items():
                if key != "insert":
                    insert_dict[key] = value
            table_insert(engine, tablename, insert_dict)
            return render_template("insert.html", tablename=tablename, columns=columns)
        elif "Back" in request.form:
            tablenames = engine.table_names()
            return redirect(url_for("database"))
        else:
            return render_template("insert.html", tablename=tablename, columns=columns)
    else:
        return render_template("insert.html", tablename=tablename, columns=columns)

#返回不存在页面的处理
@app.errorhandler(404)
def not_found(e):
    return render_template("404.html")

if __name__ == "__main__":

    print(app.url_map)
    app.run(host = "0.0.0.0", port=4000, debug=True)