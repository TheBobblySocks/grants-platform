from flask import Blueprint, render_template
from flask_wtf import FlaskForm
from wtforms import BooleanField, FloatField, IntegerField, SelectField
from wtforms.validators import DataRequired

from programme_config import PROGRAMME

public = Blueprint("public", __name__, url_prefix="/")

_ORG_TYPE_CHOICES = [
    (t, PROGRAMME["eligibility"]["org_type_labels"][t])
    for t in PROGRAMME["eligibility"]["org_types"]
]


class EligibilityCheckerForm(FlaskForm):
    org_type = SelectField("Organisation type", choices=_ORG_TYPE_CHOICES, validators=[DataRequired()])
    annual_income = FloatField("Annual income (£)", validators=[DataRequired()])
    years_serving_homeless = IntegerField(
        "Years working with people experiencing homelessness",
        validators=[DataRequired()],
    )
    operates_in_england = BooleanField("Our organisation operates in England")


@public.route("/")
def index():
    return render_template("public/index.html")


@public.route("/eligibility", methods=["GET", "POST"])
def eligibility():
    form = EligibilityCheckerForm()
    eligible = None
    reasons = []

    if form.validate_on_submit():
        rules = PROGRAMME["eligibility"]
        checks = [
            (form.org_type.data in rules["org_types"], "Your organisation type is not eligible for this fund."),
            (form.annual_income.data <= rules["max_annual_income"], f"Annual income must be £{rules['max_annual_income']:,} or less."),
            (form.years_serving_homeless.data >= rules["min_years_experience"], f"You must have at least {rules['min_years_experience']} years experience."),
            (form.operates_in_england.data, "Your organisation must operate in England."),
        ]
        reasons = [msg for passed, msg in checks if not passed]
        eligible = len(reasons) == 0

    return render_template("public/eligibility.html", form=form, eligible=eligible, reasons=reasons)
