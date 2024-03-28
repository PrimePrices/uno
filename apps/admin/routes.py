from flask import Blueprint, abort, request
from flask_login import login_required, current_user
admin_usernames=["admin"]
admin_bp= Blueprint("admin", __name__, url_prefix="/admin")
from uno.game import Game, get_game_by_id

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
    game = get_game_by_id(game_name)
    data = game.get_game_info()
    for i in game.players:
        data[i]["hand"] = game.get_player_hand(i)
    return data
@admin_bp.route("/user/<username>")
def view_users(username):
    conn = sqlite3.connect("authentication/database.db")
    cursor = conn.cursor()
    data = cursor.execute(f"SELECT * FROM users WHERE username='{username}'").fetchone()
    return data
@admin_bp.route("/user/<username>/change_value/<attribute>", methods=["POST"])
def change_value(attribute, username):
    conn = sqlite3.connect("authentication/database.db")
    cursor = conn.cursor()
    value = request.get("value")
    cursor.execute(f"UPDATE {attribute}='{value}' FROM users WHERE username='{username}'")
