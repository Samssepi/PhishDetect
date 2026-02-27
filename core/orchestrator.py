# core/orchestrator.py

from modules import authentication
from modules import url_analysis
from modules import intent

# Optional module – if infrastructure.py exists
try:
    from modules import infrastructure
    HAS_INFRA = True
except ImportError:
    HAS_INFRA = False

from core import scoring_engine


def analyze_email(raw_email: str):
    """
    Central orchestration pipeline.
    Calls independent detection modules
    and aggregates their results.
    """

    module_results = []

    # ---- Module Execution Pipeline ----
    modules = [
        authentication.analyze,
        url_analysis.analyze,
        intent.analyze
    ]

    if HAS_INFRA:
        modules.append(infrastructure.analyze)

    # ---- Execute Each Module Safely ----
    for module in modules:
        try:
            result = module(raw_email)
            if result:
                module_results.append(result)
        except Exception as e:
            # We do NOT break the pipeline if one module fails
            continue

    # ---- Aggregate & Score ----
    final_result = scoring_engine.aggregate(module_results)

    return final_result