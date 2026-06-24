from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, Dict, List
import json
import re
from pathlib import Path

router = APIRouter(prefix="/grade", tags=["grade"])
TEMPLATE_PATH = Path("data/course_template.json")


class GradePreviewRequest(BaseModel):
    student_text: str = Field(..., min_length=20, description="学生作业文本")
    template_id: Optional[str] = Field(default="mgmt_case_v1")


def load_template() -> Dict:
    if not TEMPLATE_PATH.exists():
        raise FileNotFoundError(f"模板不存在: {TEMPLATE_PATH}")
    text = TEMPLATE_PATH.read_text(encoding="utf-8-sig")
    return json.loads(text)


def split_sentences(text: str) -> List[str]:
    parts = re.split(r"[。！？\n]", text)
    return [p.strip() for p in parts if p.strip()]


def pick_evidence(sentences: List[str], keywords: List[str], top_k: int = 2) -> List[str]:
    scored = []
    for s in sentences:
        score = sum(1 for kw in keywords if kw in s)
        if score > 0:
            scored.append((score, s))
    scored.sort(key=lambda x: x[0], reverse=True)
    return [s for _, s in scored[:top_k]]


def heuristic_score(text: str, dim_id: str) -> float:
    text_len = len(text)

    if dim_id == "theory_application":
        kws = ["理论", "模型", "PEST", "SWOT", "激励", "领导", "战略"]
        hit = sum(1 for k in kws if k in text)
        return min(100, 55 + hit * 8)

    if dim_id == "logic_structure":
        kws = ["首先", "其次", "最后", "因此", "所以", "综上"]
        hit = sum(1 for k in kws if k in text)
        base = 50 + hit * 10 + (8 if text_len > 400 else 0)
        return min(100, base)

    if dim_id == "evidence_support":
        kws = ["数据", "调研", "案例", "事实", "%", "增长", "下降"]
        hit = sum(1 for k in kws if k in text)
        return min(100, 52 + hit * 9)

    if dim_id == "context_fit":
        kws = ["公司", "企业", "行业", "组织", "岗位", "情境", "约束"]
        hit = sum(1 for k in kws if k in text)
        return min(100, 54 + hit * 8)

    return 60.0


def to_level(score: float) -> str:
    if score >= 85:
        return "A"
    if score >= 75:
        return "B"
    if score >= 60:
        return "C"
    return "D"


@router.post("/preview")
def grade_preview(req: GradePreviewRequest):
    try:
        tpl = load_template()
        if req.template_id != tpl["template_id"]:
            raise HTTPException(status_code=400, detail=f"template_id 不存在: {req.template_id}")

        dims = tpl["dimensions"]
        sents = split_sentences(req.student_text)

        dim_keywords = {
            "theory_application": ["理论", "模型", "SWOT", "PEST", "战略", "激励"],
            "logic_structure": ["首先", "其次", "最后", "因此", "综上"],
            "evidence_support": ["数据", "案例", "事实", "%", "调研"],
            "context_fit": ["企业", "行业", "组织", "情境", "约束"],
        }

        analytic_scores = []
        weighted_sum = 0.0

        for d in dims:
            dim_id = d["id"]
            w = float(d["weight"])
            score = heuristic_score(req.student_text, dim_id)
            weighted_sum += score * w
            evidence = pick_evidence(sents, dim_keywords.get(dim_id, []), top_k=2)

            analytic_scores.append({
                "dimension_id": dim_id,
                "dimension_name": d["name"],
                "weight": w,
                "score": round(score, 2),
                "evidence_links": evidence
            })

        overall = round(weighted_sum, 2)
        holistic = to_level(overall)

        review_flags = []
        for row in analytic_scores:
            if len(row["evidence_links"]) == 0:
                review_flags.append({
                    "type": "missing_evidence",
                    "dimension_id": row["dimension_id"],
                    "severity": "medium"
                })

        if overall < 60 and holistic in ["A", "B"]:
            review_flags.append({"type": "score_level_mismatch", "severity": "high"})

        return {
            "template_id": tpl["template_id"],
            "course": tpl["course"],
            "assignment_type": tpl["assignment_type"],
            "analytic_scores": analytic_scores,
            "overall_score": overall,
            "holistic_level": holistic,
            "review_flags": review_flags
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
