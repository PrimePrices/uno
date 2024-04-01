import sqlite3
from typing import Any
import bcrypt
from flask_login import LoginManager, UserMixin, login_required, current_user
from flask import redirect, request
from werkzeug.security import generate_password_hash, check_password_hash
#from run import login_manager
login_manager=LoginManager()
def connect_db(function):
    def wrapper(* args, ** kwargs):
        conn=sqlite3.connect("apps/authentication/database.db")
        cursor=conn.cursor()
        try:
            result=function(cursor, conn, * args, ** kwargs)
        except BaseException as x:
            print(function.__name__ + " " + str(x))
            raise
        finally: conn.close()
        return result
    return wrapper
def access_db():
    conn=sqlite3.connect("apps/authentication/database.db")
    cursor=conn.cursor()
    return cursor, conn
def init_db():
    cursor, conn =  access_db()
    with open("apps/authentication/create.sql", "r") as create:
        cursor.executescript(create.read())
    conn.close()


class User(UserMixin):
    def __init__(self, id, username, hashed_password, email):
        self.id: int=id
        self.username:str= username
        self.email:str = email
        self.hashed_password = hashed_password
        self.authenticated:bool = False
    def get_id(self)->str:
        return str(self.id)
    def is_authenticated(self):
        return self.authenticated
    def is_active(self):
        return True
    def is_anonymous(self):
        return "default_" in self.username
    def check_password(self, password):
        return check_password_hash(self.hashed_password, password)
    def __repr__(self) -> str:
        return str(self.username)


@login_manager.user_loader
def load_user(user_id):
    cursor, conn=access_db()
    if user_id.isdigit():
        cursor.execute("SELECT * FROM user WHERE id = ?", (int(user_id),))
    else: 
        cursor.execute("SELECT * FROM user WHERE username = ?", (user_id,))
    user = cursor.fetchone()
    conn.close()
    if user is None:
        return None
    return User(user[0], user[1], user[2], user[3])