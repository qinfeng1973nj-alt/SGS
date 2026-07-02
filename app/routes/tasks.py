import os
import uuid
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, File, HTTPException, UploadFile
from pydantic import BaseModel, Field

router = APIRouter(prefix="/tasks", tags=["tasks"])

UPLOAD_DIR = "artifacts/assignments"
os.makedirs(UPLOAD_DIR, exist_ok=True)


class TaskCreateReq(BaseModel):
    title: str = Field(..., min_length=2, max_length=200)
    subject: Optional[str] = Field(default=None, max_length=100)
    grade_level: Optional[str] = Field(default=None, max_length=50)


_fake_tasks: list[dict] = []
_fake_files: list[dict] = []


def _gen_task_code() -> str:
    date = datetime.now().strftime("%Y%m%d")
    seq = len(_fake_tasks) + 1
    return f"TASK-{date}-{seq:03d}"


@router.post("")
def create_task(payload: TaskCreateReq):
    title = payload.title.strip()
    if len(title) < 2:
        raise HTTPException(status_code=422, detail="title too short")

    now = datetime.now().isoformat()
    task = {
        "id": len(_fake_tasks) + 1,
        "task_code": _gen_task_code(),
        "title": title,
        "subject": payload.subject,
        "grade_level": payload.grade_level,
        "status": "PENDING",
        "total_students": 0,
        "success_students": 0,
        "failed_students": 0,
        "created_at": now,
        "updated_at": now,
    }
    _fake_tasks.append(task)
    return task


@router.get("")
def list_tasks():
    return {"ok": True, "items": _fake_tasks}


@router.get("/{task_id}")
def get_task(task_id: int):
    task = next((t for t in _fake_tasks if t["id"] == task_id), None)
    if not task:
        raise HTTPException(status_code=404, detail="task not found")
    return {"ok": True, "item": task}


@router.post("/{task_id}/assignment-file")
async def upload_assignment_file(task_id: int, file: UploadFile = File(...)):
    task = next((t for t in _fake_tasks if t["id"] == task_id), None)
    if not task:
        raise HTTPException(status_code=404, detail="task not found")

    if not file.filename or "." not in file.filename:
        raise HTTPException(status_code=400, detail="invalid file name")

    ext = file.filename.rsplit(".", 1)[-1].lower()
    if ext not in {"pdf", "doc", "docx", "txt"}:
        raise HTTPException(status_code=400, detail="unsupported file type")

    save_name = f"{uuid.uuid4().hex}.{ext}"
    save_path = os.path.join(UPLOAD_DIR, save_name)

    content = await file.read()
    with open(save_path, "wb") as f:
        f.write(content)

    now = datetime.now().isoformat()
    rec = {
        "id": len(_fake_files) + 1,
        "task_id": task_id,
        "file_name": file.filename,
        "file_path": save_path,
        "file_type": ext,
        "file_size": len(content),
        "created_at": now,
    }
    _fake_files.append(rec)

    return {"ok": True, "task_id": task_id, "file": rec}


@router.get("/{task_id}/files")
def list_task_files(task_id: int):
    task = next((t for t in _fake_tasks if t["id"] == task_id), None)
    if not task:
        raise HTTPException(status_code=404, detail="task not found")

    items = [f for f in _fake_files if f["task_id"] == task_id]
    return {"ok": True, "task_id": task_id, "items": items}
