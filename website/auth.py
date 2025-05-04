from flask import (
    Blueprint,
    render_template,
    request,
    flash,
    redirect,
    url_for,
)
from .models import User
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from flask_login import login_user, current_user

auth = Blueprint("auth", __name__)


@auth.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        print(f"Username: {username}, Password: {password}")
        user = User.query.filter_by(username=username).first()
        print(current_user)
        if user:
            if check_password_hash(user.password, password):
                flash("Login successful!", "success")
                login_user(user, remember=True)
                return redirect(url_for("views.home"))
            else:
                flash("Incorrect password, please try again.", "error")
        else:
            flash("Username does not exist, please try again.", "error")

    return render_template("login.html", user=current_user)


@auth.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        data = request.form

        username = data.get("username")
        password = data.get("password")

        user = User.query.filter_by(username=username).first()

        if user:
            flash("Username already exists", "error")
            return render_template("register.html")
        elif not username or len(username) < 4:
            flash("Username must be at least 4 characters long", "error")
            return render_template("register.html")
        elif not password or len(password) < 8:
            flash("Password must be at least 8 characters long", "error")
            return render_template("register.html")
        elif username == password:
            flash("Username and password cannot be the same", "error")
            return render_template("register.html")
        else:
            flash("Registration successful! Now you can login.", "success")
            new_user = User(
                username=username,
                password=generate_password_hash(password, method="pbkdf2:sha256"),
            )
            db.session.add(new_user)
            db.session.commit()
            return render_template("login.html")

    return render_template("register.html", user=current_user)