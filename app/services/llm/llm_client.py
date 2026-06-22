import json
from app.core.config import settings
from app.services.llm.types import LLMScoreResult, LLMProviderError
from app.services.llm.providers import deepseek_provider


def _build_prompt(text: str) -> str:
    return (
        "请你对输入文本做质量评分，返回严格JSON："
        '{"score": 0-100, "reason": "简短中文说明"}。\n'
        f"文本：{text}"
    )


def score_with_llm(text: str) -> LLMScoreResult:
    provider = settings.LLM_PROVIDER.lower().strip()
    if provider != "deepseek":
        raise LLMProviderError(f"Unsupported provider in step1: {provider}")

    raw = deepseek_provider.chat_completion(_build_prompt(text))
    data = json.loads(raw)

    return LLMScoreResult(
        score=float(data["score"]),
        reason=str(data["reason"]),
        raw_text=raw,
        provider=provider,
        model=settings.LLM_MODEL,
    )
