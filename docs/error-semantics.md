# /score Error Semantics (v0.1.4)

## HTTP Status Mapping

- 400 Bad Request
  - Invalid JSON
  - Missing required fields
  - Wrong field types

- 422 Unprocessable Entity
  - Business validation failed
  - text is null/empty
  - text length out of range (20-20000)

- 500 Internal Server Error
  - LLM client failure
  - unexpected unhandled exception

## Error Payload (stable contract)

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "reason": "TEXT_TOO_LONG",
    "message": "text length must be between 20 and 20000"
  }
}
