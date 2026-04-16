from flask import Blueprint, flash, redirect, render_template, url_for
from flask_login import login_required, login_user, logout_user

from app.forms import LoginForm, RegisterForm
from app.models import Organisation, User, db

auth = Blueprint("auth", __name__, url_prefix="/auth")


@auth.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            if user.role in ("assessor", "admin"):
                return redirect(url_for("assessor.applications"))
            return redirect(url_for("applicant.dashboard"))
        flash("Invalid email or password.", "error")
    return render_template("auth/login.html", form=form)


@auth.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        existing = User.query.filter_by(email=form.email.data).first()
        if existing:
            flash("An account with that email already exists.", "error")
            return render_template("auth/register.html", form=form)

        org = Organisation(
            name=form.org_name.data,
            org_type=form.org_type.data,
            annual_income=form.annual_income.data,
            years_serving_homeless=form.years_serving_homeless.data,
            contact_name=form.contact_name.data,
            contact_email=form.contact_email.data,
            address=form.address.data,
        )
        db.session.add(org)
        db.session.flush()

        user = User(email=form.email.data, role="applicant", org_id=org.id)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()

        login_user(user)
        flash("Account created. Welcome.", "success")
        return redirect(url_for("applicant.dashboard"))

    return render_template("auth/register.html", form=form)


@auth.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("public.index"))
