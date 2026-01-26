from database.models import ChatSession, ChatMessage, StudentProfile, StudyPlan
from database.db_manager import SessionLocal
from llm. llm_client import LLMClient
from llm.prompts import Prompts
from llm.rag_engine import rag_engine
from datetime import datetime
import json


class ChatEngine: 
    
    @staticmethod
    def get_or_create_session(user_id: str):
        """Get active chat session or create new one"""
        db = SessionLocal()
        try:
            # Find active session (not ended)
            session = db.query(ChatSession).filter(
                ChatSession.user_id == user_id,
                ChatSession. ended_at. is_(None)
            ).first()
            
            if not session:
                # Create new session
                profile = db.query(StudentProfile).filter(StudentProfile.user_id == user_id).first()
                today_plan = db.query(StudyPlan).filter(
                    StudyPlan.user_id == user_id,
                    StudyPlan.day_number == profile. current_day_number
                ).first() if profile else None
                
                context = {
                    "current_day":  profile.current_day_number if profile else 1,
                    "current_topic": today_plan.topic if today_plan else "General",
                    "last_interaction": datetime.now().isoformat()
                }
                
                session = ChatSession(
                    user_id=user_id,
                    context=context
                )
                db.add(session)
                db.commit()
                db.refresh(session)
            
            return session
        finally:
            db.close()
    
    @staticmethod
    def get_chat_history(session_id: str, limit:  int = 10):
        """Get recent chat messages"""
        db = SessionLocal()
        try:
            messages = db.query(ChatMessage).filter(
                ChatMessage.session_id == session_id
            ).order_by(ChatMessage.timestamp.desc()).limit(limit).all()
            
            return list(reversed(messages))
        finally:
            db. close()
    
    @staticmethod
    def add_message(session_id: str, role:  str, content: str, message_type: str = 'text'):
        """Add a message to chat history"""
        db = SessionLocal()
        try:
            message = ChatMessage(
                session_id=session_id,
                role=role,
                content=content,
                message_type=message_type
            )
            db.add(message)
            
            # Update session message count and context
            session = db. query(ChatSession).filter(ChatSession.session_id == session_id).first()
            if session:
                session.message_count += 1
                
                # Handle context properly
                if session.context is None:
                    session.context = {}
                
                # If context is a string (old data), convert to dict
                if isinstance(session.context, str):
                    try:
                        session.context = json.loads(session.context)
                    except:
                        session.context = {}
                
                # Now safely update as dict
                session.context['last_interaction'] = datetime.now().isoformat()
            
            db.commit()
            db.refresh(message)
            return message
        finally:
            db.close()
    
    @staticmethod
    def get_user_context(user_id:  str):
        """Get comprehensive user context for AI"""
        db = SessionLocal()
        try:
            profile = db.query(StudentProfile).filter(StudentProfile.user_id == user_id).first()
            if not profile:
                return {}
            
            # Get today's plan
            today_plan = db. query(StudyPlan).filter(
                StudyPlan.user_id == user_id,
                StudyPlan.day_number == profile.current_day_number
            ).first()
            
            # Count completed tasks for today
            completed_tasks = 0
            total_tasks = 0
            if today_plan and today_plan.tasks:
                total_tasks = len(today_plan.tasks)
                completed_tasks = sum(1 for task in today_plan.tasks if task. get('completed', False))
            
            # ✅ NEW: Get quiz performance
            from database.models import Quiz
            
            # Recent quizzes
            recent_quizzes = db.query(Quiz).filter(
                Quiz.user_id == user_id,
                Quiz.status == 'completed'
            ).order_by(Quiz.attempted_at.desc()).limit(5).all()
            
            quiz_history = []
            total_quiz_score = 0
            quiz_count = 0
            
            for quiz in recent_quizzes: 
                if quiz.score is not None and quiz.max_score is not None and quiz.max_score > 0:
                    percentage = (quiz.score / quiz. max_score) * 100
                    quiz_history.append({
                        "topic": quiz.topic,
                        "score": quiz.score,
                        "max_score": quiz.max_score,
                        "percentage": percentage,
                        "date": quiz.attempted_at.strftime("%Y-%m-%d") if quiz.attempted_at else "N/A"
                    })
                    total_quiz_score += percentage
                    quiz_count += 1
            
            avg_quiz_score = total_quiz_score / quiz_count if quiz_count > 0 else 0
            
            # ✅ NEW: Get overall progress
            total_plans = db.query(StudyPlan).filter(StudyPlan.user_id == user_id).count()
            completed_plans = db.query(StudyPlan).filter(
                StudyPlan.user_id == user_id,
                StudyPlan.status == 'completed'
            ).count()
            
            # ✅ NEW: Find weak areas (topics with low quiz scores)
            weak_topics = []
            for quiz in recent_quizzes: 
                if quiz.score is not None and quiz.max_score is not None and quiz.max_score > 0:
                    percentage = (quiz.score / quiz. max_score) * 100
                    if percentage < 60:
                        weak_topics. append(quiz.topic)
            
            return {
                # Basic info
                "current_day": profile.current_day_number,
                "topics_learning":  profile.topics_to_learn,
                "current_topic": today_plan.topic if today_plan else "None",
                "streak": profile.streak_count,
                "hours_per_day":  profile.hours_per_day,
                
                # Today's progress
                "tasks_completed": completed_tasks,
                "total_tasks": total_tasks,
                "today_progress_percentage": (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0,
                
                # ✅ Quiz performance
                "total_quizzes_taken": quiz_count,
                "average_quiz_score": round(avg_quiz_score, 1),
                "recent_quizzes": quiz_history,
                "weak_topics": list(set(weak_topics)),  # Unique topics
                
                # ✅ Overall progress
                "total_days_planned": total_plans,
                "days_completed": completed_plans,
                "overall_progress_percentage": (completed_plans / total_plans * 100) if total_plans > 0 else 0
            }
        finally:
            db.close()
    
    @staticmethod
    def generate_ai_response(user_id: str, user_message: str, session_id: str):
        """Generate AI response with full context awareness"""
        
        # Get comprehensive user context
        context = ChatEngine.get_user_context(user_id)
        
        # Get recent chat history
        history = ChatEngine.get_chat_history(session_id, limit=5)
        history_text = "\n".join([f"{msg. role}: {msg.content}" for msg in history[-5:]])
        
        # ========== BUILD ENHANCED BASE CONTEXT (ONLY ONCE!) ==========
        base_context = f"""You are a helpful AI study companion. 

    Student Context:
    - Current Day: {context.get('current_day', 1)} of {context.get('total_days_planned', 'N/A')}
    - Current Topic: {context.get('current_topic', 'General')}
    - Overall Progress: {context.get('overall_progress_percentage', 0):.0f}% ({context.get('days_completed', 0)} days completed)
    - Today's Tasks: {context.get('tasks_completed', 0)}/{context.get('total_tasks', 0)} completed ({context.get('today_progress_percentage', 0):.0f}%)
    - Study Streak: {context.get('streak', 0)} days 🔥

    Quiz Performance: 
    - Total Quizzes Taken: {context.get('total_quizzes_taken', 0)}
    - Average Score: {context.get('average_quiz_score', 0):.1f}%"""

        # Add recent quiz details
        if context.get('recent_quizzes'):
            base_context += "\n- Recent Quiz Scores:\n"
            for quiz in context['recent_quizzes'][:3]: 
                base_context += f"  • {quiz['topic']}: {quiz['percentage']:.0f}% ({quiz['score']}/{quiz['max_score']}) on {quiz['date']}\n"
        
        # Add weak areas
        if context.get('weak_topics'):
            base_context += f"\n- Topics Needing Improvement:  {', '.join(context['weak_topics'])}\n"
        
        base_context += "\n"
        
        # ========== SMART RAG DETECTION ==========
        
        ignore_doc_keywords = [
            'forget the document', 'ignore document', 'ignore the document',
            'forget that document', 'without document', 'without the document',
            'don\'t use document', 'not from document', 'don\'t use the document',
            'ignore that', 'forget about', 'not about the document',
            'just tell me', 'general question', 'without using',
            'don\'t reference', 'aside from document'
        ]
        
        use_doc_keywords = [
            'in my document', 'from my pdf', 'in the document', 
            'what does my', 'according to my', 'in my notes',
            'my textbook says', 'uploaded material', 'my file',
            'in my upload', 'from my report', 'my medical report',
            'what\'s in my', 'from the document', 'the document says'
        ]
        
        user_message_lower = user_message.lower()
        
        explicitly_ignore_docs = any(keyword in user_message_lower for keyword in ignore_doc_keywords)
        explicitly_use_docs = any(keyword in user_message_lower for keyword in use_doc_keywords)
        
        use_rag = False
        pdf_context = None
        
        if explicitly_ignore_docs: 
            print("🚫 User explicitly asked to ignore documents")
            use_rag = False
            pdf_context = None
            
        elif explicitly_use_docs:
            print("📄 User explicitly asked for document info")
            use_rag = True
            try:
                pdf_context = rag_engine.get_context_for_query(user_id, user_message)
                if pdf_context:
                    print(f"✅ Found PDF context!  Length: {len(pdf_context)}")
                else:
                    print("❌ No PDF context found")
            except Exception as e:
                print(f"❌ Error searching PDFs: {e}")
                pdf_context = None
                
        else: 
            # Auto-detect
            general_question_indicators = [
                'what is', 'what are', 'explain', 'how does', 'how do',
                'why', 'tell me about', 'what should i', 'how to',
                'help me understand', 'can you explain', 'describe',
                'what\'s the difference', 'compare', 'i don\'t understand',
                'how am i doing', 'my progress', 'my quiz', 'my score'
            ]
            
            seems_general = any(user_message_lower.startswith(indicator) for indicator in general_question_indicators)
            is_short = len(user_message. split()) < 15
            
            if seems_general and is_short:
                print("💡 Detected short general question - not using documents")
                use_rag = False
                pdf_context = None
            else:
                print("🔍 Trying document search for potentially specific query")
                try:
                    pdf_context = rag_engine.get_context_for_query(user_id, user_message)
                    if pdf_context and len(pdf_context) > 100:
                        print(f"✅ Found relevant PDF context")
                        use_rag = True
                    else:
                        print("❌ No relevant PDF context")
                        use_rag = False
                        pdf_context = None
                except Exception as e: 
                    print(f"❌ Error in document search: {e}")
                    use_rag = False
                    pdf_context = None
        
        # ========== BUILD PROMPT ==========
        
        intent = ChatEngine._detect_intent(user_message_lower)
        
        if use_rag and pdf_context:
            # Document-based response
            prompt = f"""{base_context}

    📚 Content from Student's Uploaded Document: 
    {pdf_context}

    Student's Question: {user_message}

    INSTRUCTIONS:
    1. Use the document content above to answer the question
    2. Start with "Based on your uploaded document..." or "According to your document..."
    3. Quote specific information from the document
    4. If the document doesn't contain relevant info, say so and offer general help

    Answer: """
        
        elif intent == "greeting":
            prompt = f"""{base_context}

    Student said: "{user_message}"

    Respond warmly and briefly (2-3 sentences). Mention their current topic and progress.
    """
        
        elif intent == "doubt":
            prompt = f"""{base_context}

    Student's question: {user_message}

    Help the student understand this concept: 
    - Explain clearly for a beginner
    - Use examples if helpful
    - Be encouraging
    - Reference their progress if relevant

    Your explanation:"""
        
        elif intent == "motivation": 
            prompt = f"""{base_context}

    Student said: {user_message}

    Give them encouragement based on their progress!  Be enthusiastic and supportive. 
    Mention their achievements (streak, completed tasks, quiz scores).
    """
        
        elif intent == "explanation":
            prompt = f"""{base_context}

    Student wants explanation: {user_message}

    Explain this concept: 
    - Clear explanation for beginners
    - Use examples and analogies
    - Make it engaging
    - Connect to their current topic if relevant

    Your explanation:"""
        
        else:
            # General conversation
            prompt = f"""{base_context}

    Recent conversation: 
    {history_text}

    Student: {user_message}

    Respond helpfully.  If they're asking about their progress, quiz scores, or study status, 
    use the context information above to give specific answers. 

    Your response:"""
        
        # Call LLM
        try: 
            ai_response = LLMClient.call_llm(prompt, max_tokens=500, temperature=0.7)
            
            if not ai_response: 
                ai_response = "I'm having trouble generating a response right now. Could you try again?  🤔"
            
            return ai_response
            
        except Exception as e:
            print(f"❌ Error generating AI response: {e}")
            return "I'm having trouble connecting right now. Could you try again in a moment? 🤔"
    
    @staticmethod
    def _detect_intent(message:  str):
        """Detect user intent from message"""
        greetings = ['hi', 'hello', 'hey', 'good morning', 'good evening', 'sup', 'yo']
        doubt_keywords = ['don\'t understand', 'confused', 'what is', 'explain', 'how does', 'help me with', 'struggling']
        motivation_keywords = ['tired', 'can\'t do', 'difficult', 'hard', 'demotivated', 'frustrated', 'give up']
        explanation_keywords = ['what', 'why', 'how', 'explain', 'tell me about', 'describe']
        
        message_lower = message.lower()
        
        # Check for greetings first
        if any(message_lower.startswith(greeting) for greeting in greetings):
            return "greeting"
        elif any(keyword in message_lower for keyword in doubt_keywords):
            return "doubt"
        elif any(keyword in message_lower for keyword in motivation_keywords):
            return "motivation"
        elif any(keyword in message_lower for keyword in explanation_keywords):
            return "explanation"
        else:
            return "general"
    
    @staticmethod
    def send_daily_greeting(user_id: str, session_id: str):
        """Generate daily greeting message"""
        context = ChatEngine.get_user_context(user_id)
        
        prompt = f"""Generate a warm greeting for a student starting their study session. 

Student info:
- Day {context.get('current_day', 1)} of their learning journey
- Currently learning:  {context.get('current_topic', 'General')}
- Current streak: {context.get('streak', 0)} days

Create a brief, encouraging greeting (2-3 sentences) that:
- Welcomes them
- Mentions today's topic
- Is motivating but not overwhelming

Your greeting:"""
        
        greeting = LLMClient.call_llm(prompt, max_tokens=150, temperature=0.8)
        
        if greeting:
            ChatEngine.add_message(session_id, 'ai', greeting, 'text')
        
        return greeting