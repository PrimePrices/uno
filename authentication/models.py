import sqlite3
import bcrypt
from flask_login import LoginManager, UserMixin, login_required, current_user
from flask import redirect, request
#from run import login_manager
login_manager=LoginManager()
def connect_db(function):
    def wrapper(* args, ** kwargs):
        conn=sqlite3.connect("database.db")
        cursor=conn.cursor()
        print(f"{function.__name__} access granted")
        try:
            result=function(cursor, conn, * args, ** kwargs)
        except BaseException as x:
            print(function.__name__)
            raise
        finally: conn.close()
        print(f"{function.__name__} access finished")
        return result
    return wrapper
@connect_db
def init_db(cursor, conn):
    with open("create.sql", "r") as create:
        cursor.executescript(create.read())
    conn.close()


class User(UserMixin):
    def __init__(self, id, username, email, hashed_password):
        self.id=id
        self.username= username
        self.email = email
        self.hashed_password = hashed_password
        self.authenticated = False
    def check_password(self, password):
        if bcrypt.hashpw(bytes(password+self.username))==self.hashed_password:
            return True
        return False

@connect_db
@login_manager.user_loader
def load_user(cursor, conn, user_id):
    cursor.execute(f"SELECT * from user where id = '{user_id}'")
    user=cursor.fetchone()
    if user is None:
        return None # Change for anonymous user
    else: return User(user[0], user[1], user[2], user[3])
