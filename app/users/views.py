from flask import Flask, render_template, request, url_for, flash, redirect, Blueprint
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import uuid as uuid
import os
from sqlalchemy import desc
from datetime import datetime, date, time

from app.users.forms import LoginForm, UserForm, NamerForm
from app.models import Users
from app import db, app

users_blueprint = Blueprint("users", __name__, template_folder="templates")
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])




def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

'''USER BLOCK'''

# Add User
@users_blueprint.route('/add', methods=['GET', 'POST'])
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
                return render_template("users/add_user.html", form=form, name=name, flask1=flask1)
        form.username.data = ''
        form.name.data = ''
        form.email.data = ''
        form.password_hash.data = ''
        flash("User added successfully!")
        return redirect(url_for("app.login"))
    flask1 = Users.query.order_by(desc(Users.date_added))
    return render_template("users/add_user.html", form=form, name=name, flask1=flask1)


# Update User
@users_blueprint.route('/update/<int:id>', methods=['GET', 'POST'])
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
            return render_template('users/update.html', form=form, name_to_update=name_to_update, id=id)
        else:
            return render_template('users/update.html', form=form, name_to_update=name_to_update, id=id)
    else:
        flash("Sorry You Can't Edit This User")
        return redirect(url_for("users.add_user"))

# Delete User
@users_blueprint.route('/delete/<int:id>')
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
                return redirect(url_for("users.add_user"))

            except:
                db.session.delete(user_to_delete)
                db.session.commit()
                flash("User Deleted Successfully. Say 'Good Bye To Him'")
                return redirect(url_for("users.add_user"))
        except:
            flash("We Have Some Problems Here While Deleting User")
            return redirect(url_for("users.add_user"))
    else:
        flash("Sorry You Can't Delete This User")
        return redirect(url_for("users.add_user"))


@users_blueprint.route("/name", methods=['GET', 'POST'])
def name():
    name = None
    form = NamerForm()
    if form.validate_on_submit():
        name = form.name.data
        form.name.date = ''
        flash("Form Submitted Successfully!")

    return render_template("users/name.html", name=name, form=form)


# # Create dashboard page
@users_blueprint.route("/dashboard", methods=['GET', 'POST'])
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
            pic_name = 'user_' + str(datetime.now().date())+'_' + str(uuid.uuid1()) + '.jpeg'
            # save that image
            saver = request.files["profile_pic"]
            # change it to a string to save to db
            name_to_update.profile_pic = pic_name
            try:
                db.session.commit()
                saver.save(os.path.join(app.config['UPLOAD_FOLDER'], pic_name))

                flash("User updated successfully")
                return render_template("users/dashboard.html", form=form, name_to_update=name_to_update, id=id)
            except:
                flash("User updated successfully")
                return render_template("users/dashboard.html", form=form, name_to_update=name_to_update)
        else:
            db.session.commit()
            flash("User updated successfully")
            return render_template("users/dashboard.html", form=form, name_to_update=name_to_update, id=id)

    else:
        return render_template("users/dashboard.html", form=form, name_to_update=name_to_update, id=id)