
import json
import re
from typing import Any, Dict

from app.core.config import settings
from app.services.llm.providers.deepseek_provider import chat_completion


class LLMTimeoutError(Exception):
    pass


class LLMAuthError(Exception):
    pass


class LLMParseError(Exception):
    pass


def _build_prompt(text: str) -> str:
    return (
        "请你对输入文本做质量评分。\n"
        "要求：仅返回严格JSON，不要额外解释，不要markdown代码块。\n"
        '格式：{"score": 0-100, "reason": "简短中文说明"}\n'
        f"输入文本：{text}"
    )


def _extract_json(raw: str) -> Dict[str, Any]:
    s = (raw or "").strip()

    # 1) 兼容 ```json ... ```
    m = re.search(r"```(?:json)?\s*(\{[\s\S]*\})\s*```", s, re.IGNORECASE)
    if m:
        s = m.group(1).strip()

    # 2) 若不是纯 JSON，尝试提取首个 {...}
    if not s.startswith("{"):
        m2 = re.search(r"\{[\s\S]*\}", s)
        if m2:
            s = m2.group(0).strip()

    try:
        data = json.loads(s)
    except Exception as e:
        raise LLMParseError(f"LLM JSON parse failed: {e}; raw={raw[:300]}") from e

    if not isinstance(data, dict):
        raise LLMParseError(f"LLM JSON is not object: {type(data)}")

    return data


def score_with_llm(text: str, api_key: str | None = None) -> Dict[str, Any]:
    """
    统一 LLM 打分（固定走 DeepSeek Provider）
    返回结构：
    {
      "score": float,
      "reason": str,
      "channel": "llm:deepseek"
    }
    """
    _ = api_key  # 兼容旧签名

    try:
        raw = chat_completion(_build_prompt(text))
        data = _extract_json(raw)

        score = float(data.get("score", 0))
        score = max(0.0, min(100.0, score))
        reason = str(data.get("reason", "llm_based"))

        return {
            "score": score,
            "reason": reason,
            "channel": f"llm:{(settings.LLM_PROVIDER or 'deepseek')}",
        }

    except Exception as e:
        msg = str(e).lower()

        if "401" in msg or "unauthorized" in msg or "auth" in msg or "api key" in msg:
            raise LLMAuthError(str(e)) from e

        if "timeout" in msg or "timed out" in msg:
            raise LLMTimeoutError(str(e)) from e

        # 其他异常（如解析失败、网络异常）交给 scorer 的通用兜底
        raise
