import json
from pathlib import Path

TEMPLATE_PATH = Path("data/course_template.json")

def validate_template(path: Path) -> None:
    if not path.exists():
        raise FileNotFoundError(f"模板文件不存在: {path}")

    data = json.loads(path.read_text(encoding="utf-8-sig"))

    required_top_fields = ["template_id", "course", "assignment_type", "dimensions"]
    for f in required_top_fields:
        if f not in data:
            raise ValueError(f"缺少顶层字段: {f}")

    dimensions = data["dimensions"]
    if not isinstance(dimensions, list) or len(dimensions) == 0:
        raise ValueError("dimensions 必须是非空数组")

    total_weight = 0.0
    ids = set()

    for i, d in enumerate(dimensions):
        for f in ["id", "name", "weight", "anchors"]:
            if f not in d:
                raise ValueError(f"第{i+1}个维度缺少字段: {f}")

        if d["id"] in ids:
            raise ValueError(f"维度 id 重复: {d['id']}")
        ids.add(d["id"])

        w = d["weight"]
        if not isinstance(w, (int, float)):
            raise ValueError(f"维度 {d['id']} 的 weight 必须是数字")
        if w < 0 or w > 1:
            raise ValueError(f"维度 {d['id']} 的 weight 必须在[0,1]")

        total_weight += float(w)

    # 浮点容忍
    if abs(total_weight - 1.0) > 1e-6:
        raise ValueError(f"权重总和必须为1.0，当前为: {total_weight}")

    print("✅ 模板校验通过")
    print(f"- template_id: {data['template_id']}")
    print(f"- 维度数量: {len(dimensions)}")
    print(f"- 权重总和: {total_weight}")

if __name__ == "__main__":
    validate_template(TEMPLATE_PATH)
