from datetime import datetime, date
from typing import List, Optional
from pydantic import BaseModel, Field, field_validator, EmailStr

# --- AUTH SCHEMAS ---
class UserRegister(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: str = Field(..., min_length=5, max_length=100)
    password: str = Field(..., min_length=4, max_length=100)

class UserLogin(BaseModel):
    email: str = Field(..., min_length=5, max_length=100)
    password: str = Field(..., min_length=4, max_length=100)

class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    created_at: datetime

    class Config:
        from_attributes = True

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


# --- COURSE SCHEMAS ---
class CourseBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    question_count: int = Field(..., gt=0, description="Toplam soru sayısı (pozitif tam sayı)")
    target_net: float = Field(default=0.0, ge=0.0)
    display_order: int = Field(default=0)
    group_name: Optional[str] = None

class CourseCreate(CourseBase):
    pass

class CourseResponse(CourseBase):
    id: int
    exam_type_id: int

    class Config:
        from_attributes = True

# --- EXAM TYPE SCHEMAS ---
class ExamTypeBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    wrong_penalty_divisor: float = Field(default=4.0, gt=0, description="Yanlışların doğruyu götürme oranı (örn: 4.0)")
    target_net: float = Field(default=0.0, ge=0.0)
    exam_date: Optional[date] = None

class ExamTypeCreate(ExamTypeBase):
    courses: List[CourseCreate] = []

class ExamTypeUpdate(BaseModel):
    name: Optional[str] = None
    wrong_penalty_divisor: Optional[float] = Field(default=None, gt=0)
    target_net: Optional[float] = Field(default=None, ge=0.0)
    exam_date: Optional[date] = None
    courses: Optional[List[CourseCreate]] = None


class ExamTypeResponse(ExamTypeBase):
    id: int
    user_id: int
    created_at: datetime
    courses: List[CourseResponse] = []

    class Config:
        from_attributes = True

# --- COURSE RESULT SCHEMAS ---
class CourseResultBase(BaseModel):
    course_id: int
    correct_count: int = Field(..., ge=0)
    wrong_count: int = Field(..., ge=0)
    blank_count: int = Field(..., ge=0)

class CourseResultCreate(CourseResultBase):
    pass

class CourseResultResponse(CourseResultBase):
    id: int
    practice_exam_id: int
    net: float
    course_name: Optional[str] = None
    question_count: Optional[int] = None

    class Config:
        from_attributes = True

# --- PRACTICE EXAM SCHEMAS ---
class PracticeExamCreate(BaseModel):
    exam_type_id: int
    name: str = Field(..., min_length=1, max_length=150)
    publisher: Optional[str] = None
    exam_date: date
    duration_minutes: Optional[int] = Field(default=None, ge=0)
    difficulty: Optional[str] = Field(default=None, description="Kolay, Orta veya Zor")
    course_results: List[CourseResultCreate]

    @field_validator('difficulty')

    def validate_difficulty(cls, v):
        if v and v not in ["Kolay", "Orta", "Zor"]:
            raise ValueError("Zorluk seviyesi 'Kolay', 'Orta' veya 'Zor' olmalıdır.")
        return v

class PracticeExamUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=150)
    publisher: Optional[str] = None
    exam_date: Optional[date] = None
    duration_minutes: Optional[int] = Field(default=None, ge=0)
    difficulty: Optional[str] = None
    course_results: Optional[List[CourseResultCreate]] = None

class PracticeExamResponse(BaseModel):
    id: int
    user_id: int
    exam_type_id: int
    exam_type_name: Optional[str] = None
    name: str
    publisher: Optional[str] = None
    exam_date: date
    duration_minutes: Optional[int] = None
    difficulty: Optional[str] = None
    total_correct: int
    total_wrong: int
    total_blank: int
    total_net: float
    created_at: datetime
    updated_at: datetime
    course_results: List[CourseResultResponse] = []

    class Config:
        from_attributes = True

# --- DASHBOARD METRICS & ANALYSIS SCHEMAS ---
class DashboardMetrics(BaseModel):
    latest_exam_total_net: Optional[float] = None
    overall_net_average: Optional[float] = None
    last_3_net_average: Optional[float] = None
    last_5_net_average: Optional[float] = None
    highest_total_net: Optional[float] = None
    lowest_total_net: Optional[float] = None
    target_net: Optional[float] = None
    target_net_diff: Optional[float] = None
    most_improved_course: Optional[str] = None
    most_declined_course: Optional[str] = None
    total_exams_count: int = 0
    stability_status: Optional[str] = None  # "İstikrarlı", "Orta düzeyde dalgalı", "Dalgalı"
    explanations: List[str] = []

class CourseMetricDetail(BaseModel):
    course_id: int
    course_name: str
    latest_net: float
    overall_avg_net: float
    last_3_avg_net: float
    highest_net: float
    lowest_net: float
    period_change: Optional[float] = None  # Son 3 vs Önceki 3 farkı
    correct_avg: float
    wrong_avg: float
    blank_avg: float
    std_dev: float
    target_net: float
    target_diff: float
    explanations: List[str] = []

class GoalTrackingResponse(BaseModel):
    target_total_net: float
    latest_exam_net: Optional[float] = None
    latest_vs_target_diff: Optional[float] = None
    last_5_avg_net: Optional[float] = None
    last_5_vs_target_diff: Optional[float] = None
    closest_course_to_target: Optional[dict] = None
    furthest_course_to_target: Optional[dict] = None
    course_goals: List[dict] = []
    explanations: List[str] = []

class GeneralReportResponse(BaseModel):
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    exam_count: int
    first_exam_net: Optional[float] = None
    last_exam_net: Optional[float] = None
    net_change: Optional[float] = None
    average_net: Optional[float] = None
    highest_net: Optional[float] = None
    lowest_net: Optional[float] = None
    most_improved_course: Optional[str] = None
    most_declined_course: Optional[str] = None
    stability_status: Optional[str] = None
    target_diff: Optional[float] = None
    course_summaries: List[dict] = []
    explanations: List[str] = []

# --- STUDY NOTES SCHEMAS ---
class StudyNoteBase(BaseModel):
    exam_type_id: Optional[int] = None
    course_name: Optional[str] = None
    title: str = Field(..., min_length=1, max_length=200)
    content: str = Field(..., min_length=1)
    note_type: str = Field(default="general", description="general, formula, mistake, reminder")

class StudyNoteCreate(StudyNoteBase):
    pass

class StudyNoteUpdate(BaseModel):
    exam_type_id: Optional[int] = None
    course_name: Optional[str] = None
    title: Optional[str] = None
    content: Optional[str] = None
    note_type: Optional[str] = None

class StudyNoteResponse(StudyNoteBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# --- STUDY TASKS SCHEMAS ---
class StudyTaskBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=250)
    course_name: Optional[str] = None
    is_completed: bool = False
    priority: str = Field(default="medium", description="high, medium, low")
    due_date: Optional[date] = None

class StudyTaskCreate(StudyTaskBase):
    pass

class StudyTaskUpdate(BaseModel):
    title: Optional[str] = None
    course_name: Optional[str] = None
    is_completed: Optional[bool] = None
    priority: Optional[str] = None
    due_date: Optional[date] = None

class StudyTaskResponse(StudyTaskBase):
    id: int
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True

