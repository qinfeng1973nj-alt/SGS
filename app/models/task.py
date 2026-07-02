from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.sql import func

from app.db import Base


class AssignmentTask(Base):
    __tablename__ = "assignment_task"

    id = Column(Integer, primary_key=True, index=True)
    task_code = Column(String(32), unique=True, nullable=False, index=True)
    title = Column(String(200), nullable=False)
    subject = Column(String(100), nullable=True)
    grade_level = Column(String(50), nullable=True)
    status = Column(String(20), nullable=False, default="PENDING")

    total_students = Column(Integer, nullable=False, default=0)
    success_students = Column(Integer, nullable=False, default=0)
    failed_students = Column(Integer, nullable=False, default=0)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)


class AssignmentFile(Base):
    __tablename__ = "assignment_file"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("assignment_task.id"), nullable=False, index=True)

    file_name = Column(String(255), nullable=False)
    file_path = Column(Text, nullable=False)
    file_type = Column(String(20), nullable=False)
    file_size = Column(Integer, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
