from datetime import datetime, timezone

from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from app import db


class Organisation(db.Model):
    __tablename__ = "organisations"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    charity_number = db.Column(db.String(50), nullable=True)
    org_type = db.Column(db.String(100), nullable=False)
    annual_income = db.Column(db.Float, nullable=False)
    years_serving_homeless = db.Column(db.Integer, nullable=False)
    contact_name = db.Column(db.String(255), nullable=False)
    contact_email = db.Column(db.String(255), nullable=False)
    address = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    users = db.relationship("User", backref="organisation", lazy=True)
    applications = db.relationship("Application", backref="organisation", lazy=True)


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(50), nullable=False, default="applicant")
    org_id = db.Column(db.Integer, db.ForeignKey("organisations.id"), nullable=True)
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)


class Application(db.Model):
    __tablename__ = "applications"

    id = db.Column(db.Integer, primary_key=True)
    org_id = db.Column(db.Integer, db.ForeignKey("organisations.id"), nullable=False)
    status = db.Column(db.String(50), nullable=False, default="draft")
    funding_type = db.Column(db.String(50), nullable=True)
    revenue_amount_requested = db.Column(db.Float, nullable=True)
    capital_amount_requested = db.Column(db.Float, nullable=True)
    local_authority_area = db.Column(db.String(255), nullable=True)
    la_endorsement_confirmed = db.Column(db.Boolean, default=False)
    submitted_at = db.Column(db.DateTime(timezone=True), nullable=True)
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    section = db.relationship("ApplicationSection", backref="application", uselist=False, lazy=True)
    assessments = db.relationship("Assessment", backref="application", lazy=True)


class ApplicationSection(db.Model):
    __tablename__ = "application_sections"

    id = db.Column(db.Integer, primary_key=True)
    application_id = db.Column(db.Integer, db.ForeignKey("applications.id"), unique=True, nullable=False)
    skills_and_experience = db.Column(db.JSON, nullable=True)
    proposal_part1 = db.Column(db.JSON, nullable=True)
    proposal_part2 = db.Column(db.JSON, nullable=True)
    deliverability_part1 = db.Column(db.JSON, nullable=True)
    deliverability_part2 = db.Column(db.JSON, nullable=True)
    cost_and_value = db.Column(db.JSON, nullable=True)
    outcomes_and_impact = db.Column(db.JSON, nullable=True)


class Assessment(db.Model):
    __tablename__ = "assessments"

    id = db.Column(db.Integer, primary_key=True)
    application_id = db.Column(db.Integer, db.ForeignKey("applications.id"), nullable=False)
    assessor_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    scores = db.Column(db.JSON, nullable=True)
    weighted_total = db.Column(db.Integer, nullable=True)
    recommendation = db.Column(db.String(20), nullable=True)
    notes = db.Column(db.Text, nullable=True)
    gap_analysis = db.Column(db.JSON, nullable=True)
    auto_rejected = db.Column(db.Boolean, default=False)
    completed_at = db.Column(db.DateTime(timezone=True), nullable=True)
