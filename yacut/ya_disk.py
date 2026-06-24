"""Интеграция с Яндекс.Диском для загрузки файлов.

Предоставляет асинхронные функции для получения ссылок загрузки,
загрузки файлов на Яндекс.Диск и создания коротких ссылок на них.
"""

import asyncio
import os
from typing import Any

import aiohttp
from werkzeug.datastructures import FileStorage

from . import db
from .models import URLMap
from .utils import get_unique_short_id

DISK_TOKEN: str = os.getenv('DISK_TOKEN', '')
"""OAuth-токен для доступа к Яндекс.Диску."""

BASE_URL: str = os.getenv('BASE_URL', 'http://localhost')
"""Базовый URL приложения для формирования коротких ссылок."""

REQUEST_UPLOAD_URL: str = (
    'https://cloud-api.yandex.net/v1/disk/resources/upload'
)
"""URL для получения ссылки на загрузку файла на Яндекс.Диск."""

DOWNLOAD_LINK_URL: str = (
    'https://cloud-api.yandex.net/v1/disk/resources/download'
)
"""URL для получения ссылки на скачивание файла с Яндекс.Диска."""


async def get_upload_link(
    session: aiohttp.ClientSession, filename: str
) -> tuple[str, str]:
    """Получает ссылку для загрузки файла на Яндекс Диск.

    Args:
        session: Асинхронная HTTP-сессия aiohttp.
        filename: Имя файла для загрузки.

    Returns:
        Кортеж из URL для загрузки и HTTP-метода (PUT).
    """
    headers = {'Authorization': f'OAuth {DISK_TOKEN}'}
    params = {'path': f'/{filename}', 'overwrite': 'true'}
    async with session.get(
        REQUEST_UPLOAD_URL, headers=headers, params=params
    ) as response:
        data: dict[str, Any] = await response.json()
        return data['href'], data['method']


async def upload_file(
    session: aiohttp.ClientSession, upload_url: str, file_data: bytes
) -> int:
    """Загружает файл на Яндекс Диск по полученной ссылке.

    Args:
        session: Асинхронная HTTP-сессия aiohttp.
        upload_url: URL для загрузки файла.
        file_data: Бинарные данные файла.

    Returns:
        HTTP-статус ответа от Яндекс.Диска.
    """
    async with session.put(upload_url, data=file_data) as response:
        return response.status


async def get_download_link(
    session: aiohttp.ClientSession, filename: str
) -> str:
    """Получает ссылку для скачивания файла с Яндекс Диска.

    Args:
        session: Асинхронная HTTP-сессия aiohttp.
        filename: Имя файла для скачивания.

    Returns:
        URL для скачивания файла.
    """
    headers = {'Authorization': f'OAuth {DISK_TOKEN}'}
    params = {'path': f'/{filename}'}
    async with session.get(
        DOWNLOAD_LINK_URL, headers=headers, params=params
    ) as response:
        data: dict[str, Any] = await response.json()
        return data['href']


async def process_file(
    session: aiohttp.ClientSession, file_storage: FileStorage
) -> dict[str, str]:
    """Загружает файл на Я.Диск и создаёт короткую ссылку.

    Args:
        session: Асинхронная HTTP-сессия aiohttp.
        file_storage: Объект загруженного файла из Flask.

    Returns:
        Словарь с именем файла, короткой ссылкой и ID.
    """
    filename = file_storage.filename
    file_data = file_storage.read()

    upload_href, upload_method = await get_upload_link(session, filename)
    await upload_file(session, upload_href, file_data)
    download_href = await get_download_link(session, filename)

    short_id = get_unique_short_id()
    url_map = URLMap(original=download_href, short=short_id)
    db.session.add(url_map)
    db.session.commit()

    return {
        'filename': filename,
        'short_link': f'{BASE_URL}/{short_id}',
        'short_id': short_id,
    }


async def upload_all_files(
    files: list[FileStorage],
) -> list[dict[str, str]]:
    """Загружает все файлы на Яндекс Диск асинхронно.

    Args:
        files: Список объектов загруженных файлов.

    Returns:
        Список словарей с информацией о каждом загруженном файле.
    """
    async with aiohttp.ClientSession() as session:
        tasks = [process_file(session, f) for f in files]
        results: list[dict[str, str]] = await asyncio.gather(*tasks)
        return results


def upload_files_to_yadisk(
    files: list[FileStorage],
) -> list[dict[str, str]]:
    """Синхронная обёртка для асинхронной загрузки файлов.

    Создаёт новый цикл событий и запускает асинхронную загрузку
    всех переданных файлов на Яндекс.Диск.

    Args:
        files: Список объектов загруженных файлов.

    Returns:
        Список словарей с информацией о каждом загруженном файле.
    """
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        results = loop.run_until_complete(upload_all_files(files))
        return results
    finally:
        loop.close()