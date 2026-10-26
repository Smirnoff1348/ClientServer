from flask import (Blueprint, render_template, redirect, url_for, flash,
                   request, abort)
from app.models import storage, Student
from app.forms import StudentForm, EnrollForm
from app.utils import apply_query

bp = Blueprint("students_ui", __name__, url_prefix="/students")


@bp.route("/")
def list_students():
    items = apply_query(storage.list_students(), request.args,
                        string_fields=("id", "fullName", "email"),
                        numeric_fields=("year",))
    return render_template("students/list.html",
                           title="Студенты", students=items, args=request.args)


@bp.route("/new", methods=["GET", "POST"])
def create_student():
    form = StudentForm()
    if form.validate_on_submit():
        try:
            storage.add_student(Student(form.id.data, form.fullName.data,
                                        form.email.data, form.year.data))
            flash("Студент добавлен")
            return redirect(url_for("students_ui.list_students"))
        except ValueError as e:
            flash(str(e))
    return render_template("students/edit.html",
                           title="Новый студент", form=form, student=None)


@bp.route("/<sid>/edit", methods=["GET", "POST"])
def edit_student(sid):
    s = storage.get_student(sid)
    if not s:
        abort(404)
    form = StudentForm(obj=s)
    if form.validate_on_submit():
        storage.update_student(sid, {
            "fullName": form.fullName.data,
            "email": form.email.data,
            "year": form.year.data,
        })
        flash("Изменения сохранены")
        return redirect(url_for("students_ui.list_students"))
    return render_template("students/edit.html",
                           title=f"Студент {sid}", form=form, student=s)


@bp.route("/<sid>/delete", methods=["POST"])
def delete_student(sid):
    if not storage.delete_student(sid):
        abort(404)
    flash("Студент помечен как удалённый")
    return redirect(url_for("students_ui.list_students"))


@bp.route("/<sid>/status")
def student_status(sid):
    s = storage.get_student(sid)
    if not s:
        abort(404)
    courses = [storage.get_course(cid) for cid in s.course_ids]
    courses = [c for c in courses if c]
    return render_template("students/status.html",
                           title=f"Статус {sid}",
                           student=s, status=s.status(),
                           courses=courses, form=EnrollForm())


@bp.route("/<sid>/enroll", methods=["POST"])
def enroll(sid):
    form = EnrollForm()
    if not form.validate_on_submit():
        flash("Некорректный код курса")
        return redirect(url_for("students_ui.student_status", sid=sid))
    try:
        storage.enroll(sid, form.courseId.data)
        flash(f"Записан на {form.courseId.data}")
    except LookupError:
        flash("Студент или курс не найден")
    except (ValueError, RuntimeError) as e:
        flash(str(e))
    return redirect(url_for("students_ui.student_status", sid=sid))


@bp.route("/<sid>/drop/<cid>", methods=["POST"])
def drop(sid, cid):
    try:
        storage.drop(sid, cid)
        flash(f"Отчислен с {cid}")
    except LookupError:
        flash("Не найдено")
    except ValueError as e:
        flash(str(e))
    return redirect(url_for("students_ui.student_status", sid=sid))