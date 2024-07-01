from .routes import fact_bp
from .db import init_db

def init_fact_app(app):
    init_db()
    app.register_blueprint(fact_bp, url_prefix="/fact")