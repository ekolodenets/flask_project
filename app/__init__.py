from flask import Flask, render_template, url_for, redirect
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate


app = Flask(__name__)

# add database
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
# postgresql DB
app.config[
    "SQLALCHEMY_DATABASE_URI"] = "postgresql://aroxklnqgdwyjo:45e12ea1729c93cbcc740f010aa657cc3ef1acb074c7e4caa3858508e8d73f01@ec2-3-228-222-169.compute-1.amazonaws.com:5432/dcqng4p0da090d"
# secret key
app.config['SECRET_KEY'] = "adojaios3ijs2i342f3423ghfgf4145sijgsij63634613613cvbxdg16176s8ssdhs37695fb9dl"

UPLOAD_FOLDER = "app/static/images/"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

db = SQLAlchemy(app)
migrate = Migrate(app, db)

from app.models import Users
from app.users.views import users_blueprint
from app.admin.views import admin_blueprint
from app.categories.views import categories_blueprint
from app.cats.views import cats_blueprint
from app.views import app_blueprint

app.register_blueprint(users_blueprint, url_prefix='/users')
app.register_blueprint(admin_blueprint, url_prefix='/admin')
app.register_blueprint(categories_blueprint, url_prefix='/categories')
app.register_blueprint(cats_blueprint, url_prefix='/cats')
app.register_blueprint(app_blueprint)


login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))

@app.route("/")
def index():
    return redirect(url_for("cats.cats"))

@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404


@app.errorhandler(500)
def page_not_found(e):
    return render_template("500.html"), 500