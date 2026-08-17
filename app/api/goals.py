from typing import Optional
from fastapi import APIRouter, Depends
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

router = APIRouter(prefix="/api/goals", tags=["Hedef Takibi"])

try:
    from app.services.auth_service import get_current_user
except ModuleNotFoundError:
    try:
        from services.auth_service import get_current_user
    except ModuleNotFoundError:
        from auth_service import get_current_user

@router.get("")
def get_goal_tracking(
    exam_type_id: Optional[int] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    user = current_user

    
    exam_type = None
    if exam_type_id:
        exam_type = db.query(ExamType).filter_by(id=exam_type_id).first()
    if not exam_type:
        exam_type = db.query(ExamType).filter_by(user_id=user.id).first()

    if not exam_type:
        return {
            "target_total_net": 0.0,
            "latest_exam_net": None,
            "latest_vs_target_diff": None,
            "last_5_avg_net": None,
            "last_5_vs_target_diff": None,
            "closest_course_to_target": None,
            "furthest_course_to_target": None,
            "course_goals": [],
            "explanations": ["Henüz tanımlı bir sınav türü veya hedef bulunmuyor."]
        }

    target_total_net = exam_type.target_net

    exams = (
        db.query(PracticeExam)
        .filter_by(user_id=user.id, exam_type_id=exam_type.id)
        .order_by(PracticeExam.exam_date.asc())
        .all()
    )

    exams_dict = [{"total_net": e.total_net, "exam_date": e.exam_date} for e in exams]
    stats = AnalysisService.calculate_overall_statistics(exams_dict, target_net=target_total_net)

    latest_exam_net = stats.get("latest_exam_total_net")
    last_5_avg_net = stats.get("last_5_net_average")

    latest_vs_target_diff = round(target_total_net - latest_exam_net, 2) if latest_exam_net is not None and target_total_net > 0 else None
    last_5_vs_target_diff = round(target_total_net - last_5_avg_net, 2) if last_5_avg_net is not None and target_total_net > 0 else None

    # Ders bazlı hedefler ve ortalamalar
    courses = db.query(Course).filter_by(exam_type_id=exam_type.id).order_by(Course.display_order).all()
    course_goals = []

    for course in courses:
        results = (
            db.query(CourseResult, PracticeExam.exam_date)
            .join(PracticeExam, CourseResult.practice_exam_id == PracticeExam.id)
            .filter(CourseResult.course_id == course.id)
            .order_by(PracticeExam.exam_date.asc())
            .all()
        )
        formatted_res = [{"net": cr.net, "correct_count": cr.correct_count, "wrong_count": cr.wrong_count, "blank_count": cr.blank_count, "exam_date": exam_date} for cr, exam_date in results]
        
        c_stat = AnalysisService.calculate_course_performance(
            course_id=course.id,
            course_name=course.name,
            results_list=formatted_res,
            target_net=course.target_net
        )

        current_avg = c_stat["overall_avg_net"]
        c_target = course.target_net
        diff = round(c_target - current_avg, 2) if c_target > 0 else 0.0

        course_goals.append({
            "course_id": course.id,
            "course_name": course.name,
            "question_count": course.question_count,
            "target_net": c_target,
            "current_avg_net": current_avg,
            "latest_net": c_stat["latest_net"],
            "difference": diff,
            "is_reached": diff <= 0 if c_target > 0 else False
        })

    # Hedefe en yakın ve en uzak ders (hedef net tanımlı olanlar arasından)
    courses_with_target = [cg for cg in course_goals if cg["target_net"] > 0]
    closest_course = None
    furthest_course = None

    if courses_with_target:
        # fark (target - current_avg). En küçük fark en yakın (veya aşmış), en büyük fark en uzak
        sorted_by_diff = sorted(courses_with_target, key=lambda x: x["difference"])
        closest_course = sorted_by_diff[0]  # En az kalan veya en çok aşan
        furthest_course = sorted_by_diff[-1] # En fazla net eksiği olan

    # Kural tabanlı açıklamalar
    explanations = []
    if target_total_net > 0:
        if last_5_vs_target_diff is not None:
            if last_5_vs_target_diff > 0:
                explanations.append(f"Genel hedefine ulaşmak için son 5 deneme ortalamana göre {last_5_vs_target_diff:.1f} net artışına ihtiyacın var.")
            else:
                explanations.append(f"Tebrikler! Son 5 deneme ortalaman belirlediğin genel hedefin {abs(last_5_vs_target_diff):.1f} net üzerinde.")
    
    if closest_course and closest_course["difference"] <= 0:
        explanations.append(f"{closest_course['course_name']} dersinde hedefini başarıyla yakaladın veya aştın.")
    elif closest_course:
        explanations.append(f"Hedefe en yakın olduğun ders: {closest_course['course_name']} (Kalan fark: {closest_course['difference']:.1f} net).")

    if furthest_course and furthest_course["difference"] > 0:
        explanations.append(f"Hedefe en uzak olduğun ders: {furthest_course['course_name']} (Kalan fark: {furthest_course['difference']:.1f} net).")

    return {
        "exam_type_id": exam_type.id,
        "exam_type_name": exam_type.name,
        "target_total_net": target_total_net,
        "latest_exam_net": latest_exam_net,
        "latest_vs_target_diff": latest_vs_target_diff,
        "last_5_avg_net": last_5_avg_net,
        "last_5_vs_target_diff": last_5_vs_target_diff,
        "closest_course_to_target": closest_course,
        "furthest_course_to_target": furthest_course,
        "course_goals": course_goals,
        "explanations": explanations
    }
