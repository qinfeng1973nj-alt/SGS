from pydantic import BaseModel, Field


class ScoreRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=2000, description="待评分文本")


class ScoreResponse(BaseModel):
    score: int = Field(..., ge=0, le=100, description="评分，0-100")
    level: str = Field(..., description="评级")
    reason: str = Field(..., description="评分说明")
