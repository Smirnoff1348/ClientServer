from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from app.models import storage, Course
from app.forms import CourseForm
from app.utils import apply_query

bp = Blueprint("courses_ui", __name__, url_prefix="/courses")


@bp.route("/")
def list_courses():
    items = apply_query(storage.list_courses(), request.args,
                        string_fields=("id", "title"),
                        numeric_fields=("credits", "capacity"))
    return render_template("courses/list.html",
                           title="Курсы", courses=items, args=request.args)


@bp.route("/new", methods=["GET", "POST"])
def create_course():
    form = CourseForm()
    if form.validate_on_submit():
        try:
            storage.add_course(Course(form.id.data, form.title.data,
                                      form.credits.data, form.capacity.data))
            flash("Курс добавлен")
            return redirect(url_for("courses_ui.list_courses"))
        except ValueError as e:
            flash(str(e))
    return render_template("courses/edit.html",
                           title="Новый курс", form=form, course=None)


@bp.route("/<cid>/edit", methods=["GET", "POST"])
def edit_course(cid):
    c = storage.get_course(cid)
    if not c:
        abort(404)
    form = CourseForm(obj=c)
    if form.validate_on_submit():
        storage.update_course(cid, {
            "title": form.title.data,
            "credits": form.credits.data,
            "capacity": form.capacity.data,
        })
        flash("Изменения сохранены")
        return redirect(url_for("courses_ui.list_courses"))
    return render_template("courses/edit.html",
                           title=f"Курс {cid}", form=form, course=c)


@bp.route("/<cid>/delete", methods=["POST"])
def delete_course(cid):
    if not storage.delete_course(cid):
        abort(404)
    flash("Курс помечен как удалённый")
    return redirect(url_for("courses_ui.list_courses"))