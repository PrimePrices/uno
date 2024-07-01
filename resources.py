from flask import send_from_directory, abort, render_template
from apps.authentication.routes import logout, login, profile, sign_up
def init_defaults(app):
    @app.route("/static/scripts/<anything>")
    def get_scripts(anything):
        return send_from_directory("statics/scripts", anything)
    @app.route("/static/styles/<anything>")
    def get_styles(anything):
        return send_from_directory("statics/styles", anything)
    @app.route("/images/header/<anything>.svg")
    def get_svg(anything):
        return send_from_directory("images/header", anything+".svg")
    @app.route("/login")
    def Login():
        return login()
    @app.route("/about")
    def About():
        render_template("about.html.jinja")
    @app.route("/logout")
    def Logout():
        return logout()
    @app.route("/profile")
    def Profile():
        return profile()
    @app.route("/sign-up")
    @app.route("/signup")
    @app.route("/sign_up")
    def SignUp():
        return sign_up() # type: ignore
    @app.route("/images/<anything>.svg")
    def svg_symbol(anything):
        return send_from_directory("images", anything+".svg")

    #errors
    @app.route("/brew-coffee")
    @app.route("/coffee")
    @app.route("/coffee_pot")
    @app.route("/BrewCoffee")
    def Coffee():
        abort(418)
    @app.route("/lake")
    def Lake():
        abort(-41)
    @app.route("/favicon.ico")
    def favicon():
        return send_from_directory("apps/uno/images/blue", "reverse.svg")
    """
    @app.errorhandler(703)
    def exceptions(error):
        print(error)
        return redirect("https://xkcd.com/1024/")
    """
    """
    @app.errorhandler(404)
    def not_found(e):
        print(e)
        if str(e)=="no exception for -41":
            return send_from_directory("uno/images/none", "404.svg")
        else:
            return send_from_directory("uno/images/none", "404.svg")
    """