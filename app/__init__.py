from dotenv import load_dotenv
from .config import config

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS

db = SQLAlchemy()
migrate = Migrate()
cors = CORS()


def create_app(key='default'):
    """Create and configures the Flask application.

    Args:
        key (str, optional): Configuration option key. Defaults to 'default'.

    Returns:
        Flask: The configure Flask application instance.
    """
    load_dotenv()

    app = Flask(__name__)
    app.config.from_object(config[key])

    db.init_app(app)
    migrate.init_app(app, db)
    cors.init_app(app)

    from .books import books_bp
    from .members import members_bp

    app.register_blueprint(books_bp, url_prefix='/api/books')
    app.register_blueprint(members_bp, url_prefix='/api/members')

    return app
