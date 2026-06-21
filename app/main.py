from fastapi import FastAPI
from pydantic import BaseModel

from app.services.scorer import score_text

app = FastAPI()


class ScoreRequest(BaseModel):
    text: str


@app.post("/score")
def score(req: ScoreRequest):
    return score_text(req.text)
