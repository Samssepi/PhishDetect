# modules/url_analysis.py

import re
import json
import os

# -------- Dataset Loading --------

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DATASET_DIR = os.path.join(BASE_DIR, "datasets")

# Suspicious TLDs
with open(os.path.join(DATASET_DIR, "suspicious_tlds.json"), "r", encoding="utf-8") as f:
    TLD_DATA = json.load(f)

# Homoglyph map
with open(os.path.join(DATASET_DIR, "homoglyph_map.json"), "r", encoding="utf-8") as f:
    HOMOGLYPH_DATA = json.load(f)

# Optional shorteners (if inside TLD json or separate later)
KNOWN_SHORTENERS = [
    "bit.ly",
    "tinyurl.com",
    "rb.gy",
    "t.co"
]


# -------- URL Extraction --------

def extract_urls(raw_email: str):
    """
    Extract URLs using regex.
    """
    url_pattern = r"(https?://[^\s]+)"
    return re.findall(url_pattern, raw_email)


# -------- Main Analysis --------

def analyze(raw_email: str):
    """
    URL analysis module.
    Detects suspicious patterns in embedded links.
    """

    signals = []
    score = 0

    urls = extract_urls(raw_email)
    text = raw_email.lower()

    for url in urls:

        # ---- Shortener Detection ----
        for shortener in KNOWN_SHORTENERS:
            if shortener in url:
                signals.append({
                    "title": "Suspicious URL Shortener",
                    "description": f"URL uses redirection service: {shortener}",
                    "category": "url",
                    "impact": 15
                })
                score += 15

        # ---- IP-Based URL ----
        if re.search(r"https?://\d{1,3}(\.\d{1,3}){3}", url):
            signals.append({
                "title": "IP Address Used in URL",
                "description": "URL contains direct IP address instead of domain name.",
                "category": "url",
                "impact": 20
            })
            score += 20

        # ---- Suspicious TLD ----
        domain_match = re.search(r"https?://([^/]+)", url)
        if domain_match:
            domain = domain_match.group(1)
            tld = domain.split(".")[-1]

            for risky_tld in TLD_DATA.get("high_risk_tlds", []):
                if tld == risky_tld.replace(".", ""):
                    signals.append({
                        "title": "Suspicious Top-Level Domain",
                        "description": f"Domain uses high-risk TLD: .{tld}",
                        "category": "url",
                        "impact": 15
                    })
                    score += 15

    # ---- Homoglyph Detection ----
    for legit_char, fake_chars in HOMOGLYPH_DATA.items():
        for fake in fake_chars:
            if fake in text:
                signals.append({
                    "title": "Unicode Homoglyph Detected",
                    "description": f"Possible lookalike character '{fake}' replacing '{legit_char}'",
                    "category": "url",
                    "impact": 15
                })
                score += 15

    return {
        "category": "url",
        "score": score,
        "indicators": signals
    }