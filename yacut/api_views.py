from flask import Blueprint, current_app, jsonify, request

from yacut.extensions import db
from yacut.models import URLMap
from yacut.utils import get_unique_short_id, is_short_id_valid

RESERVED_SHORT_IDS = {'files'}

api = Blueprint('api', __name__)


@api.route('/api/id/', methods=['POST'])
def api_create_id():
    data = request.get_json(silent=True)
    if data is None:
        return jsonify({'message': 'Отсутствует тело запроса'}), 400

    url = data.get('url', '').strip()
    if not url:
        return jsonify(
            {'message': '"url" является обязательным полем!'}
        ), 400

    custom_id = data.get('custom_id', '').strip()
    if not custom_id:
        custom_id = ''

    if custom_id:
        if len(custom_id) > 16 or not is_short_id_valid(custom_id):
            return jsonify(
                {'message': 'Указано недопустимое имя для короткой '
                            'ссылки'}
            ), 400

        if custom_id in RESERVED_SHORT_IDS or URLMap.query.filter_by(
            short=custom_id
        ).first() is not None:
            return jsonify(
                {'message': 'Предложенный вариант короткой ссылки уже '
                            'существует.'}
            ), 400

        url_map = URLMap(original=url, short=custom_id)
        db.session.add(url_map)
        db.session.commit()
        short_id = custom_id
    else:
        short_id = get_unique_short_id()
        url_map = URLMap(original=url, short=short_id)
        db.session.add(url_map)
        db.session.commit()

    base_url = current_app.config.get('BASE_URL', 'http://localhost')
    return jsonify({
        'url': url,
        'short_link': f'{base_url}/{short_id}'
    }), 201


@api.route('/api/id/<short_id>/')
def api_get_url(short_id):
    url_map = URLMap.query.filter_by(short=short_id).first()
    if url_map is None:
        return jsonify({'message': 'Указанный id не найден'}), 404
    return jsonify({'url': url_map.original}), 200