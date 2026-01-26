from database.models import StudentProfile
from database.db_manager import SessionLocal
from llm.llm_client import LLMClient
from datetime import date


class OnboardingManager:
    
    @staticmethod
    def start_onboarding(user_id: str):
        """Generate AI greeting for onboarding"""
        prompt = """Generate a warm, encouraging greeting for a student starting their learning journey.  
        Keep it brief (2-3 sentences), friendly, and motivating. 
        
        Example: "Welcome!  I'm excited to help you on your learning journey. Let's create a personalized study plan that works for you.  Ready to get started?"
        
        Your greeting: """
        
        greeting = LLMClient.call_llm(prompt, max_tokens=100, temperature=0.8)
        return greeting if greeting else "Welcome!  Let's create your personalized study plan.  🎓"
    
    @staticmethod
    def save_onboarding_data(user_id: str, topics:  list, levels: dict, target_date, hours:  int):
        """Save onboarding data to profile"""
        db = SessionLocal()
        try:
            profile = db.query(StudentProfile).filter(StudentProfile.user_id == user_id).first()
            
            if not profile:
                print(f"❌ No profile found for user {user_id}")
                return False
            
            # Calculate total days
            if target_date:
                days_remaining = (target_date - date. today()).days
                total_days = max(days_remaining, len(topics) * 7)  # Min 7 days per topic
            else:
                total_days = len(topics) * 10  # 10 days per topic for self-paced
            
            # Update profile
            profile.topics_to_learn = topics
            profile. current_levels = levels
            profile.target_date = target_date
            profile.hours_per_day = hours
            profile.total_planned_days = total_days
            profile.days_remaining = days_remaining if target_date else None
            profile.onboarding_completed = True
            profile.study_start_date = date.today()  # ✅ SET START DATE
            profile.current_day_number = 1  # ✅ SET TO DAY 1
            
            db.commit()
            
            print(f"✅ Onboarding data saved for user {user_id}")
            print(f"   Topics: {topics}")
            print(f"   Total days: {total_days}")
            print(f"   Start date: {profile.study_start_date}")
            
            return True
            
        except Exception as e:
            db. rollback()
            print(f"❌ Error saving onboarding:  {e}")
            import traceback
            traceback.print_exc()
            return False
        finally:
            db.close()
    
    @staticmethod
    def create_summary(name: str, topics: list, levels: dict, hours: int, target_date: str):
        """Generate AI summary of onboarding"""
        topics_str = ", ".join([f"{t} ({levels. get(t, 'beginner')})" for t in topics])
        
        prompt = f"""Generate an encouraging summary for a student who just completed onboarding. 

Student:  {name}
Topics: {topics_str}
Study hours per day: {hours}
Target date: {target_date}

Create a brief, motivating summary (3-4 sentences) that:
1. Acknowledges their commitment
2. Highlights what they'll learn
3. Encourages them to start

Your summary:"""
        
        summary = LLMClient.call_llm(prompt, max_tokens=150, temperature=0.7)
        return summary if summary else f"Great!  You'll be learning {', '.join(topics)} with {hours} hours of daily study. Let's get started!"