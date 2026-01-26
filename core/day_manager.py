from database.models import StudentProfile, StudyPlan, ProgressAnalytics
from database.db_manager import SessionLocal
from datetime import date, datetime, timedelta
from core.plan_generator import PlanGenerator


class DayManager:
    
    @staticmethod
    def check_and_update_day(user_id:  str):
        """
        Check if a new day has started and update accordingly
        Returns:  (day_changed:  bool, new_day_number:  int, message: str)
        """
        db = SessionLocal()
        try:
            profile = db.query(StudentProfile).filter(StudentProfile.user_id == user_id).first()
            
            if not profile:
                return False, 0, "Profile not found"
            
            today = date.today()
            last_active = profile.last_active_date
            
            # Check if it's a new day
            if last_active and last_active < today:
                days_passed = (today - last_active).days
                
                # Update day number
                old_day = profile.current_day_number
                profile.current_day_number += days_passed
                profile.last_active_date = today
                
                # Update streak
                if days_passed == 1:
                    # Consecutive day - maintain streak
                    profile.streak_count += 1
                else: 
                    # Missed days - reset streak
                    profile. streak_count = 1
                
                # Check yesterday's performance
                yesterday_plan = db.query(StudyPlan).filter(
                    StudyPlan.user_id == user_id,
                    StudyPlan.day_number == old_day
                ).first()
                
                if yesterday_plan:
                    # Calculate completion
                    total_tasks = len(yesterday_plan.tasks) if yesterday_plan.tasks else 0
                    completed_tasks = sum(1 for task in yesterday_plan.tasks if task.get('completed', False)) if yesterday_plan.tasks else 0
                    
                    # If completed all tasks early, reduce days remaining
                    if completed_tasks == total_tasks and total_tasks > 0:
                        if yesterday_plan.status != 'completed':
                            yesterday_plan.status = 'completed'
                            yesterday_plan. completed_at = datetime.now()
                    
                    # Record analytics
                    DayManager._record_daily_analytics(user_id, last_active, yesterday_plan, db)
                
                # Adjust timeline if working faster
                if profile.days_remaining: 
                    profile.days_remaining = max(0, profile.days_remaining - days_passed)
                
                db.commit()
                
                message = f"Welcome to Day {profile.current_day_number}! 🌅"
                if days_passed > 1:
                    message += f" (You were away for {days_passed} days.  Streak reset to 1.)"
                
                return True, profile.current_day_number, message
            
            elif not last_active:
                # First time - set today as last active
                profile.last_active_date = today
                db.commit()
                return False, profile.current_day_number, "Welcome!"
            
            else:
                # Same day - no change
                return False, profile. current_day_number, ""
        
        except Exception as e: 
            db.rollback()
            print(f"Error in day management: {e}")
            return False, 0, "Error updating day"
        finally:
            db.close()
    
    @staticmethod
    def _record_daily_analytics(user_id: str, date_to_record: date, study_plan: StudyPlan, db):
        """Record daily analytics"""
        try:
            # Calculate metrics
            total_tasks = len(study_plan.tasks) if study_plan.tasks else 0
            completed_tasks = sum(1 for task in study_plan.tasks if task.get('completed', False)) if study_plan.tasks else 0
            
            # Get quiz performance for the day
            from database.models import Quiz
            day_quizzes = db.query(Quiz).filter(
                Quiz.user_id == user_id,
                Quiz.day_number == study_plan.day_number,
                Quiz.status == 'completed'
            ).all()
            
            avg_score = 0
            quizzes_attempted = len(day_quizzes)
            if day_quizzes:
                total_percentage = sum((q.score / q.max_score * 100) if q.max_score > 0 else 0 for q in day_quizzes)
                avg_score = total_percentage / len(day_quizzes)
            
            # Create analytics record
            analytics = ProgressAnalytics(
                user_id=user_id,
                date=date_to_record,
                topics_covered=1 if completed_tasks == total_tasks else 0,
                quizzes_attempted=quizzes_attempted,
                avg_quiz_score=avg_score,
                hours_studied=study_plan.actual_hours if study_plan.actual_hours else 0,
                tasks_completed=completed_tasks,
                streak_maintained=True  # Will be updated by streak logic
            )
            
            db.add(analytics)
            
        except Exception as e:
            print(f"Error recording analytics: {e}")
    
    @staticmethod
    def get_today_summary(user_id: str):
        """Get summary of today's progress"""
        db = SessionLocal()
        try:
            profile = db.query(StudentProfile).filter(StudentProfile.user_id == user_id).first()
            if not profile:
                return None
            
            today_plan = PlanGenerator.get_today_plan(user_id)
            
            if not today_plan:
                return {
                    "day_number": profile.current_day_number,
                    "topic":  "No plan",
                    "tasks_completed": 0,
                    "total_tasks": 0,
                    "streak":  profile.streak_count
                }
            
            total_tasks = len(today_plan.tasks) if today_plan.tasks else 0
            completed_tasks = sum(1 for task in today_plan.tasks if task.get('completed', False)) if today_plan.tasks else 0
            
            return {
                "day_number": profile.current_day_number,
                "topic": today_plan.topic,
                "tasks_completed": completed_tasks,
                "total_tasks": total_tasks,
                "progress_percentage": (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0,
                "streak": profile.streak_count,
                "days_remaining": profile.days_remaining
            }
        finally:
            db.close()
    
    @staticmethod
    def mark_day_complete(user_id: str):
        """Mark current day as complete and move to next"""
        db = SessionLocal()
        try:
            profile = db.query(StudentProfile).filter(StudentProfile.user_id == user_id).first()
            if not profile:
                return False, "Profile not found"
            
            # Get today's plan
            today_plan = db.query(StudyPlan).filter(
                StudyPlan.user_id == user_id,
                StudyPlan.day_number == profile.current_day_number
            ).first()
            
            if not today_plan: 
                return False, "No plan found for today"
            
            # Check if all tasks completed
            total_tasks = len(today_plan.tasks) if today_plan.tasks else 0
            completed_tasks = sum(1 for task in today_plan.tasks if task.get('completed', False)) if today_plan.tasks else 0
            
            if completed_tasks < total_tasks:
                return False, f"Please complete all tasks ({completed_tasks}/{total_tasks} done)"
            
            # Mark as complete
            today_plan.status = 'completed'
            today_plan.completed_at = datetime.now()
            
            # Move to next day
            profile.current_day_number += 1
            profile.last_active_date = date.today()
            profile.streak_count += 1
            
            if profile.days_remaining:
                profile.days_remaining = max(0, profile.days_remaining - 1)
            
            db.commit()
            
            return True, f"Day {profile.current_day_number - 1} completed! Moving to Day {profile.current_day_number}"
        
        except Exception as e:
            db.rollback()
            print(f"Error marking day complete: {e}")
            return False, "Error completing day"
        finally:
            db.close()
    
    @staticmethod
    def get_week_summary(user_id: str):
        """Get summary of past week"""
        db = SessionLocal()
        try:
            today = date.today()
            week_ago = today - timedelta(days=7)
            
            analytics = db.query(ProgressAnalytics).filter(
                ProgressAnalytics.user_id == user_id,
                ProgressAnalytics.date >= week_ago,
                ProgressAnalytics. date <= today
            ).all()
            
            if not analytics:
                return None
            
            total_topics = sum(a.topics_covered for a in analytics)
            total_quizzes = sum(a.quizzes_attempted for a in analytics)
            avg_score = sum(a.avg_quiz_score for a in analytics) / len(analytics) if analytics else 0
            total_hours = sum(a.hours_studied for a in analytics)
            total_tasks = sum(a.tasks_completed for a in analytics)
            
            return {
                "topics_covered": total_topics,
                "quizzes_attempted":  total_quizzes,
                "avg_quiz_score": avg_score,
                "total_hours": total_hours,
                "total_tasks": total_tasks,
                "days_active": len(analytics)
            }
        finally:
            db. close()