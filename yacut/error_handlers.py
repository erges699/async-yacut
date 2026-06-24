"""Обработчики ошибок HTTP для приложения Yacut.

Определяет кастомные страницы для ошибок 404 и 500.
"""

from flask import render_template

from . import app
from .models import db


@app.errorhandler(404)
def page_not_found(error: Exception) -> tuple[str, int]:
    """Обрабатывает ошибку 404 (страница не найдена).

    Args:
        error: Объект исключения/ошибки.

    Returns:
        Кортеж из шаблона страницы и HTTP-статуса 404.
    """
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_server_error(error: Exception) -> tuple[str, int]:
    """Обрабатывает ошибку 500 (внутренняя ошибка сервера).

    Выполняет откат незавершённой транзакции БД и
    возвращает шаблон страницы ошибки.

    Args:
        error: Объект исключения/ошибки.

    Returns:
        Кортеж из шаблона страницы и HTTP-статуса 500.
    """
    db.session.rollback()
    return render_template('500.html'), 500
