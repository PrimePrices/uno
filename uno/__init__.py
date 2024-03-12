from flask import Blueprint
from .game import init_db
from .routes import uno_bp
from .socketing import register_routes
#from . import routes


def init_uno_app(app, socketio):
    init_db()
    register_routes(socketio)
    app.register_blueprint(uno_bp, url_prefix='/uno')