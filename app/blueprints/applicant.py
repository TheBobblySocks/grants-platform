from datetime import datetime, timezone

from flask import Blueprint, abort, flash, redirect, render_template, url_for
from flask_login import current_user, login_required

from app.forms import ApplicationMetaForm, ApplicationSectionForm
from app.models import Application, ApplicationSection, db
from programme_config import PROGRAMME

applicant = Blueprint("applicant", __name__, url_prefix="/apply")

_SECTIONS = PROGRAMME["sections"]
_STEP_MAP = {s["step"]: s for s in _SECTIONS}
_TOTAL_STEPS = len(_SECTIONS)


def _require_applicant():
    if current_user.role != "applicant":
        abort(403)


def _get_or_create_draft():
    app = (
        Application.query.filter_by(org_id=current_user.org_id, status="draft")
        .order_by(Application.id.desc())
        .first()
    )
    if app is None:
        app = Application(org_id=current_user.org_id, status="draft")
        db.session.add(app)
        db.session.flush()
    return app


def _get_or_create_section(application_id: int) -> ApplicationSection:
    section = ApplicationSection.query.filter_by(application_id=application_id).first()
    if section is None:
        section = ApplicationSection(application_id=application_id)
        db.session.add(section)
        db.session.flush()
    return section


@applicant.route("/dashboard")
@login_required
def dashboard():
    _require_applicant()
    applications = (
        Application.query.filter_by(org_id=current_user.org_id)
        .order_by(Application.id.desc())
        .all()
    )
    return render_template("applicant/dashboard.html", applications=applications)


@applicant.route("/step/<int:step>", methods=["GET", "POST"])
@login_required
def apply_step(step):
    _require_applicant()
    if step not in _STEP_MAP:
        abort(404)

    section_config = _STEP_MAP[step]
    criterion_key = section_config["criterion"]
    guidance = PROGRAMME["criteria"][criterion_key]["guidance"]

    section_form = ApplicationSectionForm(prefix="section")
    section_form.content.label.text = section_config["title"]
    meta_form = ApplicationMetaForm(prefix="meta") if step == 1 else None

    application = _get_or_create_draft()
    app_section = _get_or_create_section(application.id)

    if not section_form.is_submitted():
        existing = getattr(app_section, section_config["key"])
        if existing:
            section_form.content.data = existing.get("text", "")

    if step == 1 and meta_form and not meta_form.is_submitted():
        meta_form.funding_type.data = application.funding_type
        meta_form.revenue_amount_requested.data = application.revenue_amount_requested
        meta_form.capital_amount_requested.data = application.capital_amount_requested
        meta_form.local_authority_area.data = application.local_authority_area
        meta_form.la_endorsement_confirmed.data = application.la_endorsement_confirmed

    if section_form.validate_on_submit():
        meta_valid = True
        if step == 1 and meta_form:
            meta_valid = meta_form.validate()

        if meta_valid:
            setattr(app_section, section_config["key"], {"text": section_form.content.data})

            if step == 1 and meta_form:
                application.funding_type = meta_form.funding_type.data
                application.revenue_amount_requested = meta_form.revenue_amount_requested.data
                application.capital_amount_requested = meta_form.capital_amount_requested.data
                application.local_authority_area = meta_form.local_authority_area.data
                application.la_endorsement_confirmed = meta_form.la_endorsement_confirmed.data

            db.session.commit()

            if step == _TOTAL_STEPS:
                return redirect(url_for("applicant.review"))
            return redirect(url_for("applicant.apply_step", step=step + 1))

    return render_template(
        "applicant/apply_step.html",
        section_form=section_form,
        meta_form=meta_form,
        step=step,
        section_config=section_config,
        guidance=guidance,
        total_steps=_TOTAL_STEPS,
        application=application,
    )


@applicant.route("/review")
@login_required
def review():
    _require_applicant()
    application = (
        Application.query.filter_by(org_id=current_user.org_id, status="draft")
        .order_by(Application.id.desc())
        .first()
    )
    if application is None:
        flash("No draft application found.", "warning")
        return redirect(url_for("applicant.apply_step", step=1))

    app_section = ApplicationSection.query.filter_by(application_id=application.id).first()
    return render_template(
        "applicant/review.html",
        application=application,
        app_section=app_section,
        sections=_SECTIONS,
    )


@applicant.route("/submit", methods=["POST"])
@login_required
def submit():
    _require_applicant()
    application = (
        Application.query.filter_by(org_id=current_user.org_id, status="draft")
        .order_by(Application.id.desc())
        .first()
    )
    if application is None:
        abort(404)

    application.status = "submitted"
    application.submitted_at = datetime.now(timezone.utc)
    db.session.commit()

    try:
        from app.assessor_ai import assess_application
        assess_application(application.id)
    except Exception:
        pass

    return redirect(url_for("applicant.submitted"))


@applicant.route("/submitted")
@login_required
def submitted():
    _require_applicant()
    application = (
        Application.query.filter_by(org_id=current_user.org_id)
        .filter(Application.status != "draft")
        .order_by(Application.submitted_at.desc())
        .first()
    )
    return render_template("applicant/submitted.html", application=application)
