# modules/authentication.py

import re
import json
import os


# -------- Dataset Loading --------

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DATASET_DIR = os.path.join(BASE_DIR, "datasets")

with open(os.path.join(DATASET_DIR, "legit_domain_baseline.json"), "r", encoding="utf-8") as f:
    BASELINE_DATA = json.load(f)


def extract_header_value(pattern: str, raw_email: str):
    match = re.search(pattern, raw_email, re.IGNORECASE)
    if match:
        return match.group(0)
    return None


def extract_domain_from_header(header_name: str, raw_email: str):
    pattern = rf"{header_name}:\s.*?@([^\s>]+)"
    match = re.search(pattern, raw_email, re.IGNORECASE)
    if match:
        return match.group(1).lower()
    return None


def analyze(raw_email: str):
    """
    Authentication analysis module.
    Detects SPF, DKIM, DMARC failures and domain inconsistencies.
    """

    indicators = []
    score = 0
    text = raw_email.lower()

    # -------- SPF --------
    spf_result = extract_header_value(r"spf=(fail|softfail|neutral|pass)", raw_email)
    if spf_result and "fail" in spf_result.lower():
        indicators.append({
            "title": "SPF Authentication Failed",
            "description": "Sender Policy Framework validation failed.",
            "category": "authentication",
            "impact": 20
        })
        score += 20

    # -------- DKIM --------
    dkim_result = extract_header_value(r"dkim=(fail|invalid|neutral|pass)", raw_email)
    if dkim_result and ("fail" in dkim_result.lower() or "invalid" in dkim_result.lower()):
        indicators.append({
            "title": "DKIM Signature Invalid",
            "description": "DomainKeys Identified Mail signature validation failed.",
            "category": "authentication",
            "impact": 20
        })
        score += 20

    # -------- DMARC --------
    dmarc_result = extract_header_value(r"dmarc=(fail|reject|quarantine|pass)", raw_email)
    if dmarc_result and ("fail" in dmarc_result.lower() or "reject" in dmarc_result.lower()):
        indicators.append({
            "title": "DMARC Alignment Failed",
            "description": "Domain-based Message Authentication failed alignment checks.",
            "category": "authentication",
            "impact": 25
        })
        score += 25

    # -------- Domain Mismatch --------
    from_domain = extract_domain_from_header("From", raw_email)
    return_path_domain = extract_domain_from_header("Return-Path", raw_email)

    if from_domain and return_path_domain and from_domain != return_path_domain:
        indicators.append({
            "title": "Sender Domain Mismatch",
            "description": f"From domain ({from_domain}) does not match Return-Path domain ({return_path_domain}).",
            "category": "authentication",
            "impact": 15
        })
        score += 15

    # -------- Baseline Domain Check --------
    baseline_domains = BASELINE_DATA.get("legit_domains", [])

    if from_domain and baseline_domains:
        if from_domain not in [d.lower() for d in baseline_domains]:
            indicators.append({
                "title": "Domain Not in Organizational Baseline",
                "description": f"Sender domain '{from_domain}' not found in approved baseline list.",
                "category": "authentication",
                "impact": 10
            })
            score += 10

    return {
        "category": "authentication",
        "score": score,
        "indicators": indicators
    }