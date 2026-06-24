# SGS

轻量化评分服务（FastAPI），已接入本地冒烟测试与 GitHub Actions CI 门禁。

---

## 接口最小契约

### 1) 健康检查

**GET** `/health`

#### 成功响应（示例）
```json
{
  "status": "ok"
}
