from flask import Flask, render_template, request, send_from_directory, redirect, abort, make_response, Response, url_for
from flask_socketio import SocketIO, emit, disconnect
from markupsafe import escape
from flask_login import LoginManager
import threading
import sqlite3
import random

app=Flask(__name__)
app.secret_key = "Proof by induction should always be taught by ducks!"
login_manager=LoginManager()
login_manager.init_app(app)
socketio =SocketIO(app)

from admin.__init__ import init_admin_app
from uno.__init__ import init_uno_app
from authentication.__init__ import init_auth_app
init_uno_app(app)
init_admin_app(app)
init_auth_app(app)

def has_no_empty_params(rule):
    defaults = rule.defaults if rule.defaults is not None else ()
    arguments = rule.arguments if rule.arguments is not None else ()
    return len(defaults) >= len(arguments)


@app.route("/site-map")
def site_map():
    links = []
    for rule in app.url_map.iter_rules():
        # Filter out rules we can't navigate to in a browser
        # and rules that require parameters
        if "GET" in rule.methods and has_no_empty_params(rule):
            url = url_for(rule.endpoint, **(rule.defaults or {}))
            links.append((url, rule.endpoint))
    return links
    # links is now a list of url, endpoint tuples

#errors
@app.route("/brew-coffee")
def Coffee():
    abort(418)
@app.route("/lake")
def Lake():
    abort(-41)
@app.route("/favicon.ico")
def favicon():
    return send_from_directory("uno/images/blue", "revese.svg")
"""
@app.errorhandler(703)
def exceptions(error):
    print(error)
    return redirect("https://xkcd.com/1024/")
"""
"""
@app.errorhandler(404)
def not_found(e):
    print(e)
    if str(e)=="no exception for -41":
        return send_from_directory("uno/images/none", "404.svg")
    else:
        return send_from_directory("uno/images/none", "404.svg")
"""
if __name__ == '__main__':
    socketio.run(app)
