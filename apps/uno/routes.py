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
    game=Game(create=True, username=user, rules=rules)
    return redirect("/uno/game/"+str(game.id))
@uno_bp.route("/<game_name>/join/")
def join(game_name):
    if current_user.is_authenticated:
        game=Game(game_name)
        game.add_player(current_user.username)
    return ""
@uno_bp.route("/game/<game_name>")
def render(game_name):
    game=Game(game_name)
    if game:
        return render_template("uno/game.html.jinja", data=game.get_game_info_personalised(current_user.username))
    else:
        abort(404)
@uno_bp.route("/game/personalised/<game_name>/.json")
@uno_bp.route("/game/<game_name>/personalised.json", methods=["GET"])
def render_json_personalised(game_name):
    user = current_user.username
    return Game(game_name).get_game_info_personalised(user)

    # info structure = {"id":, "rules", "number_of_players", "players": data, "next_player":, "direction":, "discard":, "draw":}
@uno_bp.route("/game/<game_name>.json")
def render_json(game_name):
    return Game(game_name).get_game_info()
    # info structure = {"id":, "rules", "number_of_players", "players": data, "next_player":, "direction":, "discard":, "draw":}
@login_required
@uno_bp.route("/")
def start():
    return render_template("uno/create.html.jinja")
@uno_bp.route("/game/<game_name>/updates", methods=["POST"])
@login_required
def updates(game_name):
    data=loads(request.data.decode("utf-8"))
    if data["action"] == "player_played_a_card":
        game=Game(game_name)
        cards_left=game.player_played_card(current_user.username, data["card"], data["card_n"])
        transmit(str(game_name), data["action"], current_user.username, {"card": data["card"], "card_n": data["card_n"], "cards_left": cards_left})
    elif data["action"] == "player_drew_a_card":
        game=Game(game_name)
        card=game.draw_card()
        player=Player(current_user.username, game_id=game.id)
        player.cards.append(str(card))
        transmit(str(game_name), data["action"], current_user.username, {})
    elif data["action"] == "uno_challenge":
        print(f'{data["from"]} uno challenges {data["to"]} at {data["timestamp"]}')
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
        return send_from_directory(f"apps/uno/images/{colour}", value)
    else: 
        return send_from_directory("apps/uno/images/none", "404.svg")
@uno_bp.route("/favicon.ico")
def favicon():
    return send_from_directory("apps/uno/images/blue", "reverse.svg")
@uno_bp.app_errorhandler(404)
def not_found(error):
    return send_from_directory("apps/uno/images/none", "404.svg")
@uno_bp.app_errorhandler(PlayerException) # type: ignore
def player_error(e):
    return render_template("404_player_not_found.html.jinja")
@uno_bp.app_errorhandler(405)
def Not_allowed():
    return render_template("bad_request.html.jinja")