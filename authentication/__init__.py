
from flask import Blueprint 
#from flask_login import LoginManager
import sqlite3
from .routes import auth_bp
from .models import login_manager
# Import routes to register them


def init_auth_app(app):
    login_manager.init_app(app)
    conn=sqlite3.connect("database.db")
    cursor=conn.cursor()
    with open("create.sql", "r") as f:
        cursor.executescript(f.read())
    conn.close()
    app.register_blueprint(auth_bp, url_prefix='/auth')
