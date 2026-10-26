from flask import Blueprint, request, jsonify
from app.models import storage, Course
from app.utils import apply_query

bp = Blueprint("courses_api", __name__)


def _err(t, m, c):
    return jsonify({"type": t, "message": m, "data": {}}), c


@bp.route("/courses", methods=["GET"])
def list_courses():
    items = apply_query(storage.list_courses(), request.args,
                        string_fields=("id", "title"),
                        numeric_fields=("credits", "capacity"))
    return jsonify([c.to_dict() for c in items])


@bp.route("/courses", methods=["POST"])
def create_course():
    d = request.get_json(silent=True) or {}
    for r in ("id", "title", "credits", "capacity"):
        if r not in d or d[r] in (None, ""):
            return _err("validation", f'Field "{r}" is required', 400)
    try:
        credits, cap = int(d["credits"]), int(d["capacity"])
        if credits <= 0 or cap <= 0:
            raise ValueError
    except (TypeError, ValueError):
        return _err("validation", "credits/capacity must be positive integers", 400)
    try:
        c = Course(d["id"], d["title"], credits, cap)
        storage.add_course(c)
    except ValueError as e:
        return _err("conflict", str(e), 409)
    return jsonify(c.to_dict()), 201


@bp.route("/courses/<cid>", methods=["GET"])
def get_course(cid):
    c = storage.get_course(cid)
    if not c:
        return _err("not_found", "Course not found", 404)
    return jsonify(c.to_dict())


@bp.route("/courses/<cid>", methods=["PATCH"])
def patch_course(cid):
    if not storage.get_course(cid):
        return _err("not_found", "Course not found", 404)
    d = request.get_json(silent=True) or {}
    if not d:
        return _err("validation", "Empty patch", 400)
    d.pop("id", None)
    for f in ("credits", "capacity"):
        if f in d:
            try:
                v = int(d[f])
                if v <= 0:
                    raise ValueError
                d[f] = v
            except (TypeError, ValueError):
                return _err("validation", f"{f} must be positive integer", 400)
    return jsonify(storage.update_course(cid, d).to_dict())


@bp.route("/courses/<cid>", methods=["DELETE"])
def delete_course(cid):
    if not storage.delete_course(cid):
        return _err("not_found", "Course not found", 404)
    return "", 204


@bp.route("/courses/<cid>/status")
def course_status(cid):
    c = storage.get_course(cid)
    if not c:
        return _err("not_found", "Course not found", 404)
    return jsonify(c.status())