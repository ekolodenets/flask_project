from flask import render_template, url_for, flash, redirect, Blueprint
from flask_login import login_required, current_user


admin_blueprint = Blueprint("admin", __name__, template_folder="templates")


@admin_blueprint.route("/")
@login_required
def admin():
    id = current_user.id
    if id == 1:
        return render_template('admin/admin.html')
    else:
        flash("Sorry, you are not the Admin")
        return redirect(url_for("app.dashboard"))