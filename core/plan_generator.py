from database. models import StudentProfile, StudyPlan
from database.db_manager import SessionLocal
from datetime import date, datetime, timedelta
import json


class PlanGenerator:
    
    # Default curriculum structure
    TOPIC_CURRICULUM = {
        "Data Structures": [
            {"topic": "Arrays & Strings", "difficulty": "easy", "days": 2},
            {"topic": "Linked Lists", "difficulty": "medium", "days": 2},
            {"topic": "Stacks & Queues", "difficulty": "medium", "days": 2},
            {"topic": "Trees", "difficulty": "hard", "days": 3},
            {"topic": "Graphs", "difficulty": "hard", "days": 3},
            {"topic": "Hashing", "difficulty": "medium", "days": 2}
        ],
        "Algorithms": [
            {"topic": "Sorting Algorithms", "difficulty": "medium", "days": 2},
            {"topic": "Searching Algorithms", "difficulty": "easy", "days": 2},
            {"topic": "Recursion & Backtracking", "difficulty": "hard", "days": 3},
            {"topic": "Dynamic Programming", "difficulty": "hard", "days": 4},
            {"topic": "Greedy Algorithms", "difficulty":  "medium", "days": 2}
        ],
        "DBMS": [
            {"topic": "ER Model", "difficulty": "easy", "days": 2},
            {"topic": "Normalization", "difficulty": "medium", "days": 2},
            {"topic": "SQL Queries", "difficulty": "medium", "days": 3},
            {"topic": "Transactions & Concurrency", "difficulty": "hard", "days": 3}
        ],
        "Operating Systems": [
            {"topic": "Process Management", "difficulty": "medium", "days": 2},
            {"topic": "CPU Scheduling", "difficulty": "medium", "days": 2},
            {"topic": "Memory Management", "difficulty": "hard", "days": 3},
            {"topic": "Deadlock", "difficulty": "hard", "days": 2}
        ],
        "Computer Networks": [
            {"topic":  "Network Layers", "difficulty": "medium", "days": 2},
            {"topic": "TCP/IP Protocol", "difficulty": "medium", "days": 2},
            {"topic": "Routing Algorithms", "difficulty": "hard", "days": 2},
            {"topic": "Network Security", "difficulty": "hard", "days": 2}
        ],
        "Python": [
            {"topic": "Python Basics", "difficulty": "easy", "days": 2},
            {"topic": "OOP in Python", "difficulty": "medium", "days": 2},
            {"topic": "File Handling", "difficulty": "easy", "days": 1},
            {"topic": "Libraries & Frameworks", "difficulty": "medium", "days": 3}
        ],
        "Java": [
            {"topic": "Java Fundamentals", "difficulty": "easy", "days": 2},
            {"topic": "OOP Concepts", "difficulty": "medium", "days": 2},
            {"topic": "Collections Framework", "difficulty": "medium", "days": 2},
            {"topic": "Multithreading", "difficulty": "hard", "days": 3}
        ],
        "Web Development": [
            {"topic": "HTML & CSS", "difficulty": "easy", "days": 2},
            {"topic": "JavaScript Basics", "difficulty": "medium", "days": 2},
            {"topic": "Frontend Frameworks", "difficulty": "hard", "days": 3},
            {"topic": "Backend Development", "difficulty": "hard", "days": 3}
        ],
        # ✅ ADD THESE TWO: 
        "Machine Learning": [
            {"topic": "Python for ML", "difficulty": "easy", "days": 2},
            {"topic": "Linear Regression", "difficulty": "medium", "days": 2},
            {"topic": "Classification Algorithms", "difficulty": "medium", "days": 3},
            {"topic": "Neural Networks Basics", "difficulty": "hard", "days": 3},
            {"topic": "Deep Learning Intro", "difficulty": "hard", "days": 3},
            {"topic": "Model Evaluation", "difficulty": "medium", "days": 2}
        ],
        "System Design":  [
            {"topic": "System Design Basics", "difficulty": "medium", "days": 2},
            {"topic": "Scalability Principles", "difficulty": "hard", "days": 2},
            {"topic": "Database Design", "difficulty": "hard", "days": 3},
            {"topic": "Caching Strategies", "difficulty": "hard", "days": 2},
            {"topic": "Load Balancing", "difficulty": "hard", "days": 2},
            {"topic": "Microservices Architecture", "difficulty": "hard", "days": 3}
        ]
    }
    
    @staticmethod
    def generate_full_plan(user_id: str):
        """Generate complete study plan for user"""
        db = SessionLocal()
        try:
            profile = db.query(StudentProfile).filter(StudentProfile.user_id == user_id).first()
            
            if not profile or not profile.topics_to_learn:
                print("❌ No profile or topics found")
                return False
            
            # ✅ FIX: Use today's date if study_start_date is not set
            if not profile.study_start_date:
                profile.study_start_date = date.today()
                print(f"✅ Set study_start_date to {profile.study_start_date}")
            
            # ✅ Ensure current_day_number is 1
            if profile.current_day_number != 1:
                profile.current_day_number = 1
                print(f"✅ Reset current_day_number to 1")
            
            db.commit()
            
            # Get all subtopics for selected topics
            all_subtopics = []
            for topic in profile. topics_to_learn:
                if topic in PlanGenerator. TOPIC_CURRICULUM:
                    for subtopic in PlanGenerator.TOPIC_CURRICULUM[topic]: 
                        all_subtopics. append({
                            "subject":  topic,
                            "topic":  subtopic["topic"],
                            "difficulty": subtopic["difficulty"],
                            "estimated_days":  subtopic["days"]
                        })
                else:
                    print(f"⚠️ Topic '{topic}' not found in curriculum")
            
            if not all_subtopics:
                print("❌ No subtopics found in curriculum")
                return False
            
            print(f"📚 Found {len(all_subtopics)} subtopics to cover")
            
            # Calculate days per topic based on total days available
            total_days = profile.total_planned_days if profile.total_planned_days else 30
            estimated_days = sum([s["estimated_days"] for s in all_subtopics])
            
            print(f"📅 Total days available: {total_days}, Estimated days needed: {estimated_days}")
            
            # Adjust if needed
            if total_days < estimated_days:
                # Compress plan
                for subtopic in all_subtopics:
                    subtopic["estimated_days"] = max(1, int(subtopic["estimated_days"] * total_days / estimated_days))
                print(f"⚠️ Compressed plan to fit {total_days} days")
            
            # ✅ Delete any existing plans first (in case of regeneration)
            existing_count = db.query(StudyPlan).filter(StudyPlan.user_id == user_id).count()
            if existing_count > 0:
                db.query(StudyPlan).filter(StudyPlan.user_id == user_id).delete()
                db.commit()
                print(f"🗑️ Deleted {existing_count} existing plans")
            
            # Generate day-by-day plans
            current_day = 1
            current_date = profile.study_start_date
            
            print(f"📅 Generating plan starting from Day {current_day}, Date: {current_date}")
            
            for subtopic in all_subtopics:
                days_for_topic = subtopic["estimated_days"]
                
                for day in range(days_for_topic):
                    tasks = PlanGenerator._generate_tasks_for_topic(
                        subtopic["topic"],
                        subtopic["difficulty"],
                        day + 1,
                        days_for_topic
                    )
                    
                    plan = StudyPlan(
                        user_id=user_id,
                        day_number=current_day,
                        plan_date=current_date,
                        topic=subtopic["topic"],
                        subtopics=[subtopic["topic"]],
                        tasks=tasks,
                        estimated_hours=profile.hours_per_day,
                        status='pending'
                    )
                    
                    db.add(plan)
                    print(f"✅ Added Day {current_day}:  {subtopic['topic']}")
                    
                    current_day += 1
                    current_date += timedelta(days=1)
                    
                    if current_day > total_days: 
                        break
                
                if current_day > total_days:
                    break
            
            # ✅ Commit all plans
            db.commit()
            
            # ✅ Verify plans were saved
            saved_plans = db.query(StudyPlan).filter(StudyPlan.user_id == user_id).count()
            print(f"✅ Successfully saved {saved_plans} plans to database")
            
            return True
            
        except Exception as e:
            db.rollback()
            print(f"❌ Error generating plan: {e}")
            import traceback
            traceback.print_exc()
            return False
        finally: 
            db.close()
    
    @staticmethod
    def _generate_tasks_for_topic(topic: str, difficulty: str, current_day: int, total_days: int) -> list:
        """Generate tasks for a specific topic and day"""
        tasks = []
        
        if current_day == 1:
            # First day:  Introduction
            tasks.append({
                "type": "video",
                "title": f"Introduction to {topic}",
                "duration_min": 30,
                "completed": False
            })
            tasks.append({
                "type":  "reading",
                "title":  f"{topic} - Basics",
                "duration_min": 45,
                "completed": False
            })
            tasks.append({
                "type": "practice",
                "title": f"{topic} - Easy Problems",
                "count": 3,
                "completed": False
            })
        elif current_day == total_days:
            # Last day: Practice and quiz
            tasks.append({
                "type": "revision",
                "title": f"Review {topic} concepts",
                "duration_min":  30,
                "completed":  False
            })
            tasks.append({
                "type": "practice",
                "title": f"{topic} - Mixed Problems",
                "count": 5,
                "completed": False
            })
            tasks.append({
                "type": "quiz",
                "title": f"{topic} Assessment",
                "duration_min":  20,
                "completed": False
            })
        else:
            # Middle days: Deep dive
            tasks.append({
                "type": "reading",
                "title": f"{topic} - Advanced Concepts",
                "duration_min": 40,
                "completed": False
            })
            tasks.append({
                "type": "practice",
                "title": f"{topic} - {difficulty. title()} Problems",
                "count":  4,
                "completed":  False
            })
        
        return tasks
    
    @staticmethod
    def get_today_plan(user_id:  str):
        """Get today's study plan"""
        db = SessionLocal()
        try:
            profile = db.query(StudentProfile).filter(StudentProfile.user_id == user_id).first()
            if not profile:
                print(f"❌ No profile found for user {user_id}")
                return None
            
            print(f"🔍 Looking for Day {profile.current_day_number} plan for user {user_id}")
            
            plan = db.query(StudyPlan).filter(
                StudyPlan.user_id == user_id,
                StudyPlan.day_number == profile. current_day_number
            ).first()
            
            if plan:
                print(f"✅ Found plan: Day {plan.day_number} - {plan.topic}")
            else:
                print(f"❌ No plan found for Day {profile.current_day_number}")
            
            return plan
        finally:
            db.close()
    
    @staticmethod
    def mark_task_complete(plan_id: str, task_index: int):
        """Mark a specific task as complete"""
        db = SessionLocal()
        try:
            plan = db.query(StudyPlan).filter(StudyPlan.plan_id == plan_id).first()
            
            if not plan:
                return False, "Plan not found"
            
            if not plan.tasks or task_index >= len(plan. tasks):
                return False, "Invalid task index"
            
            # Mark task as complete
            plan. tasks[task_index]['completed'] = True
            
            # Check if all tasks are complete
            all_complete = all(task. get('completed', False) for task in plan.tasks)
            
            if all_complete:
                plan.status = 'completed'
                plan.completed_at = datetime.utcnow()
            elif plan.status == 'pending':
                plan.status = 'in_progress'
            
            # Force SQLAlchemy to detect the change in JSON field
            from sqlalchemy.orm. attributes import flag_modified
            flag_modified(plan, 'tasks')
            
            db.commit()
            return True, "Task marked complete"
            
        except Exception as e:
            db.rollback()
            print(f"Error marking task complete: {e}")
            return False, str(e)
        finally:
            db. close()