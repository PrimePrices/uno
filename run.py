from flask import Flask, render_template, request, send_from_directory, redirect, abort, make_response, Response, url_for
from flask_socketio import SocketIO
from flask_login import login_required
from admin.__init__ import init_admin_app
from uno.__init__ import init_uno_app
from authentication.__init__ import init_auth_app
from authentication.routes import logout, login, profile, sign_up
from datetime import timedelta
from uno.socketing import *
import logging
app=Flask(__name__)
app.secret_key = "Proof by induction should always be taught by ducks!"
socketio=SocketIO(app)
app.config["REMEMBER_COOKIE_DURATION"] = timedelta(days=30)
init_uno_app(app, socketio)
init_admin_app(app)
init_auth_app(app)
def has_no_empty_params(rule)->bool:
    defaults = rule.defaults if rule.defaults is not None else ()
    arguments = rule.arguments if rule.arguments is not None else ()
    return len(defaults) >= len(arguments)
logger=logging.getLogger("werkzeug")
class ExcludeRoutesFilter(logging.Filter):
    def filter(self, record):
        excluded_strings = [
            "GET /uno/images/",
            "GET /uno/favicon.ico",
            "GET /uno/static/",
            "GET /static/"]
        for i in excluded_strings:
            if i in record.getMessage():
                return False
        return True
logger.addFilter(ExcludeRoutesFilter())
@app.route("/site-map")
def site_map()->list:
    links = []
    for rule in app.url_map.iter_rules():  
        if "GET" in rule.methods and has_no_empty_params(rule):
            url = url_for(rule.endpoint, **(rule.defaults or {}))
            links.append((url, rule.endpoint))
    return links
    # links is now a list of url, endpoint tuples
@app.route("/")
@app.route("/index")
@login_required
def index():
    return render_template("base.html")
@app.route("/static/<anything>")
def get(anything):
    return send_from_directory("statics", anything)
@app.route("/login")
def Login():
    return login()
@app.route("/logout")
def Logout():
    return logout()
@app.route("/profile")
def Profile():
    return profile()
@app.route("/sign-up")
def SignUp():
    return sign_up()

#errors
@app.route("/brew-coffee")
@app.route("/coffee")
@app.route("/coffee_pot")
@app.route("/BrewCoffee")
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
