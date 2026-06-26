# SGS

轻量化评分服务（FastAPI），已接入本地冒烟测试与 GitHub Actions CI 门禁。
---

## Release & Verification

- Latest stable tag: **v0.1.1**
- Changelog: [CHANGELOG.md](./CHANGELOG.md)

### Quick local check (Windows PowerShell)

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\smoke_test.ps1
```

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

#### 请求体字段约束（契约）
- `student_text`（string，必填）：学生作业文本，长度要求 `20 <= len <= 20000`
- `template_id`（string，可选）：默认值 `mgmt_case_v1`

#### 请求体（示例）
```json
{
  "student_text": "这是一段不少于二十字的学生作业文本，用于评分预览接口的契约验证。",
  "template_id": "mgmt_case_v1"
}
```
#### 成功响应（最小契约）
```json
{
  "template_id": "mgmt_case_v1",
  "course": "string",
  "assignment_type": "string",
  "analytic_scores": [],
  "overall_score": 52.95,
  "holistic_level": "D",
  "review_flags": []
}
```
#### 失败响应（校验错误示例）
当 `student_text` 不满足长度约束（`20 <= len <= 20000`）时，返回：

```json
{
  "detail": [
    {
      "loc": ["body", "student_text"],
      "msg": "ensure this value has at most 20000 characters",
      "type": "value_error.any_str.max_length"
    }
  ]
}
```
状态码：`422 Unprocessable Entity`

---
## 本地开发

### 环境要求

- Python 3.10+
- pip 23+
- 建议使用虚拟环境（venv）

### 安装依赖

```bash
python -m venv .venv

# macOS/Linux
source .venv/bin/activate

# Windows PowerShell
.\.venv\Scripts\Activate.ps1

pip install -U pip
pip install -r requirements.txt
```
### 启动服务

```bash
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
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
    "student_text": "这是一段不少于二十字的学生作业文本，用于评分预览接口的契约验证。",
    "template_id": "mgmt_case_v1"
  }'
```
PowerShell 示例：

```powershell
$body = @{
  student_text = "这是一段不少于二十字的学生作业文本，用于评分预览接口的契约验证。"
  template_id  = "mgmt_case_v1"
} | ConvertTo-Json

Invoke-RestMethod -Method Post `
  -Uri "http://127.0.0.1:8000/grade/preview" `
  -ContentType "application/json" `
  -Body $body
```
预期响应（示例）：
```json
{
  "template_id": "mgmt_case_v1",
  "course": "管理学",
  "assignment_type": "案例分析",
  "analytic_scores": [],
  "overall_score": 52.95,
  "holistic_level": "D",
  "review_flags": []
}
```
