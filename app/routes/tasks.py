from fastapi import APIRouter

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.post("")
def create_task():
    return {"ok": True, "message": "create_task placeholder"}


@router.get("")
def list_tasks():
    return {"ok": True, "items": []}
