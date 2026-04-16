from flask_wtf import FlaskForm
from wtforms import (
    BooleanField,
    EmailField,
    FloatField,
    IntegerField,
    PasswordField,
    RadioField,
    SelectField,
    StringField,
    TextAreaField,
)
from wtforms.validators import DataRequired, Email, EqualTo, NumberRange, Optional

from programme_config import PROGRAMME

_ORG_TYPE_CHOICES = [
    (t, PROGRAMME["eligibility"]["org_type_labels"][t])
    for t in PROGRAMME["eligibility"]["org_types"]
]


class LoginForm(FlaskForm):
    email = EmailField("Email address", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])


class RegisterForm(FlaskForm):
    email = EmailField("Email address", validators=[DataRequired(), Email()])
    password = PasswordField("Create a password", validators=[DataRequired()])
    confirm_password = PasswordField(
        "Confirm password",
        validators=[DataRequired(), EqualTo("password", message="Passwords must match")],
    )
    org_name = StringField("Organisation name", validators=[DataRequired()])
    org_type = SelectField("Organisation type", choices=_ORG_TYPE_CHOICES, validators=[DataRequired()])
    annual_income = FloatField("Annual income (£)", validators=[DataRequired()])
    years_serving_homeless = IntegerField(
        "Years working with people experiencing homelessness",
        validators=[DataRequired(), NumberRange(min=0)],
    )
    contact_name = StringField("Contact name", validators=[DataRequired()])
    contact_email = EmailField("Contact email", validators=[DataRequired(), Email()])
    address = TextAreaField("Organisation address", validators=[DataRequired()])


class ApplicationSectionForm(FlaskForm):
    content = TextAreaField("Response", validators=[DataRequired()])


class ApplicationMetaForm(FlaskForm):
    funding_type = RadioField(
        "Type of funding",
        choices=[
            ("revenue", "Revenue funding"),
            ("capital", "Capital funding"),
            ("both", "Both revenue and capital funding"),
        ],
        validators=[DataRequired()],
    )
    revenue_amount_requested = FloatField("Revenue amount requested (£)", validators=[Optional()])
    capital_amount_requested = FloatField("Capital amount requested (£)", validators=[Optional()])
    local_authority_area = StringField("Local authority area", validators=[DataRequired()])
    la_endorsement_confirmed = BooleanField("I confirm we have a local authority endorsement letter")
