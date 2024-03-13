from flask import Blueprint
from .routes import admin_bp

def init_admin_app(app):
    app.register_blueprint(admin_bp, url_prefix='/admin')
