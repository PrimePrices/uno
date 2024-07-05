from .routes import fact_bp


def init_fact_app(app):
    app.register_blueprint(fact_bp, url_prefix="/fact")