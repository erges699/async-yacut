"""Утилиты для генерации и проверки коротких идентификаторов.

Предоставляет функции для создания случайных коротких ID,
проверки их валидности и уникальности в базе данных.
"""

from random import choices
from string import ascii_letters, digits

from .models import URLMap

CUSTOM_ID_LENGTH: int = 6
"""Длина короткого идентификатора по умолчанию."""

ALPHABET: str = ascii_letters + digits
"""Набор допустимых символов для короткого идентификатора."""

RESERVED_SHORT_IDS: set = {'files'}
"""Множество зарезервированных коротких идентификаторов."""

MAX_SHORT_ID_ATTEMPTS: int = 10
"""Максимальное количество попыток генерации уникального short_id."""


def generate_short_id(length: int = CUSTOM_ID_LENGTH) -> str:
    """Генерирует случайную строку из букв и цифр заданной длины.

    Args:
        length: Длина генерируемой строки (по умолчанию 6).

    Returns:
        Случайная строка указанной длины из допустимых символов.
    """
    return ''.join(choices(ALPHABET, k=length))


def is_short_id_valid(short_id: str) -> bool:
    """Проверяет, что short_id состоит только из допустимых символов.

    Args:
        short_id: Проверяемая строка короткого идентификатора.

    Returns:
        True, если все символы входят в ALPHABET, иначе False.
    """
    return all(char in ALPHABET for char in short_id)


def check_short_id_exists(short_id: str) -> bool:
    """Проверяет, существует ли уже такой short_id в базе.

    Args:
        short_id: Короткий идентификатор для проверки.

    Returns:
        True, если запись с таким short_id найдена, иначе False.
    """
    return URLMap.query.filter_by(short=short_id).first() is not None


def get_unique_short_id(length: int = CUSTOM_ID_LENGTH) -> str:
    """Генерирует уникальный short_id, которого нет в базе.

    Повторяет генерацию случайного идентификатора до тех пор,
    пока не будет найден уникальный (отсутствующий в БД).

    Args:
        length: Длина генерируемого идентификатора (по умолчанию 6).

    Returns:
        Уникальный короткий идентификатор.

    Raises:
        RuntimeError: Если не удалось сгенерировать уникальный
            short_id за MAX_SHORT_ID_ATTEMPTS попыток.
    """
    for _ in range(MAX_SHORT_ID_ATTEMPTS):
        short_id = generate_short_id(length)
        if not check_short_id_exists(short_id):
            return short_id
    raise RuntimeError(
        f'Не удалось сгенерировать уникальный short_id '
        f'за {MAX_SHORT_ID_ATTEMPTS} попыток'
    )