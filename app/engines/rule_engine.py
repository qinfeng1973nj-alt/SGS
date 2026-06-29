from typing import Dict, Any


def score_by_rules(text: str) -> Dict[str, Any]:
    t = (text or "").strip()
    length = len(t)

    penalties = []
    base = {
        "content": 70.0,
        "structure": 70.0,
        "language": 70.0,
        "task": 70.0,
    }

    if length < 50:
        penalties.append("文本过短，信息不足")
        base["content"] -= 20
        base["task"] -= 15

    if length > 5000:
        penalties.append("文本过长，可能存在冗余")
        base["structure"] -= 10

    if "。" not in t and "." not in t:
        penalties.append("缺少句末标点，结构可读性受影响")
        base["structure"] -= 15
        base["language"] -= 10

    for k in base:
        base[k] = max(0.0, min(100.0, base[k]))

    return {
        "dimension_scores": base,
        "penalties": penalties,
        "engine": "rule_engine_v1",
    }
