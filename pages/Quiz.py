import streamlit as st
from core.quiz_engine import QuizEngine
from database.models import StudentProfile, StudyPlan, Quiz, QuizResponse
from database.db_manager import SessionLocal
from datetime import datetime
from styles.design_system import DesignSystem as DS
from styles.components import UIComponents

st.set_page_config(page_title="Quiz", page_icon="📝", layout="wide")

# Inject CSS
UIComponents.render_custom_css()

# Check authentication
if 'user_id' not in st.session_state:
    st.warning("⚠️ Please login first")
    st.stop()

user_id = st.session_state['user_id']

# Initialize session state
if 'current_quiz' not in st.session_state:
    st.session_state.current_quiz = None
if 'quiz_answers' not in st.session_state:
    st.session_state.quiz_answers = {}
if 'quiz_submitted' not in st.session_state:
    st.session_state.quiz_submitted = False
if 'quiz_results' not in st.session_state:
    st.session_state.quiz_results = None
if 'view_mode' not in st.session_state:
    st.session_state.view_mode = 'home'
if 'selected_quiz_id' not in st.session_state:
    st.session_state.selected_quiz_id = None

# Get user's current topic
db = SessionLocal()
try:
    profile = db.query(StudentProfile).filter(StudentProfile.user_id == user_id).first()
    today_plan = db.query(StudyPlan).filter(
        StudyPlan.user_id == user_id,
        StudyPlan.day_number == profile.current_day_number
    ).first() if profile else None
    
    current_topic = today_plan.topic if today_plan else None
finally:
    db.close()

# Header
st.markdown(f"""
<div style="text-align: center; margin-bottom: {DS.SPACE_8};">
    <h1 style="color: {DS.PRIMARY};">📝 Quiz Time!</h1>
    <p style="color: {DS.TEXT_SECONDARY}; font-size: {DS.FONT_SIZE_LG};">
        Test your knowledge and track your progress
    </p>
</div>
""", unsafe_allow_html=True)

# ==================== HOME VIEW ====================
if st.session_state.view_mode == 'home':
    
    st.markdown(f"""
    <div class="modern-card">
        <h2 style="color: {DS.PRIMARY};">🎯 Start a New Quiz</h2>
        <p style="color: {DS.TEXT_SECONDARY};">Choose your topic and difficulty level</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown(f"<div style='margin: {DS.SPACE_6} 0;'></div>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Topic selection
        if current_topic:
            topic_options = [current_topic, "Custom Topic"]
            topic_choice = st.selectbox("📚 Select Topic", topic_options)
            
            if topic_choice == "Custom Topic":
                topic = st.text_input("Enter topic", placeholder="e.g., Python Functions")
            else:
                topic = current_topic
        else:
            topic = st.text_input("📚 Enter Topic", placeholder="e.g., Python Basics")
        
        # Quiz type
        quiz_type = st.selectbox(
            "📋 Quiz Type",
            ["mcq", "descriptive", "coding"],
            format_func=lambda x: {
                'mcq': '✅ Multiple Choice',
                'descriptive': '✍️ Descriptive',
                'coding': '💻 Coding'
            }[x]
        )
    
    with col2:
        # Difficulty
        difficulty = st.selectbox(
            "⚡ Difficulty",
            ["easy", "medium", "hard"],
            index=1,
            format_func=lambda x: x.capitalize()
        )
        
        # Number of questions
        num_questions = st.slider("🔢 Number of Questions", 3, 10, 5)
    
    st.markdown(f"<div style='margin: {DS.SPACE_6} 0;'></div>", unsafe_allow_html=True)
    
    # Generate quiz button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🚀 Generate Quiz", type="primary", use_container_width=True):
            if not topic:
                st.error("❌ Please enter a topic")
            else:
                with st.spinner(f"🤖 Generating {num_questions} {quiz_type.upper()} questions about {topic}..."):
                    quiz, error = QuizEngine.generate_quiz(
                        user_id=user_id,
                        topic=topic,
                        quiz_type=quiz_type,
                        difficulty=difficulty,
                        num_questions=num_questions
                    )
                    
                    if quiz:
                        st.session_state.current_quiz = quiz
                        st.session_state.quiz_answers = {}
                        st.session_state.quiz_submitted = False
                        st.session_state.quiz_results = None
                        st.session_state.view_mode = 'taking_quiz'
                        st.success("✅ Quiz generated! Let's begin!")
                        st.rerun()
                    else:
                        st.error(f"❌ Failed to generate quiz: {error}")
    
    st.markdown(f"<div style='margin: {DS.SPACE_8} 0;'></div>", unsafe_allow_html=True)
    
    # Button to view all quizzes
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("📊 View All My Quizzes", use_container_width=True):
            st.session_state.view_mode = 'quiz_list'
            st.rerun()

# ==================== TAKING QUIZ VIEW ====================
elif st.session_state.view_mode == 'taking_quiz':
    quiz = st.session_state.current_quiz
    
    if not quiz:
        st.session_state.view_mode = 'home'
        st.rerun()
    
    st.markdown(f"""
    <div class="modern-card" style="background: {DS.GRADIENT_PRIMARY}; padding: {DS.SPACE_6};">
        <h2 style="color: white;">📚 {quiz.topic}</h2>
        <p style="color: rgba(255,255,255,0.9);">
            🏷️ {quiz.quiz_type.upper()} | ⚡ {len(quiz.questions)} Questions | 🎯 {quiz.max_score} Points
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown(f"<div style='margin: {DS.SPACE_6} 0;'></div>", unsafe_allow_html=True)
    
    # Progress bar
    answered = len(st.session_state.quiz_answers)
    total = len(quiz.questions)
    progress = answered / total if total > 0 else 0
    
    st.markdown(f"""
    <div style="background: {DS.SURFACE}; padding: {DS.SPACE_4}; border-radius: {DS.RADIUS_LG}; margin-bottom: {DS.SPACE_6};">
        <div style="display: flex; justify-content: space-between; margin-bottom: {DS.SPACE_3};">
            <span style="color: {DS.TEXT_SECONDARY};">Progress</span>
            <span style="color: {DS.PRIMARY}; font-weight: 700;">{answered}/{total} answered</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.progress(progress)
    
    st.markdown(f"<div style='margin: {DS.SPACE_8} 0;'></div>", unsafe_allow_html=True)
    
    # Display questions
    for i, question in enumerate(quiz.questions):
        st.markdown(f"""
        <div class="modern-card">
            <h3 style="color: {DS.PRIMARY}; margin-bottom: {DS.SPACE_4};">Question {i+1}</h3>
            <p style="color: {DS.TEXT_PRIMARY}; font-size: {DS.FONT_SIZE_LG}; font-weight: 600;">
                {question.get('question', '')}
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"<div style='margin: {DS.SPACE_4} 0;'></div>", unsafe_allow_html=True)
        
        # MCQ - Radio buttons
        if quiz.quiz_type == 'mcq':
            options = question.get('options', [])
            answer = st.radio(
                "Select your answer:",
                options,
                key=f"q_{i}",
                index=None,
                label_visibility="collapsed"
            )
            if answer:
                st.session_state.quiz_answers[str(i)] = answer
        
        # Descriptive - Text area
        elif quiz.quiz_type == 'descriptive':
            st.info(f"💡 Key points to cover: {', '.join(question.get('key_points', []))}")
            answer = st.text_area(
                "Your answer:",
                key=f"q_{i}",
                height=150,
                placeholder="Write your answer here...",
                label_visibility="collapsed"
            )
            if answer:
                st.session_state.quiz_answers[str(i)] = answer
        
        # Coding - Code editor
        elif quiz.quiz_type == 'coding':
            with st.expander("📋 Requirements"):
                for req in question.get('requirements', []):
                    st.write(f"• {req}")
            
            st.write(f"**Sample Input:** `{question.get('sample_input', '')}`")
            st.write(f"**Expected Output:** `{question.get('sample_output', '')}`")
            
            answer = st.text_area(
                "Your code:",
                key=f"q_{i}",
                height=200,
                placeholder="# Write your code here...",
                label_visibility="collapsed"
            )
            if answer:
                st.session_state.quiz_answers[str(i)] = answer
        
        st.markdown(f"<div style='margin: {DS.SPACE_6} 0;'></div>", unsafe_allow_html=True)
    
    # Submit button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("✅ Submit Quiz", type="primary", use_container_width=True):
            if len(st.session_state.quiz_answers) < len(quiz.questions):
                st.warning(f"⚠️ You've answered {len(st.session_state.quiz_answers)}/{len(quiz.questions)} questions. Submit anyway?")
            
            with st.spinner("🤖 Grading your quiz..."):
                success, results = QuizEngine.submit_quiz(quiz.quiz_id, st.session_state.quiz_answers)
                
                if success:
                    st.session_state.quiz_submitted = True
                    st.session_state.quiz_results = results
                    st.session_state.selected_quiz_id = quiz.quiz_id
                    st.session_state.view_mode = 'analysis'
                    st.balloons()
                    st.rerun()
                else:
                    st.error(f"❌ Error submitting quiz: {results}")

# ==================== QUIZ LIST VIEW ====================
elif st.session_state.view_mode == 'quiz_list':
    
    if st.button("⬅️ Back to Home"):
        st.session_state.view_mode = 'home'
        st.rerun()
    
    st.markdown(f"<div style='margin: {DS.SPACE_6} 0;'></div>", unsafe_allow_html=True)
    
    # Get all quizzes
    db = SessionLocal()
    try:
        quizzes = db.query(Quiz).filter(
            Quiz.user_id == user_id,
            Quiz.status == 'completed'
        ).order_by(Quiz.attempted_at.desc()).all()
    finally:
        db.close()
    
    if not quizzes:
        UIComponents.glass_card(
            "No Quizzes Yet",
            "Take your first quiz to see your performance here!",
            "📝"
        )
    else:
        for idx, quiz in enumerate(quizzes, 1):
            percentage = round((quiz.score / quiz.max_score) * 100, 1) if quiz.max_score > 0 else 0
            
            # Determine badge
            if percentage >= 80:
                badge = UIComponents.badge("Excellent", "success")
                color = DS.ACCENT
            elif percentage >= 60:
                badge = UIComponents.badge("Good", "primary")
                color = DS.PRIMARY
            else:
                badge = UIComponents.badge("Needs Practice", "warning")
                color = DS.ACCENT_WARNING
            
            # Create clickable card
            if st.button(
                f"📝 {quiz.topic} - {percentage}%",
                key=f"quiz_{quiz.quiz_id}",
                use_container_width=True
            ):
                st.session_state.selected_quiz_id = quiz.quiz_id
                st.session_state.view_mode = 'analysis'
                st.rerun()
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.caption(f"🏷️ {quiz.quiz_type.upper()}")
            with col2:
                st.caption(f"🎯 {quiz.score}/{quiz.max_score} points")
            with col3:
                st.caption(f"📅 {quiz.attempted_at.strftime('%b %d, %Y') if quiz.attempted_at else 'N/A'}")
            with col4:
                st.caption(f"❓ {len(quiz.questions)} questions")
            
            st.markdown("---")

# ==================== ANALYSIS VIEW ====================
elif st.session_state.view_mode == 'analysis':
    
    if not st.session_state.selected_quiz_id:
        st.session_state.view_mode = 'home'
        st.rerun()
    
    # Get quiz data
    db = SessionLocal()
    try:
        quiz = db.query(Quiz).filter(Quiz.quiz_id == st.session_state.selected_quiz_id).first()
        responses = db.query(QuizResponse).filter(
            QuizResponse.quiz_id == st.session_state.selected_quiz_id
        ).order_by(QuizResponse.question_number).all()
    finally:
        db.close()
    
    if not quiz:
        st.error("Quiz not found")
        st.session_state.view_mode = 'home'
        st.rerun()
    
    # Back button
    if st.button("⬅️ Back"):
        st.session_state.view_mode = 'quiz_list'
        st.rerun()
    
    st.markdown(f"<div style='margin: {DS.SPACE_6} 0;'></div>", unsafe_allow_html=True)
    
    # Score card
    percentage = round((quiz.score / quiz.max_score) * 100, 1) if quiz.max_score > 0 else 0
    
    if percentage >= 80:
        emoji = "🏆"
        message = "Outstanding!"
        gradient = DS.GRADIENT_SUCCESS
    elif percentage >= 60:
        emoji = "✅"
        message = "Good Job!"
        gradient = DS.GRADIENT_PRIMARY
    else:
        emoji = "📖"
        message = "Keep Practicing!"
        gradient = DS.GRADIENT_WARNING
    
    st.markdown(f"""
    <div style="text-align: center; padding: {DS.SPACE_10}; background: {gradient}; 
                border-radius: {DS.RADIUS_2XL}; margin-bottom: {DS.SPACE_8}; box-shadow: {DS.SHADOW_2XL};">
        <div style="font-size: 4rem; margin-bottom: {DS.SPACE_4};">{emoji}</div>
        <h1 style="color: white; margin-bottom: {DS.SPACE_2};">{message}</h1>
        <h2 style="color: white; margin-bottom: {DS.SPACE_2};">{quiz.score} / {quiz.max_score} Points</h2>
        <h3 style="color: rgba(255,255,255,0.9);">{percentage}%</h3>
        <p style="color: rgba(255,255,255,0.8); margin-top: {DS.SPACE_4};">
            📚 {quiz.topic} | 🏷️ {quiz.quiz_type.upper()}
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Summary stats
    correct_count = sum(1 for r in responses if r.is_correct)
    wrong_count = len(responses) - correct_count
    
    col1, col2, col3 = st.columns(3)
    with col1:
        UIComponents.stat_card("Correct", correct_count, "✅")
    with col2:
        UIComponents.stat_card("Wrong", wrong_count, "❌")
    with col3:
        UIComponents.stat_card("Accuracy", f"{percentage}%", "📊")
    
    st.markdown(f"<div style='margin: {DS.SPACE_10} 0;'></div>", unsafe_allow_html=True)
    
    # Question-by-question analysis
    st.markdown(f"<h2 style='color: {DS.PRIMARY};'>📋 Detailed Analysis</h2>", unsafe_allow_html=True)
    
    for response in responses:
        is_correct = response.is_correct
        status_icon = "✅" if is_correct else "❌"
        border_color = DS.ACCENT if is_correct else DS.ACCENT_ERROR
        
        st.markdown(f"""
        <div class="modern-card" style="border-left: 4px solid {border_color};">
            <h3 style="color: {DS.PRIMARY};">{status_icon} Question {response.question_number + 1}</h3>
            <p style="color: {DS.TEXT_PRIMARY}; font-weight: 600; margin: {DS.SPACE_3} 0;">
                {response.question_text}
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        if quiz.quiz_type == 'mcq':
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**Your answer:** {response.student_answer or 'Not answered'}")
            with col2:
                st.write(f"**Correct answer:** {response.correct_answer}")
        else:
            st.write("**Your answer:**")
            st.code(response.student_answer or 'Not answered')
        
        if response.ai_feedback:
            if is_correct:
                st.success(f"💡 {response.ai_feedback}")
            else:
                st.info(f"💡 {response.ai_feedback}")
        
        st.markdown(f"<div style='margin: {DS.SPACE_6} 0;'></div>", unsafe_allow_html=True)
    
    # Action buttons
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📝 Take Another Quiz", use_container_width=True, type="primary"):
            st.session_state.view_mode = 'home'
            st.session_state.current_quiz = None
            st.session_state.quiz_answers = {}
            st.session_state.quiz_submitted = False
            st.session_state.quiz_results = None
            st.session_state.selected_quiz_id = None
            st.rerun()
    
    with col2:
        if st.button("📊 View All Quizzes", use_container_width=True):
            st.session_state.view_mode = 'quiz_list'
            st.rerun()