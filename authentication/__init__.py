from .routes import auth_bp
# Import routes to register them


def init_auth_app(app):
    app.register_blueprint(auth_bp, url_prefix='/auth')