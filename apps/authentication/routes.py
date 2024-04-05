from flask import render_template, redirect, request, flash, Blueprint
from flask_login import login_user, current_user, logout_user
from .models import login_manager, connect_db, User, load_user
from werkzeug.security import check_password_hash
from werkzeug.security import generate_password_hash
auth_bp = Blueprint('auth', __name__, static_folder="uno/statics", template_folder="templates/authentication")


@auth_bp.route("/logout")
def logout():
    logout_user()
    return redirect(request.referrer or "/login")
@auth_bp.route("/profile")
def profile():
    return "profile"
@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect("/profile")
    if request.method=="POST":
        name=request.form.get("username")
        password=request.form.get("password")
        remember_me:bool="True"==request.form.get("remember_me")
        next=request.args.get("next")
        User=load_user(name)
        print(f"{User} is trying to log in")
        if User is None:
            return render_template("authenticationlogin.html.jinja", username_invalid=True)
        if User.check_password(password):
            User.authenticated=True
            login_user(User, remember=True)
            flash("Logged in successfully", "success")
            print(f"{current_user=}, {current_user.is_authenticated()=}")
            print("password accepted")
            return redirect(next or "/index")
        else:
            print(f"{password=}")
            return render_template("authentication/login.html.jinja", password_invalid=True)
    return render_template("authentication/login.html.jinja")

@auth_bp.route("/sign_up", methods=["GET", "POST"])
@connect_db
def sign_up(cursor, conn):
    if request.method=="POST":
        username=request.form.get("username")
        password=request.form.get("password")
        password_again=request.form.get("password_repeated")
        email=request.form.get("email")
        if username is None:
            return render_template("authentication/sign_up.html.jinja")
        if "default_" in username:
            return render_template("authentication/sign_up.html.jinja", invalid_format=True)
        cursor.execute(f"SELECT * FROM user WHERE username='{username}'")
        if cursor.fetchone() or "default_" in username:
            return render_template("signup.html.jinja", username_invalid=True)
        if password!=password_again or password is None:
            return render_template("signup.html.jinja", password_dont_match=True)
        cursor.execute(f"SELECT * FROM user WHERE email='{email}'")
        if cursor.fetchone():
            return render_template("signup.html.jinja", email_taken=True)
        h_pass=generate_password_hash(password)
        print(f"{password=} {h_pass=}")
        cursor.execute(f"INSERT INTO user (username, hashed_password, email) VALUES ('{username}', '{h_pass}', '{email}') ")
        conn.commit()
        return "Accepted"
    else:
        return render_template("signup.html.jinja")

@login_manager.unauthorized_handler
def unauthorized_callback():
    print(f"unathorised access to {request.path} by user {current_user}")
    return redirect("/login?next="+request.path)