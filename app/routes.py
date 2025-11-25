from flask import Blueprint, request, redirect, url_for, render_template, session
from .models import db, User, Debtor
from sqlalchemy import text, select
main = Blueprint('main', __name__)


@main.route("/", methods=["GET", "POST"])
def login():
    error_message = None

    if request.method == "POST":
        username_input = request.form.get("username", "").strip()
        user = User.query.filter_by(username=username_input).first()

        if user:
            session["username"] = username_input
            return redirect(url_for("main.dashboard"))
        else:
            error_message = "Please enter a valid username."

    return render_template("index.html", error_message=error_message)


@main.route("/dashboard")
def dashboard():
    username = session.get("username")
    if not username:
        return redirect(url_for("main.login"))

    # ✅ Use filter() with column reference, not filter_by()
    debtors = Debtor.query.filter(Debtor.user_username == username).all()

    return render_template("dashboard.html", debtors=debtors, username=username)

from flask import redirect, url_for, session

@main.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return redirect(url_for("main.login"))


@main.route("/dbtest")
def dbtest():
    try:
        db.session.execute(text("SELECT 1;"))
        return "DB connection OK!"
    except Exception as e:
        return str(e)
    