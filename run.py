from flask import Flask, render_template, request, send_from_directory, redirect, abort, make_response, Response, url_for
from flask_socketio import SocketIO, emit, disconnect
from flask_login import login_required
from admin.__init__ import init_admin_app
from uno.__init__ import init_uno_app
from authentication.__init__ import init_auth_app
from authentication.routes import logout, login, profile, sign_up
from datetime import timedelta
app=Flask(__name__)
app.secret_key = "Proof by induction should always be taught by ducks!"
socketio =SocketIO(app)
app.config["REMEMBER_COOKIE_DURATION"] = timedelta(days=30)
init_uno_app(app)
init_admin_app(app)
init_auth_app(app)

def has_no_empty_params(rule)->bool:
    defaults = rule.defaults if rule.defaults is not None else ()
    arguments = rule.arguments if rule.arguments is not None else ()
    return len(defaults) >= len(arguments)

@app.route("/site-map")
def site_map()->list:
    links = []
    for rule in app.url_map.iter_rules():
        # Filter out rules we can't navigate to in a browser
        # and rules that require parameters
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
def a_1():
    return login()
@app.route("/logout")
def a_2():
    return logout()
@app.route("/profile")
def a_3():
    return profile()
@app.route("/sign-up")
def a_4():
    return sign_up()

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
