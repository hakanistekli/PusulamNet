from datetime import datetime, date
from sqlalchemy import (
    Column, Integer, String, Float, DateTime, Date, ForeignKey, UniqueConstraint, Text, Boolean
)

from sqlalchemy.orm import relationship
try:
    from app.database import Base
except ModuleNotFoundError:
    try:
        from database import Base
    except ModuleNotFoundError:
        from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), nullable=False, unique=True, index=True)
    hashed_password = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


    exam_types = relationship("ExamType", back_populates="user", cascade="all, delete-orphan")
    practice_exams = relationship("PracticeExam", back_populates="user", cascade="all, delete-orphan")

class ExamType(Base):
    __tablename__ = "exam_types"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(100), nullable=False)
    wrong_penalty_divisor = Column(Float, default=4.0, nullable=False)  # 4 yanlış 1 doğruyu götürür
    target_net = Column(Float, default=0.0, nullable=False)
    exam_date = Column(Date, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


    user = relationship("User", back_populates="exam_types")
    courses = relationship("Course", back_populates="exam_type", cascade="all, delete-orphan", order_by="Course.display_order")
    practice_exams = relationship("PracticeExam", back_populates="exam_type", cascade="all, delete-orphan")

class Course(Base):
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, index=True)
    exam_type_id = Column(Integer, ForeignKey("exam_types.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(100), nullable=False)
    question_count = Column(Integer, nullable=False)
    target_net = Column(Float, default=0.0, nullable=False)
    display_order = Column(Integer, default=0, nullable=False)
    group_name = Column(String(100), nullable=True, default=None)  # Ders grubu (ör: 'Temel Tıp', 'Klinik Diş')

    exam_type = relationship("ExamType", back_populates="courses")
    course_results = relationship("CourseResult", back_populates="course", cascade="all, delete-orphan")

class PracticeExam(Base):
    __tablename__ = "practice_exams"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    exam_type_id = Column(Integer, ForeignKey("exam_types.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(150), nullable=False)
    publisher = Column(String(100), nullable=True)
    exam_date = Column(Date, default=date.today, nullable=False)
    duration_minutes = Column(Integer, nullable=True)
    difficulty = Column(String(20), nullable=True) # Kolay, Orta, Zor
    total_correct = Column(Integer, default=0, nullable=False)
    total_wrong = Column(Integer, default=0, nullable=False)
    total_blank = Column(Integer, default=0, nullable=False)
    total_net = Column(Float, default=0.0, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="practice_exams")
    exam_type = relationship("ExamType", back_populates="practice_exams")
    course_results = relationship("CourseResult", back_populates="practice_exam", cascade="all, delete-orphan")

class CourseResult(Base):
    __tablename__ = "course_results"

    id = Column(Integer, primary_key=True, index=True)
    practice_exam_id = Column(Integer, ForeignKey("practice_exams.id", ondelete="CASCADE"), nullable=False)
    course_id = Column(Integer, ForeignKey("courses.id", ondelete="CASCADE"), nullable=False)
    correct_count = Column(Integer, nullable=False, default=0)
    wrong_count = Column(Integer, nullable=False, default=0)
    blank_count = Column(Integer, nullable=False, default=0)
    net = Column(Float, nullable=False, default=0.0)

    practice_exam = relationship("PracticeExam", back_populates="course_results")
    course = relationship("Course", back_populates="course_results")

    __table_args__ = (
        UniqueConstraint("practice_exam_id", "course_id", name="uix_exam_course"),
    )

class StudyNote(Base):
    __tablename__ = "study_notes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    exam_type_id = Column(Integer, ForeignKey("exam_types.id", ondelete="SET NULL"), nullable=True)
    course_name = Column(String(100), nullable=True)
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    note_type = Column(String(50), default="general")  # general, formula, mistake, reminder
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User")
    exam_type = relationship("ExamType")

class StudyTask(Base):
    __tablename__ = "study_tasks"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(250), nullable=False)
    course_name = Column(String(100), nullable=True)
    is_completed = Column(Boolean, default=False, nullable=False)
    priority = Column(String(20), default="medium")  # high, medium, low
    due_date = Column(Date, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User")

