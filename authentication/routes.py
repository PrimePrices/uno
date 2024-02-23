from flask import render_template, redirect, request, flash, Blueprint
#from flask_login import current_user
from .models import login_manager, connect_db, User, load_user

auth_bp = Blueprint('auth', __name__, static_folder="uno/statics", template_folder="templates")


@auth_bp.route("/dashboard")
def dashboard():
    return "Index"

@auth_bp.route("/logout")
def logout():
    return "Logout"
@auth_bp.route("/")
def index():
    return "Index"
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
            return redirect("/auth/login?username_valid=False")
        if User.check_password(password):
            return redirect("/uno")
    print(request.args.get("username_valid"))
    print(request.args.get("username_valid", default=True, type=bool))
    print("invalid_username=", not(request.args.get("username_valid", default=True, type=bool)))
    return render_template("login.html", usename_invalid=not(request.args.get("username_valid", default=True, type=bool)))
@auth_bp.route("/sign_up")
def sign_up():
    return "Sign up"

@login_manager.unauthorized_handler
def unauthorized_callback():
    return redirect("/auth/login?next="+request.path)

