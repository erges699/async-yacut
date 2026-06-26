"""Представления веб-интерфейса для приложения Yacut.

Определяет маршруты для главной страницы (создание коротких ссылок),
загрузки файлов на Яндекс.Диск и редиректа по короткому ID.
"""

from flask import abort, flash, redirect, render_template

from . import app
from .models import db, URLMap
from .utils import get_unique_short_id, validate_custom_id
from .forms import FileUploadForm, URLMapForm
from .ya_disk import upload_files_to_yadisk


@app.route('/', methods=['GET', 'POST'])
def index() -> str:
    """Главная страница с формой создания короткой ссылки.

    Returns:
        HTML-шаблон главной страницы.
    """
    form = URLMapForm()
    short_link = None

    if form.validate_on_submit():
        original = form.original_link.data.strip()
        custom_id = form.custom_id.data.strip() if form.custom_id.data else ''

        if custom_id:
            error_message = validate_custom_id(custom_id)
            if error_message:
                flash(error_message)
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


@app.route('/files', methods=['GET', 'POST'])
def files_view() -> str:
    """Страница загрузки файлов на Яндекс.Диск.

    Returns:
        HTML-шаблон страницы загрузки файлов.
    """
    form = FileUploadForm()
    uploaded_files = []

    if form.validate_on_submit():
        files = form.files.data
        uploaded_files = upload_files_to_yadisk(files)

    return render_template('files.html', form=form,
                           uploaded_files=uploaded_files)


@app.route('/<short_id>')
def redirect_to_original(short_id: str):
    """Перенаправляет с короткого ID на оригинальный URL.

    Args:
        short_id: Короткий идентификатор ссылки.

    Returns:
        Редирект на оригинальный URL (статус 302)
        или ошибка 404, если ID не найден.
    """
    url_map = URLMap.query.filter_by(short=short_id).first()
    if url_map is None:
        abort(404)
    return redirect(url_map.original)