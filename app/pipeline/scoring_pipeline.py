from typing import Dict, Any
from app.domain.rubric import rubric_weights, validate_rubric
from app.engines.rule_engine import score_by_rules
from app.engines.llm_engine import score_by_llm_stub
from app.services.explainer import build_explanations


def _fuse(rule_scores: Dict[str, float], llm_scores: Dict[str, float]) -> Dict[str, float]:
    # v0.1.9 fusion policy: 60% rule + 40% llm
    fused = {}
    for k in rule_scores.keys():
        fused[k] = rule_scores[k] * 0.6 + llm_scores.get(k, rule_scores[k]) * 0.4
    return fused


def run_scoring_pipeline(text: str) -> Dict[str, Any]:
    validate_rubric()

    rule_out = score_by_rules(text)
    llm_out = score_by_llm_stub(text)

    fused = _fuse(rule_out["dimension_scores"], llm_out["dimension_scores"])
    weights = rubric_weights()

    total = 0.0
    for k, s in fused.items():
        total += s * weights[k]

    explanation = build_explanations(
        fused_scores=fused,
        llm_rationale=llm_out.get("rationale", {}),
        penalties=rule_out.get("penalties", []),
    )

    return {
        "total_score": round(total, 2),
        "dimension_scores": {k: round(v, 2) for k, v in fused.items()},
        "explanation": explanation,
        "meta": {
            "rule_engine": rule_out.get("engine"),
            "llm_engine": llm_out.get("engine"),
            "fusion": "0.6_rule_0.4_llm",
            "rubric_version": "v1",
        },
    }
