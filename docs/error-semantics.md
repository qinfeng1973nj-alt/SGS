# /score Error Semantics (v0.1.6)

## HTTP Status Mapping

- **400 Bad Request**
  - Invalid JSON
  - Missing required fields
  - Wrong field types

- **422 Unprocessable Entity**
  - Business validation failed
  - `text` is null/empty
  - `text` length out of range (`20-20000`)

- **500 Internal Server Error**
  - Unexpected unhandled exception in scoring flow
  - Unknown scorer/LLM runtime failures are normalized to `INTERNAL_ERROR`

---

## Error Payload (stable contract)

### Validation example (422)

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "reason": "TEXT_TOO_LONG",
    "message": "text length must be between 20 and 20000"
  }
}
```

### Unknown exception example (500, v0.1.6)

```json
{
  "error": {
    "code": "INTERNAL_ERROR",
    "reason": "INTERNAL_ERROR",
    "message": "unexpected internal error",
    "details": {
      "reason": "RuntimeError"
    }
  }
}
```
---
