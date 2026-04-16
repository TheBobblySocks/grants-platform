from programme_config import PROGRAMME

WEIGHTS = {k: v["weight"] for k, v in PROGRAMME["criteria"].items()}


def calculate_weighted_score(scores: dict) -> int:
    return sum(scores[k] * w for k, w in WEIGHTS.items())


def has_auto_reject(scores: dict) -> bool:
    return any(v == 0 for v in scores.values())


def get_recommendation(scores: dict, weighted_total: int) -> str:
    if has_auto_reject(scores):
        return "reject"
    thresholds = PROGRAMME["thresholds"]
    if weighted_total >= thresholds["fund"]:
        return "fund"
    if weighted_total >= thresholds["refer"]:
        return "refer"
    return "reject"
