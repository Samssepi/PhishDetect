# modules/intent.py

import re
import json
import os

# -------- Dataset Loading --------

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DATASET_DIR = os.path.join(BASE_DIR, "datasets")

with open(os.path.join(DATASET_DIR, "bec_intent_patterns.json"), "r", encoding="utf-8") as f:
    INTENT_DATA = json.load(f)


def analyze(raw_email: str):
    """
    Intent analysis module.
    Detects Business Email Compromise patterns,
    credential harvesting attempts,
    and urgency / coercion language.
    """

    indicators = []
    score = 0
    content = raw_email.lower()

    # Expected JSON structure:
    # {
    #   "financial_patterns": [],
    #   "credential_patterns": [],
    #   "urgency_patterns": []
    # }

    # -------- Financial Fraud --------
    for pattern in INTENT_DATA.get("financial_patterns", []):
        if re.search(pattern.lower(), content):
            indicators.append({
                "title": "Financial Fraud Intent Detected",
                "description": f"Pattern detected: '{pattern}'",
                "category": "intent",
                "impact": 20
            })
            score += 20

    # -------- Credential Harvesting --------
    for pattern in INTENT_DATA.get("credential_patterns", []):
        if re.search(pattern.lower(), content):
            indicators.append({
                "title": "Credential Harvesting Intent",
                "description": f"Pattern detected: '{pattern}'",
                "category": "intent",
                "impact": 15
            })
            score += 15

    # -------- Urgency / Coercion --------
    for pattern in INTENT_DATA.get("urgency_patterns", []):
        if re.search(pattern.lower(), content):
            indicators.append({
                "title": "Urgency / Coercion Language",
                "description": f"Urgency phrase detected: '{pattern}'",
                "category": "intent",
                "impact": 10
            })
            score += 10

    return {
        "category": "intent",
        "score": score,
        "indicators": indicators
    }