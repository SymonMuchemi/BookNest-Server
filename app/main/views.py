from app.main import main_bp
from flask import render_template


@main_bp.route("/", methods=["GET"])
def index():
    """Render the index page."""
    return render_template("index.html")
