from flask import render_template, request, url_for, flash, redirect, Blueprint
from flask_login import login_required, current_user
import uuid as uuid
import os
from sqlalchemy import desc
from datetime import datetime
from app.cats.forms import CatForm
from app.models import Cats, Category
from app import db, app

cats_blueprint = Blueprint("cats", __name__, template_folder="templates")

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}



def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


@cats_blueprint.route("/add", methods=['GET', 'POST'])
@login_required
def add_cat():
    form = CatForm()
    info = ' '
    if form.validate_on_submit():
        poster_id = current_user.id
        if request.files["cat_pic"] and allowed_file(request.files["cat_pic"].filename):
            try:
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
                flash("Cat added successfully!")
            except:
                post = Cats(category=form.category.data, age=abs(form.age.data),
                            price=form.price.data, city=form.city.data,
                            contact=form.contact.data, info=form.info.data,
                            poster_id=poster_id)
                # Add post to DB
                db.session.add(post)
                db.session.commit()
                flash("Cat added successfully! Without Picture!")
        else:
            post = Cats(category=form.category.data, age=abs(form.age.data),
                        price=form.price.data, city=form.city.data,
                        contact=form.contact.data, info=form.info.data,
                        poster_id=poster_id)


            # Add post to DB
            db.session.add(post)
            db.session.commit()
            flash("Cat added successfully!")
        # Message

        return redirect(url_for("cats.cats"))
    # Redirect
    return render_template("cats/add_cat.html", form=form)


# Edit Cat
@cats_blueprint.route("/edit/<int:id>", methods=['GET', 'POST'])
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
        return redirect(url_for("cats.cat", id=cat.id))

    if current_user.id == cat.poster_id:
        form.category.data = cat.category
        form.age.data = cat.age
        form.price.data = cat.price
        form.city.data = cat.city
        form.contact.data = cat.contact
        form.info.data = cat.info
        return render_template("cats/edit_cat.html", form=form, cat=cat)
    else:
        flash("You Aren't Authorized To Edit This")
        cats = Cats.query.order_by(desc(Cats.date_posted))
        return render_template("cats/cats.html", cats=cats)


# Delete Cat
@cats_blueprint.route("/delete/<int:id>")
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

                return redirect(url_for("cats.cats"))

            except:  # If fails to find the picture - delete the cat
                db.session.delete(cat_to_delete)
                db.session.commit()
                flash("Cat Deleted Successfully")
                return redirect(url_for("cats.cats"))
        except:
            flash('Some Problem While Deleting Cat')
            cats = Cats.query.order_by(Cats.date_posted)
            return render_template(desc('cats/cats.html', cats=cats))
    else:
        flash("You Aren't Authorized To Delete That Cat!")
        cats = Cats.query.order_by(desc(Cats.date_posted))
        return render_template('cats/cats.html', cats=cats)


# List of Cats
@cats_blueprint.route("/")
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

    return render_template("cats/cats.html", cats=cats, category=category, exist=exist, clean_l=clean_l)


# Cat's Page
import datetime
@cats_blueprint.route("/<int:id>")
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

    return render_template("cats/cat.html", cat=cat, passed=passed, category=category)




