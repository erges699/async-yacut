"""Настройки Flask-приложения Yacut.

Определяет класс конфигурации, загружающий параметры
из переменных окружения.
"""

import os
from typing import Optional


class Config(object):
    """Конфигурация приложения.

    Attributes:
        SQLALCHEMY_DATABASE_URI: URI подключения к базе данных.
        SECRET_KEY: Секретный ключ для подписи сессий и CSRF-токенов.
        DISK_TOKEN: OAuth-токен для доступа к Яндекс.Диску.
    """

    SQLALCHEMY_DATABASE_URI: Optional[str] = os.getenv('DATABASE_URI')
    SECRET_KEY: Optional[str] = os.getenv('SECRET_KEY')
    DISK_TOKEN: Optional[str] = os.getenv('DISK_TOKEN')
