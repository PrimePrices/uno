from flask import Blueprint

admin_bp = Blueprint('admin', __name__)

# Import routes to register them
from . import routes

def init_admin_app(app):
    app.register_blueprint(admin_bp, url_prefix='/admin')