from flask import Flask, redirect, url_for
from config import Config


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    from app.views.students import bp as ui_students
    from app.views.courses import bp as ui_courses

    app.register_blueprint(ui_students)
    app.register_blueprint(ui_courses)

    from app.errors import register_error_handlers
    register_error_handlers(app)

    @app.route("/")
    def index():
        return redirect(url_for("students_ui.list_students"))

    return app