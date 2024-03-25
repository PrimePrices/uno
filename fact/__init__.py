from .routes import fact_bp 
def init_app(app):
  app.register_bluprint(fact_bp, namespace="/facts")
