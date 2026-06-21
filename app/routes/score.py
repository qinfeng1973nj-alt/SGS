from fastapi import APIRouter
from app.schemas import ScoreRequest, ScoreResponse

router = APIRouter(prefix="/score", tags=["score"])


@router.post("", response_model=ScoreResponse)
def score_text(payload: ScoreRequest):
    text = payload.text.strip()
    length = len(text)

    # 最小可运行的 mock 评分逻辑（后续可替换成模型推理）
    if length < 20:
        score = 60
        level = "C"
        reason = "文本较短，信息量有限"
    elif length < 100:
        score = 78
        level = "B"
        reason = "文本长度适中，表达基本完整"
    else:
        score = 90
        level = "A"
        reason = "文本信息充分，结构较完整"

    return ScoreResponse(score=score, level=level, reason=reason)
