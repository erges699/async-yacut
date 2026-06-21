import string
from random import choices

from yacut.models import URLMap

SHORT_ID_LENGTH = 6
ALPHABET = string.ascii_letters + string.digits


def generate_short_id(length=SHORT_ID_LENGTH):
    """Генерирует случайную строку из букв и цифр заданной длины."""
    return ''.join(choices(ALPHABET, k=length))


def is_short_id_valid(short_id):
    """Проверяет, что short_id состоит только из допустимых символов."""
    return all(char in ALPHABET for char in short_id)


def check_short_id_exists(short_id):
    """Проверяет, существует ли уже такой short_id в базе."""
    return URLMap.query.filter_by(short=short_id).first() is not None


def get_unique_short_id(length=SHORT_ID_LENGTH):
    """Генерирует уникальный short_id, которого нет в базе."""
    while True:
        short_id = generate_short_id(length)
        if not check_short_id_exists(short_id):
            return short_id