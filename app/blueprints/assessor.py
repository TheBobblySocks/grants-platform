from flask import Blueprint, abort, render_template
from flask_login import current_user, login_required

from app.models import Application, ApplicationSection, Assessment, db
from programme_config import PROGRAMME

assessor = Blueprint("assessor", __name__, url_prefix="/assessor")

_SECTIONS = PROGRAMME["sections"]
_CRITERIA = PROGRAMME["criteria"]


def _require_assessor():
    if current_user.role not in ("assessor", "admin"):
        abort(403)


@assessor.route("/applications")
@login_required
def applications():
    _require_assessor()
    rows = (
        db.session.query(Application, Assessment)
        .outerjoin(Assessment, Assessment.application_id == Application.id)
        .filter(Application.status != "draft")
        .order_by(Application.submitted_at.desc())
        .all()
    )
    return render_template("assessor/applications.html", rows=rows)


@assessor.route("/application/<int:application_id>")
@login_required
def application_detail(application_id):
    _require_assessor()
    application = Application.query.get_or_404(application_id)
    if application.status == "draft":
        abort(404)

    app_section = ApplicationSection.query.filter_by(application_id=application_id).first()
    assessment = Assessment.query.filter_by(application_id=application_id).first()

    return render_template(
        "assessor/application_detail.html",
        application=application,
        app_section=app_section,
        assessment=assessment,
        sections=_SECTIONS,
        criteria=_CRITERIA,
    )
