from flask import Flask, render_template, request, send_from_directory, redirect, abort, make_response, Response
from flask_socketio import SocketIO, emit
from markupsafe import escape
import threading
import sqlite3
import random
from db import *
app=Flask(__name__)
socketio =SocketIO(app)
app.secret_key = "Proof by induction should always be taught by ducks!"

special_cards={"u0":"blank","u1":"wild","u2":"N/A","u3":"N/A","u4":"draw4","u5":"N/A","u6":"N/A","u7":"N/A","u8":"N/A","u9":"N/A"}
@app.route("/uno/newgame/<rules>", methods=["GET", "POST"])
def newGame(rules):
    user=request.cookies.get("username", "default")
    game_name=make_game(rules, user)
    return redirect("/uno/"+game_name)
@app.route("/uno/<game_name>/join/")
def join(game):
    if request.cookies["username"]:
        add_player()
@app.route("/uno/game/<game_name>")
def render(game_name):
    return render_template("game.html")
@app.route("/uno/game/<game_name>/<me>.json")
def render_json_personalised(game_name, me):
    info=get_game_info_personalised(game_name, me)
    # info structure = {"id":, "rules", "number_of_players", "players": data, "next_player":, "direction":, "discard":, "draw":}
    return info
@app.route("/uno/game/<game_name>.json")
def render_json(game_name):
    info=get_game_info(game_name)
    # info structure = {"id":, "rules", "number_of_players", "players": data, "next_player":, "direction":, "discard":, "draw":}
    return info
    #main.games[escape(game_name)]

#login
@app.route("/uno/index/")
@app.route("/uno/")
def start():
    if request.cookies.get("username", 0)!=0:
        return render_template("create.html")
    return redirect("/login")
@app.route("/new_account")
def create_account():
    return 1
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method=="GET":
        return render_template("login.html")
    else:
        print(request.form["username"])
        response=make_response(redirect("/uno/"))
        response.set_cookie("username", request.form["username"])
        response.set_cookie("password", request.form["password"], secure=True)
        return response

#images and resources
@app.route("/uno/static/<anything>", methods=["GET"])
def get(anything):
    return send_from_directory("statics",anything)
@app.route("/uno/images/<colour>/<value>.svg")
def get_svg(colour, value):
    value=value+".svg"
    if colour in ["blue", "red", "yellow", "green", "none"]: 
        return send_from_directory(f"images/{colour}", value)
    else: 
        return send_from_directory("images/none", "404.svg")
@app.route("/uno/favicon.ico")
def favicon():
    return send_from_directory("images/blue", "reverse.svg")

#errors
@app.route("/brew-coffee")
def Coffee():
    abort(418)
@app.route("/lake")
def Lake():
    abort(-41)
"""
@app.errorhandler(703)
def exceptions(error):
    print(error)
    return redirect("https://xkcd.com/1024/")
"""
@app.errorhandler(404)
def not_found(e):
    if str(e)=="no exception for -41":
        return send_from_directory("images/none", "404.svg")
    else:
        return send_from_directory("images/none", "404.svg")

"""
@socketio.on('connect', namespace='/updates/game/<game_id>')
def handle_connect(game_id):
    a=get_game_info(id)
    socketio.emit('update_game_state', a)
    print(a)
"""

if __name__ == '__main__':
    # Start the game state updater in a separate thread
    init_db()
    socketio.run(app)
    #game_state_broadcaster(socketio)
    #, debug=True)
    #updater_thread = threading.Thread(target=game_state_broadcaster)
    #updater_thread.start()
    # Run the Flask application with SocketIO
    