import logging

from app.core.config import settings
from app.services.llm_client import (
    score_with_llm,
    LLMTimeoutError,
    LLMAuthError,
)

logger = logging.getLogger(__name__)


def rule_score(text: str) -> dict:
    score = min(len(text), 100)
    return {
        "score": score,
        "channel": "rule",
        "reason": "rule_based",
    }


def llm_score(text: str) -> dict:
    return score_with_llm(text=text, api_key=settings.LLM_API_KEY)


def score_text(text: str) -> dict:
    if settings.ENABLE_LLM:
        try:
            result = llm_score(text)
            logger.info("score.success channel=llm")
            return result
        except LLMTimeoutError as e:
            logger.warning("score.fallback reason=llm_timeout error=%s", str(e))
            return rule_score(text)
        except LLMAuthError as e:
            logger.warning("score.fallback reason=llm_auth error=%s", str(e))
            return rule_score(text)

    logger.info("score.success channel=rule reason=llm_disabled")
    return rule_score(text)
