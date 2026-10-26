import traceback
from flask import jsonify, current_app, request
from werkzeug.exceptions import HTTPException


def _payload(type_, message, data=None, stack=None):
    body = {"type": type_, "message": message, "data": data or {}}
    if stack and current_app.config.get("DEBUG"):
        body["stack"] = stack
    return body


def register_error_handlers(app):
    @app.errorhandler(HTTPException)
    def http_error(e):
        return jsonify(_payload(e.name.lower().replace(" ", "_"), e.description)), e.code

    @app.errorhandler(Exception)
    def generic_error(e):
        current_app.logger.exception("Unhandled error on %s %s", request.method, request.path)
        return jsonify(_payload("internal_error", "Internal server error",
                                stack=traceback.format_exc())), 500