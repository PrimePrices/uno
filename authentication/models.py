from . import db
import sqlite3
from flask_login import LoginManager, UserMixin, login_required, current_user
from run import login_manager

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
    def __init__(self, id, email, password):
         self.id = unicode(id)
         self.email = email
         self.password = password
         self.authenticated = False
    def is_anonymous(self):
         return False
    def is_authenticated(self):
         return self.authenticated
    def is_active(self):
         return True
    def get_id(self):
         return self.id
@connect_db
@login_manager.user_loader
def load_user(cursor, conn, user_id):
    