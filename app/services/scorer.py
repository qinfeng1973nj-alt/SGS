from app.core.config import settings


def rule_score(text: str) -> dict:
    # 简单规则：先保证稳定，后续再替换成真实策略
    score = 80 if len(text.strip()) >= 10 else 60
    return {"score": score, "channel": "rule"}


def llm_score(text: str) -> dict:
    # 占位实现：没有 key 就抛错，交给上层回退
    if not settings.llm_api_key:
        raise RuntimeError("LLM_API_KEY is missing")
    # 后续在这里接真实 LLM 调用
    return {"score": 85, "channel": "llm"}


def score_text(text: str) -> dict:
    if settings.enable_llm:
        try:
            return llm_score(text)
        except Exception:
            return rule_score(text)
    return rule_score(text)
