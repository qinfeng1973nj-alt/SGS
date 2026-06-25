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
    text = payload.get("text", "")
    return score_text(text)
