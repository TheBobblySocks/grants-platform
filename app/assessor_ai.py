"""AI-powered automatic assessment layer.

Called immediately after an application is submitted. Uses Claude to:
  1. Read the applicant's answers and the grant's scoring criteria.
  2. Produce a score (0-max) for each criterion.
  3. Persist an Assessment row with scores_json, notes_json, weighted_total,
     and a recommendation.

The AI assessor user (assessor_id) is a synthetic system account upserted on
first run so the non-nullable FK is satisfied without a schema change.
"""

from __future__ import annotations

import json
import logging
from datetime import UTC, datetime

import anthropic

from app.extensions import db
from app.models import (
    Application,
    Assessment,
    AssessmentRecommendation,
    User,
    UserRole,
)
from app.scoring import calculate_weighted_score, has_auto_reject

log = logging.getLogger(__name__)

_AI_ASSESSOR_EMAIL = "ai-assessor@system.local"
_MODEL = "claude-sonnet-4-6"


def _get_or_create_ai_user() -> User:
    """Return the synthetic AI assessor user, creating it if absent."""
    user = User.query.filter_by(email=_AI_ASSESSOR_EMAIL).first()
    if user is None:
        user = User(
            email=_AI_ASSESSOR_EMAIL,
            password_hash="!",  # unusable password -- account cannot log in
            role=UserRole.ASSESSOR,
        )
        db.session.add(user)
        db.session.flush()
        log.info("Created synthetic AI assessor user (id=%s)", user.id)
    return user


def _build_prompt(application: Application, criteria: list[dict]) -> str:
    """Render a structured prompt for Claude from the application answers."""
    answers = application.answers_json or {}
    answers_block = "
".join(
        f"  {key}: {json.dumps(value, ensure_ascii=False)}"
        for key, value in answers.items()
    ) or "  (no answers provided)"

    criteria_block = "
".join(
        "  - id={!r}, label={!r}, max={}, weight={}{}".format(
            c["id"],
            c["label"],
            c["max"],
            c["weight"],
            " [AUTO-REJECT if zero]" if c.get("auto_reject_on_zero") else "",
        )
        for c in criteria
    )

    return f"""You are an expert grant assessor for the {application.grant.name} programme.

## Application answers
{answers_block}

## Scoring criteria
Score each criterion from 0 to its stated max. Return ONLY valid JSON with no prose outside it.

{criteria_block}

## Required JSON output (strictly this shape)
{{
  "scores": {{"<criterion_id>": <int>, ...}},
  "notes": {{"<criterion_id>": "<rationale string>", ...}},
  "gap_analysis": "<brief overall narrative of strengths and gaps>",
  "recommendation": "fund" | "reject" | "refer"
}}

Scoring guide (adjust if max != 3): 0 = does not meet threshold, 1 = partially meets, 2 = meets, 3 = exceeds.
Auto-reject criteria must score > 0 unless the evidence is genuinely absent.
Base the recommendation on the weighted total relative to max and any auto-reject flags."""


def _parse_response(text: str) -> dict:
    """Extract the JSON block from Claude's response."""
    text = text.strip()
    if text.startswith("```"):
        lines = text.splitlines()
        inner = lines[1:-1] if lines[-1].strip() == "```" else lines[1:]
        text = "
".join(inner)
    return json.loads(text)


def assess_application(application_id: int) -> Assessment | None:
    """Run AI assessment for the given application.

    Creates and commits an Assessment row. Returns the Assessment on success,
    or None if the application is missing, has no criteria, or parsing fails.
    Idempotent: returns the existing Assessment if one already exists.
    """
    application = db.session.get(Application, application_id)
    if application is None:
        log.warning("assess_application: application %s not found", application_id)
        return None

    existing = Assessment.query.filter_by(application_id=application_id).first()
    if existing is not None:
        log.info("assess_application: application %s already assessed", application_id)
        return existing

    criteria: list[dict] = application.grant.config_json.get("criteria", [])
    if not criteria:
        log.warning(
            "assess_application: grant %s has no criteria", application.grant.slug
        )
        return None

    ai_user = _get_or_create_ai_user()
    prompt = _build_prompt(application, criteria)

    client = anthropic.Anthropic()
    log.info("assess_application: calling Claude for application %s", application_id)
    message = client.messages.create(
        model=_MODEL,
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}],
    )
    raw = message.content[0].text

    try:
        parsed = _parse_response(raw)
    except (json.JSONDecodeError, KeyError, IndexError) as exc:
        log.error(
            "assess_application: failed to parse Claude response: %s
%s", exc, raw
        )
        return None

    scores: dict[str, int] = {
        k: int(v) for k, v in parsed.get("scores", {}).items()
    }
    notes: dict[str, str] = parsed.get("notes", {})
    gap_analysis: str = parsed.get("gap_analysis", "")
    raw_recommendation: str = parsed.get("recommendation", "refer")

    auto_rejected = has_auto_reject(scores, criteria)
    weighted_total = calculate_weighted_score(scores, criteria)

    if auto_rejected:
        recommendation = AssessmentRecommendation.REJECT
    else:
        try:
            recommendation = AssessmentRecommendation(raw_recommendation)
        except ValueError:
            recommendation = AssessmentRecommendation.REFER

    assessment = Assessment(
        application_id=application_id,
        assessor_id=ai_user.id,
        scores_json=scores,
        notes_json={**notes, "_gap_analysis": gap_analysis},
        weighted_total=weighted_total,
        recommendation=recommendation,
        completed_at=datetime.now(UTC),
    )
    db.session.add(assessment)
    db.session.commit()

    log.info(
        "assess_application: application %s -> weighted_total=%s recommendation=%s",
        application_id,
        weighted_total,
        recommendation.value,
    )
    return assessment
