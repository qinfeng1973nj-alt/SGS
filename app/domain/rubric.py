from dataclasses import dataclass
from typing import Dict, List


@dataclass(frozen=True)
class Dimension:
    key: str
    name: str
    weight: float
    min_score: float = 0.0
    max_score: float = 100.0


RUBRIC_V1: List[Dimension] = [
    Dimension(key="content", name="内容相关性与完整性", weight=0.35),
    Dimension(key="structure", name="结构与连贯性", weight=0.25),
    Dimension(key="language", name="语言表达与规范性", weight=0.25),
    Dimension(key="task", name="任务完成度", weight=0.15),
]


def rubric_weights() -> Dict[str, float]:
    return {d.key: d.weight for d in RUBRIC_V1}


def validate_rubric() -> None:
    total = sum(d.weight for d in RUBRIC_V1)
    if abs(total - 1.0) > 1e-9:
        raise ValueError(f"Rubric weights must sum to 1.0, got {total}")
