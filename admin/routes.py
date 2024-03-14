from flask import Blueprint, abort
from flask_login import login_required, current_user
admin_usernames=["admin"]
admin_bp= Blueprint("admin", __name__, url_prefix="/admin")
from uno.game import game, get_game_by_id

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
    return "dashboard"
@admin_bp.route("/uno/view_game/<game_name>")
def view_game(game_name):
    game = get_game_by_id(game_name)
    data = game.get_game_info()
    for i in game.players:
        data[i]["hand"] = game.get_player_hand(i)
    return "game"
@admin_bp.route("/user/<username>")
def view_users(username):
    return "user"
@admin_bp.route("/user/<username>/change_password")
def change_password(user):
    return "changed"
