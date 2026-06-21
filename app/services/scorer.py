from app.core.config import settings


def rule_score(text: str) -> dict:
    # 这里保持你现有规则逻辑即可；以下是一个稳定占位实现
    score = min(len(text), 100)
    return {
        "score": score,
        "channel": "rule",
        "reason": "rule_based",
    }


def llm_score(text: str) -> dict:
    """
    LLM桩函数（当前不发起真实外部调用）
    - 有 key：返回 llm 通道占位结果
    - 无 key：抛错，触发上层回退
    """
    if not settings.LLM_API_KEY:
        raise RuntimeError("LLM_API_KEY is missing")

    # 占位输出：后续再替换为真实LLM调用
    return {
        "score": 88,
        "channel": "llm",
        "reason": "llm_stub",
    }


def score_text(text: str) -> dict:
    if settings.ENABLE_LLM:
        try:
            return llm_score(text)
        except Exception:
            return rule_score(text)
    return rule_score(text)

