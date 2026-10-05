"""Transparent, assumption-driven FDSE ROI model."""
from __future__ import annotations

from dataclasses import dataclass

from .contracts import validate_document

IBM_2025_GLOBAL_BREACH_COST = {
    "title": "IBM Cost of a Data Breach Report 2025",
    "year": 2025,
    "url": "https://www.ibm.com/reports/data-breach",
    "metric": "Global average cost of a data breach; informational benchmark only.",
}


@dataclass(frozen=True)
class ROIInput:
    analysis_id: str
    investment_usd: float
    baseline_annual_loss_usd: float
    risk_reduction_assumption: float

    def validate(self) -> None:
        if self.investment_usd < 0 or self.baseline_annual_loss_usd < 0:
            raise ValueError("monetary values cannot be negative")
        if not 0 <= self.risk_reduction_assumption <= 1:
            raise ValueError("risk reduction must be between 0 and 1")


def calculate_roi(inputs: ROIInput) -> dict:
    inputs.validate()
    avoided = inputs.baseline_annual_loss_usd * inputs.risk_reduction_assumption
    roi_multiple = ((avoided - inputs.investment_usd) / inputs.investment_usd) if inputs.investment_usd else 0.0
    payback = (inputs.investment_usd / avoided * 12) if avoided else None
    sensitivity = []
    for reduction in (0.10, 0.25, 0.50):
        value = inputs.baseline_annual_loss_usd * reduction
        multiple = ((value - inputs.investment_usd) / inputs.investment_usd) if inputs.investment_usd else 0.0
        sensitivity.append({"risk_reduction": reduction, "expected_loss_avoided_usd": round(value, 2), "roi_multiple": round(multiple, 4)})
    result = {
        "schema_version": "1.0.0",
        "analysis_id": inputs.analysis_id,
        "investment_usd": round(inputs.investment_usd, 2),
        "baseline_annual_loss_usd": round(inputs.baseline_annual_loss_usd, 2),
        "risk_reduction_assumption": inputs.risk_reduction_assumption,
        "expected_loss_avoided_usd": round(avoided, 2),
        "roi_multiple": round(roi_multiple, 4),
        "payback_months": round(payback, 2) if payback is not None else None,
        "assumptions": [
            "Baseline annual loss is a customer/engagement assumption, not a universal breach-cost benchmark.",
            "Risk reduction is an explicit scenario assumption; detection latency is not treated as a causal proxy for dollars avoided.",
        ],
        "benchmark_sources": [IBM_2025_GLOBAL_BREACH_COST],
        "sensitivity": sensitivity,
    }
    validate_document("roi-analysis", result)
    return result
