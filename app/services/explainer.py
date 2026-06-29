from typing import Dict, Any, List


def build_explanations(
    fused_scores: Dict[str, float],
    llm_rationale: Dict[str, str],
    penalties: List[str],
) -> Dict[str, Any]:
    details = {}
    for k, s in fused_scores.items():
        details[k] = {
            "score": round(s, 2),
            "reason": llm_rationale.get(k, "暂无说明"),
        }

    return {
        "details": details,
        "penalties": penalties,
    }
