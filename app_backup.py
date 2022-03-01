from flask import Flask, flash, request, jsonify, render_template, request, url_for, flash, redirect, abort
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField, validators, PasswordField, BooleanField, ValidationError
from wtforms.validators import DataRequired, EqualTo, Length
from wtforms.widgets import TextArea
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

import sqlite3
import psycopg2
# from config import config

# # export FLASK_APP = run.py

# # python -m venv myvenv
# # myvenv\Scripts\activate
# # export FLASK_ENV=development
# # flask run --host="0.0.0.0" --port="5007"
# python run.py
from wtforms.widgets import TextArea

app = Flask(__name__)

# add database
# old QSLite DB
#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
# postgresql DB
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://postgres:password@localhost/flask1'

# secret key
app.config['SECRET_KEY'] = 'adojaio3ijo2i342fsijgsijgdl'
#@ database
db = SQLAlchemy(app)
migrate = Migrate(app, db)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))

#Create login from
class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Submit')

#Create login page
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(username=form.username.data).first()
        if user:
            if check_password_hash(user.password_hash, form.password.data):
                login_user(user)
                flash('Success')
                return redirect(url_for('dashboard'))
            else:
                flash('Wrong password - Try again!')
        else:
            flash('That user does not exist - Try again!')
    return render_template('login.html', form=form)

#Create logout page
@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


#Create dashboard page
@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    form = UserForm()
    id = current_user.id
    name_to_update = Users.query.get_or_404(id)
    if request.method == 'POST':
        name_to_update.name = request.form['name']
        name_to_update.email = request.form['email']
        name_to_update.favourite_color = request.form['favourite_color']
        name_to_update.username = request.form['username']
        try:
            db.session.commit()
            flash('User updated successfully')
            return render_template('dashboard.html', form=form, name_to_update=name_to_update, id=id)
        except:
            flash('User updated successfully')
            return render_template('dashboard.html', form=form, name_to_update=name_to_update)
    else:
        return render_template('dashboard.html', form=form, name_to_update=name_to_update, id=id)

    return render_template('dashboard.html')

#Create model
class Cats(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(255))
    age = db.Column(db.Integer)
    price = db.Column(db.Integer)
    city = db.Column(db.String(20))
    contact = db.Column(db.String(255))
    info = db.Column(db.Text)
    date_posted = db.Column(db.DateTime, default=datetime.utcnow)

class CatForm(FlaskForm):
    category = StringField('Category', validators=[DataRequired()])
    age = IntegerField('Age', validators=[DataRequired()])
    price = IntegerField('Price', validators=[DataRequired()])
    city = StringField('City', validators=[DataRequired()])
    contact = StringField('Contact', validators=[DataRequired()])
    info = StringField('Info', validators=[DataRequired()], widget=TextArea())
    submit = SubmitField('Submit')


@app.route('/cats')
def cats():
    #grab all the cats from the data base
    cats = Cats.query.order_by(Cats.date_posted)
    return render_template('cats.html', cats=cats)


@app.route('/cats/<int:id>')
def cat(id):
    cat = Cats.query.get_or_404(id)
    return render_template('cat.html', cat=cat)


#add Cats page
@app.route('/add-cat', methods=['GET', 'POST'])
def add_cat():
    form = CatForm()

    if form.validate_on_submit():
        post = Cats(category=form.category.data, age=form.age.data, price=form.price.data, city=form.city.data, contact=form.contact.data, info=form.info.data)

        # Clear the form
        form.category.data = ''
        form.age.data = 0
        form.price.data = 0
        form.city.data = ''
        form.contact.data = ''
        form.info.data = ''

        # Add post to DB
        db.session.add(post)
        db.session.commit()

        # Message
        flash('Cat added successfully!')

    # Redirect
    return render_template('add_cat.html', form=form)

#Create model
class Posts(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    author = db.Column(db.String(255))
    content = db.Column(db.Text)
    date_posted = db.Column(db.DateTime, default=datetime.utcnow)

class PostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    author = StringField('Author', validators=[DataRequired()])
    content = StringField('Content', validators=[DataRequired()], widget=TextArea())
    submit = SubmitField('Submit')


@app.route('/cat/edit/<int:id>', methods=['GET', 'POST'])
def edit_cat(id):
    cat = Cats.query.get_or_404(id)
    form = CatForm()
    if form.validate_on_submit():
        cat.category = form.category.data
        cat.age = form.age.data
        cat.price = form.price.data
        cat.city = form.city.data
        cat.contact = form.contact.data
        cat.info = form.info.data

        #update DB
        db.session.add(cat)
        db.session.commit()
        return redirect(url_for('cat', id=cat.id))
    form.category.data = cat.category
    form.age.data = cat.age
    form.price.data = cat.price
    form.city.data = cat.city
    form.contact.data = cat.contact
    form.info.data = cat.info
    return render_template('edit_cat.html', form=form)

@app.route('/cat/delete/<int:id>')
def delete_cat(id):
    cat_to_delete = Cats.query.get_or_404(id)
    try:
        db.session.delete(cat_to_delete)
        db.session.commit()

        flash('Cat was deleted')
        cats = Cats.query.order_by(Cats.date_posted)
        return render_template('cats.html', cats=cats)

    except:
        flash('some problem while deleting')
        cats = Cats.query.order_by(Cats.date_posted)
        return render_template('cats.html', cats=cats)



@app.route('/posts')
def posts():
    posts = Posts.query.order_by(Posts.date_posted)
    return render_template('posts.html', posts=posts)


#add Post page
@app.route('/add-post', methods=['GET', 'POST'])
def add_post():
    form = PostForm()

    if form.validate_on_submit():
        post = Posts(title=form.title.data, author=form.author.data, content=form.content.data)

        # Clear the form
        form.title.data = ''
        form.author.data = ''
        form.content.data = ''

        # Add post to DB
        db.session.add(post)
        db.session.commit()

        # Message
        flash('Post added successfully!')

    # Redirect
    return render_template('add_post.html', form=form)

class Users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    name = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(120), nullable=False, unique=True)
    favourite_color = db.Column(db.String(120))
    date_added = db.Column(db.DateTime, default=datetime.utcnow)

    password_hash = db.Column(db.String(128))
    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')
    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    #create  a string
    def __repr__(self):
        return '<Name %r>' % self.name

@app.route('/delete/<int:id>')
def delete(id):
    name = None
    form = UserForm()
    user_to_delete = Users.query.get_or_404(id)
    try:
        db.session.delete(user_to_delete)
        db.session.commit()
        flash('User deleted successfully')
        flask1 = Users.query.order_by(Users.date_added)
        return render_template('add_user.html', form=form, name=name, flask1=flask1)
    except:
        flash('some problem')
        return render_template('add_user.html', form=form, name=name, flask1=flask1)

# Create Form class
class UserForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    name = StringField("Name", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired()])
    favourite_color = StringField('Favourite Color')
    password_hash = PasswordField('Password', validators=[DataRequired(), EqualTo('password_hash2', message='Passwards Must Match!')])
    password_hash2 = PasswordField('Confirm Password', validators=[DataRequired()])
    submit = SubmitField('Submit')

# Update record
@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update(id):
    form = UserForm()
    name_to_update = Users.query.get_or_404(id)
    if request.method == 'POST':
        name_to_update.name = request.form['name']
        name_to_update.email = request.form['email']
        name_to_update.favourite_color= request.form['favourite_color']
        name_to_update.username = request.form['username']
        try:
            db.session.commit()
            flash('User updated successfully')
            return render_template('update.html', form=form, name_to_update=name_to_update, id=id)
        except:
            flash('User updated successfully')
            return render_template('update.html', form=form, name_to_update=name_to_update)
    else:
        return render_template('update.html', form=form, name_to_update=name_to_update, id=id)

# Create Form class
class PasswordForm(FlaskForm):
    email = StringField("What's Your Email", validators=[DataRequired()])
    password_hash = PasswordField("What's Your Password", validators=[DataRequired()])
    submit = SubmitField('Submit')

class NamerForm(FlaskForm):
    name = StringField("What's Your Name", validators=[DataRequired()])
    submit = SubmitField('Submit')

@app.route('/user/add', methods=['GET', 'POST'])
def add_user():
    name = None
    form = UserForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(email=form.email.data).first()
        if user is None:

            hashed_pw = generate_password_hash(form.password_hash.data, 'sha256')

            user = Users(username=form.username.data, name=form.name.data, email=form.email.data, favourite_color=form.favourite_color.data, password_hash=hashed_pw)
            db.session.add(user)
            db.session.commit()
        name = form.name.data
        form.username.data = ''
        form.name.data =''
        form.email.data =''
        form.favourite_color.data = ''
        form.password_hash.data = ''
        flash('User added successfully!')
    flask1 = Users.query.order_by(Users.date_added)
    return render_template('add_user.html', form=form, name=name, flask1=flask1)


@app.route('/')
def index():
    pizza = ['pepperoni', 'Cheese', 'Beefe', 'Pineapple', 35]
    return render_template('index.html', pizza=pizza)

@app.route('/user/<name>')
def user(name):
    return render_template('user.html', user_name=name)

@app.errorhandler(404)
def page_not_found(e):
    # return "<h1>404</h1><p>C'mon, this page does not exist</p>", 404
    return render_template('404.html'), 404

@app.errorhandler(500)
def page_not_found(e):
    # return "<h1>404</h1><p>C'mon, this page does not exist</p>", 404
    return render_template('500.html'), 500

@app.route('/test_pw', methods=['GET', 'POST'])
def test_pw():
    email = None
    password = None
    pw_to_check = None
    passed = None
    form = PasswordForm()
    #validate form
    if form.validate_on_submit():
        email = form.email.data
        password = form.password_hash.data
        form.email.date = ''
        form.password_hash.data = ''
        #Lookup User by Email address
        pw_to_check = Users.query.filter_by(email=email).first()
        # flash("Form submitted successfully!")
        passed = check_password_hash(pw_to_check.password_hash, password)

    return render_template('test_pw.html', email=email, password=password, pw_to_check=pw_to_check, passed=passed,  form=form)


@app.route('/name', methods=['GET', 'POST'])
def name():
    name = None
    form = NamerForm()
    if form.validate_on_submit():
        name = form.name.data
        form.name.date = ''
        flash("Form submitted successfully!")

    return render_template('name.html', name=name, form=form)



if __name__ == "__main__":
    app.run(host='localhost', port=5000, debug=True)
