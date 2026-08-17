from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

try:
    from app.database import get_db
except ModuleNotFoundError:
    from database import get_db

try:
    from app.models import User, StudyNote, StudyTask
except ModuleNotFoundError:
    from models import User, StudyNote, StudyTask

try:
    from app.schemas import (
        StudyNoteCreate, StudyNoteUpdate, StudyNoteResponse,
        StudyTaskCreate, StudyTaskUpdate, StudyTaskResponse
    )
except ModuleNotFoundError:
    from schemas import (
        StudyNoteCreate, StudyNoteUpdate, StudyNoteResponse,
        StudyTaskCreate, StudyTaskUpdate, StudyTaskResponse
    )

try:
    from app.services.auth_service import get_current_user
except ModuleNotFoundError:
    try:
        from services.auth_service import get_current_user
    except ModuleNotFoundError:
        from auth_service import get_current_user

router = APIRouter(prefix="/api/planner", tags=["Çalışma Notları ve Planlayıcı"])

# --- STUDY NOTES ---
@router.get("/notes", response_model=List[StudyNoteResponse])
def get_notes(
    exam_type_id: Optional[int] = None,
    course_name: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(StudyNote).filter(StudyNote.user_id == current_user.id)
    if exam_type_id:
        query = query.filter(StudyNote.exam_type_id == exam_type_id)
    if course_name:
        query = query.filter(StudyNote.course_name == course_name)
    return query.order_by(StudyNote.created_at.desc()).all()

@router.post("/notes", response_model=StudyNoteResponse, status_code=status.HTTP_201_CREATED)
def create_note(
    note_in: StudyNoteCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    note = StudyNote(
        user_id=current_user.id,
        exam_type_id=note_in.exam_type_id,
        course_name=note_in.course_name,
        title=note_in.title,
        content=note_in.content,
        note_type=note_in.note_type
    )
    db.add(note)
    db.commit()
    db.refresh(note)
    return note

@router.put("/notes/{note_id}", response_model=StudyNoteResponse)
def update_note(
    note_id: int,
    note_in: StudyNoteUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    note = db.query(StudyNote).filter(StudyNote.id == note_id, StudyNote.user_id == current_user.id).first()
    if not note:
        raise HTTPException(status_code=404, detail="Not bulunamadı.")
    
    update_data = note_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(note, field, value)
    
    db.commit()
    db.refresh(note)
    return note

@router.delete("/notes/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_note(
    note_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    note = db.query(StudyNote).filter(StudyNote.id == note_id, StudyNote.user_id == current_user.id).first()
    if not note:
        raise HTTPException(status_code=404, detail="Not bulunamadı.")
    db.delete(note)
    db.commit()
    return None

# --- STUDY TASKS (TODO) ---
@router.get("/tasks", response_model=List[StudyTaskResponse])
def get_tasks(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return db.query(StudyTask).filter(StudyTask.user_id == current_user.id).order_by(StudyTask.is_completed.asc(), StudyTask.created_at.desc()).all()

@router.post("/tasks", response_model=StudyTaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(
    task_in: StudyTaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    task = StudyTask(
        user_id=current_user.id,
        title=task_in.title,
        course_name=task_in.course_name,
        is_completed=task_in.is_completed,
        priority=task_in.priority,
        due_date=task_in.due_date
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return task

@router.put("/tasks/{task_id}", response_model=StudyTaskResponse)
def update_task(
    task_id: int,
    task_in: StudyTaskUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    task = db.query(StudyTask).filter(StudyTask.id == task_id, StudyTask.user_id == current_user.id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Görev bulunamadı.")
    
    update_data = task_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(task, field, value)
    
    db.commit()
    db.refresh(task)
    return task

@router.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    task = db.query(StudyTask).filter(StudyTask.id == task_id, StudyTask.user_id == current_user.id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Görev bulunamadı.")
    db.delete(task)
    db.commit()
    return None
