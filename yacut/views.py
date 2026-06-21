from flask import (
    Blueprint, abort, flash, redirect, render_template,
)

from yacut.extensions import db
from yacut.forms import FileUploadForm, URLMapForm
from yacut.models import URLMap
from yacut.utils import get_unique_short_id
from yacut.yandex_disk import upload_files_to_yadisk

RESERVED_SHORT_IDS = {'files'}

bp = Blueprint('yacut', __name__)


@bp.route('/', methods=['GET', 'POST'])
def index_view():
    form = URLMapForm()
    short_link = None

    if form.validate_on_submit():
        original = form.original_link.data.strip()
        custom_id = form.custom_id.data.strip() if form.custom_id.data else ''

        if custom_id:
            if custom_id in RESERVED_SHORT_IDS or URLMap.query.filter_by(
                short=custom_id
            ).first() is not None:
                flash(
                    'Предложенный вариант короткой ссылки уже существует.'
                )
                return render_template('index.html', form=form,
                                       short_link=None)

            url_map = URLMap(original=original, short=custom_id)
            db.session.add(url_map)
            db.session.commit()
            short_link = custom_id
        else:
            short_id = get_unique_short_id()
            url_map = URLMap(original=original, short=short_id)
            db.session.add(url_map)
            db.session.commit()
            short_link = short_id

    return render_template('index.html', form=form, short_link=short_link)


@bp.route('/files', methods=['GET', 'POST'])
def files_view():
    form = FileUploadForm()
    uploaded_files = []

    if form.validate_on_submit():
        files = form.files.data
        uploaded_files = upload_files_to_yadisk(files)

    return render_template('files.html', form=form,
                           uploaded_files=uploaded_files)


@bp.route('/<short_id>')
def redirect_to_original(short_id):
    url_map = URLMap.query.filter_by(short=short_id).first()
    if url_map is None:
        abort(404)
    return redirect(url_map.original)