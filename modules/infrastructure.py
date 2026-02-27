# modules/infrastructure.py

import json
import os
import re


# -------- Dataset Loading --------

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DATASET_DIR = os.path.join(BASE_DIR, "datasets")

with open(os.path.join(DATASET_DIR, "risky_asn.json"), "r", encoding="utf-8") as f:
    ASN_DATA = json.load(f)


def analyze(raw_email: str):
    """
    Infrastructure analysis module.
    Detects risky hosting providers / ASN references
    from email Received headers.
    """

    indicators = []
    score = 0
    text = raw_email.lower()

    risky_asns = ASN_DATA.get("risky_asn", [])

    # -------- ASN / Hosting Detection --------
    for asn in risky_asns:
        if asn.lower() in text:
            indicators.append({
                "title": "High-Risk Infrastructure Detected",
                "description": f"Email originated from risky infrastructure provider: {asn}",
                "category": "infrastructure",
                "impact": 15
            })
            score += 15

    # -------- Suspicious Received Chain --------
    received_headers = re.findall(r"received:.*", raw_email, re.IGNORECASE)

    if len(received_headers) <= 1:
        indicators.append({
            "title": "Incomplete Mail Transfer Chain",
            "description": "Email contains unusually short or incomplete Received header chain.",
            "category": "infrastructure",
            "impact": 10
        })
        score += 10

    return {
        "category": "infrastructure",
        "score": score,
        "indicators": indicators
    }