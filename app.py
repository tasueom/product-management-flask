from flask import Flask, render_template as ren, request, redirect, url_for, session
import sqlite3
import hashlib

app = Flask(__name__)
app.secret_key = "secret_key_123"

def conn_db():
    conn = sqlite3.connect("database.db")
    cur = conn.cursor()
    
    return conn, cur

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
                    pid integer not null,
                    name text not null,
                    price integer not null,
                    amount integer not null,
                    tot integer not null,
                    unique(username, pid)
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
        conn.close()
        
        if user:
            session["uid"] = user[0]
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
    return ren("list.html", rows=rows, user = session.get("user"), role=session.get("role"))

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

@app.route("/add_to_cart/<int:pid>")
def add_to_cart(pid):
    username = session.get("user")
    
    conn, cur = conn_db()
    
    cur.execute("select stock from products where pid=?",(pid,))
    stock = cur.fetchone()[0]
    
    if stock < 1:
        cur.execute("select * from products")
        rows = cur.fetchall()
    
        conn.commit()
        conn.close()
    
        return ren("list.html", rows=rows, user = session.get("user"), role=session.get("role"), msg="재고가 부족합니다.")
        
    else:    
        cur.execute("select * from cart where pid=? and username=?",(pid,username))
        result = cur.fetchone()
    
        if result:
            cur.execute("""
                        update cart set
                        amount = amount+1,
                        tot = price * (amount+1)
                        where pid=? and username=?
                        """,(pid,username))
        else:
            cur.execute("select name, price from products where pid=?",(pid,))
            name, price = cur.fetchone()
        
            cur.execute("""insert into cart(username, pid, name, price, amount, tot)
                        values(?, ?, ?, ?, ?, ?)""",
                        (username, pid, name, price, 1, price))
        
    cur.execute("select * from products")
    rows = cur.fetchall()
    
    conn.commit()
    conn.close()
    
    return ren("list.html", rows=rows, user = session.get("user"), role=session.get("role"), msg="상품이 장바구니에 담겼습니다.")

@app.route("/cart")
def cart():
    username = session.get("user")
    
    conn, cur = conn_db()
    
    cur.execute("select pid, name, price, amount, tot from cart where username=?",
                (username,))
    rows = cur.fetchall()
    
    cur.execute("select sum(tot) from cart where username=?",(username,))
    sum_tot = cur.fetchone()[0]
    
    conn.close()
    
    return ren("cart.html", rows=rows, user = session.get("user"), role=session.get("role"), sum_tot=sum_tot)

@app.route("/purchase")
def purchase():
    username = session.get("user")
    conn, cur = conn_db()

    cur.execute("""
        select pid, sum(amount)
        from cart
        where username = ?
        group by pid
    """, (username,))
    rows = cur.fetchall()

    for pid, cnt in rows:
        cur.execute("update products set stock = stock - ? where pid = ?", (cnt, pid))

    cur.execute("delete from cart where username = ?", (username,))
    conn.commit()
    conn.close()
    
    return ren("cart.html", user = session.get("user"), role=session.get("role"), msg="구매 성공")

@app.route("/my_info")
def my_info():
    uid = session.get("uid")
    
    conn, cur = conn_db()
    
    cur.execute("select username, email, uid from users where uid=?",(uid,))
    info = cur.fetchone()
    
    conn.close()
    
    return ren("my_info.html", user=session.get("user"), role=session.get("role"), info=info)

@app.route("/update_user", methods=['POST'])
def update_user():
    uid = session.get("uid")
    username=request.form["username"]
    email=request.form["email"]
    
    conn, cur = conn_db()
    
    try:
        cur.execute("update users set username=?, email=? where uid=?",(username, email, uid))
        conn.commit()
        session["user"] = username
    except sqlite3.IntegrityError:
            cur.execute("select username, email from users where uid=?", (uid,))
            info = cur.fetchone()
            conn.close()
            return ren("my_info.html",
                    user=session.get("user"),
                    role=session.get("role"),
                    info=info,
                    uid=uid,
                    msg="이미 존재하는 이름입니다.")
    cur.execute("select username, email from users where uid=?", (uid,))
    info = cur.fetchone()
    conn.close()
    return ren("my_info.html",
                    user=session.get("user"),
                    role=session.get("role"),
                    info=info,
                    uid=uid,
                    msg="회원 정보가 수정되었습니다.")

if __name__ == "__main__":
    init_db()
    app.run(debug=True)