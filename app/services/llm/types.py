from dataclasses import dataclass


class LLMError(Exception):
    """LLM 基类异常"""
    pass


class LLMTimeoutError(LLMError):
    pass


class LLMProviderError(LLMError):
    pass


@dataclass
class LLMScoreResult:
    score: float
    reason: str
    raw_text: str
    provider: str
    model: str
