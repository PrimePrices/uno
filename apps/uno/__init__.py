from flask import Blueprint
from .routes import uno_bp
from .socketing import register_routes


def init_uno_app(app, socketio):
    register_routes(socketio)
    app.register_blueprint(uno_bp, url_prefix='/uno')