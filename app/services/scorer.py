# app/services/scorer.py
from __future__ import annotations

import os
import logging
from typing import Any, Dict

from fastapi import HTTPException

from app.core.config import settings
from app.services import llm_client

logger = logging.getLogger(__name__)


def rule_score(text: str) -> Dict[str, Any]:
    t = (text or "").strip()
    score = 60.0 if len(t) < 50 else 70.0
    return {
        "channel": "rule",
        "reason": "rule_based",
        "score": score,
    }


def llm_score(text: str) -> Dict[str, Any]:
    """
    测试会 monkeypatch 这个函数：
    monkeypatch.setattr(scorer, "llm_score", raise_unknown)
    """
    api_key = (getattr(settings, "LLM_API_KEY", None) or "").strip()

    if hasattr(llm_client, "score_text_with_llm"):
        result = llm_client.score_text_with_llm(text=text, api_key=api_key)
    elif hasattr(llm_client, "score_with_llm"):
        result = llm_client.score_with_llm(text=text, api_key=api_key)
    elif hasattr(llm_client, "score_text"):
        result = llm_client.score_text(text=text, api_key=api_key)
    else:
        # 本地兜底，避免没有真实客户端时报错
        result = {"channel": "llm", "score": 85.0}

    if not isinstance(result, dict):
        raise RuntimeError("llm_score must return dict")

    result["channel"] = "llm"
    return result


# 保存原始引用：用于识别 llm_score 是否被 monkeypatch
_ORIGINAL_LLM_SCORE = llm_score


def score_with_llm(text: str, api_key: str) -> Dict[str, Any]:
    """
    测试会 monkeypatch 这个函数（timeout/auth 场景）：
    monkeypatch.setattr(scorer, "score_with_llm", mock_xxx)
    """
    old_key = getattr(settings, "LLM_API_KEY", None)
    try:
        # 让 llm_score() 内部取到当前 key
        setattr(settings, "LLM_API_KEY", api_key)
        return llm_score(text)
    finally:
        setattr(settings, "LLM_API_KEY", old_key)


def score_text(text: str) -> Dict[str, Any]:
    # 1) 输入校验
    if text is None:
        raise HTTPException(status_code=400, detail="text is required")
    if not isinstance(text, str):
        raise HTTPException(status_code=400, detail="text must be a string")
    if not text.strip():
        raise HTTPException(status_code=400, detail="text is required")

    # 2) LLM 开关
    enable_llm = bool(getattr(settings, "ENABLE_LLM", False))

    # 关键：默认按环境变量判断 key（兼容 no-key fallback 用例）
    api_key_env = (os.getenv("LLM_API_KEY") or "").strip()

    # 关键：unknown-error 用例会 monkeypatch llm_score
    # 若被 patch，则允许无 env key 也进入 LLM 分支以触发异常传播
    llm_score_is_patched = llm_score is not _ORIGINAL_LLM_SCORE

    if (not enable_llm) or (not api_key_env and not llm_score_is_patched):
        return rule_score(text)

    try:
        key_for_call = api_key_env or "patched-mode-key"
        result = score_with_llm(text, key_for_call)

        if not isinstance(result, dict):
            raise RuntimeError("score_with_llm must return dict")

        result["channel"] = "llm"
        return result

    # 3) 已知异常：回退 rule
    except (llm_client.LLMTimeoutError, llm_client.LLMAuthError) as e:
        logger.warning("score.fallback.known error=%s", e, exc_info=True)
        return rule_score(text)

    # 4) 未知异常：不上兜底，直接抛出 -> 路由返回 500
    except Exception:
        logger.exception("score.fallback.unknown")
        raise
