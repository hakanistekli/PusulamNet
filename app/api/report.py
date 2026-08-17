from typing import Optional
from datetime import date
from fastapi import APIRouter, Depends, Response
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

router = APIRouter(prefix="/api/report", tags=["Genel Rapor"])

def build_report_data(

    db: Session,
    user: User,
    exam_type_id: Optional[int] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None
) -> dict:

    
    exam_type = None
    if exam_type_id:
        exam_type = db.query(ExamType).filter_by(id=exam_type_id).first()
    if not exam_type:
        exam_type = db.query(ExamType).filter_by(user_id=user.id).first()

    query = db.query(PracticeExam).filter_by(user_id=user.id)
    if exam_type:
        query = query.filter(PracticeExam.exam_type_id == exam_type.id)
    if start_date:
        query = query.filter(PracticeExam.exam_date >= start_date)
    if end_date:
        query = query.filter(PracticeExam.exam_date <= end_date)

    exams = query.order_by(PracticeExam.exam_date.asc(), PracticeExam.id.asc()).all()

    if not exams:
        return {
            "start_date": start_date.strftime("%d.%m.%Y") if start_date else None,
            "end_date": end_date.strftime("%d.%m.%Y") if end_date else None,
            "exam_count": 0,
            "first_exam_net": None,
            "last_exam_net": None,
            "net_change": None,
            "average_net": None,
            "highest_net": None,
            "lowest_net": None,
            "most_improved_course": None,
            "most_declined_course": None,
            "stability_status": "Yetersiz Veri",
            "target_diff": None,
            "course_summaries": [],
            "explanations": ["Seçilen tarih aralığında deneme sınavı kaydı bulunamadı."]
        }

    exams_dict = [
        {
            "id": e.id,
            "name": e.name,
            "exam_date": e.exam_date.strftime("%d.%m.%Y"),
            "raw_date": e.exam_date,
            "total_correct": e.total_correct,
            "total_wrong": e.total_wrong,
            "total_blank": e.total_blank,
            "total_net": e.total_net
        }
        for e in exams
    ]

    target_total_net = exam_type.target_net if exam_type else 0.0
    stats = AnalysisService.calculate_overall_statistics(exams_dict, target_net=target_total_net)

    first_exam_net = round(exams[0].total_net, 2)
    last_exam_net = round(exams[-1].total_net, 2)
    net_change = round(last_exam_net - first_exam_net, 2)

    # Ders bazlı istatistikler
    course_summaries = []
    if exam_type:
        courses = db.query(Course).filter_by(exam_type_id=exam_type.id).order_by(Course.display_order).all()
        for course in courses:
            results_query = (
                db.query(CourseResult, PracticeExam.exam_date)
                .join(PracticeExam, CourseResult.practice_exam_id == PracticeExam.id)
                .filter(CourseResult.course_id == course.id)
            )
            if start_date:
                results_query = results_query.filter(PracticeExam.exam_date >= start_date)
            if end_date:
                results_query = results_query.filter(PracticeExam.exam_date <= end_date)

            results = results_query.order_by(PracticeExam.exam_date.asc()).all()
            formatted_res = [
                {
                    "net": cr.net,
                    "correct_count": cr.correct_count,
                    "wrong_count": cr.wrong_count,
                    "blank_count": cr.blank_count,
                    "exam_date": exam_date
                }
                for cr, exam_date in results
            ]

            c_stat = AnalysisService.calculate_course_performance(
                course_id=course.id,
                course_name=course.name,
                results_list=formatted_res,
                target_net=course.target_net
            )
            course_summaries.append(c_stat)

    most_improved, most_declined = AnalysisService.identify_course_growth_and_decline(course_summaries)
    stats["most_improved_course"] = most_improved
    stats["most_declined_course"] = most_declined

    explanations = ExplanationService.generate_dashboard_explanations(
        overall_stats=stats,
        most_improved=most_improved,
        most_declined=most_declined
    )

    return {
        "start_date": start_date.strftime("%d.%m.%Y") if start_date else "Tüm Zamanlar",
        "end_date": end_date.strftime("%d.%m.%Y") if end_date else "Tüm Zamanlar",
        "exam_count": len(exams),
        "first_exam_net": first_exam_net,
        "last_exam_net": last_exam_net,
        "net_change": net_change,
        "average_net": stats.get("overall_net_average"),
        "highest_net": stats.get("highest_total_net"),
        "lowest_net": stats.get("lowest_total_net"),
        "most_improved_course": most_improved,
        "most_declined_course": most_declined,
        "stability_status": stats.get("stability_status"),
        "target_diff": stats.get("target_net_diff"),
        "course_summaries": course_summaries,
        "explanations": explanations
    }

@router.get("")
def get_report(
    exam_type_id: Optional[int] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return build_report_data(db, current_user, exam_type_id, start_date, end_date)

@router.get("/export/csv")
def export_report_csv(
    exam_type_id: Optional[int] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    report_data = build_report_data(db, current_user, exam_type_id, start_date, end_date)
    csv_content = ExportService.export_report_to_csv(report_data)
    
    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=genel_performans_raporu.csv"}
    )

@router.get("/export/excel")
def export_report_excel(
    exam_type_id: Optional[int] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    report_data = build_report_data(db, current_user, exam_type_id, start_date, end_date)
    excel_bytes = ExportService.export_report_to_excel(report_data)
    
    return Response(
        content=excel_bytes,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=genel_performans_raporu.xlsx"}
    )

