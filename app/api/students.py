from flask import Blueprint, request, jsonify
from app.models import storage, Student
from app.utils import apply_query

bp = Blueprint("students_api", __name__)


def _err(t, m, c):
    return jsonify({"type": t, "message": m, "data": {}}), c


@bp.route("/students", methods=["GET"])
def list_students():
    items = apply_query(storage.list_students(), request.args,
                        string_fields=("id", "fullName", "email"),
                        numeric_fields=("year",))
    return jsonify([s.to_dict() for s in items])


@bp.route("/students", methods=["POST"])
def create_student():
    d = request.get_json(silent=True) or {}
    for r in ("id", "fullName", "email", "year"):
        if r not in d or d[r] in (None, ""):
            return _err("validation", f'Field "{r}" is required', 400)
    try:
        year = int(d["year"])
        if not 1 <= year <= 6:
            raise ValueError
    except (TypeError, ValueError):
        return _err("validation", "year must be integer in [1..6]", 400)
    try:
        s = Student(d["id"], d["fullName"], d["email"], year)
        storage.add_student(s)
    except ValueError as e:
        return _err("conflict", str(e), 409)
    return jsonify(s.to_dict()), 201


@bp.route("/students/<sid>", methods=["GET"])
def get_student(sid):
    s = storage.get_student(sid)
    if not s:
        return _err("not_found", "Student not found", 404)
    return jsonify(s.to_dict())


@bp.route("/students/<sid>", methods=["PATCH"])
def patch_student(sid):
    s = storage.get_student(sid)
    if not s:
        return _err("not_found", "Student not found", 404)
    d = request.get_json(silent=True) or {}
    if not d:
        return _err("validation", "Empty patch", 400)
    d.pop("id", None)
    d.pop("enrolledOn", None)
    if "year" in d:
        try:
            y = int(d["year"])
            if not 1 <= y <= 6:
                raise ValueError
            d["year"] = y
        except (TypeError, ValueError):
            return _err("validation", "year must be integer in [1..6]", 400)
    return jsonify(storage.update_student(sid, d).to_dict())


@bp.route("/students/<sid>", methods=["DELETE"])
def delete_student(sid):
    if not storage.delete_student(sid):
        return _err("not_found", "Student not found", 404)
    return "", 204


@bp.route("/students/<sid>/status")
def student_status(sid):
    s = storage.get_student(sid)
    if not s:
        return _err("not_found", "Student not found", 404)
    return jsonify(s.status())


@bp.route("/students/<sid>/courses/<cid>", methods=["POST"])
def enroll(sid, cid):
    try:
        storage.enroll(sid, cid)
    except LookupError:
        return _err("not_found", "Student or course not found", 404)
    except (ValueError, RuntimeError) as e:
        return _err("conflict", str(e), 409)
    return "", 204


@bp.route("/students/<sid>/courses/<cid>", methods=["DELETE"])
def drop(sid, cid):
    try:
        storage.drop(sid, cid)
    except LookupError:
        return _err("not_found", "Student or course not found", 404)
    except ValueError as e:
        return _err("conflict", str(e), 409)
    return "", 204