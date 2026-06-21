import asyncio
import os

import aiohttp

from yacut.extensions import db
from yacut.models import URLMap
from yacut.utils import get_unique_short_id

DISK_TOKEN = os.getenv('DISK_TOKEN', '')
BASE_URL = os.getenv('BASE_URL', 'http://localhost')
REQUEST_UPLOAD_URL = (
    'https://cloud-api.yandex.net/v1/disk/resources/upload'
)
DOWNLOAD_LINK_URL = (
    'https://cloud-api.yandex.net/v1/disk/resources/download'
)


async def get_upload_link(session, filename):
    """Получает ссылку для загрузки файла на Яндекс Диск."""
    headers = {'Authorization': f'OAuth {DISK_TOKEN}'}
    params = {'path': f'/{filename}', 'overwrite': 'true'}
    async with session.get(
        REQUEST_UPLOAD_URL, headers=headers, params=params
    ) as response:
        data = await response.json()
        return data['href'], data['method']


async def upload_file(session, upload_url, file_data):
    """Загружает файл на Яндекс Диск по полученной ссылке."""
    async with session.put(upload_url, data=file_data) as response:
        return response.status


async def get_download_link(session, filename):
    """Получает ссылку для скачивания файла с Яндекс Диска."""
    headers = {'Authorization': f'OAuth {DISK_TOKEN}'}
    params = {'path': f'/{filename}'}
    async with session.get(
        DOWNLOAD_LINK_URL, headers=headers, params=params
    ) as response:
        data = await response.json()
        return data['href']


async def process_file(session, file_storage):
    """Загружает файл на Я.Диск и создаёт короткую ссылку."""
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


async def upload_all_files(files):
    """Загружает все файлы на Яндекс Диск асинхронно."""
    async with aiohttp.ClientSession() as session:
        tasks = [process_file(session, f) for f in files]
        results = await asyncio.gather(*tasks)
        return results


def upload_files_to_yadisk(files):
    """Синхронная обёртка для асинхронной загрузки файлов."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        results = loop.run_until_complete(upload_all_files(files))
        return results
    finally:
        loop.close()