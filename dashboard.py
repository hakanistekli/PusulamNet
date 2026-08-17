from typing import Optional, List, Dict, Any
from datetime import date
from fastapi import APIRouter, Depends, Query
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
    from app.services.auth_service import get_current_user
except ModuleNotFoundError:
    try:
        from services.auth_service import get_current_user
    except ModuleNotFoundError:
        from auth_service import get_current_user

router = APIRouter(prefix="/api/dashboard", tags=["Ana Panel"])

@router.get("")
def get_dashboard_data(
    exam_type_id: Optional[int] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    user = current_user

    
    # Varsayılan sınav türünü belirle
    selected_exam_type = None
    if exam_type_id:
        selected_exam_type = db.query(ExamType).filter_by(id=exam_type_id, user_id=user.id).first()
    if not selected_exam_type:
        selected_exam_type = db.query(ExamType).filter_by(user_id=user.id).first()

    target_net = selected_exam_type.target_net if selected_exam_type else 0.0


    # Query practice exams
    query = db.query(PracticeExam).filter_by(user_id=user.id)
    if selected_exam_type:
        query = query.filter(PracticeExam.exam_type_id == selected_exam_type.id)
    if start_date:
        query = query.filter(PracticeExam.exam_date >= start_date)
    if end_date:
        query = query.filter(PracticeExam.exam_date <= end_date)

    # Sort chronologically for analysis
    exams = query.order_by(PracticeExam.exam_date.asc(), PracticeExam.id.asc()).all()

    exams_list_dict = [
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

    # Calculate overall statistics
    stats = AnalysisService.calculate_overall_statistics(exams_list_dict, target_net=target_net)

    # Ders bazlı analizleri hesapla (En çok gelişen / düşen dersi bulmak için)
    course_analysis_list = []
    declined_amount = None
    if selected_exam_type:
        courses = db.query(Course).filter_by(exam_type_id=selected_exam_type.id).order_by(Course.display_order).all()
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
            course_analysis_list.append(c_stat)

    most_improved, most_declined = AnalysisService.identify_course_growth_and_decline(course_analysis_list)
    stats["most_improved_course"] = most_improved
    stats["most_declined_course"] = most_declined

    if most_declined:
        for c in course_analysis_list:
            if c["course_name"] == most_declined:
                diff = c.get("period_change")
                if diff is not None:
                    declined_amount = abs(diff)
                else:
                    declined_amount = abs(round(c["last_3_avg_net"] - c["overall_avg_net"], 2))

    # Otomatik metin açıklamaları üret
    explanations = ExplanationService.generate_dashboard_explanations(
        overall_stats=stats,
        most_improved=most_improved,
        most_declined=most_declined,
        declined_amount=declined_amount
    )
    stats["explanations"] = explanations

    # Grafikler İçin Veri Hazırlığı
    # 1. Tarihe Göre Toplam Net Çizgi Grafiği
    trend_chart = [
        {"date": e["exam_date"], "exam_name": e["name"], "total_net": e["total_net"]}
        for e in exams_list_dict
    ]

    # 2. Son Denemedeki Ders Netleri Sütun Grafiği
    latest_exam_courses_chart = []
    if exams:
        latest_exam = exams[-1]
        for cr in latest_exam.course_results:
            c = db.query(Course).filter_by(id=cr.course_id).first()
            c_name = c.name if c else f"Ders #{cr.course_id}"
            latest_exam_courses_chart.append({
                "course_name": c_name,
                "net": cr.net,
                "target_net": c.target_net if c else 0.0
            })

    # 3. Doğru/Yanlış/Boş Dağılımı Çizgi/Sütun Grafiği
    answers_breakdown_chart = [
        {
            "date": e["exam_date"],
            "exam_name": e["name"],
            "correct": e["total_correct"],
            "wrong": e["total_wrong"],
            "blank": e["total_blank"]
        }
        for e in exams_list_dict
    ]

    # 4. Son 5 Deneme Ortalaması ile Hedef Net Karşılaştırması
    last_5_avg = stats.get("last_5_net_average", 0.0) or 0.0
    target_vs_last5_chart = [
        {"metric": "Son 5 Deneme Ortalaması", "net": last_5_avg},
        {"metric": "Hedef Toplam Net", "net": target_net}
    ]

    return {
        "metrics": stats,
        "selected_exam_type_id": selected_exam_type.id if selected_exam_type else None,
        "selected_exam_type_name": selected_exam_type.name if selected_exam_type else "",
        "charts": {
            "trend_chart": trend_chart,
            "latest_exam_courses": latest_exam_courses_chart,
            "answers_breakdown": answers_breakdown_chart,
            "target_vs_last5": target_vs_last5_chart
        }
    }
