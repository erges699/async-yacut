from flask_wtf import FlaskForm
from flask_wtf.file import FileRequired, MultipleFileField
from wtforms import StringField
from wtforms.validators import DataRequired, Length, Regexp


class URLMapForm(FlaskForm):
    original_link = StringField(
        'Длинная ссылка',
        validators=[
            DataRequired(
                message='Обязательное поле "Длинная ссылка" не заполнено.'
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
    files = MultipleFileField(
        'Файлы',
        validators=[
            FileRequired(message='Не выбраны файлы для загрузки.'),
        ],
    )