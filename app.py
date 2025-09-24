from flask import Flask, render_template as ren, request, redirect, url_for, session
import sqlite3
import hashlib

app = Flask(__name__)
app.secret_key = "secret_key_123"

if __name__ == "__main__":
    app.run(debug=True)