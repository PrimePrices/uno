from flask import Blueprint
from flask_login import login_required, current_user
admin_usernames=["admin"]
admin_bp= Blueprint("admin", __name__, url_prefix="/admin")

def admin_only():
    if not current_user.authenticated:
        abort(403)
    if current_user.username not in admin_usernames:
        abort(403)
    else: 
        return None


@login_required
@admin_bp.route("/dashboard")
def dashboard():
    admin_only()
    return "dashboard
@admin_bp.route("/uno/view_game/<game_name:str>)
def view_game(game_name):
    return "game"
@admin_bp.route("/user/<username:str>)
def view_users(username):
    return "user"
@admin_bp.route("/user/<username:str>/change_password)
def change_password(user):
    return "changed"
