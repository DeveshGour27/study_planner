from database.models import Quiz, QuizResponse, StudentProfile, StudyPlan
from database.db_manager import SessionLocal
from llm.llm_client import LLMClient
from datetime import datetime
import json
import re


class QuizEngine:
    
    @staticmethod
    def generate_quiz(user_id:  str, topic: str, quiz_type: str = 'mcq', difficulty: str = 'medium', num_questions: int = 5):
        """Generate AI-powered quiz for a topic"""
        db = SessionLocal()
        try:
            # Get user's current level for adaptive difficulty
            profile = db.query(StudentProfile).filter(StudentProfile.user_id == user_id).first()
            current_level = profile.current_levels.get(topic, 'beginner') if profile and profile.current_levels else 'beginner'
            
            # Generate questions using LLM
            if quiz_type == 'mcq':
                questions = QuizEngine._generate_mcq_questions(topic, difficulty, num_questions)
            elif quiz_type == 'descriptive':
                questions = QuizEngine._generate_descriptive_questions(topic, difficulty, num_questions)
            elif quiz_type == 'coding':
                questions = QuizEngine._generate_coding_questions(topic, difficulty, num_questions)
            else:
                questions = []
            
            if not questions:
                return None, "Failed to generate quiz questions"
            
            # Create quiz in database
            quiz = Quiz(
                user_id=user_id,
                topic=topic,
                quiz_type=quiz_type,
                questions=questions,
                max_score=len(questions) * 10,  # 10 points per question
                status='pending'
            )
            
            db.add(quiz)
            db.commit()
            db.refresh(quiz)
            
            return quiz, None
            
        except Exception as e:
            db.rollback()
            print(f"❌ Quiz generation error: {e}")
            import traceback
            traceback.print_exc()
            return None, str(e)
        finally:
            db.close()
    
    @staticmethod
    def _generate_mcq_questions(topic: str, difficulty: str, num_questions: int):
        """Generate MCQ questions using AI"""
        prompt = f"""You are a quiz generator. Generate {num_questions} multiple choice questions about {topic} at {difficulty} level.

    IMPORTANT: Return ONLY a valid JSON array. No extra text before or after.

    Format:
    [
    {{
        "question": "Your question here?",
        "options": ["Option A", "Option B", "Option C", "Option D"],
        "correct_answer": "Option A",
        "explanation": "Brief explanation"
    }}
    ]

    Rules:
    - Questions must be clear and unambiguous
    - All 4 options should be plausible
    - Only one correct answer
    - Keep explanations under 50 words
    - Escape all special characters properly
    - Do NOT include markdown formatting

    Generate {num_questions} questions now:"""

        # ✅ INCREASED TOKEN LIMIT
        response = LLMClient.call_llm(prompt, max_tokens=3000, temperature=0.7)
        
        if not response:
            return []
        
        try:
            # Clean response
            response = response.strip()
            
            # Extract JSON array
            json_match = re.search(r'\[.*\]', response, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                questions = json.loads(json_str)
                
                # ✅ VALIDATE PARSED QUESTIONS
                validated_questions = []
                for q in questions:
                    if all(key in q for key in ['question', 'options', 'correct_answer', 'explanation']):
                        if len(q['options']) == 4:
                            validated_questions.append(q)
                
                print(f"✅ Successfully generated {len(validated_questions)} MCQ questions")
                return validated_questions
            else:
                print("❌ No JSON array found in response")
                print(f"Response preview: {response[:300]}")
                return []
                
        except json.JSONDecodeError as e:
            print(f"❌ JSON parsing error: {e}")
            print(f"Response was: {response[:500]}")
            
            # ✅ FALLBACK: Try to salvage partial response
            try:
                # Find the last complete question object
                last_complete = response.rfind('}')
                if last_complete != -1:
                    truncated = response[:last_complete + 1] + ']'
                    questions = json.loads(truncated)
                    print(f"⚠️ Recovered {len(questions)} questions from partial response")
                    return questions
            except:
                pass
            
            return []
        except Exception as e:
            print(f"❌ Error parsing MCQ questions: {e}")
            return []


    @staticmethod
    def _generate_descriptive_questions(topic: str, difficulty: str, num_questions: int):
        """Generate descriptive questions using AI"""
        prompt = f"""You are a quiz generator. Generate {num_questions} descriptive questions about {topic} at {difficulty} level.

    IMPORTANT: Return ONLY a valid JSON array. No extra text.

    Format:
    [
    {{
        "question": "Explain the concept of...",
        "key_points": ["Point 1", "Point 2", "Point 3"],
        "sample_answer": "A good answer would include..."
    }}
    ]

    Rules:
    - Test understanding, not memorization
    - Provide 3-5 key points
    - Keep sample answers under 100 words
    - Escape all special characters

    Generate {num_questions} questions now:"""

        # ✅ INCREASED TOKEN LIMIT
        response = LLMClient.call_llm(prompt, max_tokens=2500, temperature=0.7)
        
        if not response:
            return []
        
        try:
            response = response.strip()
            json_match = re.search(r'\[.*\]', response, re.DOTALL)
            
            if json_match:
                questions = json.loads(json_match.group())
                
                # ✅ VALIDATE
                validated = []
                for q in questions:
                    if all(key in q for key in ['question', 'key_points', 'sample_answer']):
                        validated.append(q)
                
                print(f"✅ Generated {len(validated)} descriptive questions")
                return validated
            else:
                print("❌ No JSON found in response")
                return []
                
        except Exception as e:
            print(f"❌ Error parsing descriptive questions: {e}")
            print(f"Response: {response[:300]}")
            return []


    @staticmethod
    def _generate_coding_questions(topic: str, difficulty: str, num_questions: int):
        """Generate coding questions using AI"""
        prompt = f"""You are a coding quiz generator. Generate {num_questions} coding problems about {topic} at {difficulty} level.

    IMPORTANT: Return ONLY a valid JSON array. No extra text.

    Format:
    [
    {{
        "question": "Write a function to...",
        "requirements": ["Requirement 1", "Requirement 2"],
        "sample_input": "Example input",
        "sample_output": "Expected output",
        "sample_solution": "def example():\\n    pass"
    }}
    ]

    Rules:
    - Problems should be practical
    - Use \\n for newlines in code
    - Keep solutions under 20 lines
    - Escape all special characters properly

    Generate {num_questions} problems now:"""

        # ✅ INCREASED TOKEN LIMIT
        response = LLMClient.call_llm(prompt, max_tokens=3500, temperature=0.7)
        
        if not response:
            return []
        
        try:
            response = response.strip()
            json_match = re.search(r'\[.*\]', response, re.DOTALL)
            
            if json_match:
                questions = json.loads(json_match.group())
                
                # ✅ VALIDATE
                validated = []
                for q in questions:
                    required_keys = ['question', 'requirements', 'sample_input', 'sample_output', 'sample_solution']
                    if all(key in q for key in required_keys):
                        validated.append(q)
                
                print(f"✅ Generated {len(validated)} coding questions")
                return validated
            else:
                print("❌ No JSON found")
                return []
                
        except Exception as e:
            print(f"❌ Error parsing coding questions: {e}")
            print(f"Response: {response[:300]}")
            return []
    
    @staticmethod
    def submit_quiz(quiz_id: str, answers: dict):
        """Submit quiz and calculate score"""
        db = SessionLocal()
        try:
            quiz = db.query(Quiz).filter(Quiz.quiz_id == quiz_id).first()
            
            if not quiz:
                return False, "Quiz not found"
            
            if quiz.status == 'completed':
                return False, "Quiz already completed"
            
            # Grade based on quiz type
            if quiz.quiz_type == 'mcq': 
                score, feedback = QuizEngine._grade_mcq(quiz. questions, answers)
            elif quiz.quiz_type == 'descriptive':
                score, feedback = QuizEngine._grade_descriptive(quiz.questions, answers, quiz.user_id)
            elif quiz. quiz_type == 'coding': 
                score, feedback = QuizEngine._grade_coding(quiz. questions, answers, quiz.user_id)
            else:
                score = 0
                feedback = {}
            
            # Update quiz
            quiz.score = score
            quiz.status = 'completed'
            quiz.attempted_at = datetime.utcnow()
            
            # Save individual responses
            for i, answer in answers.items():
                question_num = int(i)
                question = quiz.questions[question_num] if question_num < len(quiz.questions) else {}
                
                response = QuizResponse(
                    quiz_id=quiz_id,
                    question_number=question_num,
                    question_text=question.get('question', ''),
                    student_answer=answer,
                    correct_answer=question.get('correct_answer', '') if quiz.quiz_type == 'mcq' else '',
                    is_correct=feedback.get(str(i), {}).get('is_correct', False),
                    points_earned=feedback.get(str(i), {}).get('points', 0),
                    ai_feedback=feedback.get(str(i), {}).get('feedback', '')
                )
                db.add(response)
            
            db.commit()
            
            return True, {
                'score': score,
                'max_score': quiz.max_score,
                'percentage': round((score / quiz.max_score) * 100, 1) if quiz.max_score > 0 else 0,
                'feedback': feedback
            }
            
        except Exception as e:
            db.rollback()
            print(f"❌ Quiz submission error: {e}")
            import traceback
            traceback.print_exc()
            return False, str(e)
        finally:
            db.close()
    
    @staticmethod
    def _grade_mcq(questions:  list, answers: dict):
        """Grade MCQ quiz"""
        score = 0
        feedback = {}
        
        for i, question in enumerate(questions):
            student_answer = answers.get(str(i), '')
            correct_answer = question. get('correct_answer', '')
            
            is_correct = student_answer == correct_answer
            points = 10 if is_correct else 0
            score += points
            
            feedback[str(i)] = {
                'is_correct': is_correct,
                'points': points,
                'correct_answer': correct_answer,
                'explanation': question.get('explanation', ''),
                'feedback': '✅ Correct!' if is_correct else f'❌ Incorrect. The correct answer is: {correct_answer}'
            }
        
        return score, feedback
    
    @staticmethod
    def _grade_descriptive(questions: list, answers: dict, user_id: str):
        """Grade descriptive quiz using AI"""
        score = 0
        feedback = {}
        
        for i, question in enumerate(questions):
            student_answer = answers.get(str(i), '')
            
            if not student_answer or len(student_answer. strip()) < 10:
                feedback[str(i)] = {
                    'is_correct': False,
                    'points': 0,
                    'feedback': '❌ Answer too short or empty'
                }
                continue
            
            # Use AI to grade descriptive answer
            prompt = f"""Grade this student's answer: 

Question:  {question. get('question', '')}

Key points to cover:  {', '.join(question.get('key_points', []))}

Student's answer: 
{student_answer}

Sample answer:
{question.get('sample_answer', '')}

Provide feedback in this format:
Score: [0-10]
Feedback: [Brief feedback on what was good and what could be improved]

Be fair but constructive. Award partial credit for partially correct answers."""

            ai_response = LLMClient. call_llm(prompt, max_tokens=300, temperature=0.3)
            
            # Parse AI response
            try: 
                score_match = re.search(r'Score:\s*(\d+)', ai_response)
                points = int(score_match.group(1)) if score_match else 5
                points = min(max(points, 0), 10)  # Clamp between 0-10
                
                feedback_match = re.search(r'Feedback:\s*(.*)', ai_response, re.DOTALL)
                ai_feedback = feedback_match.group(1).strip() if feedback_match else 'Good effort!'
                
            except: 
                points = 5
                ai_feedback = 'Answer received and reviewed.'
            
            score += points
            
            feedback[str(i)] = {
                'is_correct':  points >= 7,
                'points': points,
                'feedback': ai_feedback
            }
        
        return score, feedback
    
    @staticmethod
    def _grade_coding(questions: list, answers:  dict, user_id: str):
        """Grade coding quiz using AI"""
        score = 0
        feedback = {}
        
        for i, question in enumerate(questions):
            student_code = answers.get(str(i), '')
            
            if not student_code or len(student_code.strip()) < 10:
                feedback[str(i)] = {
                    'is_correct': False,
                    'points': 0,
                    'feedback': '❌ No code submitted or too short'
                }
                continue
            
            # Use AI to grade code
            prompt = f"""Review this student's code:

Problem: {question.get('question', '')}

Requirements: 
{chr(10).join('- ' + req for req in question.get('requirements', []))}

Student's code:
```
{student_code}
```

Sample solution:
```
{question.get('sample_solution', '')}
```

Evaluate the code on:
1. Correctness (does it solve the problem?)
2. Code quality (is it readable and efficient?)
3. Meeting requirements

Provide feedback in this format:
Score: [0-10]
Feedback: [Brief feedback on correctness, quality, and improvements]"""

            ai_response = LLMClient.call_llm(prompt, max_tokens=400, temperature=0.3)
            
            # Parse AI response
            try:
                score_match = re.search(r'Score:\s*(\d+)', ai_response)
                points = int(score_match.group(1)) if score_match else 5
                points = min(max(points, 0), 10)
                
                feedback_match = re.search(r'Feedback:\s*(.*)', ai_response, re.DOTALL)
                ai_feedback = feedback_match. group(1).strip() if feedback_match else 'Code reviewed.'
                
            except:
                points = 5
                ai_feedback = 'Code received and reviewed.'
            
            score += points
            
            feedback[str(i)] = {
                'is_correct': points >= 7,
                'points': points,
                'feedback': ai_feedback
            }
        
        return score, feedback
    
    @staticmethod
    def get_quiz_history(user_id: str, limit: int = 10):
        """Get user's quiz history"""
        db = SessionLocal()
        try:
            quizzes = db.query(Quiz).filter(
                Quiz.user_id == user_id,
                Quiz.status == 'completed'
            ).order_by(Quiz.attempted_at.desc()).limit(limit).all()
            
            return quizzes
        finally:
            db.close()