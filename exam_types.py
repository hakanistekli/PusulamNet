from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
try:
    from app.database import get_db
except ModuleNotFoundError:
    try:
        from database import get_db
    except ModuleNotFoundError:
        from database import get_db
try:
    from app.models import User, ExamType, Course
except ModuleNotFoundError:
    try:
        from models import User, ExamType, Course
    except ModuleNotFoundError:
        from models import User, ExamType, Course
try:
    from app.schemas import ExamTypeCreate, ExamTypeUpdate, ExamTypeResponse, CourseCreate
except ModuleNotFoundError:
    try:
        from schemas import ExamTypeCreate, ExamTypeUpdate, ExamTypeResponse, CourseCreate
    except ModuleNotFoundError:
        from schemas import ExamTypeCreate, ExamTypeUpdate, ExamTypeResponse, CourseCreate

router = APIRouter(prefix="/api/exam-types", tags=["Sınav Ayarları"])

try:
    from app.services.auth_service import get_current_user
except ModuleNotFoundError:
    try:
        from services.auth_service import get_current_user
    except ModuleNotFoundError:
        from auth_service import get_current_user
try:
    from app.services.demo_data_service import DemoDataService
except ModuleNotFoundError:
    try:
        from services.demo_data_service import DemoDataService
    except ModuleNotFoundError:
        from demo_data_service import DemoDataService

@router.get("", response_model=List[ExamTypeResponse])
def list_exam_types(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    count = db.query(ExamType).filter_by(user_id=current_user.id).count()
    if count == 0:
        DemoDataService.create_predefined_exam_types(db, current_user)
    exam_types = db.query(ExamType).filter_by(user_id=current_user.id).all()
    return exam_types

@router.post("", response_model=ExamTypeResponse, status_code=status.HTTP_201_CREATED)
def create_exam_type(data: ExamTypeCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    exam_type = ExamType(
        user_id=current_user.id,
        name=data.name,
        wrong_penalty_divisor=data.wrong_penalty_divisor,
        target_net=data.target_net,
        exam_date=data.exam_date
    )


    db.add(exam_type)
    db.commit()
    db.refresh(exam_type)

    for idx, c in enumerate(data.courses, start=1):
        course = Course(
            exam_type_id=exam_type.id,
            name=c.name,
            question_count=c.question_count,
            target_net=c.target_net,
            display_order=c.display_order if c.display_order > 0 else idx,
            group_name=c.group_name
        )
        db.add(course)

    db.commit()
    db.refresh(exam_type)
    return exam_type

@router.get("/{exam_type_id}", response_model=ExamTypeResponse)
def get_exam_type(exam_type_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    exam_type = db.query(ExamType).filter_by(id=exam_type_id, user_id=current_user.id).first()
    if not exam_type:
        raise HTTPException(status_code=404, detail="Sınav türü bulunamadı.")
    return exam_type

@router.put("/{exam_type_id}", response_model=ExamTypeResponse)
def update_exam_type(exam_type_id: int, data: ExamTypeUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    exam_type = db.query(ExamType).filter_by(id=exam_type_id, user_id=current_user.id).first()
    if not exam_type:
        raise HTTPException(status_code=404, detail="Sınav türü bulunamadı.")

    if data.name is not None:
        exam_type.name = data.name
    if data.wrong_penalty_divisor is not None:
        exam_type.wrong_penalty_divisor = data.wrong_penalty_divisor
    if data.target_net is not None:
        exam_type.target_net = data.target_net
    if data.exam_date is not None:
        exam_type.exam_date = data.exam_date


    if data.courses is not None:
        # Mevcut dersleri sil ve yenilerini ekle
        db.query(Course).filter_by(exam_type_id=exam_type.id).delete()
        for idx, c in enumerate(data.courses, start=1):
            course = Course(
                exam_type_id=exam_type.id,
                name=c.name,
                question_count=c.question_count,
                target_net=c.target_net,
                display_order=c.display_order if c.display_order > 0 else idx,
                group_name=c.group_name
            )
            db.add(course)

    db.commit()
    db.refresh(exam_type)
    return exam_type

@router.delete("/{exam_type_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_exam_type(exam_type_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    exam_type = db.query(ExamType).filter_by(id=exam_type_id, user_id=current_user.id).first()
    if not exam_type:
        raise HTTPException(status_code=404, detail="Sınav türü bulunamadı.")
    db.delete(exam_type)
    db.commit()
    return None
