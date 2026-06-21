import logging
import uuid

from fastapi import FastAPI, Request
from pydantic import BaseModel

from app.services.scorer import score_text

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)

app = FastAPI()
logger = logging.getLogger(__name__)


class ScoreRequest(BaseModel):
    text: str


@app.middleware("http")
async def add_request_id(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
    request.state.request_id = request_id
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    return response


@app.post("/score")
def score(payload: ScoreRequest, request: Request):
    result = score_text(payload.text)
    logger.info(
        "api.score request_id=%s channel=%s",
        request.state.request_id,
        result.get("channel"),
    )
    return result

