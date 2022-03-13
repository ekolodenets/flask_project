from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import DataRequired, EqualTo
from flask_wtf.file import FileField


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField("Submit")


class UserForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    name = StringField("Your Name", validators=[DataRequired()])
    email = StringField("Your Email", validators=[DataRequired()])
    password_hash = PasswordField('Password', validators=[DataRequired(),
                                                          EqualTo('password_hash2', message='Passwords Must Match!')])
    password_hash2 = PasswordField('Confirm', validators=[DataRequired()])
    profile_pic = FileField('Profile Picture')
    submit = SubmitField("Sign Up")


class PasswordForm(FlaskForm):
    email = StringField("What's Your Email", validators=[DataRequired()])
    password_hash = PasswordField("What's Your Password", validators=[DataRequired()])
    submit = SubmitField("Submit")


class NamerForm(FlaskForm):
    name = StringField("What's Your Name", validators=[DataRequired()])
    submit = SubmitField("Submit")