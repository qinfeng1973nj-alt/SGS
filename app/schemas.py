from pydantic import BaseModel, Field


class ScoreRequest(BaseModel):
    # 允许 None；缺失字段时默认 None。
    # 这样可由 /score 统一返回旧协议的 400 + error body，而不是框架 422。
    text: str | None = Field(default=None, description="待评分文本")


class ScoreResponse(BaseModel):
    score: int = Field(..., ge=0, le=100, description="评分，0-100")
    level: str = Field(..., description="评级")
    reason: str = Field(..., description="评分说明")
