# Ending Homelessness in Communities Fund — Grant Management System

## Project Overview

A web-based grant management system for the **Ending Homelessness in Communities Fund (EHCF)** administered by MHCLG. Two user types:

- **Applicants**: Voluntary, community, and faith sector (VCFS) organisations applying for grant funding
- **Assessors**: Department staff reviewing, scoring, and making funding decisions

Grant details: £37 million over 3 years (2026–2029). Applications assess organisations on 7 weighted criteria scored 0–3.

---

## Tech Stack

| Layer | Choice | Rationale |
|---|---|---|
| Framework | Flask (Python) | Lightweight, fast to build, Jinja2 templates |
| Database | PostgreSQL + SQLAlchemy | Robust ORM, Flask-SQLAlchemy integration |
| Migrations | Flask-Migrate (Alembic) | Schema version control |
| Auth | Flask-Login + Flask-Bcrypt | Session-based auth, password hashing |
| Forms | WTForms + Flask-WTF | Validation, CSRF protection |
| Styling | GOV.UK Frontend | GOV.UK Design System compliant |
| Jinja macros | govuk-frontend-jinja | GOV.UK components as Jinja2 macros |
| Form widgets | govuk-frontend-wtf | WTForms fields rendered as GOV.UK components |
| File uploads | Local filesystem or S3 (boto3) | Budget Excel, PDFs, letters |
| Deployment | Render or Railway | Simple Postgres + Flask deployment |

---

## Architecture

```
/app
  __init__.py          — app factory, register blueprints
  models.py            — SQLAlchemy models
  /blueprints
    public.py          — landing page, eligibility checker
    applicant.py       — applicant portal routes
    assessor.py        — assessor portal routes (role-gated)
    auth.py            — login, register, logout
  /templates
    /public/
    /applicant/
      apply_step1.html ... apply_step7.html
      dashboard.html
    /assessor/
      applications.html
      application_detail.html
      dashboard.html
    /auth/
    base.html
  /static
  scoring.py           — weighted score calculation logic
  forms.py             — WTForms definitions
config.py              — config classes (Dev/Prod)
run.py                 — entry point
requirements.txt
```

---

## Data Model (key tables)

### `organisations`
- id, name, charity_number, org_type (charity/CIO/CIC/etc)
- annual_income, years_serving_homeless
- contact_name, contact_email, address

### `applications`
- id, org_id, status (draft | submitted | under_review | approved | rejected)
- funding_type (revenue | capital | both)
- revenue_amount_requested, capital_amount_requested
- local_authority_area, la_endorsement_confirmed
- submitted_at

### `application_sections` (JSON fields per section)
- skills_and_experience
- proposal_part1 (challenges + local evidence)
- proposal_part2 (project description)
- deliverability_part1 (milestones + governance)
- deliverability_part2 (risk register)
- cost_and_value (budget narrative)
- outcomes_and_impact

### `documents`
- id, application_id, type (budget_excel | project_plan | la_letter | risk_register | other)
- storage_path, filename, uploaded_at

### `assessments`
- id, application_id, assessor_id
- scores: { skills: 0-3, proposal1: 0-3, proposal2: 0-3, deliverability1: 0-3, deliverability2: 0-3, cost: 0-3, outcomes: 0-3 }
- weighted_total (calculated)
- recommendation (fund | reject | refer)
- notes, completed_at

### `users`
- id, email, role (applicant | assessor | admin)
- org_id (null for assessors)

---

## Scoring Logic

Weighted scoring out of 300:

| Criterion | Weight | Max raw score | Weighted max |
|---|---|---|---|
| Skills and experience | 10% | 3 | 30 |
| Proposal Part 1 | 10% | 3 | 30 |
| Proposal Part 2 | 30% | 3 | 90 |
| Deliverability Part 1 | 25% | 3 | 75 |
| Deliverability Part 2 | 5% | 3 | 15 |
| Cost and value | 10% | 3 | 30 |
| Outcomes and impact | 10% | 3 | 30 |

**Auto-reject rule**: any criterion scoring 0 → application rejected regardless of total.

```python
# scoring.py
WEIGHTS = {
    "skills": 10, "proposal1": 10, "proposal2": 30,
    "deliverability1": 25, "deliverability2": 5,
    "cost": 10, "outcomes": 10
}

def calculate_weighted_score(scores: dict) -> int:
    return sum(scores[k] * w for k, w in WEIGHTS.items())

def has_auto_reject(scores: dict) -> bool:
    return any(v == 0 for v in scores.values())
```

---

## Key User Flows

### Applicant Flow
1. **Eligibility checker** — gate on: England-based, VCFS org type, income ≤ £5m, ≥ 3 years experience
2. **Register** — email/password via Flask-Login + Flask-Bcrypt, create org profile
3. **Multi-step application form** — save as draft at each step, validation per section
4. **Document upload** — budget (Excel), project plan, LA support letter, risk register
5. **Review & submit** — read-only summary, confirm and submit (cannot withdraw after)
6. **Status tracking** — dashboard showing: submitted → under review → outcome

### Assessor Flow
1. **Application list** — filter by status, local authority area, funding type, score
2. **Application detail** — side-by-side: applicant answers + scoring form
3. **Score each criterion** — 0–3 per criterion with mandatory justification notes
4. **Flag for moderation** — if borderline or conflicted
5. **Funding allocation dashboard** — ranked list, running total against £37m budget

---

## Eligibility Rules (enforce at form entry)

- `org_type` must be one of: charity, CIO, CIC, community_benefit_society, parochial_church_council
- `annual_income` ≤ £5,000,000
- `years_serving_homeless` ≥ 3
- `operates_in_england` = true
- LA endorsement letter required before submission
- Capital funding: year 1 readiness checklist (planning permission, tenure, contractor)

---

## Key Dependencies (requirements.txt)

```
flask
flask-sqlalchemy
flask-migrate
flask-login
flask-bcrypt
flask-wtf
wtforms
psycopg2-binary
python-dotenv
govuk-frontend-jinja
govuk-frontend-wtf
boto3          # only if using S3 for file storage
```

## GOV.UK Frontend Setup

### Flask app factory (`app/__init__.py`)
```python
from jinja2 import ChoiceLoader, PackageLoader, PrefixLoader
from govuk_frontend_wtf.main import WTFormsHelpers

def create_app():
    app = Flask(__name__)

    app.jinja_loader = ChoiceLoader([
        PackageLoader("app"),
        PrefixLoader({
            "govuk_frontend_jinja": PackageLoader("govuk_frontend_jinja"),
            "govuk_frontend_wtf": PackageLoader("govuk_frontend_wtf"),
        }),
    ])

    WTFormsHelpers(app)
    # ... register blueprints, db, login_manager etc.
```

### Base template (`templates/base.html`)
```html
<!DOCTYPE html>
<html lang="en" class="govuk-template">
<head>
  <link rel="stylesheet" href="{{ url_for('static', filename='govuk-frontend.min.css') }}">
</head>
<body class="govuk-template__body">
  {% from 'govuk_frontend_jinja/components/skip-link/macro.html' import govukSkipLink %}
  {{ govukSkipLink({'text': 'Skip to main content', 'href': '#main-content'}) }}
  {% include 'partials/header.html' %}
  <div class="govuk-width-container">
    <main class="govuk-main-wrapper" id="main-content">
      {% block content %}{% endblock %}
    </main>
  </div>
  <script src="{{ url_for('static', filename='govuk-frontend.min.js') }}"></script>
</body>
</html>
```

### Form field example (`forms.py` + template)
```python
# forms.py
from govuk_frontend_wtf.wtforms_widgets import GovTextInput, GovSubmitInput, GovRadioInput
from wtforms import StringField, RadioField
from wtforms.validators import DataRequired

class OrganisationForm(FlaskForm):
    name = StringField("Organisation name", widget=GovTextInput(), validators=[DataRequired()])
    org_type = RadioField("Organisation type", widget=GovRadioInput(), choices=[
        ("charity", "Registered charity"),
        ("CIO", "Charitable Incorporated Organisation (CIO)"),
        ("CIC", "Community Interest Company (CIC)"),
    ])
    submit = SubmitField("Continue", widget=GovSubmitInput())
```

```html
<!-- template -->
{% from 'govuk_frontend_jinja/components/error-summary/macro.html' import govukErrorSummary %}
{% if form.errors %}
  {{ govukErrorSummary({'titleText': 'There is a problem', 'errorList': wtforms_errors(form)}) }}
{% endif %}
<form method="POST">
  {{ form.hidden_tag() }}
  {{ form.name(params={'label': {'text': 'Organisation name'}}) }}
  {{ form.org_type() }}
  {{ form.submit() }}
</form>
```

### GOV.UK Frontend assets
Download `govuk-frontend.min.css` and `govuk-frontend.min.js` from the [GOV.UK Frontend releases](https://github.com/alphagov/govuk-frontend/releases) and place in `app/static/`.

---

## Environment Variables

```
FLASK_SECRET_KEY=
DATABASE_URL=postgresql://user:pass@localhost/ehcf
UPLOAD_FOLDER=uploads/       # or S3 bucket name
```

---

## Grant Context

- **Fund**: Ending Homelessness in Communities Fund (EHCF)
- **Administrator**: Ministry of Housing, Communities & Local Government (MHCLG)
- **Total pot**: £37 million over 3 years
- **Per-award range**: £50k–£200k/year revenue; £50k–£200k capital (year 1 or 2 only)
- **Contact**: ehcf@communities.gov.uk
- **Prospectus**: https://www.gov.uk/guidance/ending-homelessness-in-communities-fund-prospectus