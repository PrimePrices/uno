from flask import Flask, render_template, request, send_from_directory, redirect, abort, make_response, Response, url_for
from flask_socketio import SocketIO
from flask_login import login_required
import logging
from datetime import timedelta

from apps.admin.__init__ import init_admin_app
from apps.uno.__init__ import init_uno_app
from apps.authentication.__init__ import init_auth_app
from apps.fact.__init__ import init_fact_app
from resources import init_defaults
from get_db import get_db
from apps.uno.socketing import *

app=Flask(__name__)
app.secret_key = "Proof by induction should always be taught by ducks!"
socketio=SocketIO(app)
app.template_folder = "templates"
#app.config["REMEMBER_COOKIE_DURATION"] = timedelta(days=30)
init_defaults(app)
init_uno_app(app, socketio)
init_admin_app(app)
init_auth_app(app)
init_fact_app(app)
def has_no_empty_params(rule)->bool:
    defaults = rule.defaults if rule.defaults is not None else ()
    arguments = rule.arguments if rule.arguments is not None else ()
    return len(defaults) >= len(arguments)

logger=logging.getLogger("werkzeug")
def init_db():
    conn=get_db()
    with open("create.sql", "r") as create:
        conn.executescript(create.read())
    conn.close()
init_db()

@app.context_processor
def inject_variables(): 
    return {"logged_in":current_user.is_authenticated,
            "url": request.url} 
class ExcludeRoutesFilter(logging.Filter):
    def filter(self, record):
        excluded_strings = [
            "GET /uno/images/",
            "GET /uno/static/",
            "GET /uno/favicon.ico",
            "GET /favicon.ico",
            "GET /static/",
            "GET /images/header/",
            "GET /socket.io/"]
        for i in excluded_strings:
            if i in record.getMessage():
                return False
        return True
logger.addFilter(ExcludeRoutesFilter())
@app.route("/site-map")
def site_map()->list:
    links = []
    for rule in app.url_map.iter_rules():  
        if "GET" in rule.methods:# and has_no_empty_params(rule): # type: ignore
            if has_no_empty_params(rule):
                url = url_for(rule.endpoint, **(rule.defaults or {}))
                links.append(url)
            else:
                print(rule, rule.endpoint)
                links.append([rule.endpoint, list(rule.arguments)])
    print(links)
    return links
    # links is now a list of url, endpoint tuples
@app.route("/")
@app.route("/index")
def index():
    print(f"{current_user.is_authenticated=}")
    return render_template("index.html.jinja")

if __name__ == '__main__':
    socketio.run(app, use_reloader=False, log_output=True, port=5000)#, ssl_context="adhoc")
