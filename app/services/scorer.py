import logging
from typing import Any, Dict

from app.core.config import settings
from app.services.llm_client import (
    score_with_llm,
    LLMTimeoutError,
    LLMAuthError,
)

logger = logging.getLogger(__name__)


def rule_score(text: str) -> Dict[str, Any]:
    """
    规则打分兜底逻辑
    """
    t = text or ""
    score = min(len(t), 100)
    return {
        "score": float(score),
        "channel": "rule",
        "reason": "rule_based",
    }


def llm_score(text: str) -> Dict[str, Any]:
    """
    LLM 打分封装：
    - 调用 llm_client
    - 将结果统一为 scorer 对外结构：score/channel/reason
    """
    result = score_with_llm(
        text=text,
        api_key=settings.LLM_API_KEY,
    )

    # 兼容两类返回：
    # 1) dict: {"score":..., "reason":..., "channel":...}
    # 2) 对象: result.score / result.reason / result.provider
    if isinstance(result, dict):
        score = float(result.get("score", 0))
        reason = str(result.get("reason", "llm_based"))
        channel = str(result.get("channel", "llm"))
        return {
            "score": max(0.0, min(100.0, score)),
            "channel": channel,
            "reason": reason,
        }

    score = float(getattr(result, "score", 0))
    reason = str(getattr(result, "reason", "llm_based"))
    provider = str(getattr(result, "provider", "llm"))
    return {
        "score": max(0.0, min(100.0, score)),
        "channel": f"llm:{provider}",
        "reason": reason,
    }


def score_text(text: str) -> Dict[str, Any]:
    """
    对外统一打分入口：
    1) ENABLE_LLM=True 且有 API Key -> 尝试 LLM
    2) LLM 超时/鉴权失败 -> 回退 rule
    3) 其他情况 -> rule
    """
    logger.info(
        "score.entry ENABLE_LLM=%s API_KEY_SET=%s",
        settings.ENABLE_LLM,
        bool(settings.LLM_API_KEY),
    )

    if settings.ENABLE_LLM and settings.LLM_API_KEY:
        try:
            result = llm_score(text)
            logger.info("score.success channel=%s", result.get("channel"))
            return result

        except LLMTimeoutError as e:
            logger.warning("score.fallback.timeout error=%s", e)
            return rule_score(text)

        except LLMAuthError as e:
            logger.warning("score.fallback.auth error=%s", e)
            return rule_score(text)

        except Exception as e:
            # 防御性兜底，避免服务 500
            logger.warning("score.fallback.unknown error=%s", e, exc_info=True)
            return rule_score(text)

    logger.info("score.success channel=rule reason=llm_disabled_or_no_key")
    return rule_score(text)


