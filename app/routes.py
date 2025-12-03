from flask import Blueprint, request, redirect, url_for, render_template, session
from app.models import db, User, Debtor, AuditLog
from datetime import datetime
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
            session["role"] = user.role
            return redirect(url_for("main.dashboard"))
        else:
            error_message = "Please enter a valid username."

    return render_template("index.html", error_message=error_message)

def log_access(username, action, resource_type, resource_id, details=None):
    print("LOGGING →", username, action, resource_type, resource_id)

    entry = AuditLog(
        username=username,
        action=action,
        resource_type=resource_type,
        resource_id=str(resource_id),
        details=details
    )

    db.session.add(entry)
    db.session.commit()


@main.route("/dashboard")
def dashboard():
    username = session.get("username")
    role = session.get("role")
    if not username:
        return redirect(url_for("main.login"))

    debtors = Debtor.query.filter(Debtor.user_username == username).all()

    # Log that the user accessed their debtor list
    log_access(
        username=username,
        action="viewed list",
        resource_type="Debtor",
        resource_id="ALL"
    )

    return render_template(
    "dashboard.html",
    debtors=debtors,
    username=username,
    user_role = role
    )



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


@main.route("/audit")
def audit_log():
    if session.get("role") != "admin":
        return "Unauthorized", 403

    logs = AuditLog.query.order_by(AuditLog.timestamp.desc()).all()

    return render_template("audit.html", logs=logs)

from flask import jsonify, session, request
from sqlalchemy import or_

@main.route("/api/debtors")
def api_debtors():
    username = session.get("username")
    if not username:
        return jsonify([])  # not logged in, return empty

    search_query = request.args.get("q", "").strip()

    query = Debtor.query.filter(Debtor.user_username == username)

    if search_query:
        query = query.filter(
            or_(
                Debtor.name.ilike(f"%{search_query}%"),
                Debtor.address.ilike(f"%{search_query}%"),
                Debtor.national_id.cast(db.String).ilike(f"%{search_query}%")
            )
        )

    debtors = query.all()

    return jsonify([
        {
            "national_id": d.national_id,
            "name": d.name,
            "address": d.address,
            "created_at": d.created_at.strftime("%Y-%m-%d %H:%M:%S") if d.created_at else "",
            "financial_data_source": d.financial_data_source
        }
        for d in debtors
    ])

@main.route("/add-debtor", methods=["GET"])
def add_debtor_page():
    username = session.get("username")
    if not username:
        return redirect(url_for("main.login"))

    return render_template("add_debtor.html")

@main.route("/add-debtor", methods=["POST"])
def add_debtor_submit():
    username = session.get("username")
    if not username:
        return redirect(url_for("main.login"))

    national_id = request.form.get("national_id")
    name = request.form.get("name")
    address = request.form.get("address")
    source = request.form.get("financial_data_source")

    new_debtor = Debtor(
        national_id=national_id,
        name=name,
        address=address,
        financial_data_source=source,
        user_username=username
    )

    db.session.add(new_debtor)
    db.session.commit()

    # optional logging
    log_access(username, "created", "Debtor", national_id)

    return redirect(url_for("main.dashboard"))

@main.route("/debtor/<int:national_id>")
def debtor_detail(national_id):
    username = session.get("username")
    if not username:
        return redirect(url_for("main.login"))

    debtor = Debtor.query.filter_by(national_id=national_id).first()

    if not debtor:
        return "Debtor not found", 404

    # enforce that users only view their own debtors unless admin
    if debtor.user_username != username and session.get("role") != "admin":
        return "Forbidden", 403

    # Log access
    log_access(
        username=username,
        action="viewed detail",
        resource_type="Debtor",
        resource_id=national_id
    )

    return render_template("debtor_detail.html", debtor=debtor)
