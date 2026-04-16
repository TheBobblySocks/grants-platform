---
name: stream-c
description: Context loader for Stream C (Assessor and Scoring). Read before working on the assessor queue, application detail view, scoring form, allocation dashboard, or decision recording.
---

# Stream C — Assessor & Scoring

## What This Stream Owns

**Edit freely:**
- `app/assessor.py` — /assess routes (queue, detail, score-save, allocation, decision)
- `app/assessor_ai.py` — AI-assisted assessment (provider wrapper with real/mock)
- `app/scoring.py` — pure scoring helpers (weighted total, auto-reject, etc.)
- `app/award_rules.py` — award range derivation and scale-up eligibility
- `app/templates/assessor/**` — queue.html, application_detail.html, allocation.html
- `tests/test_scoring.py`
- `tests/test_assessor.py`
- `tests/test_assessor_ai.py`
- `tests/test_award_rules.py`

**Do NOT edit:** auth.py, applicant.py, forms_runner.py, models.py, uploads.py,
seed.py, conftest.py, base.html, or any file not listed above.

## Public API This Stream Exposes

```python
from app.scoring import (
    calculate_weighted_score, has_auto_reject,
    missing_criteria, max_weighted_total,
)
```

Route names other streams may `url_for`:
- `assessor.queue`, `assessor.detail`, `assessor.save_score`,
  `assessor.allocation`, `assessor.record_decision`

## Imports From Other Streams

```python
# Stream A (auth decorators)
from app.auth import assessor_required, login_required

# Stream B (form runner + templates)
from app.forms_runner import list_pages
# Also renders templates/forms/summary.html in the detail view

# Stream D (models)
from app.models import (
    Application, Assessment, User, Grant, Form, Organisation,
    ApplicationStatus, AssessmentRecommendation,
)
from app.extensions import db

# Stream D (uploads) — may be stubbed
from app.uploads import list_documents, document_url
```

## Current Implementation Status

Read `app/assessor.py` and `app/scoring.py` to check. As of last scan:
- **assessor.py** — **fully implemented** (queue, detail, score-save, flag, decision, allocation, email notification)
- **scoring.py** — **fully implemented** (calculate_weighted_score, has_auto_reject, missing_criteria, max_weighted_total)
- **assessor_ai.py** — **fully implemented** (AI assessment with Claude API, prompt construction, response parsing)
- **award_rules.py** — **fully implemented** (award range derivation, scale-up eligibility)

## Pending Work (check PLAN.md for latest)

- P3.1-P3.6 items may need refinement based on testing
- B2 filters (status, LA area, funding type, score) on the queue
- Integration with uploads (show documents in detail view)
- Moderation workflow (B9 — stretch)

## Key Patterns

- **Scoring is pure.** `scoring.py` takes (scores_dict, criteria_list), returns numbers.
  No DB, no Flask context.
- **Criteria come from grant config.** `grant.config_json["criteria"]` has id, label,
  weight, max, auto_reject_on_zero. Never hardcode these.
- **Scores payload:** `{criterion_id: int}` — keys match criteria[].id exactly.
- **Notes payload:** `{criterion_id: str}` — per-criterion justification text.
- **Recommendations:** fund | reject | refer (AssessmentRecommendation enum).
- **AI is triage support.** Frame as "AI-assisted" with human confirmation.
  Show provenance, evidence snippets, confidence. Capture assessor overrides.
- **WTForms for the scoring form** — fields generated dynamically from criteria config.
- **Allocation dashboard** ranks by weighted_total desc, running sum against budget.
