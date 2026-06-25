# Score 模块契约（冻结）

## 1. 输入校验
- text 为空 -> HTTP 400
- text 非字符串 -> HTTP 400
- text 全空白 -> HTTP 400

## 2. 通道选择
- ENABLE_LLM=False -> 走 rule
- ENABLE_LLM=True 且无 LLM_API_KEY -> 走 rule
- ENABLE_LLM=True 且有 LLM_API_KEY -> 走 llm
- 特殊：测试 monkeypatch llm_score 时，即便无 key 也应进入 LLM 分支（用于验证未知异常传播）

## 3. 返回结构
### rule_score
- channel: "rule"
- reason: "rule_based"
- score: number

### llm 成功
- channel: "llm"（统一，不带供应商后缀）
- score: number
- 其他字段可扩展

## 4. 异常策略
- 已知 LLM 异常（超时/鉴权）-> 回退 rule
- 未知异常 -> 直接抛出，由路由层返回 500

## 5. 可被测试 monkeypatch 的函数（不可随意删除/改名）
- llm_score(text)
- score_with_llm(text, api_key)

