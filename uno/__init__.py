from flask import Blueprint
from .db import init_db
from .routes import uno_bp
#uno_bp = Blueprint('uno', __name__)

# Import routes to register them
from . import routes

def init_uno_app(app):
    print("uno app initialised?")
    init_db()
    app.register_blueprint(uno_bp, url_prefix='/uno')