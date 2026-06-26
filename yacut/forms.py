"""Формы для веб-интерфейса приложения Yacut.

Определяет формы для создания коротких ссылок
и загрузки файлов на Яндекс.Диск.
"""

from flask_wtf import FlaskForm
from flask_wtf.file import FileRequired, MultipleFileField
from wtforms import StringField
from wtforms.validators import DataRequired, Length, Regexp, URL


class URLMapForm(FlaskForm):
    """Форма для создания короткой ссылки.

    Attributes:
        original_link: Поле для ввода длинной ссылки (обязательное).
        custom_id: Поле для ввода пользовательского короткого ID
            (необязательное, макс. 16 символов, только буквы и цифры).
    """

    original_link = StringField(
        'Длинная ссылка',
        validators=[
            DataRequired(
                message='Обязательное поле "Длинная ссылка" не заполнено.'
            ),
            URL(
                message='Поле "Длинная ссылка" должно содержать URL.'
            ),
        ],
    )
    custom_id = StringField(
        'Ваш вариант короткой ссылки',
        validators=[
            Length(
                max=16,
                message='Указано недопустимое имя для короткой ссылки',
            ),
            Regexp(
                r'^[A-Za-z0-9]*$',
                message='Указано недопустимое имя для короткой ссылки',
            ),
        ],
    )


class FileUploadForm(FlaskForm):
    """Форма для загрузки файлов на Яндекс.Диск.

    Attributes:
        files: Поле для выбора нескольких файлов (обязательное).
    """

    files = MultipleFileField(
        'Файлы',
        validators=[
            FileRequired(message='Не выбраны файлы для загрузки.'),
        ],
    )