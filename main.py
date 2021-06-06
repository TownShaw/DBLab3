import functools

from flask import Flask, session
from flask import redirect
from flask import request, make_response
from flask import render_template
from flask import url_for
from flask import flash

from db import *

# 生成一个app
app = Flask(__name__, instance_relative_config=True)
app.secret_key = 'lab3'

# 对app执行请求页面地址到函数的绑定
@app.route("/", methods=("GET", "POST"))                # Python 装饰器, 使得 / 和 /login 都重定向到 login.html
@app.route("/login", methods=("GET", "POST"))
def login():
    """Log in a registered user by adding the user id to the session."""
    if request.method == "POST":
        # 客户端在login页面发起的POST请求
        username = request.form["username"]
        password = request.form["password"]
        ipaddr   = request.form["ipaddr"]
        database = request.form["database"]

        db = db_login(username, password, ipaddr, database)

        if db == None:
            return render_template("login_fail.html")
        else:
            session['username'] = username
            session['password'] = password
            session['ipaddr'] = ipaddr
            session['database'] = database

            return redirect(url_for('table'))
    else :
        # 客户端GET 请求login页面时
        return render_template("login.html")

# 请求url为host/table的页面返回结果
@app.route("/table", methods=(["GET", "POST"]))
def table():
    # 出于简单考虑，每次请求都需要连接数据库，可以尝试使用其它context保存数据库连接
    if 'username' in session:
        db = db_login(session['username'], session['password'],
                        session['ipaddr'], session['database'])
    else:
        return redirect(url_for('login'))
    
    tabs = db_showtable(db)

    db_close(db)
    if request.method == "POST":
        if 'clear' in request.form:
            return render_template("table.html", rows = '', dbname=session['database'])         # 调用模板, 随后参数为键值对, 将表示模板中变量对应的具体值.
        elif 'search' in request.form:
            return render_template("table.html", rows = tabs, dbname=session['database'])
        elif 'select' in request.form:
            # print(type(request.form))
            session['table'] = request.form['select']
            return redirect(url_for("lines"))
        else:
            print("No handler, Error!")
            return render_template("table.html", rows = tabs, dbname=session['database'])

    else:
        return render_template("table.html", rows = tabs, dbname=session['database'])

@app.route("/table/lines", methods=(["GET", "POST"]))
def lines():
    # 出于简单考虑，每次请求都需要连接数据库，可以尝试使用其它context保存数据库连接
    if 'username' in session:
        db = db_login(session['username'], session['password'], session['ipaddr'], session['database'])
    else:
        return redirect(url_for('login'))

    if 'table' not in session:
        return redirect(url_for('table'))
    table = session['table']
    columns, rows = table_showlines(db, table, None)
    

    if request.method == "POST":
        if 'clear' in request.form:
            db_close(db)
            return render_template("lines.html", columns = '', rows = '', tablename = table)         # 调用模板, 随后参数为键值对, 将表示模板中变量对应的具体值.
        elif 'show all' in request.form:
            db_close(db)
            return render_template("lines.html", columns = columns, rows = rows, tablename = table)
        elif "search" in request.form:
            search_conf = dict()
            for key, value in request.form.items():
                if key != "search" and value != '':
                    search_conf[key] = value
            columns, rows = table_showlines(db, table, search_conf)
            db_close(db)
            return render_template("lines.html", columns = columns, rows = rows, tablename = table)
        elif "Back" in request.form:
            db_close(db)
            return redirect(url_for("table"))
        else:
            db_close(db)
            return render_template("lines.html", columns = columns, rows = rows, tablename = table)
    else:
        db_close(db)
        return render_template("lines.html", columns = columns, rows = rows, tablename = table)


# 测试URL下返回html page
@app.route("/hello")
def hello():
    return "hello world!"

#返回不存在页面的处理
@app.errorhandler(404)
def not_found(e):
    return render_template("404.html")

if __name__ == "__main__":

    print(app.url_map)
    app.run(host = "0.0.0.0", port=4000, debug=True)