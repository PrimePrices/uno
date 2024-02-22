from flask import Blueprint

admin_bp= Blueprint("admin", __name__)

@admin_bp.route("/dashboard")
def dashboard():
    return "dashboard"