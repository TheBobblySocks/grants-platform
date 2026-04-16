---
name: stream-d
description: Context loader for Stream D (Platform, Data and Uploads). Read before working on models, seed data, uploads, dev fixtures, config, Docker, or static assets.
---

# Stream D — Platform, Data & Uploads

## What This Stream Owns

**Edit freely:**
- `app/models.py` — SQLAlchemy models + shared enums (additive changes only)
- `app/extensions.py` — db, login_manager, csrf singletons
- `app/public.py` — landing page, /healthz, GOV.UK asset routing
- `app/uploads.py` — file save, serve, authorise; Document row creation
- `seed.py` — grant + form loading from disk
- `seed/grants/*.json` — grant config files
- `seed/dev_fixtures.py` (create if needed) — dev test data
- `tests/conftest.py` — shared fixtures
- `tests/test_seed.py`
- `tests/test_uploads.py`
- `tests/test_smoke.py`
- `config.py`
- `Dockerfile`, `docker-compose.yml`
- `app/static/**` — GOV.UK Frontend CSS/JS/fonts/images

**Do NOT edit:** auth.py, applicant.py, assessor.py, scoring.py, forms_runner.py,
or templates outside of partials/ unless coordinated.

## Public API This Stream Exposes

```python
# Models and enums — everyone imports these
from app.models import (
    User, Organisation, Grant, Form, Application, Document, Assessment,
    UserRole, GrantStatus, FormKind, ApplicationStatus, AssessmentRecommendation,
)
from app.extensions import db, login_manager, csrf

# Uploads — Streams A and C import these
from app.uploads import save_upload, list_documents, document_url
```

Test fixtures (in tests/conftest.py):
```python
@pytest.fixture
def app(): ...           # Test app with TestConfig
@pytest.fixture
def db(): ...            # SQLAlchemy database instance
@pytest.fixture
def client(): ...        # Flask test client
@pytest.fixture
def seeded_grant(): ...  # EHCF grant with one criterion
# TODO: add these
# applicant_user, assessor_user, submitted_application
```

## Imports From Other Streams

**None.** Stream D is upstream of everyone. It imports nothing from other streams.

## Current Implementation Status

As of last scan:
- **models.py** — **fully implemented** (all models and enums)
- **extensions.py** — **fully implemented**
- **public.py** — **fully implemented** (landing page, healthz, asset routing)
- **uploads.py** — **MOSTLY STUBBED** (save_upload and document_url raise NotImplementedError;
  list_documents returns empty list)
- **seed.py** — **fully implemented** (validation, upsert, CLI)
- **conftest.py** — **basic fixtures** (app, db, client, seeded_grant)
- **config.py** — **fully implemented**

## Pending Work (check PLAN.md for latest)

- P2.3 **Uploads implementation** — save_upload, list_documents, document_url,
  serve_document route (authz-gated)
- **Dev fixtures** — applicant_user, assessor_user, submitted_application fixtures
  for conftest.py. Also `python seed.py --dev` flag for demo data.
- P4.1 **Second grant** — Common Ground Award: seed/grants/common-ground.json +
  app/forms/common-ground-application-v1.json
- **Model additions** if other streams need them (Organisation.la_area, etc.)
- Docker polish — prod `docker compose up` serves a browser-visible demo

## Key Patterns

- **Enums are centralised.** Define once in models.py, import everywhere.
  Never use string literals for status checks.
- **Grant config is the single source of truth** for grant-specific data.
  Eligibility rules, criteria, weights, award ranges — all in config_json.
- **Seed is idempotent.** Running `seed.py` twice doesn't duplicate data.
  Uses upsert logic keyed on grant slug.
- **Uploads go to UPLOAD_FOLDER/<application_id>/<kind>/<filename>.**
  save_upload creates the Document row. list_documents returns Document objects.
  document_url returns the URL for the authz-gated download route.
- **Fixtures are shared.** Other streams' tests import from conftest.py.
  Don't make other streams invent their own test users.
