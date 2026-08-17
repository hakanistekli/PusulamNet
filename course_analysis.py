from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
try:
    from app.database import get_db
except ModuleNotFoundError:
    try:
        from database import get_db
    except ModuleNotFoundError:
        from database import get_db
try:
    from app.models import Course, PracticeExam, CourseResult
except ModuleNotFoundError:
    try:
        from models import Course, PracticeExam, CourseResult
    except ModuleNotFoundError:
        from models import Course, PracticeExam, CourseResult
try:
    from app.services.analysis_service import AnalysisService
except ModuleNotFoundError:
    try:
        from services.analysis_service import AnalysisService
    except ModuleNotFoundError:
        from analysis_service import AnalysisService
try:
    from app.services.explanation_service import ExplanationService
except ModuleNotFoundError:
    try:
        from services.explanation_service import ExplanationService
    except ModuleNotFoundError:
        from explanation_service import ExplanationService

router = APIRouter(prefix="/api/course-analysis", tags=["Ders Analizi"])

@router.get("/courses")
def get_available_courses(exam_type_id: Optional[int] = None, db: Session = Depends(get_db)):
    query = db.query(Course)
    if exam_type_id:
        query = query.filter_by(exam_type_id=exam_type_id)
    courses = query.order_by(Course.display_order).all()
    return [{"id": c.id, "name": c.name, "question_count": c.question_count, "exam_type_id": c.exam_type_id} for c in courses]

@router.get("/{course_id}")
def get_course_analysis(course_id: int, db: Session = Depends(get_db)):
    course = db.query(Course).filter_by(id=course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Ders bulunamadı.")

    results_query = (
        db.query(CourseResult, PracticeExam.exam_date, PracticeExam.name.label("exam_name"))
        .join(PracticeExam, CourseResult.practice_exam_id == PracticeExam.id)
        .filter(CourseResult.course_id == course.id)
        .order_by(PracticeExam.exam_date.asc())
        .all()
    )

    formatted_results = [
        {
            "net": cr.net,
            "correct_count": cr.correct_count,
            "wrong_count": cr.wrong_count,
            "blank_count": cr.blank_count,
            "exam_date": exam_date,
            "exam_date_str": exam_date.strftime("%d.%m.%Y"),
            "exam_name": exam_name
        }
        for cr, exam_date, exam_name in results_query
    ]

    stats = AnalysisService.calculate_course_performance(
        course_id=course.id,
        course_name=course.name,
        results_list=formatted_results,
        target_net=course.target_net
    )

    explanations = ExplanationService.generate_course_explanations(stats)
    stats["explanations"] = explanations
    stats["question_count"] = course.question_count

    # Trend chart data
    chart_data = [
        {
            "date": item["exam_date_str"],
            "exam_name": item["exam_name"],
            "net": item["net"],
            "correct": item["correct_count"],
            "wrong": item["wrong_count"],
            "blank": item["blank_count"]
        }
        for item in formatted_results
    ]

    # Comparison table (Reverse chronological)
    comparison_table = list(reversed(formatted_results))

    return {
        "metrics": stats,
        "chart_data": chart_data,
        "comparison_table": comparison_table
    }
