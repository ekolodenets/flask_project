from flask import render_template, url_for, flash, redirect, Blueprint
from flask_login import login_user, login_required, logout_user
from werkzeug.security import check_password_hash
from app.users.forms import LoginForm
from app.models import Users

app_blueprint = Blueprint("app", __name__, template_folder="templates")


@app_blueprint.route("/about")
def about():
    return render_template('about.html')


@app_blueprint.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        post = Users.query.filter_by(username=form.username.data).first()
        if post:
            if check_password_hash(post.password_hash, form.password.data):
                login_user(post)
                flash("Successfuly Logged In")
                return redirect(url_for("users.dashboard"))
            else:
                flash("Wrong password - Try again!")
        else:
            flash("That User Does Not Exist - Try again!")
    return render_template("login.html", form=form)


# Create logout page
@app_blueprint.route("/logout", methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for("cats.cats"))