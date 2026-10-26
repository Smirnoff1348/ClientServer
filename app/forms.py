from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField
from wtforms.validators import DataRequired, Email, NumberRange, Length


class StudentForm(FlaskForm):
    id = StringField("ID студента", validators=[DataRequired(), Length(max=32)])
    fullName = StringField("ФИО", validators=[DataRequired(), Length(max=150)])
    email = StringField("Email", validators=[DataRequired(), Email()])
    year = IntegerField("Курс", validators=[DataRequired(), NumberRange(1, 6)])
    submit = SubmitField("Сохранить")


class CourseForm(FlaskForm):
    id = StringField("Код курса", validators=[DataRequired(), Length(max=16)])
    title = StringField("Название", validators=[DataRequired(), Length(max=150)])
    credits = IntegerField("Кредиты", validators=[DataRequired(), NumberRange(1, 30)])
    capacity = IntegerField("Мест", validators=[DataRequired(), NumberRange(1, 500)])
    submit = SubmitField("Сохранить")


class EnrollForm(FlaskForm):
    courseId = StringField("Код курса", validators=[DataRequired()])
    submit = SubmitField("Записать")