from flask import Blueprint, render_template, send_from_directory, request, redirect
from .game import *
from json import loads
from flask_login import login_required, current_user
uno_bp = Blueprint("uno", __name__)
from .socketing import transmit

special_cards={"u0":"blank","u1":"wild","u2":"N/A","u3":"N/A","u4":"draw4","u5":"N/A","u6":"N/A","u7":"N/A","u8":"N/A","u9":"N/A"}
@uno_bp.route("/newgame/<rules>", methods=["GET", "POST"])
def newGame(rules):
    user=current_user.username
    game=make_game(user, rules)
    return redirect("/uno/game/"+str(game.id))
@uno_bp.route("/<game_name>/join/")
def join(game_name):
    if current_user.is_authenticated:
        game=get_game_by_id(game_name)
        game.add_player(current_user.username)
    return ""
@uno_bp.route("/game/<game_name>")
def render(game_name):
    return render_template("game.html")
@uno_bp.route("/game/personalised/<game_name>/.json")
@uno_bp.route("/game/<game_name>/personalised.json", methods=["GET"])
def render_json_personalised(game_name):
    user = current_user.username
    game=get_game_by_id(game_name)
    info=game.get_game_info_personalised(user)
    # info structure = {"id":, "rules", "number_of_players", "players": data, "next_player":, "direction":, "discard":, "draw":}
    return info
@uno_bp.route("/game/<game_name>.json")
def render_json(game_name):
    game=get_game_by_id(game_name)
    info=game.get_game_info()
    # info structure = {"id":, "rules", "number_of_players", "players": data, "next_player":, "direction":, "discard":, "draw":}
    return info
    #main.games[escape(game_name)]
@login_required
@uno_bp.route("/")
def start():
    return render_template("create.html")

@uno_bp.route("/game/<game_name>/updates", methods=["POST"])
@login_required
def updates(game_name):
    data=loads(request.data.decode("utf-8"))
    if data["action"] == "player_played_a_card":
        game=get_game_by_id(game_name)
        cards_left=game.player_played_card(current_user.username, data["card"], data["card_n"])
        transmit(game_name, data["action"], current_user.username, {"card": data["card"], "card_n": data["card_n"], "cards_left": cards_left})
    elif data["action"] == "player_drew_a_card":
        game=get_game_by_id(game_name)
        card=game.draw_card()
        #db wrangling here
        #emit_to_socketio
    else: print(data)
    return {"a": True}

#images and resources
@uno_bp.route("/static/<anything>", methods=["GET"])
def get(anything):
    return send_from_directory("statics", anything)
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
@uno_bp.error_handler(404)
def not_found(error):
    return send_from_directory("uno/images/none", "404.svg")
