from flask import jsonify, render_template


def register_errorhandlers(app):
    """Регистрирует обработчики ошибок для UI и API."""

    @app.errorhandler(404)
    def page_not_found(error):
        return render_template('404.html'), 404

    @app.errorhandler(500)
    def internal_error(error):
        return render_template('500.html'), 500

    @app.errorhandler(404)
    def api_not_found(error):
        return jsonify({'message': 'Запрашиваемый ресурс не найден'}), 404

    @app.errorhandler(500)
    def api_internal_error(error):
        return jsonify(
            {'message': 'Внутренняя ошибка сервера'}
        ), 500