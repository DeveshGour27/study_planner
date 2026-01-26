from sqlalchemy import Column, String, Integer, JSON, Boolean, Date, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import uuid

Base = declarative_base()


class User(Base):
    __tablename__ = 'users'
    
    user_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    username = Column(String, unique=True, nullable=False, index=True)
    email = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=False)
    full_name = Column(String, nullable=False)
    age_group = Column(String, nullable=True)  # ← Added this
    
    is_active = Column(Boolean, default=True)
    last_login = Column(DateTime, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)


class StudentProfile(Base):
    __tablename__ = 'student_profiles'
    
    profile_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey('users.user_id'), nullable=False)
    
    topics_to_learn = Column(JSON, default=list)
    current_levels = Column(JSON, default=dict)
    
    hours_per_day = Column(Integer, default=4)
    
    # Date fields (matching your database)
    target_date = Column(Date, nullable=True)
    target_completion_date = Column(Date, nullable=True)
    study_start_date = Column(Date, nullable=True)
    last_active_date = Column(Date, nullable=True)
    
    # Day tracking
    current_day_number = Column(Integer, default=1)
    total_planned_days = Column(Integer, default=30)
    days_remaining = Column(Integer, nullable=True)
    streak_count = Column(Integer, default=0)
    
    # Settings
    timezone = Column(String, nullable=True)
    onboarding_completed = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, nullable=True)


class StudyPlan(Base):
    __tablename__ = 'study_plans'
    
    plan_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey('users.user_id'), nullable=False)
    
    day_number = Column(Integer, nullable=False)
    plan_date = Column(Date, nullable=True)  # ← Added this
    topic = Column(String, nullable=False)
    subtopics = Column(JSON, default=list)
    tasks = Column(JSON, default=list)  # ← Added this
    
    estimated_hours = Column(Integer, default=4)
    actual_hours = Column(Integer, nullable=True)  # ← Added this
    
    status = Column(String, default='pending')
    completed_at = Column(DateTime, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)


class Quiz(Base):
    __tablename__ = 'quizzes'
    
    quiz_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey('users.user_id'), nullable=False)
    
    day_number = Column(Integer, nullable=True)  # ← Added this
    topic = Column(String, nullable=False)
    quiz_type = Column(String, nullable=False)
    
    questions = Column(JSON, nullable=False)
    
    score = Column(Integer, nullable=True)
    max_score = Column(Integer, nullable=True)  # ← Added this
    time_taken_seconds = Column(Integer, nullable=True)  # ← Added this
    
    status = Column(String, default='pending')
    created_at = Column(DateTime, default=datetime.utcnow)
    attempted_at = Column(DateTime, nullable=True)  # ← Added this


class ChatSession(Base):
    __tablename__ = 'chat_sessions'
    
    session_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey('users.user_id'), nullable=False)
    
    started_at = Column(DateTime, default=datetime.utcnow)
    ended_at = Column(DateTime, nullable=True)
    message_count = Column(Integer, default=0)
    context = Column(JSON, nullable=True, default=dict)  # ← CHANGED # ← CHANGED from Text to JSON# ← Added this


class ChatMessage(Base):
    __tablename__ = 'chat_messages'
    
    message_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String, ForeignKey('chat_sessions.session_id'), nullable=False)
    
    role = Column(String, nullable=False)
    content = Column(String, nullable=False)
    
    timestamp = Column(DateTime, default=datetime.utcnow)  # ← Changed from created_at
    message_type = Column(String, nullable=True)  # ← Added this


class UploadedResource(Base):
    __tablename__ = 'uploaded_resources'
    
    resource_id = Column(String, primary_key=True, default=lambda: str(uuid. uuid4()))
    user_id = Column(String, ForeignKey('users.user_id'), nullable=False)
    
    filename = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    file_type = Column(String, nullable=False)
    
    topic = Column(String, nullable=True)
    
    extracted_text = Column(Text, nullable=True)
    processed = Column(Boolean, default=False)
    embeddings_generated = Column(Boolean, default=False)
    
    uploaded_at = Column(DateTime, default=datetime.utcnow)


class ProgressAnalytics(Base):
    __tablename__ = 'progress_analytics'
    
    analytics_id = Column(String, primary_key=True, default=lambda: str(uuid. uuid4()))
    user_id = Column(String, ForeignKey('users.user_id'), nullable=False)
    
    date = Column(Date, nullable=False)
    topics_covered = Column(JSON, default=list)
    quizzes_attempted = Column(Integer, default=0)
    avg_quiz_score = Column(Integer, nullable=True)
    hours_studied = Column(Integer, default=0)
    tasks_completed = Column(Integer, default=0)
    streak_maintained = Column(Boolean, default=False)


class Notification(Base):
    __tablename__ = 'notifications'
    
    notification_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey('users.user_id'), nullable=False)
    
    title = Column(String, nullable=False)
    message = Column(String, nullable=False)
    type = Column(String, nullable=False)
    
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    scheduled_for = Column(DateTime, nullable=True)


class QuizResponse(Base):
    __tablename__ = 'quiz_responses'
    
    response_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    quiz_id = Column(String, ForeignKey('quizzes.quiz_id'), nullable=False)
    
    question_number = Column(Integer, nullable=False)
    question_text = Column(String, nullable=False)
    student_answer = Column(String, nullable=True)
    correct_answer = Column(String, nullable=True)
    is_correct = Column(Boolean, nullable=True)
    points_earned = Column(Integer, default=0)
    ai_feedback = Column(Text, nullable=True)
    
    submitted_at = Column(DateTime, default=datetime.utcnow)