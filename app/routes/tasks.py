import os
import uuid
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.db import get_db
from app.models.task import AssignmentFile, AssignmentTask

router = APIRouter(prefix="/tasks", tags=["tasks"])

UPLOAD_DIR = "artifacts/assignments"
os.makedirs(UPLOAD_DIR, exist_ok=True)


class TaskCreateReq(BaseModel):
    title: str = Field(..., min_length=2, max_length=200)
    subject: Optional[str] = Field(default=None, max_length=100)
    grade_level: Optional[str] = Field(default=None, max_length=50)


def _gen_task_code(db: Session) -> str:
    date = datetime.now().strftime("%Y%m%d")
    seq = db.query(AssignmentTask).count() + 1
    return f"TASK-{date}-{seq:03d}"


def _task_to_dict(t: AssignmentTask) -> dict:
    return {
        "id": t.id,
        "task_code": t.task_code,
        "title": t.title,
        "subject": t.subject,
        "grade_level": t.grade_level,
        "status": t.status,
        "total_students": t.total_students,
        "success_students": t.success_students,
        "failed_students": t.failed_students,
        "created_at": str(t.created_at),
        "updated_at": str(t.updated_at),
    }


def _file_to_dict(f: AssignmentFile) -> dict:
    return {
        "id": f.id,
        "task_id": f.task_id,
        "file_name": f.file_name,
        "file_path": f.file_path,
        "file_type": f.file_type,
        "file_size": f.file_size,
        "created_at": str(f.created_at),
    }


@router.post("")
def create_task(payload: TaskCreateReq, db: Session = Depends(get_db)):
    title = payload.title.strip()
    if len(title) < 2:
        raise HTTPException(status_code=422, detail="title too short")

    task = AssignmentTask(
        task_code=_gen_task_code(db),
        title=title,
        subject=payload.subject,
        grade_level=payload.grade_level,
        status="PENDING",
        total_students=0,
        success_students=0,
        failed_students=0,
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return _task_to_dict(task)


@router.get("")
def list_tasks(db: Session = Depends(get_db)):
    rows = db.query(AssignmentTask).order_by(AssignmentTask.id.desc()).all()
    return {"ok": True, "items": [_task_to_dict(x) for x in rows]}


@router.get("/{task_id}")
def get_task(task_id: int, db: Session = Depends(get_db)):
    task = db.query(AssignmentTask).filter(AssignmentTask.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="task not found")
    return {"ok": True, "item": _task_to_dict(task)}


@router.post("/{task_id}/assignment-file")
async def upload_assignment_file(
    task_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    task = db.query(AssignmentTask).filter(AssignmentTask.id == task_id).first()
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

    rec = AssignmentFile(
        task_id=task_id,
        file_name=file.filename,
        file_path=save_path,
        file_type=ext,
        file_size=len(content),
    )
    db.add(rec)
    db.commit()
    db.refresh(rec)

    return {"ok": True, "task_id": task_id, "file": _file_to_dict(rec)}


@router.get("/{task_id}/files")
def list_task_files(task_id: int, db: Session = Depends(get_db)):
    task = db.query(AssignmentTask).filter(AssignmentTask.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="task not found")

    rows = (
        db.query(AssignmentFile)
        .filter(AssignmentFile.task_id == task_id)
        .order_by(AssignmentFile.id.desc())
        .all()
    )
    return {"ok": True, "task_id": task_id, "items": [_file_to_dict(x) for x in rows]}
