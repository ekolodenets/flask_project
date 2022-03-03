from flask import Flask, render_template, request, url_for, flash, redirect
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import uuid as uuid
import os
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField, validators, PasswordField, BooleanField, ValidationError
from wtforms.validators import DataRequired, EqualTo, Length
from wtforms.widgets import TextArea
from flask_wtf.file import FileField, FileRequired
from wtforms_sqlalchemy.fields import QuerySelectField
from sqlalchemy import desc

app = Flask(__name__)

# add database
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
# postgresql DB
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql+psycopg2://postgres:password@localhost/flask1"

# secret key
app.config['SECRET_KEY'] = "adojaios3ijs2i342f3423ghfgf4145sijgsij63634613613cvbxdg16176s8ssdhs37695fb9dl"
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
UPLOAD_FOLDER = "static/images/"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


db = SQLAlchemy(app)
migrate = Migrate(app, db)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))

#pass search to navbar
@app.context_processor
def base():
    form = SearchForm()
    return dict(form=form)

#search
# @app.route("/search", methods=['POST'])
# def search():
#     form = SearchForm()
#     cats = Cats.query
#     if form.validate_on_submit():
#         cat.searched = form.searched.data
#
#         cats = cats.filter(Cats.category.like('%' + cat.searched + '%'))
#         cats = cats.order_by(Cats.date_posted).all()
#
#         return render_template("search.html", form=form, searched=cat.searched, cats=cats)

'''ADMINISTRATION BLOCK'''

# Admin Page
@app.route("/admin")
@login_required
def admin():
    id = current_user.id
    if id == 5:
        return render_template('admin.html')
    else:
        flash("Sorry, you are not the Admin")
        return redirect(url_for("dashboard"))


# Create login page
@app.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        post = Users.query.filter_by(username=form.username.data).first()
        if post:
            if check_password_hash(post.password_hash, form.password.data):
                login_user(post)
                flash("Successfuly Logged In")
                return redirect(url_for("dashboard"))
            else:
                flash("Wrong password - Try again!")
        else:
            flash("That User Does Not Exist - Try again!")
    return render_template("login.html", form=form)


# Create logout page
@app.route("/logout", methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for("index"))

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


# # Create dashboard page
@app.route("/dashboard", methods=['GET', 'POST'])
@login_required
def dashboard():
    form = UserForm()
    id = current_user.id
    name_to_update = Users.query.get_or_404(id)
    if request.method == "POST":
        name_to_update.name = request.form["name"]
        name_to_update.email = request.form["email"]
        # name_to_update.favourite_color = request.form["favourite_color"]
        name_to_update.username = request.form["username"]
        #check for profile_pic
        if request.files["profile_pic"] and allowed_file(request.files["profile_pic"].filename):
            name_to_update.profile_pic = request.files["profile_pic"]

            #grab image name
            pic_filename = secure_filename(name_to_update.profile_pic.filename)
            #set UUID
            pic_name = str(uuid.uuid1()) + "_" + pic_filename
            #save that image
            saver = request.files["profile_pic"]
            #change it to a string to save to db
            name_to_update.profile_pic = pic_name
            try:
                db.session.commit()
                saver.save(os.path.join(app.config['UPLOAD_FOLDER'], pic_name))

                flash("User updated successfully")
                return render_template("dashboard.html", form=form, name_to_update=name_to_update, id=id)
            except:
                flash("User updated successfully")
                return render_template("dashboard.html", form=form, name_to_update=name_to_update)
        else:
            db.session.commit()
            flash("User updated successfully")
            return render_template("dashboard.html", form=form, name_to_update=name_to_update, id=id)

    else:
        return render_template("dashboard.html", form=form, name_to_update=name_to_update, id=id)

'''END ADMINISTRATION BLOCK'''



'''USER BLOCK'''

# Add User
@app.route('/user/add', methods=['GET', 'POST'])
def add_user():
    name = None
    form = UserForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(email=form.email.data).first()
        if user is None:
            hashed_pw = generate_password_hash(form.password_hash.data, 'sha256')
            user = Users(username=form.username.data, name=form.name.data, email=form.email.data, password_hash=hashed_pw)
            db.session.add(user)
            db.session.commit()
        # name = form.name.data
        form.username.data = ''
        form.name.data = ''
        form.email.data = ''
        # form.favourite_color.data = ''
        form.password_hash.data = ''
        flash("User added successfully!")
        return redirect(url_for("login"))
    flask1 = Users.query.order_by(desc(Users.date_added))
    return render_template("add_user.html", form=form, name=name, flask1=flask1)


# Update User
@app.route('/update/<int:id>', methods=['GET', 'POST'])
@login_required
def update(id):
    form = UserForm()
    name_to_update = Users.query.get_or_404(id)
    if request.method == 'POST':
        name_to_update.name = request.form['name']
        name_to_update.email = request.form['email']
        # name_to_update.favourite_color = request.form['favourite_color']
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


# Delete User
@app.route('/delete/<int:id>')
@login_required
def delete(id):
    if id == current_user.id:
        name = None
        form = UserForm()
        user_to_delete = Users.query.get_or_404(id)
        try:
            db.session.delete(user_to_delete)
            db.session.commit()
            flash("User Deleted Successfully. Say 'Good Bye To Him'")
            flask1 = Users.query.order_by(Users.date_added)
            return render_template("add_user.html", form=form, name=name, flask1=flask1)
        except:
            flash("We Have Some Problems Here While Deleting User")
            return render_template("add_user.html")
    else:
        flash("Sorry You Can't Delete This User")
        return redirect(url_for("dashboard"))

'''END USER BLOCK'''






'''CAT BLOCK'''

# Add Cats
@app.route("/add_cat", methods=['GET', 'POST'])
@login_required
def add_cat():
    form = CatForm()
    if form.validate_on_submit():
        poster_id = current_user.id
        if request.files["cat_pic"] and allowed_file(request.files["cat_pic"].filename):
            cat_pic = request.files["cat_pic"]
            # pic_filename = secure_filename(cat_pic.filename)
            cat_pic = datetime.now().strftime('%Y_%m_%d_%H_%M_%S_%f_') + str(uuid.uuid1()) + '.jpeg'
            saver = request.files["cat_pic"]
            saver.save(os.path.join(app.config['UPLOAD_FOLDER'], cat_pic))
            post = Cats(category=form.category.data, age=form.age.data,
                        price=form.price.data, city=form.city.data,
                        contact=form.contact.data, info=form.info.data,
                        poster_id=poster_id, cat_pic=cat_pic)

            # Clear the form
            # form.category.data = ''
            # form.age.data = ''
            # form.price.data = ''
            # form.city.data = ''
            # form.contact.data = ''
            # form.info.data = ''

            # Add post to DB
            db.session.add(post)
            db.session.commit()

            # Message
            flash("Cat added successfully!")
            return redirect(url_for("cats"))
    # Redirect
    return render_template("add_cat.html", form=form)


# Edit Cat
@app.route("/cat/edit/<int:id>", methods=['GET', 'POST'])
@login_required
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

        # update DB
        db.session.add(cat)
        db.session.commit()
        return redirect(url_for("cat", id=cat.id))

    if current_user.id == cat.poster_id:
        form.category.data = cat.category
        form.age.data = cat.age
        form.price.data = cat.price
        form.city.data = cat.city
        form.contact.data = cat.contact
        form.info.data = cat.info
        return render_template("edit_cat.html", form=form)
    else:
        flash("You Aren't Authorized To Edit This")
        cats = Cats.query.order_by(Cats.date_posted)
        return render_template("cats.html", cats=cats)


# Delete Cat
@app.route("/cat/delete/<int:id>")
@login_required
def delete_cat(id):
    cat_to_delete = Cats.query.get_or_404(id)
    id = current_user.id
    if id == cat_to_delete.poster.id or id == 5:
        try:
            db.session.delete(cat_to_delete)
            db.session.commit()

            flash("Cat was deleted")
            cats = Cats.query.order_by(Cats.date_posted)
            return render_template("cats.html", cats=cats)

        except:
            flash('Some Problem While Deleting Cat')
            cats = Cats.query.order_by(Cats.date_posted)
            return render_template('cats.html', cats=cats)
    else:
        flash("You Aren't Authorized To Delete That Cat!" )
        cats = Cats.query.order_by(Cats.date_posted)
        return render_template('cats.html', cats=cats)



# List of Cats
@app.route("/cats")
def cats():
    # grab all the cats from the data base
    cats = Cats.query.order_by(desc(Cats.date_posted))
    return render_template("cats.html", cats=cats)


# Cat's Page
@app.route("/cat/<int:id>")
def cat(id):
    cat = Cats.query.get_or_404(id)
    return render_template("cat.html", cat=cat)

'''END CAT BLOCK'''



'''CATEGORY BLOCK'''

# Add Breed
@app.route('/breed/add', methods=['GET', 'POST'])
def add_breed():
    name = None
    wool = ''
    origin = ''
    about = ''
    form = CategoryForm()
    if form.validate_on_submit():
        post = Category.query.filter_by(name=form.name.data).first()
        if post is None:
            post = Category(name=form.name.data, wool=form.wool.data,
                            origin=form.origin.data, about=form.about.data)
            db.session.add(post)
            db.session.commit()
        name = form.name.data
        wool = form.wool.data
        origin = form.origin.data
        about = form.about.data
        form.name.data = ''
        form.wool.data = ''
        form.origin.data = ''
        form.about.data = ''
        flash('User added successfully!')
        return redirect(url_for("breeds"))
    category = Category.query.order_by(Category.name)
    return render_template('add_breed.html', form=form, name=name, wool=wool, origin=origin, about=about, category=category)


# Edit category(Breed)
@app.route("/category/edit/<int:id>", methods=['GET', 'POST'])
@login_required
def edit_category(id):
    category = Category.query.get_or_404(id)
    form = CategoryForm()
    if form.validate_on_submit():
        category.name = form.name.data
        category.wool = form.wool.data
        category.origin = form.origin.data

        # update DB
        db.session.add(category)
        db.session.commit()
        return redirect(url_for("breeds", id=category.id))

    form.name.data = category.name
    form.wool.data = category.wool
    form.origin.data = category.origin

    return render_template("edit_breed.html", form=form)


# List of Breeds
@app.route('/breeds', methods=['GET', 'POST'])
def breeds():
    category = Category.query.order_by(Category.name)
    return render_template('breeds.html', category=category)

'''END CATEGORY BLOCK'''



# INDEX PAGE
@app.route("/")
def index():
    pizza = ['pepperoni', 'Cheese', 'Beefe', 'Pineapple', 35]
    return render_template('index.html', pizza=pizza)


@app.route("/user/<name>")
def user(name):
    return render_template("user.html", user_name=name)


@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404


@app.errorhandler(500)
def page_not_found(e):
    return render_template("500.html"), 500

# NAME PAGE
@app.route("/name", methods=['GET', 'POST'])
def name():
    name = None
    form = NamerForm()
    if form.validate_on_submit():
        name = form.name.data
        form.name.date = ''
        flash("Form Submitted Successfully!")

    return render_template("name.html", name=name, form=form)



'''FORMS'''

class SearchForm(FlaskForm):
    searched = StringField('searched', validators=[DataRequired()])
    submit = SubmitField("Submit")


#Create login from
class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField("Submit")


def enabled_categories():
    return Category.query.order_by(Category.name).all()


class CatForm(FlaskForm):
    age = IntegerField('Age', validators=[DataRequired()])
    price = IntegerField('Price', validators=[DataRequired()])
    city = StringField('City', validators=[DataRequired()])
    contact = StringField('Contact', validators=[DataRequired()])
    info = StringField('Info', validators=[DataRequired()], widget=TextArea())
    submit = SubmitField("Submit")
    category = QuerySelectField(query_factory=enabled_categories, validators=[DataRequired()],
                                allow_blank=False)
    cat_pic = FileField('Profile Picture')


class UserForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    name = StringField("Name", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired()])
    password_hash = PasswordField('Password', validators=[DataRequired(), EqualTo('password_hash2', message='Passwords Must Match!')])
    password_hash2 = PasswordField('Confirm Password', validators=[DataRequired()])
    profile_pic = FileField('Profile Picture')
    submit = SubmitField("Submit")


class PasswordForm(FlaskForm):
    email = StringField("What's Your Email", validators=[DataRequired()])
    password_hash = PasswordField("What's Your Password", validators=[DataRequired()])
    submit = SubmitField("Submit")


class NamerForm(FlaskForm):
    name = StringField("What's Your Name", validators=[DataRequired()])
    submit = SubmitField("Submit")


class CategoryForm(FlaskForm):
    name = StringField("Name Breed", validators=[DataRequired()])
    wool = StringField("Wool length")
    about = StringField("About", widget=TextArea())
    origin = StringField("Origin")
    submit = SubmitField("Submit")
'''END FORMS'''


'''MODELS'''

# Create model
class Cats(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # category = db.Column(db.String(255))
    age = db.Column(db.Integer)
    price = db.Column(db.Integer)
    city = db.Column(db.String(20))
    contact = db.Column(db.String(255))
    info = db.Column(db.Text)
    date_posted = db.Column(db.DateTime, default=datetime.utcnow)
    # ForeignKey to link users
    poster_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))
    category = db.relationship('Category', backref=db.backref('cats', lazy='dynamic'))
    cat_pic = db.Column(db.String(), nullable=True)

    # def __init__(self, category):
    #     self.category = category

    def __repr__(self):
        return '<Cats %r>' % self.contact


class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False, unique=True)
    wool = db.Column(db.String(50))
    origin = db.Column(db.String(50))
    about = db.Column(db.Text)

    def __init__(self, name, wool, origin, about):
        self.name = name
        self.wool = wool
        self.origin = origin
        self.about = about

    def __repr__(self):
        return self.name


class Users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    name = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(120), nullable=False, unique=True)
    # favourite_color = db.Column(db.String(120))
    date_added = db.Column(db.DateTime, default=datetime.utcnow)
    password_hash = db.Column(db.String(128))
    profile_pic = db.Column(db.String(), nullable=True)
    # user can have many Cats
    cats = db.relationship('Cats', backref='poster')

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    # create  a string
    def __repr__(self):
        return '<Name %r>' % self.name
'''END MODELS'''


if __name__ == "__main__":
    app.run(host="localhost", port=5000, debug=True)
