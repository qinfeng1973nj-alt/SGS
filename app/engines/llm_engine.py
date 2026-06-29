from typing import Dict, Any


def score_by_llm_stub(text: str) -> Dict[str, Any]:
    # v0.1.9: stub only, deterministic output for CI stability
    return {
        "dimension_scores": {
            "content": 75.0,
            "structure": 75.0,
            "language": 75.0,
            "task": 75.0,
        },
        "rationale": {
            "content": "观点基本完整，但论证深度一般。",
            "structure": "段落组织较清晰，过渡可加强。",
            "language": "表达基本通顺，细节规范性可提升。",
            "task": "任务要求基本覆盖。",
        },
        "engine": "llm_stub_v1",
    }
