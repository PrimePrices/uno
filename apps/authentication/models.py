import sqlite3
from typing import Any
import bcrypt
from flask_login import LoginManager, UserMixin, login_required, current_user
from flask import redirect, request
from werkzeug.security import generate_password_hash, check_password_hash
from get_db import get_db
#from run import login_manager
login_manager=LoginManager()



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
    conn=get_db()
    if user_id.isdigit():
        user = conn.execute("SELECT * FROM user WHERE user_id = ?", (int(user_id),)).fetchone()
    else: 
        user = conn.execute("SELECT * FROM user WHERE username = ?", (user_id,)).fetchone()
    conn.close()
    if user is None:
        return None
    return User(user[0], user[1], user[2], user[3])