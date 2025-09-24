from flask import Flask, render_template as ren, request, redirect, url_for, session
import sqlite3
import hashlib

app = Flask(__name__)
app.secret_key = "secret_key_123"

def init_db():
    conn, cur = conn_db()
    cur.execute("""
                create table if not exists users(
                    uid integer primary key autoincrement,
                    username text not null unique,
                    email text not null,
                    password text not null,
                    role text not null default 'user'
                )
                """)
    cur.execute("""
                create table if not exists products(
                    pid integer primary key autoincrement,
                    name text not null,
                    price integer not null,
                    stock integer not null,
                    description text
                )
                """)
    cur.execute("""
                create table if not exists cart(
                    username text not null,
                    pid integer not null unique,
                    name text not null,
                    price integer not null,
                    amount integer not null,
                    tot integer not null
                )
                """)
    conn.commit()
    conn.close()
    
@app.route("/")
def index():
    return ren("index.html", user = session.get("user"), role=session.get("role"))

@app.route("/signup", methods=['GET','POST'])
def signup():
    if request.method=="POST":
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]
        hashed_pw = hashlib.sha256(password.encode()).hexdigest()
        
        conn, cur = conn_db()
        cur.execute("select count(*) from users")
        cnt = cur.fetchone()[0]
        role = "admin" if cnt == 0 else "user"
        
        try:
            cur.execute("insert into users(username, email, password, role) values(?, ?, ?, ?)",
                        (username, email, hashed_pw, role))
            conn.commit()
        except sqlite3.IntegrityError:
            conn.close()
            return ren("signup.html",err = "이미 존재하는 이름입니다.")
        conn.close()
        return redirect(url_for("signin"))
    
    return ren("signup.html")

@app.route("/signin", methods=['GET','POST'])
def signin():
    if request.method == 'POST':
        username = request.form["username"]
        password = request.form["password"]
        hashed_pw = hashlib.sha256(password.encode()).hexdigest()
        
        conn, cur = conn_db()
        cur.execute("select uid, username, role from users where username=? and password = ?",
                    (username, hashed_pw))
        user = cur.fetchone()
        conn.close
        
        if user:
            session["user"] = user[1]
            session["role"] = user[2]
            return redirect(url_for("index"))
        else:
            return ren("signin.html", err="로그인 실패. 아이디 혹은 비밀번호를 확인하세요.")
    
    return ren("signin.html")

@app.route("/signout")
def signout():
    session.clear()
    return redirect(url_for("index"))

@app.route("/list")
def list_product():
    if "user" not in session:
        return redirect(url_for("signin"))
    
    conn, cur = conn_db()
    
    cur.execute("select * from products")
    rows = cur.fetchall()
    
    conn.close()
    return ren("list.html", rows=rows, user = session.get("user"), role=session["role"])

@app.route("/insert", methods=['GET','POST'])
def insert():
    if request.method == "POST":
        name = request.form["name"]
        price = int(request.form["price"])
        stock = int(request.form["stock"])
        description = request.form["description"]
        
        conn, cur = conn_db()
        cur.execute("insert into products(name, price, stock, description) values (?, ?, ?, ?)",(name,price,stock,description))
        
        conn.commit()
        conn.close()
        
        return redirect(url_for("list_product"))
    return ren("insert.html", user = session.get("user"), role=session.get("role"))

@app.route("/update/<int:pid>", methods=['GET','POST'])
def update(pid):
    if request.method=="POST":
        name = request.form["name"]
        price = int(request.form["price"])
        stock = int(request.form["stock"])
        description = request.form["description"]
        
        conn, cur = conn_db()
        
        cur.execute("""
                    update products set
                    name = ?,
                    price = ?,
                    stock = ?,
                    description = ?
                    where pid = ?
                    """,(name, price, stock, description, pid))
        conn.commit()
        conn.close()
        return redirect(url_for("list_product"))
    
    conn, cur = conn_db()
    
    cur.execute("select * from products where pid = ?",(pid,))
    product = cur.fetchone()
    
    conn.close()
    
    return ren("update.html", product = product, user = session.get("user"), role=session.get("role"))

@app.route("/delete/<int:pid>")
def delete(pid):
    conn, cur = conn_db()
    
    cur.execute("delete from products where pid = ?",(pid,))
    conn.commit()
    conn.close()
    
    return redirect(url_for("list_product"))

@app.route("/cart")
def cart():
    username = session.get("user")
    
    conn, cur = conn_db()
    
    cur.execute("select pid, name, price, amount, tot from cart where username=?",
                (username,))
    rows = cur.fetchall()
    
    conn.close()
    
    return ren("cart.html", rows=rows, user = session.get("user"), role=session.get("role"))

def conn_db():
    conn = sqlite3.connect("database.db")
    cur = conn.cursor()
    
    return conn, cur

if __name__ == "__main__":
    init_db()
    app.run(debug=True)