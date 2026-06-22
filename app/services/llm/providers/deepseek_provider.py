import json
from typing import Any, Dict

import httpx

from app.core.config import settings


class DeepSeekAuthError(Exception):
    pass


class DeepSeekTimeoutError(Exception):
    pass


class DeepSeekRequestError(Exception):
    pass


def _build_payload(prompt: str) -> Dict[str, Any]:
    return {
        "model": settings.LLM_MODEL or "deepseek-chat",
        "messages": [
            {"role": "system", "content": "你是一个严谨的评分助手。"},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.2,
        "stream": False,
    }


def chat_completion(prompt: str) -> str:
    """
    调用 DeepSeek Chat Completions，返回纯文本 content。
    """
    base_url = (settings.LLM_BASE_URL or "https://api.deepseek.com").rstrip("/")
    url = f"{base_url}/chat/completions"

    headers = {
        "Authorization": f"Bearer {settings.LLM_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = _build_payload(prompt)

    try:
        with httpx.Client(timeout=30.0, trust_env=False) as client:
            resp = client.post(url, headers=headers, json=payload)

        if resp.status_code == 401:
            raise DeepSeekAuthError(
                f"401 Authorization Required: {resp.text}"
            )

        resp.raise_for_status()

        data = resp.json()
        # 兼容标准结构：choices[0].message.content
        return (
            data.get("choices", [{}])[0]
            .get("message", {})
            .get("content", "")
            .strip()
        )

    except httpx.TimeoutException as e:
        raise DeepSeekTimeoutError(f"DeepSeek request timeout: {e}") from e

    except httpx.HTTPStatusError as e:
        raise DeepSeekRequestError(
            f"DeepSeek HTTP error: {e.response.status_code} {e.response.text}"
        ) from e

    except httpx.RequestError as e:
        raise DeepSeekRequestError(f"DeepSeek request error: {e}") from e

    except json.JSONDecodeError as e:
        raise DeepSeekRequestError(f"DeepSeek response is not valid JSON: {e}") from e
