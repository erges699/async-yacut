import os

from flask import Flask

from yacut.extensions import db


def create_app():
    app = Flask(__name__)

    app.config.from_mapping(
        SECRET_KEY=os.getenv('SECRET_KEY', 'default-secret-key'),
        SQLALCHEMY_DATABASE_URI=os.getenv(
            'DATABASE_URI', 'sqlite:///db.sqlite3'
        ),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        DISK_TOKEN=os.getenv('DISK_TOKEN', ''),
        BASE_URL=os.getenv('BASE_URL', 'http://localhost'),
    )

    db.init_app(app)

    from . import models  # noqa

    with app.app_context():
        db.create_all()

    from yacut.error_handlers import register_errorhandlers
    register_errorhandlers(app)

    from yacut.views import bp as views_bp
    app.register_blueprint(views_bp)

    from yacut.api_views import api as api_bp
    app.register_blueprint(api_bp)

    return app


app = create_app()