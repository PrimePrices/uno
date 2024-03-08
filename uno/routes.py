from flask import Blueprint, render_template, send_from_directory, request, redirect
from .db import *
from flask_login import login_required, current_user
uno_bp = Blueprint("uno", __name__)

special_cards={"u0":"blank","u1":"wild","u2":"N/A","u3":"N/A","u4":"draw4","u5":"N/A","u6":"N/A","u7":"N/A","u8":"N/A","u9":"N/A"}
@uno_bp.route("/newgame/<rules>", methods=["GET", "POST"])
def newGame(rules):
    user=current_user.username
    game_name=make_game(rules, user)
    return redirect("/uno/"+game_name)
@uno_bp.route("/<game_name>/join/")
def join(game):
    if request.cookies["username"]:
        add_player()
    return ""
@uno_bp.route("/game/<game_name>")
def render(game_name):
    return render_template("game.html")
@uno_bp.route("/game/personalised/<game_name>/.json")
@uno_bp.route("/game/<game_name>/personalised.json", methods=["GET"])
def render_json_personalised(game_name):
    user = current_user.username
    info=get_game_info_personalised(game_name, user)
    # info structure = {"id":, "rules", "number_of_players", "players": data, "next_player":, "direction":, "discard":, "draw":}
    return info
@uno_bp.route("/game/<game_name>.json")
def render_json(game_name):
    info=get_game_info(game_name)
    # info structure = {"id":, "rules", "number_of_players", "players": data, "next_player":, "direction":, "discard":, "draw":}
    return info
    #main.games[escape(game_name)]
@login_required
@uno_bp.route("/")
def start():
    print("start accessed")
    return render_template("create.html")

#images and resources
@uno_bp.route("/static/<anything>", methods=["GET"])
def get(anything):
    return send_from_directory("statics",anything)
@uno_bp.route("/images/<colour>/<value>.svg")
def get_svg(colour, value):
    value=value+".svg"
    if colour in ["blue", "red", "yellow", "green", "none"]: 
        return send_from_directory(f"uno/images/{colour}", value)
    else: 
        return send_from_directory("uno/images/none", "404.svg")
@uno_bp.route("/favicon.ico")
def favicon():
    return send_from_directory("uno/images/blue", "reverse.svg")