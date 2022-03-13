from flask import render_template, url_for, flash, redirect, Blueprint
from flask_login import login_required
from sqlalchemy import desc
from app.categories.forms import CategoryForm
from app.models import Category, Cats
from app import db, app



categories_blueprint = Blueprint("categories", __name__, template_folder="templates")


@categories_blueprint.route('/add', methods=['GET', 'POST'])
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
        form.name.data = ''
        form.wool.data = ''
        form.origin.data = ''
        form.about.data = ''
        flash('Breed added successfully!')
        return redirect(url_for("categories.add_breed"))
    category = Category.query.order_by(Category.name)
    return render_template('categories/add_breed.html', form=form, name=name, wool=wool, origin=origin, about=about,
                           category=category)


@categories_blueprint.route("/edit/<int:id>", methods=['GET', 'POST'])
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
        return redirect(url_for("categories.breeds", id=category.id))

    form.name.data = category.name
    form.wool.data = category.wool
    form.origin.data = category.origin
    form.about.data = category.about
    return render_template("categories/edit_breed.html", form=form)



@categories_blueprint.route('/', methods=['GET', 'POST'])
def breeds():
    category = Category.query.order_by(Category.name)
    return render_template('categories/breeds.html', category=category)



@categories_blueprint.route("/<int:id>", methods=['GET', 'POST'])
def filter_category(id):
    category2 = Category.query.get_or_404(id)
    category = Category.query.order_by(Category.name)
    cats = Cats.query.order_by(desc(Cats.date_posted))
    clean_l = []
    for i in cats:
        if i.category not in clean_l:
            clean_l.append(i.category)

    # Getting list of existing categories
    exist = []
    for i in cats:
        if str(i.category)[0] not in exist:
            exist.append(str(i.category)[0])

    return render_template("categories/filter_category.html", cats=cats, category=category, exist=exist, clean_l=clean_l, category2=category2)
