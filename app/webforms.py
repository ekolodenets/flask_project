from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField, validators, PasswordField, BooleanField, ValidationError
from wtforms.validators import DataRequired, EqualTo, Length
from wtforms.widgets import TextArea

#Create login from
class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Submit')

class CatForm(FlaskForm):
    category = StringField('Category', validators=[DataRequired()])
    age = IntegerField('Age', validators=[DataRequired()])
    price = IntegerField('Price', validators=[DataRequired()])
    city = StringField('City', validators=[DataRequired()])
    contact = StringField('Contact', validators=[DataRequired()])
    info = StringField('Info', validators=[DataRequired()], widget=TextArea())
    submit = SubmitField('Submit')
#
# class PostForm(FlaskForm):
#     title = StringField('Title', validators=[DataRequired()])
#     author = StringField('Author', validators=[DataRequired()])
#     content = StringField('Content', validators=[DataRequired()], widget=TextArea())
#     submit = SubmitField('Submit')

class UserForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    name = StringField("Name", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired()])
    favourite_color = StringField('Favourite Color')
    password_hash = PasswordField('Password', validators=[DataRequired(), EqualTo('password_hash2', message='Passwords Must Match!')])
    password_hash2 = PasswordField('Confirm Password', validators=[DataRequired()])
    submit = SubmitField('Submit')

class PasswordForm(FlaskForm):
    email = StringField("What's Your Email", validators=[DataRequired()])
    password_hash = PasswordField("What's Your Password", validators=[DataRequired()])
    submit = SubmitField('Submit')

class NamerForm(FlaskForm):
    name = StringField("What's Your Name", validators=[DataRequired()])
    submit = SubmitField('Submit')

class CategoryForm(FlaskForm):
    name = StringField("Add new breed", validators=[DataRequired()])
    submit = SubmitField('Submit')