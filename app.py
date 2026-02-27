from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import random

app = FastAPI(title="PhishScope Intelligence Engine")

# Allow frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------
# Request Model
# -------------------------
class EmailRequest(BaseModel):
    raw_email: str


# -------------------------
# Health Check
# -------------------------
@app.get("/health")
def health():
    return {"status": "operational"}



# -------------------------
# Core Analysis Logic (Mock for Now)
# -------------------------
def analyze_logic(raw_email: str):
    """
    Temporary mock scoring logic.
    Replace later with orchestrator + scoring engine.
    """

    from core.orchestrator import analyze_email as orchestrator_analyze
    return orchestrator_analyze(raw_email)

    # Basic signal simulation
    if "spf=fail" in raw_email.lower():
        score += 25
    if "dkim=fail" in raw_email.lower():
        score += 20
    if "dmarc=fail" in raw_email.lower():
        score += 25
    if "urgent" in raw_email.lower():
        score += 10
    if "verify" in raw_email.lower():
        score += 10
    if "http://" in raw_email.lower() or "https://" in raw_email.lower():
        score += 10

    score = min(score, 100)

    # Severity mapping
    if score >= 80:
        severity = "Critical"
    elif score >= 60:
        severity = "High"
    elif score >= 30:
        severity = "Medium"
    else:
        severity = "Low"

    confidence = min(score + random.randint(5, 15), 100)

    return {
        "risk_score": score,
        "severity": severity,
        "confidence": confidence
    }


# -------------------------
# Analyze via JSON
# -------------------------
@app.post("/analyze")
def analyze_email(request: EmailRequest):
    if not request.raw_email.strip():
        raise HTTPException(status_code=400, detail="Empty email content")

    return analyze_logic(request.raw_email)


# -------------------------
# Analyze via .eml file
# -------------------------
@app.post("/analyze-file")
async def analyze_file(file: UploadFile = File(...)):
    if not file.filename.endswith(".eml"):
        raise HTTPException(status_code=400, detail="Only .eml files supported")

    content = await file.read()
    raw_email = content.decode(errors="ignore")

    from core.orchestrator import analyze_email
    return analyze_email(raw_email)