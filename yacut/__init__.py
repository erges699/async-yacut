"""Инициализация Flask-приложения Yacut.

Создаёт экземпляр Flask, настраивает подключение к базе данных
и регистрирует миграции, а также импортирует модули представлений
и обработчиков ошибок.
"""

from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

from .settings import Config

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)

from . import api_views, views, error_handlers
# cli_commands
