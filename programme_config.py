"""
programme_config.py — Single source of truth for grant programme parameters.
Swap this file to adapt the platform for a different grant programme.
"""

PROGRAMME = {
    "name": "Ending Homelessness in Communities Fund",
    "short_name": "EHCF",
    "administrator": "MHCLG",
    "total_pot": 37_000_000,
    "revenue_min": 50_000,
    "revenue_max": 200_000,
    "capital_min": 50_000,
    "capital_max": 200_000,
    "contact_email": "ehcf@communities.gov.uk",
    "years": "2026-2029",
    "eligibility": {
        "max_annual_income": 5_000_000,
        "min_years_experience": 3,
        "org_types": [
            "charity",
            "CIO",
            "CIC",
            "community_benefit_society",
            "parochial_church_council",
        ],
        "org_type_labels": {
            "charity": "Registered charity",
            "CIO": "Charitable Incorporated Organisation (CIO)",
            "CIC": "Community Interest Company (CIC)",
            "community_benefit_society": "Community benefit society",
            "parochial_church_council": "Parochial church council",
        },
    },
    "criteria": {
        "skills": {
            "label": "Skills and Experience",
            "weight": 10,
            "guidance": (
                "Demonstrate your organisation's relevant expertise, track record "
                "working with people experiencing homelessness, and staffing capacity "
                "to deliver the proposed project."
            ),
        },
        "proposal1": {
            "label": "Proposal Part 1 - Local Evidence",
            "weight": 10,
            "guidance": (
                "Set out the homelessness challenge in your local area. Use credible "
                "local data and evidence to demonstrate the need your project will address."
            ),
        },
        "proposal2": {
            "label": "Proposal Part 2 - Project Design",
            "weight": 30,
            "guidance": (
                "Describe your proposed project in detail. Explain what you will do, "
                "who will benefit, and why this approach is appropriate to the identified need."
            ),
        },
        "deliverability1": {
            "label": "Deliverability - Milestones and Governance",
            "weight": 25,
            "guidance": (
                "Set out your project milestones and timeline. Describe your governance "
                "arrangements and demonstrate your organisation's capacity to deliver."
            ),
        },
        "deliverability2": {
            "label": "Deliverability - Risk Register",
            "weight": 5,
            "guidance": (
                "Identify the key risks to your project and describe credible, "
                "proportionate mitigation measures for each."
            ),
        },
        "cost": {
            "label": "Cost and Value for Money",
            "weight": 10,
            "guidance": (
                "Provide a detailed budget breakdown. Explain and justify each cost, "
                "and demonstrate that your project represents value for public money."
            ),
        },
        "outcomes": {
            "label": "Outcomes and Impact",
            "weight": 10,
            "guidance": (
                "Describe the outcomes your project will achieve. Explain how you will "
                "measure them and demonstrate they are realistic within the grant period."
            ),
        },
    },
    "sections": [
        {"key": "skills_and_experience",  "criterion": "skills",          "title": "Skills and Experience",                    "step": 1},
        {"key": "proposal_part1",         "criterion": "proposal1",       "title": "Proposal Part 1 - Local Evidence",         "step": 2},
        {"key": "proposal_part2",         "criterion": "proposal2",       "title": "Proposal Part 2 - Project Design",         "step": 3},
        {"key": "deliverability_part1",   "criterion": "deliverability1", "title": "Deliverability - Milestones and Governance","step": 4},
        {"key": "deliverability_part2",   "criterion": "deliverability2", "title": "Deliverability - Risk Register",            "step": 5},
        {"key": "cost_and_value",         "criterion": "cost",            "title": "Cost and Value for Money",                 "step": 6},
        {"key": "outcomes_and_impact",    "criterion": "outcomes",        "title": "Outcomes and Impact",                      "step": 7},
    ],
    "thresholds": {
        "fund": 210,
        "refer": 150,
    },
}
