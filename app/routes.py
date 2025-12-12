from flask import Blueprint, request, redirect, url_for, render_template, session, flash, abort
from app.models import db, User, Debtor, AuditLog, FinancialData
from sqlalchemy import text
from app.final_code import clean_vat_number, api_get, parse_details, parse_financials
from app.ratios import solvabiliteitsscore
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
            error_message = "Wrong username. Please try again."

    return render_template("index.html", error_message=error_message)


def log_access(username, action, resource_id):

    entry = AuditLog(
        username=username,
        action=action,
        resource_id=str(resource_id),
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
        action="viewed dashboard",
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


@main.route("/audit")
def audit_log():
    if session.get("role") != "admin":
        return "Unauthorized", 403

    logs = AuditLog.query.order_by(AuditLog.timestamp.desc()).all()

    return render_template("audit.html", logs=logs)

from flask import jsonify, session, request
from sqlalchemy import or_

# Assuming your imports include:
# from flask import jsonify, request, session
# from your_models import Debtor, db
# from sqlalchemy import or_

@main.route("/api/debtors")
def api_debtors():
    username = session.get("username")
    if not username:
        return jsonify([])

    search_query = request.args.get("q", "").strip()

    # Base query filtered by the logged-in user
    query = Debtor.query.filter(Debtor.user_username == username)

    if search_query:
        search_pattern = f"%{search_query}%"
        # Filter for the search query across Name, Address, BTW Nummer, and National ID
        query = query.filter(
            or_(
                Debtor.name.ilike(search_pattern),
                Debtor.address.ilike(search_pattern),
                # Added BTW Nummer to search fields
                Debtor.btw_nummer.ilike(search_pattern), 
            )
        )

    # Optional: Order the results
    debtors = query.order_by(Debtor.name).all()

    return jsonify([
        {
            "national_id": d.national_id,
            "name": d.name,
            "address": d.address,
            # CRITICAL FIX: Included 'btw_nummer' and 'health_indicator'
            "btw_nummer": d.btw_nummer, 
            "health_indicator": d.health_indicator,
        }
        for d in debtors
    ])

def is_btw_connected_to_specific_user(btw_number_to_check, username_to_check):
    # Query the Debtor table, filtering by both BTW number and user_username.
    debtor_exists = db.session.execute(
        db.select(Debtor).filter_by(
            btw_nummer=btw_number_to_check,
            user_username=username_to_check
        )
    ).scalar_one_or_none() is not None
    
    return debtor_exists

def format_btw_number(nummer: str) -> str:
    """Format a cleaned BTW number into standard display format."""
    if len(nummer) == 9:
        return f"BE0{nummer}"
    elif len(nummer) == 10:
        return f"BE{nummer}"


@main.route("/add-debtor", methods=["GET", "POST"])
def add_debtor():
    username = session.get("username")
    if not username:
        return redirect(url_for("main.login"))

    error_message = None

    if request.method == "POST":
        btw_nummer = request.form.get("btw-nummer")
        
        try:
            nummer = clean_vat_number(btw_nummer)
        except ValueError as e:
            flash(f"Ongeldig BTW-nummer ({btw_nummer})", "error")
            return redirect(url_for("main.add_debtor"))

        if is_btw_connected_to_specific_user(format_btw_number(nummer), username):
            flash(f"Het BTW-nummer {btw_nummer} is al gekoppeld aan uw account.", "error")
            return redirect(url_for("main.add_debtor"))
        
        try:
            financials_raw = api_get(f"{nummer}/financials")
        except Exception as e:
            flash(f"\nKon financiële data niet ophalen voor {nummer}", "error")
            return redirect(url_for("main.add_debtor"))
        
        financials = parse_financials(financials_raw)

        if not financials:
            flash(f"\nGeen financiële gegevens beschikbaar.", "error")
            return redirect(url_for("main.add_debtor"))
        else:
            for account in financials:
                year = account.get("year")
                
                # Check for existing FinancialData record for this BTW and Year
                financial_exists = FinancialData.query.filter_by(
                    btw_nummer=format_btw_number(nummer), 
                    year=year
                ).first()
                
                if not financial_exists:
                    # Only add the record if it does NOT exist
                    new_financial = FinancialData(
                        btw_nummer=format_btw_number(nummer),
                        year=year,
                        current_ratio=account.current_ratio,
                        quick_ratio=account.quick_ratio,
                        solvabiliteitsscore=solvabiliteitsscore(account.equity, account.total_assets)
                    )
                    db.session.add(new_financial)        

        try:
            details_raw = api_get(f"{nummer}")
        except Exception as e:
            debtor = Debtor(
                address="Onbekend",
                name="Onbekend",
                btw_nummer=format_btw_number(nummer),
                user_username=username,
                health_indicator = "Onbekend"
            )
            db.session.add(debtor)
        else:
            details = parse_details(details_raw)
            debtor = Debtor(
                address= f"{details.street}, {details.zip_code} {details.city}, {details.country}",
                name= details.get("name"),
                btw_nummer=format_btw_number(nummer),
                user_username=username,
                health_indicator = financials[0].health_indicator
            )
            db.session.add(debtor)


            db.session.commit()
            log_access(username, "created debtor", format_btw_number(nummer))
            flash("Debtor added successfully!", "success")
            return redirect(url_for("main.dashboard"))

    return render_template("add_debtor.html", error_message=error_message)

@main.route("/debtor/<uuid:national_id>")
def debtor_detail(national_id):
    username = session.get("username")
    if not username:
        return redirect(url_for("main.login"))

    # 1. Fetch the Debtor record
    debtor = Debtor.query.filter_by(national_id=national_id).first()

    if not debtor:
        return "Debtor not found", 404

    # enforce that users only view their own debtors unless admin
    if debtor.user_username != username and session.get("role") != "admin":
        return "Forbidden", 403

    # Get the BTW number for filtering
    btw_nummer = debtor.btw_nummer 
    
    financial_records = FinancialData.query.filter_by(btw_nummer=btw_nummer) \
                                           .order_by(FinancialData.year.desc()) \
                                           .all()



    # Log access
    log_access(
        username=username,
        action="viewed detail",
        resource_id= btw_nummer
    )

    return render_template(
        "debtor_detail.html", 
        debtor=debtor, 
        financial_data=financial_records # This must be the ORM list
    )

@main.route('/delete-debtor/<uuid:debtor_id>', methods=['POST'])
def delete_debtor(debtor_id):
    debtor = Debtor.query.get_or_404(debtor_id)
    username = session.get('username')


    # Log the deletion BEFORE removing, in case you need debtor info
    log_access(
        username=username,
        action="deleted debtor",
        resource_id=debtor.btw_nummer,
    )

    db.session.delete(debtor)
    db.session.commit()

    return redirect(url_for('main.dashboard'))

@main.route('/register', methods=['GET', 'POST'])
def register():
    from app import db
    if request.method == 'POST':
        username = request.form.get('username').strip()

        if not username:
            flash("Please enter a username.", "error")
            return redirect(url_for('main.register'))

        # Check if the user already exists
        existing = User.query.filter_by(username=username).first()
        if existing:
            flash("Username already exists.", "error")
            return redirect(url_for('main.register'))

        # Create new user with bailiff role
        new_user = User(username=username, role="bailiff")
        db.session.add(new_user)
        db.session.commit()
        log_access(username=username, action="registered account", resource_id=username)

        flash("Account created successfully! You can now log in.", "success")
        return redirect(url_for('main.login'))

    return render_template('register.html')

def admin_only():
    """Simple helper: return username of admin or abort(403)."""
    username = session.get("username")
    if not username:
        return None
    user = User.query.filter_by(username=username).first()
    if not user or user.role != "admin":
        abort(403)
    return user

@main.route("/manage-users")
def manage_users():
    # Only admins allowed
    admin = admin_only()
    # if admin_only aborted, execution stops; otherwise continue
    users = User.query.order_by(User.username).all()
    return render_template("manage_users.html", users=users, current_username=admin.username)

@main.route("/upgrade-user/<string:target_username>", methods=["POST"])
def upgrade_user(target_username):
    admin = admin_only()
    target = User.query.filter_by(username=target_username).first_or_404()

    if target.role == "admin":
        flash("User is already an admin.", "error")
        return redirect(url_for("main.manage_users"))

    target.role = "admin"
    db.session.commit()

    # Audit log: who performed the action is admin.username
    log_access(
        username=admin.username,
        action="upgraded user",
        resource_id=target.username,
    )

    flash(f"{target.username} is now an admin!", "success")
    return redirect(url_for("main.manage_users"))

@main.route("/delete-user/<string:target_username>", methods=["POST"])
def delete_user(target_username):
    admin = admin_only()
    target = User.query.filter_by(username=target_username).first_or_404()

    # Prevent deleting yourself
    if target.username == admin.username:
        flash("You cannot delete your own account.", "error")
        return redirect(url_for("main.manage_users"))

    # Optional: prevent deleting last admin (rough check)
    if target.role == "admin":
        admin_count = User.query.filter_by(role="admin").count()
        if admin_count <= 1:
            flash("Cannot delete the last admin.", "error")
            return redirect(url_for("main.manage_users"))

    db.session.delete(target)
    db.session.commit()

    log_access(
        username=admin.username,
        action="deleted user",
        resource_id=target.username,
    )

    flash("User deleted successfully.", "success")
    return redirect(url_for("main.manage_users"))