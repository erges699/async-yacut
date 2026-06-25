"""Модели базы данных для приложения Yacut.

Определяет модель URLMap для хранения соответствий
между оригинальными URL и короткими идентификаторами.
"""

from datetime import datetime, timezone

from flask import url_for
from sqlalchemy import Column, DateTime, Integer, String

from . import db


class URLMap(db.Model):  # type: ignore[name-defined]
    """Модель для хранения соответствий между URL и короткими ссылками.

    Attributes:
        id: Уникальный идентификатор записи.
        original: Оригинальный (длинный) URL.
        short: Короткий идентификатор (уникальный).
        timestamp: Дата и время создания записи.
    """

    __tablename__ = 'url_map'

    id = Column(Integer, primary_key=True)
    original = Column(String(256), nullable=False)
    short = Column(String(16), unique=True, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)

    def to_dict(self) -> dict:
        """Преобразует запись в словарь для API-ответа.

        Returns:
            Словарь с оригинальным URL и полной короткой ссылкой.
        """
        return dict(
            url=self.original,
            short_link=url_for(
                'redirect_to_original', short_id=self.short, _external=True
            )
        )

    def from_dict(self, data: dict) -> None:
        """Заполняет поля модели из словаря.

        Args:
            data: Словарь с ключами 'url' и 'custom_id'.
        """
        self.original = data['url']
        self.short = data['custom_id']