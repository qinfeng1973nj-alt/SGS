from fastapi import APIRouter
from fastapi.responses import JSONResponse

router = APIRouter()

@router.get("/health")
def health():
    return JSONResponse({"status": "ok"})

@router.get("/")
def root():
    return {"message": "Auto Grader API is running"}
