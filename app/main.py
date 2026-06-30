import json
import logging
import os
import uuid

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.pipeline.scoring_pipeline import run_scoring_pipeline
from app.routes.grade_preview import router as grade_preview_router
from app.schemas import ScoreRequest


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

MIN_LEN = 20
MAX_LEN = 20000
APP_VERSION = os.getenv("APP_VERSION", "v0.2.1-dev")
GIT_SHA = os.getenv("GIT_SHA", "unknown")


def error_response(
    request: Request,
    status_code: int,
    code: str,
    reason: str,
    message: str,
    details: dict | None = None,
):
    trace_id = getattr(request.state, "request_id", None)
    body = {
        "error": {
            "code": code,
            "reason": reason,
            "message": message,
            "path": request.url.path,
            "trace_id": trace_id,
        }
    }
    if details is not None:
        body["error"]["details"] = details
    return JSONResponse(status_code=status_code, content=body)


@app.exception_handler(RequestValidationError)
async def request_validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    仅对 /score 兼容旧语义；其他路由维持 FastAPI 默认 422（但统一 envelope）。
    """
    errors = exc.errors() or []

    if request.url.path != "/score":
        return error_response(
            request=request,
            status_code=422,
            code="VALIDATION_ERROR",
            reason="REQUEST_INVALID",
            message="request validation failed",
            details={"errors": errors},
        )

    reason = "MISSING_FIELD"
    message = "text is required"

    for err in errors:
        loc = tuple(err.get("loc", ()))
        err_type = err.get("type", "")

        if loc == ("body", "text") and err_type == "missing":
            reason = "MISSING_FIELD"
            message = "text is required"
            break

        # 类型不匹配（如 text=123、body 非对象等）
        if err_type.startswith(("string_type", "model_attributes_type", "dict_type", "json_invalid")):
            reason = "INVALID_TYPE"
            message = "text must be a string"
            break

    return error_response(
        request=request,
        status_code=400,
        code="VALIDATION_ERROR",
        reason=reason,
        message=message,
    )


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """
    统一 404/405 等 Starlette/FastAPI HTTP 异常为 ErrorEnvelope。
    """
    status_code = exc.status_code
    reason_map = {
        404: "NOT_FOUND",
        405: "METHOD_NOT_ALLOWED",
    }
    reason = reason_map.get(status_code, "HTTP_ERROR")
    message = str(exc.detail) if exc.detail else "http error"

    return error_response(
        request=request,
        status_code=status_code,
        code="HTTP_ERROR",
        reason=reason,
        message=message,
    )


@app.middleware("http")
async def add_request_id(request: Request, call_next):
    x_trace_id = request.headers.get("X-Trace-Id")
    x_request_id = request.headers.get("X-Request-ID")

    trace_id = (x_trace_id or "").strip() or (x_request_id or "").strip() or str(uuid.uuid4())
    request.state.request_id = trace_id

    response = await call_next(request)
    response.headers["X-Trace-Id"] = trace_id
    response.headers["X-Request-ID"] = trace_id  # backward compatibility
    return response


@app.get("/health")
def health():
    return {"ok": True}


@app.get("/healthz")
def healthz():
    return {"ok": True}


@app.get("/version")
def version():
    return {
        "version": APP_VERSION,
        "commit": GIT_SHA,
    }


def score_text(text: str) -> dict:
    """
    兼容层：
    - 保留 app.main.score_text，供旧测试 monkeypatch
    - 内部实际走 pipeline
    """
    result = run_scoring_pipeline(text)
    return {
        "score": result["total_score"],
        "channel": "rule",
        "reason": "fallback_rule",
        "ok": True,
        "data": result,
    }


@app.post("/score")
def score(payload: ScoreRequest, request: Request):
    try:
        # 1) 字段缺失 -> MISSING_FIELD
        if "text" not in payload.model_fields_set:
            return error_response(
                request, 400, "VALIDATION_ERROR", "MISSING_FIELD", "text is required"
            )

        # 2) 显式 null -> INVALID_TYPE
        if payload.text is None:
            return error_response(
                request, 400, "VALIDATION_ERROR", "INVALID_TYPE", "text must be a string"
            )

        text = payload.text

        # 防御式保留
        if not isinstance(text, str):
            return error_response(
                request, 400, "VALIDATION_ERROR", "INVALID_TYPE", "text must be a string"
            )

        if text == "":
            return error_response(
                request, 422, "VALIDATION_ERROR", "TEXT_NULL", "text must not be null or empty"
            )

        n = len(text)
        if n < MIN_LEN:
            return error_response(
                request,
                422,
                "VALIDATION_ERROR",
                "TEXT_TOO_SHORT",
                f"text length must be between {MIN_LEN} and {MAX_LEN}",
            )

        if n > MAX_LEN:
            return error_response(
                request,
                422,
                "VALIDATION_ERROR",
                "TEXT_TOO_LONG",
                f"text length must be between {MIN_LEN} and {MAX_LEN}",
            )

        return score_text(text)

    except Exception as e:
        logger.exception("Unhandled error in /score: %s", e)
        return error_response(
            request,
            500,
            "INTERNAL_ERROR",
            "INTERNAL_ERROR",
            "unexpected internal error",
            {"reason": type(e).__name__},
        )
