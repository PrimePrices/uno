from flask import Blueprint, abort, request
from flask_login import login_required, current_user
from apps.uno.game import Game
from apps.authentication.models import access_db as authentication_access_db

admin_usernames=["admin"]
admin_bp = Blueprint("admin", __name__, url_prefix="/admin")

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
    admin_only()
    game = Game(game_name)
    data = game.get_game_info()
    for i in game.players:
        data[i]["hand"] = game.get_player_hand(i)
    return data
@admin_bp.route("/user/<username>")
def view_users(username):
    cursor, conn = authentication_access_db()
    data = cursor.execute(f"SELECT * FROM users WHERE username='{username}'").fetchone()
    conn.close()
    return data
@admin_bp.route("/user/<username>/change_value/<attribute>", methods=["POST"])
def change_value(attribute, username):
    cursor, conn = authentication_access_db()
    value = request.args.get("value")
    cursor.execute(f"UPDATE {attribute}='{value}' FROM users WHERE username='{username}'")
    conn.commit()
    conn.close()
    return "success"
