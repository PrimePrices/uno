from flask import Blueprint, render_template
auth_bp = Blueprint('auth', __name__, static_folder="uno/statics", template_folder="templates")
@auth_bp.route("/")
def index():
    return "Index"
@auth_bp.route("/profile")
def profile():
    return "profile"
@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    return render_template("login.html")
@auth_bp.route("/sign_up")
def sign_up():
    return "Sign up"
