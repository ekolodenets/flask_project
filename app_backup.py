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
from datetime import datetime, date, time
import string

app = Flask(__name__)

# add database
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
# postgresql DB
app.config[
    "SQLALCHEMY_DATABASE_URI"] = "postgresql://aroxklnqgdwyjo:45e12ea1729c93cbcc740f010aa657cc3ef1acb074c7e4caa3858508e8d73f01@ec2-3-228-222-169.compute-1.amazonaws.com:5432/dcqng4p0da090d"
# app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql+psycopg2://postgres:password@localhost/flask1"

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


# pass search to navbar
@app.context_processor
def base():
    form = SearchForm()
    return dict(form=form)


# search
# @app.route("/search", methods=['POST'])
# def search():
#     form = SearchForm()
#     cats = Cats.query
#     if form.validate_on_submit():
#         cat.searched = form.searched.data
#
#         cats = cats.filter(Cats.categories.like('%' + cat.searched + '%'))
#         cats = cats.order_by(Cats.date_posted).all()
#
#         return render_template("search.html", form=form, searched=cat.searched, cats=cats)

'''ADMINISTRATION BLOCK'''


# Admin Page
@app.route("/admin")
@login_required
def admin():
    id = current_user.id
    if id == 1:
        return render_template('app/admin/templates/admin.html')
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
    return render_template("app/users/templates/login.html", form=form)


# Create logout page
@app.route("/logout", methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for("cats"))


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
        name_to_update.username = request.form["username"]
        # check for profile_pic
        if request.files["profile_pic"] and allowed_file(request.files["profile_pic"].filename):
            name_to_update.profile_pic = request.files["profile_pic"]

            # grab image name
            pic_filename = secure_filename(name_to_update.profile_pic.filename)
            # set UUID
            pic_name = 'user_' + str(datetime.datetime.now().date())+'_' + str(uuid.uuid1()) + '.jpeg'
            # save that image
            saver = request.files["profile_pic"]
            # change it to a string to save to db
            name_to_update.profile_pic = pic_name
            try:
                db.session.commit()
                saver.save(os.path.join(app.config['UPLOAD_FOLDER'], pic_name))

                flash("User updated successfully")
                return render_template("app/users/templates/dashboard.html", form=form, name_to_update=name_to_update, id=id)
            except:
                flash("User updated successfully")
                return render_template("app/users/templates/dashboard.html", form=form, name_to_update=name_to_update)
        else:
            db.session.commit()
            flash("User updated successfully")
            return render_template("app/users/templates/dashboard.html", form=form, name_to_update=name_to_update, id=id)

    else:
        return render_template("app/users/templates/dashboard.html", form=form, name_to_update=name_to_update, id=id)

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
            try:
                hashed_pw = generate_password_hash(form.password_hash.data, 'sha256')
                user = Users(username=form.username.data, name=form.name.data, email=form.email.data,
                             password_hash=hashed_pw)
                db.session.add(user)
                db.session.commit()
            except:
                flash("Email or User is Already in Base")
                flask1 = Users.query.order_by(desc(Users.date_added))
                return render_template("app/users/templates/add_user.html", form=form, name=name, flask1=flask1)
        form.username.data = ''
        form.name.data = ''
        form.email.data = ''
        form.password_hash.data = ''
        flash("User added successfully!")
        return redirect(url_for("login"))
    flask1 = Users.query.order_by(desc(Users.date_added))
    return render_template("app/users/templates/add_user.html", form=form, name=name, flask1=flask1)


# Update User
@app.route('/update/<int:id>', methods=['GET', 'POST'])
@login_required
def update(id):
    if id == current_user.id or current_user.id == 1:
        form = UserForm()
        name_to_update = Users.query.get_or_404(id)
        if request.method == 'POST':
            name_to_update.name = request.form['name']
            name_to_update.email = request.form['email']
            name_to_update.username = request.form['username']
            db.session.commit()
            flash('User updated successfully')
            return render_template('app/users/templates/update.html', form=form, name_to_update=name_to_update, id=id)
        else:
            return render_template('app/users/templates/update.html', form=form, name_to_update=name_to_update, id=id)
    else:
        flash("Sorry You Can't Edit This User")
        return redirect(url_for("add_user"))

# Delete User
@app.route('/delete/<int:id>')
@login_required
def delete(id):
    if current_user.id == 1:
        name = None
        form = UserForm()
        user_to_delete = Users.query.get_or_404(id)
        try:
            try:
                profile_pic = user_to_delete.profile_pic
                os.remove(os.path.join(app.config['UPLOAD_FOLDER'], profile_pic))

                db.session.delete(user_to_delete)
                db.session.commit()
                flash("User Deleted Successfully. Say 'Good Bye To Him'")
                return redirect(url_for("add_user"))

            except:
                db.session.delete(user_to_delete)
                db.session.commit()
                flash("User Deleted Successfully. Say 'Good Bye To Him'")
                return redirect(url_for("add_user"))
        except:
            flash("We Have Some Problems Here While Deleting User")
            return redirect(url_for("add_user"))
    else:
        flash("Sorry You Can't Delete This User")
        return redirect(url_for("add_user"))


'''END USER BLOCK'''



'''CAT BLOCK'''

# Add Cats
@app.route("/add_cat", methods=['GET', 'POST'])
@login_required
def add_cat():
    form = CatForm()
    info = ' '
    if form.validate_on_submit():
        poster_id = current_user.id
        if request.files["cat_pic"] and allowed_file(request.files["cat_pic"].filename):
            # cat_pic = request.files["cat_pic"]
            # pic_filename = secure_filename(cat_pic.filename)
            cat_pic = 'cat_' + str(datetime.datetime.now().date()) + '_' + str(uuid.uuid1()) + '.jpeg'
            saver = request.files["cat_pic"]
            saver.save(os.path.join(app.config['UPLOAD_FOLDER'], cat_pic))

            post = Cats(category=form.category.data, age=abs(form.age.data),
                        price=form.price.data, city=form.city.data,
                        contact=form.contact.data, info=form.info.data,
                        poster_id=poster_id, cat_pic=cat_pic)
            db.session.add(post)
            db.session.commit()
        else:
            post = Cats(category=form.category.data, age=abs(form.age.data),
                        price=form.price.data, city=form.city.data,
                        contact=form.contact.data, info=form.info.data,
                        poster_id=poster_id)

            # Add post to DB
            db.session.add(post)
            db.session.commit()

        # Message
        flash("Cat added successfully!")
        return redirect(url_for("cats"))
    # Redirect
    return render_template("app/cats/templates/add_cat.html", form=form)


# Edit Cat
@app.route("/cat/edit/<int:id>", methods=['GET', 'POST'])
@login_required
def edit_cat(id):
    cat = Cats.query.get_or_404(id)
    form = CatForm()
    if form.validate_on_submit():
        cat.category = form.category.data
        cat.age = abs(form.age.data)
        cat.price = abs(form.price.data)
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
        return render_template("app/cats/templates/edit_cat.html", form=form, cat=cat)
    else:
        flash("You Aren't Authorized To Edit This")
        cats = Cats.query.order_by(desc(Cats.date_posted))
        return render_template("app/cats/templates/cats.html", cats=cats)


# Delete Cat
@app.route("/cat/delete/<int:id>")
@login_required
def delete_cat(id):
    cat_to_delete = Cats.query.get_or_404(id)
    id = current_user.id
    if id == cat_to_delete.poster.id or id == 1:
        try:
            try:  # Trying to delete pic & cat
                cat_pic = cat_to_delete.cat_pic
                os.remove(os.path.join(app.config['UPLOAD_FOLDER'], cat_pic))
                db.session.delete(cat_to_delete)
                db.session.commit()
                flash("Cat Deleted Successfully")

                return redirect(url_for("cats"))

            except:  # If fails to find the picture - delete the cat
                db.session.delete(cat_to_delete)
                db.session.commit()
                flash("Cat Deleted Successfully")
                return redirect(url_for("cats"))
        except:
            flash('Some Problem While Deleting Cat')
            cats = Cats.query.order_by(Cats.date_posted)
            return render_template(desc('cats.html', cats=cats))
    else:
        flash("You Aren't Authorized To Delete That Cat!")
        cats = Cats.query.order_by(desc(Cats.date_posted))
        return render_template('app/cats/templates/cats.html', cats=cats)


# List of Cats
@app.route("/")
def cats():

    # grab all the cats from the data base
    cats = Cats.query.order_by(desc(Cats.date_posted))
    category = Category.query.order_by(Category.name)
    clean_l = []
    for i in cats:
        if i.category not in clean_l:
            clean_l.append(i.category)

    # Getting list of existing categories
    exist = []
    for i in cats:
        if str(i.category)[0] not in exist:
            exist.append(str(i.category)[0])

    return render_template("app/cats/templates/cats.html", cats=cats, category=category, exist=exist, clean_l=clean_l)


# Cat's Page
import datetime
@app.route("/cat/<int:id>")
def cat(id):

    cat = Cats.query.get_or_404(id)
    category = Category.query

    #setting time passed
    time = datetime.datetime.now()
    diff = time - cat.date_posted
    x = divmod(diff.total_seconds(), 60)
    m_t = divmod(x[0], 60)
    h_t = divmod(m_t[0], 24)
    d, h = int(h_t[0]), int(h_t[1])
    if d == 0:
        passed = f'{h} h ago'
    else:
        passed = f'{d} d {h} h ago'

    return render_template("app/cats/templates/cat.html", cat=cat, passed=passed, category=category)

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
        flash('Breed added successfully!')
        return redirect(url_for("add_breed"))
    category = Category.query.order_by(Category.name)
    return render_template('app/cats/templates/add_breed.html', form=form, name=name, wool=wool, origin=origin, about=about,
                           category=category)


# Edit categories(Breed)
@app.route("/category/edit/<int:id>", methods=['GET', 'POST'])
@login_required
def edit_category(id):
    category = Category.query.get_or_404(id)
    form = CategoryForm()
    if form.validate_on_submit():
        category.name = form.name.data
        category.wool = form.wool.data
        category.origin = form.origin.data
        category.about = form.about.data

        # update DB
        db.session.add(category)
        db.session.commit()
        return redirect(url_for("breeds", id=category.id))

    form.name.data = category.name
    form.wool.data = category.wool
    form.origin.data = category.origin
    form.about.data = category.about
    return render_template("app/cats/templates/edit_breed.html", form=form)


# List of Breeds
@app.route('/breeds', methods=['GET', 'POST'])
def breeds():
    category = Category.query.order_by(Category.name)
    return render_template('app/cats/templates/breeds.html', category=category)


# Edit categories(Breed)
@app.route("/category/<int:id>", methods=['GET', 'POST'])
def filter_category(id):
    category2 = Category.query.get_or_404(id)
    category = Category.query.order_by(Category.name)
    cats = Cats.query.order_by(desc(Cats.date_posted))
    # categories = Category.query.order_by(Category.name)
    clean_l = []
    for i in cats:
        if i.category not in clean_l:
            clean_l.append(i.category)

    # Getting list of existing categories
    exist = []
    for i in cats:
        if str(i.category)[0] not in exist:
            exist.append(str(i.category)[0])

    return render_template("app/cats/templates/filter_category.html", cats=cats, category=category, exist=exist, clean_l=clean_l, category2=category2)




'''END CATEGORY BLOCK'''



@app.route("/about")
def about():
    return render_template('app/templates/about.html')


# # INDEX PAGE
# @app.route("/")
# def index():
#     pizza = ['pepperoni', 'Cheese', 'Beefe', 'Pineapple', 35]
#     return render_template('index.html', pizza=pizza)


@app.errorhandler(404)
def page_not_found(e):
    return render_template("app/templates/404.html"), 404


@app.errorhandler(500)
def page_not_found(e):
    return render_template("app/templates/500.html"), 500


# NAME PAGE
@app.route("/name", methods=['GET', 'POST'])
def name():
    name = None
    form = NamerForm()
    if form.validate_on_submit():
        name = form.name.data
        form.name.date = ''
        flash("Form Submitted Successfully!")

    return render_template("app/users/templates/name.html", name=name, form=form)



'''FORMS'''

class SearchForm(FlaskForm):
    searched = StringField('searched', validators=[DataRequired()])
    submit = SubmitField("Submit")


# Create login from
class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField("Submit")


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
    age = db.Column(db.Integer)
    price = db.Column(db.Integer)
    city = db.Column(db.String(20))
    contact = db.Column(db.String(255))
    info = db.Column(db.Text)
    date_posted = db.Column(db.DateTime, default=datetime.datetime.now)
    # ForeignKey to link users
    poster_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'))
    category = db.relationship('Category', backref=db.backref('cats', lazy='dynamic'))
    cat_pic = db.Column(db.String(), nullable=True)

    def __repr__(self):
        return '<Cats %r>' % self.contact

    # Example of checking input data
    # class UserRegistrationForm(FlaskForm):
    #     # ...
    #     submit = SubmitField(label=('Submit'))
    #
    #     def validate_username(self, username):
    #         excluded_chars = " *?!'^+%&amp;/()=}][{$#"
    #         for char in self.username.data:
    #             if char in excluded_chars:
    #                 raise ValidationError(
    #                     f"Character {char} is not allowed in username.")


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
    date_added = db.Column(db.DateTime, default=datetime.datetime.now)
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

# if __name__ == "__main__":
#     app.run(host="localhost", port=5000, debug=True)
