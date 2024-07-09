from flask import Blueprint, render_template, send_from_directory, request, redirect, flash
from .game import *
from json import loads
from flask_login import login_required, current_user


uno_bp = Blueprint("uno", __name__, static_folder="apps/uno/static", url_prefix="/uno", template_folder="templates")


special_cards={"u0":"blank","u1":"wild","u2":"N/A","u3":"N/A","u4":"draw4","u5":"N/A","u6":"N/A","u7":"N/A","u8":"N/A","u9":"N/A"}

@uno_bp.route("/newgame/<rules>", methods=["GET", "POST"])
@login_required
def newGame(rules):
    user=current_user.username
    game=Game(create=True, username=user, rules=rules)
    return redirect("/uno/game/"+str(game.id))
@uno_bp.route("/game/<game_name>/join/")
def join(game_name):
    if current_user.is_authenticated:
        game=Game(game_name)
        game.add_player(current_user.username)
    return redirect("/uno/game/"+str(game_name))
@login_required
@uno_bp.route("/game/<game_name>")
def render(game_name):
    if not current_user.is_authenticated:
        return redirect("/login?next=/uno/game/"+str(game_name))
    game=Game(game_name)
    if game:
        print(game.get_game_info_personalised(current_user.username))
        return render_template("game.html.jinja", data=game.get_game_info_personalised(current_user.username))
    else:
        abort(404)
@uno_bp.route("/game/personalised/<game_name>/.json", methods=["GET"])
@uno_bp.route("/game/<game_name>/personalised.json", methods=["GET"])
def render_json_personalised(game_name):
    user = current_user.username
    return Game(game_name).get_game_info_personalised(user)

    # info structure = {"id":, "rules", "number_of_players", "players": data, "next_player":, "direction":, "discard":, "draw":}
@uno_bp.route("/game/<game_name>.json", methods=["GET"])
def render_json(game_name):
    return Game(game_name).get_game_info()
    # info structure = {"id":, "rules", "number_of_players", "players": data, "next_player":, "direction":, "discard":, "draw":}
@login_required
@uno_bp.route("/")
def start():
    return render_template("create.html.jinja")




#images and resources
@uno_bp.route("/static/<folder>/<anything>", methods=["GET"])
def get_static(folder, anything):
    if folder == "script":
        return send_from_directory("apps/uno/static/script", anything)
    elif folder == "style":
        return send_from_directory("apps/uno/static/style", anything)
    elif folder == "image":
        return send_from_directory("apps/uno/static/image", anything)
    else: 
        abort(404)
@uno_bp.route("/static/image/<colour>/<anything>.svg", methods=["GET"])
@uno_bp.route("/image/<colour>/<anything>.svg", methods=["GET"])
def get_image(colour, anything):
    return send_from_directory(f"apps/uno/static/image/{colour}", anything+".svg")

@uno_bp.app_errorhandler(404)
def not_found(error):
    return send_from_directory("apps/uno/static/image/none", "404.svg")
@uno_bp.app_errorhandler(PlayerException) # type: ignore
def player_error(e):
    return render_template("404_player_not_found.html.jinja")
@uno_bp.app_errorhandler(405)
def Not_allowed(e):
    return render_template("bad_request.html.jinja")
@uno_bp.app_errorhandler(422)
def invalid_data(e):
    print(e, e.description)
    return render_template("422_invalid_data.html.jinja")

@uno_bp.app_errorhandler(CardInvalidException)
def Unplayable(error):
    print("This card cannot be played at this moment error raised")
    flash("This card cannot be played at this moment")
    return ""
@uno_bp.app_errorhandler(ColourNotProvidedException)
def ColourError(error):
    print("Colour not provided error raised")
    flash("Colour not provided")
    return ""