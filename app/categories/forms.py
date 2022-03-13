from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from wtforms.widgets import TextArea


class CategoryForm(FlaskForm):
    name = StringField("Name Breed", validators=[DataRequired()])
    wool = StringField("Wool length")
    about = StringField("About", widget=TextArea())
    origin = StringField("Origin")
    submit = SubmitField("Submit")
