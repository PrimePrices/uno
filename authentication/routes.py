from flask import render_template, redirect, request, flash, Blueprint
#from flask_login import current_user
from .models import login_manager, connect_db, User, load_user

auth_bp = Blueprint('auth', __name__, static_folder="uno/statics", template_folder="templates")




@auth_bp.route("/logout")
def logout():
    return "Logout"
@auth_bp.route("/profile")
def profile():
    return "profile"
@auth_bp.route("/login", methods=["GET", "POST"])
def login():
#    if current_user.is_authenticated:
#        return redirect("/profile")
    if request.method=="POST":
        name=request.form.get("username")
        password=request.form.get("password")
        remember_me=request.form.get("remember_me")
        User=load_user(name)
        if User is None:
            return redirect("/login?username_valid=0")
        if User.check_password(password):
            return redirect("/uno")
    print(request.args.get("username_valid"))
    print(request.args.get("username_valid", default=1, type=int))
    print("invalid_username=", not request.args.get("username_valid", default=1, type=int))
    return render_template("login.html", usename_invalid=not request.args.get("username_valid", default=1, type=int))
@auth_bp.route("/sign_up")
def sign_up():
    return "Sign up"

@login_manager.unauthorized_handler
def unauthorized_callback():
    return redirect("/login?next="+request.path)

