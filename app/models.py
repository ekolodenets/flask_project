from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from app import db


class Cats(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    age = db.Column(db.Integer)
    price = db.Column(db.Integer)
    city = db.Column(db.String(20))
    contact = db.Column(db.String(255))
    info = db.Column(db.Text)
    date_posted = db.Column(db.DateTime, default=datetime.now)
    # ForeignKey to link users
    poster_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))
    category = db.relationship('Category', backref=db.backref('cats', lazy='dynamic'))
    cat_pic = db.Column(db.String(), nullable=True)

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
    date_added = db.Column(db.DateTime, default=datetime.now)
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