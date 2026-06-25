# SGS

轻量化评分服务（FastAPI），已接入本地冒烟测试与 GitHub Actions CI 门禁。

---

## 接口契约（最小）

### 1) 健康检查

**GET** `/health`

#### 成功响应（示例）
```json
{
  "ok": true
}
```
### 2) 评分预览

**POST** `/grade/preview`

#### 请求体（示例）
```json
{
  "student_text": "Alice 的成绩是：语文95，数学88，英语92。请给出等级预览。"
}
```
#### 成功响应（最小契约）
```json
{
  "overall_score": 52.95,
  "holistic_level": "D",
  "analytic_scores": []
}
```
---

## 本地开发

### 环境要求

- Python 3.10+
- pip 23+
- 建议使用虚拟环境（venv）

### 安装依赖

```bash
python -m venv .venv
source .venv/bin/activate  # Windows 使用: .venv\Scripts\activate
pip install -U pip
pip install -r requirements.txt
```
### 启动服务

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
服务默认地址：`http://127.0.0.1:8000`

### 快速自检

#### 1) 健康检查

```bash
curl -X GET "http://127.0.0.1:8000/health"
```

预期响应： 
```json
{
  "ok": true
}
```
#### 2) 评分预览

```bash
curl -X POST "http://127.0.0.1:8000/grade/preview" \
  -H "Content-Type: application/json" \
  -d '{
    "student_text": "Alice 的成绩是：语文95，数学88，英语92。请给出等级预览。"
  }'
```
预期响应（示例）：
```json
{
  "overall_score": 52.95,
  "holistic_level": "D",
  "analytic_scores": []
}
```
