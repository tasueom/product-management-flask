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
                    username text not null,
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
    
@app.route("/")
def index():
    return ren("index.html", user = session.get("user"), role=session.get("role"))

@app.route("/signup", methods=['GET','POST'])
def signup():
    return ren("signup.html")

def conn_db():
    conn = sqlite3.connect("product-management-flask/database.db")
    cur = conn.cursor()
    
    return conn, cur

if __name__ == "__main__":
    init_db()
    app.run(debug=True)