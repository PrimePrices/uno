import sqlite3
import bcrypt
from flask_login import LoginManager, UserMixin, login_required, current_user
from flask import redirect, request
from werkzeug.security import generate_password_hash, check_password_hash
#from run import login_manager
login_manager=LoginManager()
def connect_db(function):
    def wrapper(* args, ** kwargs):
        conn=sqlite3.connect("authentication/database.db")
        cursor=conn.cursor()
        print(f"{function.__name__} access granted to authentication")
        try:
            result=function(cursor, conn, * args, ** kwargs)
        except BaseException as x:
            print(function.__name__)
            raise
        finally: conn.close()
        print(f"{function.__name__} access finished")
        return result
    return wrapper
def get_db():
    conn=sqlite3.connect("authentication/database.db")
    cursor=conn.cursor()
    return conn, cursor
@connect_db
def init_db(cursor, conn):
    with open("authentication/create.sql", "r") as create:
        cursor.executescript(create.read())
    cursor.execute("SELECT username FROM user")
    print(cursor.fetchall())
    conn.close()


class User(UserMixin):
    def __init__(self, id, username, hashed_password, email):
        self.id=id
        self.username= username
        self.email = email
        self.hashed_password = hashed_password
        self.authenticated = False
    def check_password(self, password):
        return check_password_hash(self.hashed_password, password)


@login_manager.user_loader
def load_user(user_id):
    conn, cursor = get_db() 
    if type(user_id)==int:
        cursor.execute(f"SELECT * from user where id = {user_id}")
    else: #username
        cursor.execute(f"SELECT * FROM user WHERE username = '{user_id}'")
    user=cursor.fetchone()
    conn.close()
    print(f"{user=}")
    if user is None:
        return None # Change for anonymous user
    else: return User(user[0], user[1], user[2], user[3])
    
