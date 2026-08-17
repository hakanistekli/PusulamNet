from typing import List, Optional
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, status, Query, Response
from sqlalchemy.orm import Session
try:
    from app.database import get_db
except ModuleNotFoundError:
    try:
        from database import get_db
    except ModuleNotFoundError:
        from database import get_db
try:
    from app.models import User, ExamType, Course, PracticeExam, CourseResult
except ModuleNotFoundError:
    try:
        from models import User, ExamType, Course, PracticeExam, CourseResult
    except ModuleNotFoundError:
        from models import User, ExamType, Course, PracticeExam, CourseResult
try:
    from app.schemas import PracticeExamCreate, PracticeExamUpdate, PracticeExamResponse
except ModuleNotFoundError:
    try:
        from schemas import PracticeExamCreate, PracticeExamUpdate, PracticeExamResponse
    except ModuleNotFoundError:
        from schemas import PracticeExamCreate, PracticeExamUpdate, PracticeExamResponse
try:
    from app.services.net_calculator import NetCalculatorService
except ModuleNotFoundError:
    try:
        from services.net_calculator import NetCalculatorService
    except ModuleNotFoundError:
        from net_calculator import NetCalculatorService
try:
    from app.services.export_service import ExportService
except ModuleNotFoundError:
    try:
        from services.export_service import ExportService
    except ModuleNotFoundError:
        from export_service import ExportService

try:
    from app.services.auth_service import get_current_user
except ModuleNotFoundError:
    try:
        from services.auth_service import get_current_user
    except ModuleNotFoundError:
        from auth_service import get_current_user

router = APIRouter(prefix="/api/exams", tags=["Deneme Sınavları"])

@router.get("", response_model=List[PracticeExamResponse])
def list_exams(
    exam_type_id: Optional[int] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(PracticeExam).filter_by(user_id=current_user.id)

    if exam_type_id:
        query = query.filter(PracticeExam.exam_type_id == exam_type_id)
    if start_date:
        query = query.filter(PracticeExam.exam_date >= start_date)
    if end_date:
        query = query.filter(PracticeExam.exam_date <= end_date)

    exams = query.order_by(PracticeExam.exam_date.desc(), PracticeExam.id.desc()).all()
    
    response_list = []
    for exam in exams:
        item = PracticeExamResponse.model_validate(exam)
        item.exam_type_name = exam.exam_type.name if exam.exam_type else ""
        for cr in item.course_results:
            course = db.query(Course).filter_by(id=cr.course_id).first()
            if course:
                cr.course_name = course.name
                cr.question_count = course.question_count
        response_list.append(item)
        
    return response_list

@router.post("", response_model=PracticeExamResponse, status_code=status.HTTP_201_CREATED)
def create_exam(data: PracticeExamCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    exam_type = db.query(ExamType).filter_by(id=data.exam_type_id).first()
    if not exam_type:
        raise HTTPException(status_code=404, detail="Seçilen sınav türü bulunamadı.")

    courses = db.query(Course).filter_by(exam_type_id=exam_type.id).all()
    question_count_map = {c.id: c.question_count for c in courses}
    course_name_map = {c.id: c.name for c in courses}

    course_data_input = [cr.model_dump() for cr in data.course_results]

    try:
        tot_correct, tot_wrong, tot_blank, tot_net, validated_results = NetCalculatorService.calculate_exam_totals(
            course_data_list=course_data_input,
            question_count_map=question_count_map,
            penalty_divisor=exam_type.wrong_penalty_divisor,
            course_name_map=course_name_map
        )
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))

    practice_exam = PracticeExam(
        user_id=current_user.id,
        exam_type_id=exam_type.id,
        name=data.name,
        publisher=data.publisher,
        exam_date=data.exam_date,
        duration_minutes=data.duration_minutes,
        difficulty=data.difficulty,
        total_correct=tot_correct,
        total_wrong=tot_wrong,
        total_blank=tot_blank,
        total_net=tot_net
    )

    db.add(practice_exam)
    db.commit()
    db.refresh(practice_exam)

    for vr in validated_results:
        cr_obj = CourseResult(
            practice_exam_id=practice_exam.id,
            course_id=vr["course_id"],
            correct_count=vr["correct_count"],
            wrong_count=vr["wrong_count"],
            blank_count=vr["blank_count"],
            net=vr["net"]
        )
        db.add(cr_obj)

    db.commit()
    db.refresh(practice_exam)

    res = PracticeExamResponse.model_validate(practice_exam)
    res.exam_type_name = exam_type.name
    for cr in res.course_results:
        course = db.query(Course).filter_by(id=cr.course_id).first()
        if course:
            cr.course_name = course.name
            cr.question_count = course.question_count
    return res

@router.get("/{exam_id}", response_model=PracticeExamResponse)
def get_exam(exam_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    exam = db.query(PracticeExam).filter_by(id=exam_id, user_id=current_user.id).first()
    if not exam:
        raise HTTPException(status_code=404, detail="Deneme sınavı bulunamadı.")
    
    res = PracticeExamResponse.model_validate(exam)
    res.exam_type_name = exam.exam_type.name if exam.exam_type else ""
    for cr in res.course_results:
        course = db.query(Course).filter_by(id=cr.course_id).first()
        if course:
            cr.course_name = course.name
            cr.question_count = course.question_count
    return res

@router.put("/{exam_id}", response_model=PracticeExamResponse)
def update_exam(exam_id: int, data: PracticeExamUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    exam = db.query(PracticeExam).filter_by(id=exam_id, user_id=current_user.id).first()
    if not exam:
        raise HTTPException(status_code=404, detail="Deneme sınavı bulunamadı.")

    if data.name is not None:
        exam.name = data.name
    if data.publisher is not None:
        exam.publisher = data.publisher
    if data.exam_date is not None:
        exam.exam_date = data.exam_date
    if data.duration_minutes is not None:
        exam.duration_minutes = data.duration_minutes
    if data.difficulty is not None:
        exam.difficulty = data.difficulty

    if data.course_results is not None:
        courses = db.query(Course).filter_by(exam_type_id=exam.exam_type_id).all()
        question_count_map = {c.id: c.question_count for c in courses}
        course_name_map = {c.id: c.name for c in courses}
        penalty_divisor = exam.exam_type.wrong_penalty_divisor if exam.exam_type else 4.0

        course_data_input = [cr.model_dump() for cr in data.course_results]

        try:
            tot_correct, tot_wrong, tot_blank, tot_net, validated_results = NetCalculatorService.calculate_exam_totals(
                course_data_list=course_data_input,
                question_count_map=question_count_map,
                penalty_divisor=penalty_divisor,
                course_name_map=course_name_map
            )
        except ValueError as ve:
            raise HTTPException(status_code=400, detail=str(ve))

        exam.total_correct = tot_correct
        exam.total_wrong = tot_wrong
        exam.total_blank = tot_blank
        exam.total_net = tot_net

        db.query(CourseResult).filter_by(practice_exam_id=exam.id).delete()
        for vr in validated_results:
            cr_obj = CourseResult(
                practice_exam_id=exam.id,
                course_id=vr["course_id"],
                correct_count=vr["correct_count"],
                wrong_count=vr["wrong_count"],
                blank_count=vr["blank_count"],
                net=vr["net"]
            )
            db.add(cr_obj)

    db.commit()
    db.refresh(exam)

    res = PracticeExamResponse.model_validate(exam)
    res.exam_type_name = exam.exam_type.name if exam.exam_type else ""
    for cr in res.course_results:
        course = db.query(Course).filter_by(id=cr.course_id).first()
        if course:
            cr.course_name = course.name
            cr.question_count = course.question_count
    return res

@router.delete("/{exam_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_exam(exam_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    exam = db.query(PracticeExam).filter_by(id=exam_id, user_id=current_user.id).first()
    if not exam:
        raise HTTPException(status_code=404, detail="Deneme sınavı bulunamadı.")
    db.delete(exam)
    db.commit()
    return None

@router.get("/export/csv")
def export_csv(
    exam_type_id: Optional[int] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    exams = list_exams(exam_type_id=exam_type_id, start_date=start_date, end_date=end_date, current_user=current_user, db=db)
    exam_dicts = [e.model_dump() for e in exams]
    csv_content = ExportService.export_exams_to_csv(exam_dicts)
    
    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=deneme_sinavlari.csv"}
    )

@router.get("/export/excel")
def export_excel(
    exam_type_id: Optional[int] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    exams = list_exams(exam_type_id=exam_type_id, start_date=start_date, end_date=end_date, current_user=current_user, db=db)
    exam_dicts = [e.model_dump() for e in exams]
    excel_bytes = ExportService.export_exams_to_excel(exam_dicts)
    
    return Response(
        content=excel_bytes,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=deneme_sinavlari.xlsx"}
    )
