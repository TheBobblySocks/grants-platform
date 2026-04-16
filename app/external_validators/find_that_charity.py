"""Validator backed by findthatcharity.uk — the free UK register aggregator.

Why this source:

* **Free & keyless.** No registration, no per-org subscription. Safe to
  integrate at hackathon speed.
* **Open data.** findthatcharity.uk aggregates the four official UK
  registers — Charity Commission for England & Wales (CCEW), OSCR (Scotland),
  CCNI (Northern Ireland) and Companies House — under a single
  Organisation Identifier (``GB-CHC-``, ``GB-SC-``, ``GB-NIC-``,
  ``GB-COH-``). Each record exposes a stable JSON document at
  ``/orgid/<id>.json``.
* **Reputable.** Maintained by David Kane, widely used across UK civic-tech
  projects; data is refreshed from the official downloads.

For production use with higher SLAs we would fall through to the primary
registers (Charity Commission API / Companies House API); see
``companies_house.py`` for the pattern. FindThatCharity is sufficient for
MVP triage and gives us a single call that covers both charity and company
numbers.
"""

from __future__ import annotations

import logging
import re
from typing import Any

from app.external_validators.base import (
    DEFAULT_TIMEOUT_SECONDS,
    ExternalValidatorError,
    JsonFetcher,
    ValidationResult,
    http_get_json,
)

log = logging.getLogger(__name__)

# Map the ``org_type`` values used across UK grant forms to the register
# prefixes Find That Charity understands. A list means "try each in order";
# charities may sit on any of the three national charity registers, and
# most grants let applicants self-declare one umbrella category.
_ORG_TYPE_PREFIXES: dict[str, list[str]] = {
    "charity": ["GB-CHC", "GB-SC", "GB-NIC"],
    "CIO": ["GB-CHC", "GB-SC", "GB-NIC"],
    "CIC": ["GB-COH"],
    "CBS": ["GB-COH"],
    "PCC": ["GB-CHC"],
    # Common synonyms so we degrade gracefully if a grant uses lowercase
    # values or longer-form labels.
    "cio": ["GB-CHC", "GB-SC", "GB-NIC"],
    "cic": ["GB-COH"],
    "cbs": ["GB-COH"],
    "pcc": ["GB-CHC"],
    "company": ["GB-COH"],
    "limited_company": ["GB-COH"],
}

# Fallbacks when ``org_type`` is missing or unrecognised — charities first
# (by far the most common VCFS applicant shape), then companies.
_FALLBACK_PREFIXES: list[str] = ["GB-CHC", "GB-COH", "GB-SC", "GB-NIC"]

# Prefixes we can detect inside the raw user input, e.g. the applicant
# pasted "GB-CHC-1234567" or "CHC1234567". Key = compact form after
# stripping non-alphanumerics and upper-casing, value = canonical prefix.
_COMPACT_PREFIXES: dict[str, str] = {
    "GBCHC": "GB-CHC",
    "GBSC": "GB-SC",
    "GBNIC": "GB-NIC",
    "GBCOH": "GB-COH",
    "CHC": "GB-CHC",
    "SC": "GB-SC",
    "NIC": "GB-NIC",
    "COH": "GB-COH",
}

# Company numbers may include a leading alpha prefix (SC for Scotland,
# NI for Northern Ireland, etc.) so we keep letters when stripping.
_NON_IDENTIFIER = re.compile(r"[^A-Z0-9]")


class FindThatCharityValidator:
    """Look up a UK charity or company registration number.

    Parameters
    ----------
    fetcher
        JSON GET function — defaults to :func:`app.external_validators.base.http_get_json`.
        Tests inject a fake to avoid hitting the network.
    timeout
        Per-request timeout in seconds. Each candidate prefix is an
        independent request, so worst-case wall-clock is
        ``timeout * len(prefixes)``; we keep this low (seconds) and rely on
        the blueprint's skip-on-error semantics if everything times out.
    base_url
        Override for self-hosted mirrors or tests.
    """

    name = "find_that_charity"

    def __init__(
        self,
        *,
        fetcher: JsonFetcher = http_get_json,
        timeout: float = DEFAULT_TIMEOUT_SECONDS,
        base_url: str = "https://findthatcharity.uk",
    ) -> None:
        self._fetch = fetcher
        self._timeout = timeout
        self._base_url = base_url.rstrip("/")

    # ---- public API ------------------------------------------------------

    def validate(self, value: str, context: dict[str, Any]) -> ValidationResult:
        candidates = self._candidates(value, context)
        if not candidates:
            return ValidationResult(
                ok=False,
                message="Enter a valid charity or company registration number",
            )

        for orgid in candidates:
            url = f"{self._base_url}/orgid/{orgid}.json"
            try:
                body = self._fetch(url, self._timeout)
            except ExternalValidatorError as exc:
                # A single candidate failing transport-wise shouldn't stop us
                # trying the others — but if the *first* call errored we likely
                # have a systemic outage. Log once and degrade to "skipped".
                log.warning("find_that_charity lookup failed for %s: %s", orgid, exc)
                return ValidationResult(
                    ok=True,
                    skipped=True,
                    message=(
                        "We couldn't verify this registration number right now. "
                        "You can continue; we'll check it again when you submit."
                    ),
                    metadata={"attempted": list(candidates)},
                )

            if body is not None:
                return ValidationResult(
                    ok=True,
                    message=f"Matched: {self._org_name(body)}",
                    metadata={
                        "orgid": orgid,
                        "name": self._org_name(body),
                        "source": self._base_url,
                    },
                )

        return ValidationResult(
            ok=False,
            message=(
                "We couldn't find a UK registered organisation with that number. "
                "Check the number and that your organisation type is correct."
            ),
            metadata={"attempted": list(candidates)},
        )

    # ---- helpers ---------------------------------------------------------

    def _candidates(self, raw_value: str, context: dict[str, Any]) -> list[str]:
        """Build the ordered list of full ``GB-XXX-<num>`` IDs to try."""
        compact = _NON_IDENTIFIER.sub("", str(raw_value or "").upper())
        if not compact:
            return []

        # If the user's input already carries a recognised prefix, trust it.
        for compact_prefix, canonical in _COMPACT_PREFIXES.items():
            if compact.startswith(compact_prefix):
                remainder = compact[len(compact_prefix) :]
                if remainder:
                    return [f"{canonical}-{remainder}"]

        prefixes = self._prefixes_for(context.get("org_type"))
        # De-duplicate while preserving order (dict preserves insertion order
        # on py3.7+; cheaper than a set-based filter for tiny lists).
        seen: dict[str, None] = {}
        for prefix in prefixes:
            seen.setdefault(prefix, None)
        return [f"{prefix}-{compact}" for prefix in seen]

    @staticmethod
    def _prefixes_for(org_type: Any) -> list[str]:
        if isinstance(org_type, str) and org_type:
            # Exact match first (covers the grant-canonical values in
            # ``_ORG_TYPE_PREFIXES``), then lowercase, then fallback.
            if org_type in _ORG_TYPE_PREFIXES:
                return _ORG_TYPE_PREFIXES[org_type]
            if org_type.lower() in _ORG_TYPE_PREFIXES:
                return _ORG_TYPE_PREFIXES[org_type.lower()]
        return _FALLBACK_PREFIXES

    @staticmethod
    def _org_name(body: dict[str, Any]) -> str:
        """Pull a human-readable name out of Find That Charity's JSON.

        Find That Charity normalises names under ``name`` for most records;
        we walk common fallbacks so new register shapes don't silently return
        "(unnamed organisation)".
        """
        for key in ("name", "organisation_name", "charity_name", "title"):
            value = body.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()
        # Some API shapes nest the name under "organisation" or "data".
        for nested_key in ("organisation", "data"):
            nested = body.get(nested_key)
            if isinstance(nested, dict):
                for key in ("name", "organisation_name", "charity_name", "title"):
                    value = nested.get(key)
                    if isinstance(value, str) and value.strip():
                        return value.strip()
        return "(unnamed organisation)"
