from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField
from wtforms.validators import DataRequired
from wtforms.widgets import TextArea
from flask_wtf.file import FileField
from wtforms_sqlalchemy.fields import QuerySelectField
from app.models import Category


def enabled_categories():
    return Category.query.order_by(Category.name).all()


class CatForm(FlaskForm):
    age = IntegerField('Months', validators=[DataRequired()])
    price = IntegerField('Price, $')
    city = StringField('City', validators=[DataRequired()])
    contact = StringField('Contact', validators=[DataRequired()])
    info = StringField('Info', widget=TextArea())
    submit = SubmitField("Submit")
    category = QuerySelectField(query_factory=enabled_categories, validators=[DataRequired()],
                                allow_blank=False)
    cat_pic = FileField('Cat Picture')


