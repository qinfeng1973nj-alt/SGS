import json
import logging
import uuid

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from app.pipeline.scoring_pipeline import run_scoring_pipeline
from app.routes.grade_preview import router as grade_preview_router


class UTF8JSONResponse(JSONResponse):
    media_type = "application/json; charset=utf-8"

    def render(self, content) -> bytes:
        return json.dumps(content, ensure_ascii=False).encode("utf-8")


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)

logger = logging.getLogger(__name__)

app = FastAPI(default_response_class=UTF8JSONResponse)
app.include_router(grade_preview_router)


class ScoreRequest(BaseModel):
    text: str


MIN_LEN = 20
MAX_LEN = 20000


def error_response(
    status_code: int,
    code: str,
    reason: str,
    message: str,
    details: dict | None = None,
):
    body = {
        "error": {
            "code": code,
            "reason": reason,
            "message": message,
        }
    }
    if details is not None:
        body["error"]["details"] = details
    return JSONResponse(status_code=status_code, content=body)


@app.middleware("http")
async def add_request_id(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
    request.state.request_id = request_id
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    return response


@app.get("/health")
def health():
    return {"ok": True}


def score_text(text: str) -> dict:
    """
    兼容层：
    - 保留 app.main.score_text，供旧测试 monkeypatch
    - 内部实际走 v0.1.9 pipeline
    """
    result = run_scoring_pipeline(text)
    return {
        # 旧协议兼容字段（测试依赖）
        "score": result["total_score"],
        "channel": "rule",
        "reason": "fallback_rule",
        # 新协议字段
        "ok": True,
        "data": result,
    }


@app.post("/score")
def score(payload: dict):
    try:
        if "text" not in payload:
            return error_response(
                400, "VALIDATION_ERROR", "MISSING_FIELD", "text is required"
            )

        text = payload["text"]

        if not isinstance(text, str):
            return error_response(
                400, "VALIDATION_ERROR", "INVALID_TYPE", "text must be a string"
            )

        if text == "":
            return error_response(
                422, "VALIDATION_ERROR", "TEXT_NULL", "text must not be null or empty"
            )

        n = len(text)
        if n < MIN_LEN:
            return error_response(
                422,
                "VALIDATION_ERROR",
                "TEXT_TOO_SHORT",
                f"text length must be between {MIN_LEN} and {MAX_LEN}",
            )

        if n > MAX_LEN:
            return error_response(
                422,
                "VALIDATION_ERROR",
                "TEXT_TOO_LONG",
                f"text length must be between {MIN_LEN} and {MAX_LEN}",
            )

        return score_text(text)

    except Exception as e:
        logger.exception("Unhandled error in /score: %s", e)
        return error_response(
            500,
            "INTERNAL_ERROR",
            "INTERNAL_ERROR",
            "unexpected internal error",
            {"reason": type(e).__name__},
        )
