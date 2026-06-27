from fastapi.responses import JSONResponse


def error_response(status_code: int, code: str, reason: str, message: str):
    return JSONResponse(
        status_code=status_code,
        content={
            "error": {
                "code": code,
                "reason": reason,
                "message": message,
            }
        },
    )
