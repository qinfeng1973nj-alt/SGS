import json
import logging
import uuid

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from app.services.scorer import score_text
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

# 只创建一次 app，并保留 UTF-8 默认响应类
app = FastAPI(default_response_class=UTF8JSONResponse)

# 只挂载一次路由
app.include_router(grade_preview_router)


class ScoreRequest(BaseModel):
    text: str


MIN_LEN = 20
MAX_LEN = 20000


def error_response(status_code: int, code: str, reason: str, message: str):
    return JSONResponse(
        status_code=status_code,
        content={
            "error": {
                "code": code,
                "reason": reason,
                "message": message,
            }
        },
    )


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


@app.post("/score")
def score(payload: dict):
    try:
        # 400: 缺字段 / 类型错误
        if "text" not in payload:
            return error_response(
                400, "VALIDATION_ERROR", "MISSING_FIELD", "text is required"
            )

        text = payload["text"]

        if not isinstance(text, str):
            return error_response(
                400, "VALIDATION_ERROR", "INVALID_TYPE", "text must be a string"
            )

        # 422: 业务校验失败
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

        # 正常路径：沿用你现有服务函数
        return score_text(text)

    except Exception as e:
        logger.exception("Unhandled error in /score: %s", e)
        return error_response(
            500, "INTERNAL_ERROR", "INTERNAL_ERROR", "unexpected internal error"
        )
