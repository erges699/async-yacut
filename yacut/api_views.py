"""API-представления для приложения Yacut.

Предоставляет REST API для создания коротких ссылок
и получения оригинальных URL по короткому идентификатору.
"""

from flask import jsonify, request
from flask.typing import ResponseReturnValue

from . import app
from .models import db, URLMap
from .utils import (
    get_unique_short_id,
    is_url_valid,
    validate_custom_id,
)


@app.route('/api/id/', methods=['POST'])
def api_create_id() -> ResponseReturnValue:
    """Создаёт новую короткую ссылку через API.

    Ожидает JSON-тело запроса с полями:
        - url (str, обязательное): оригинальный URL.
        - custom_id (str, опциональное): желаемый короткий ID.

    Returns:
        JSON-ответ с оригинальным URL и короткой ссылкой (статус 201)
        или сообщением об ошибке (статус 400).
    """
    data = request.get_json(silent=True)
    if data is None:
        return jsonify({'message': 'Отсутствует тело запроса'}), 400

    url = data.get('url')
    if not isinstance(url, str) or not url.strip():
        return jsonify(
            {'message': '"url" является обязательным полем!'}
        ), 400
    url = url.strip()

    if not is_url_valid(url):
        return jsonify(
            {'message': 'Поле "url" должно содержать корректный URL.'}
        ), 400

    custom_id = data.get('custom_id')
    if isinstance(custom_id, str):
        custom_id = custom_id.strip()
    else:
        custom_id = ''

    if custom_id:
        error_message = validate_custom_id(custom_id)
        if error_message:
            return jsonify({'message': error_message}), 400

        url_map = URLMap(original=url, short=custom_id)
        db.session.add(url_map)
        db.session.commit()
        short_id = custom_id
    else:
        short_id = get_unique_short_id()
        url_map = URLMap(original=url, short=short_id)
        db.session.add(url_map)
        db.session.commit()

    base_url = app.config.get('BASE_URL', 'http://localhost')
    return jsonify({
        'url': url,
        'short_link': f'{base_url}/{short_id}'
    }), 201


@app.route('/api/id/<short_id>/')
def api_get_url(short_id: str) -> ResponseReturnValue:
    """Возвращает оригинальный URL по короткому идентификатору.

    Args:
        short_id: Короткий идентификатор ссылки.

    Returns:
        JSON-ответ с оригинальным URL (статус 200)
        или сообщением об ошибке (статус 404).
    """
    url_map = URLMap.query.filter_by(short=short_id).first()
    if url_map is None:
        return jsonify({'message': 'Указанный id не найден'}), 404
    return jsonify({'url': url_map.original}), 200