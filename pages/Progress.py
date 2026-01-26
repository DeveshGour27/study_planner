import streamlit as st
from core.auth_manager import AuthManager
from core.day_manager import DayManager
from database.models import StudyPlan, Quiz, ProgressAnalytics
from database.db_manager import SessionLocal
from utils import safe_percentage, safe_format, UIHelpers
from styles.design_system import DesignSystem as DS
from styles.components import UIComponents
import pandas as pd
from datetime import date, timedelta

st.set_page_config(page_title="Progress", page_icon="📈", layout="wide")

# Inject CSS
UIComponents.render_custom_css()

# Check authentication
if 'user_id' not in st.session_state:
    st.warning("⚠️ Please login first")
    st.stop()

user_id = st.session_state['user_id']
user = AuthManager.get_user_by_id(user_id)
profile = AuthManager.get_user_profile(user_id)

if not profile or not profile.onboarding_completed:
    st.warning("⚠️ Please complete onboarding first!")
    st.stop()

# Header
st.markdown(f"""
<div style="text-align: center; margin-bottom: {DS.SPACE_8};">
    <h1 style="color: {DS.PRIMARY};">📈 Your Learning Progress</h1>
    <p style="color: {DS.TEXT_SECONDARY}; font-size: {DS.FONT_SIZE_LG};">
        Track your achievements and growth
    </p>
</div>
""", unsafe_allow_html=True)

# Get summary
summary = DayManager.get_today_summary(user_id)

# Header Stats
col1, col2, col3, col4 = st.columns(4)

with col1:
    UIComponents.stat_card(
        "Current Day",
        f"{profile.current_day_number}/{profile.total_planned_days}",
        "📅"
    )

with col2:
    UIComponents.stat_card(
        "Streak",
        f"{profile.streak_count} days",
        "🔥"
    )

with col3:
    if profile.days_remaining:
        UIComponents.stat_card(
            "Days Left",
            profile.days_remaining,
            "⏰"
        )
    else:
        UIComponents.stat_card(
            "Pace",
            "Self-paced",
            "🎯"
        )

with col4:
    progress_pct = safe_percentage(profile.current_day_number - 1, profile.total_planned_days, 0)
    UIComponents.stat_card(
        "Overall Progress",
        f"{progress_pct:.0f}%",
        "📈"
    )

st.markdown(f"<div style='margin: {DS.SPACE_8} 0;'></div>", unsafe_allow_html=True)

# Today's Progress
st.markdown(f"""
<div class="modern-card">
    <h2 style="color: {DS.PRIMARY};">📅 Today's Progress</h2>
</div>
""", unsafe_allow_html=True)

if summary:
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(f"""
        <div style="background: {DS.SURFACE}; padding: {DS.SPACE_4}; border-radius: {DS.RADIUS_MD}; text-align: center;">
            <p style="color: {DS.TEXT_MUTED}; margin-bottom: {DS.SPACE_2};">Topic</p>
            <h3 style="color: {DS.PRIMARY};">{summary.get('topic', 'N/A')}</h3>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        tasks_completed = summary.get('tasks_completed', 0)
        total_tasks = summary.get('total_tasks', 0)
        st.markdown(f"""
        <div style="background: {DS.SURFACE}; padding: {DS.SPACE_4}; border-radius: {DS.RADIUS_MD}; text-align: center;">
            <p style="color: {DS.TEXT_MUTED}; margin-bottom: {DS.SPACE_2};">Tasks</p>
            <h3 style="color: {DS.ACCENT};">{tasks_completed}/{total_tasks}</h3>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        progress = safe_percentage(
            summary.get('tasks_completed', 0), 
            summary.get('total_tasks', 1), 
            0
        )
        st.markdown(f"""
        <div style="background: {DS.SURFACE}; padding: {DS.SPACE_4}; border-radius: {DS.RADIUS_MD}; text-align: center;">
            <p style="color: {DS.TEXT_MUTED}; margin-bottom: {DS.SPACE_2};">Completion</p>
            <h3 style="color: {DS.PRIMARY};">{progress:.0f}%</h3>
        </div>
        """, unsafe_allow_html=True)

    st.markdown(f"<div style='margin: {DS.SPACE_4} 0;'></div>", unsafe_allow_html=True)

    # Progress bar
    day_number = summary.get('day_number', profile.current_day_number)
    st.progress(progress / 100)
else:
    st.info("📊 No progress data available. Start completing today's tasks!")

st.markdown(f"<div style='margin: {DS.SPACE_10} 0;'></div>", unsafe_allow_html=True)

# Week Summary
st.markdown(f"""
<div class="modern-card">
    <h2 style="color: {DS.PRIMARY};">📆 This Week's Summary</h2>
</div>
""", unsafe_allow_html=True)

week_summary = DayManager.get_week_summary(user_id)

if week_summary:
    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        UIComponents.stat_card("Topics", week_summary.get('topics_covered', 0), "📚")

    with col2:
        UIComponents.stat_card("Quizzes", week_summary.get('quizzes_attempted', 0), "📝")

    with col3:
        avg_score = week_summary.get('avg_quiz_score', 0)
        UIComponents.stat_card("Avg Score", safe_format(avg_score, "{:.0f}%", "N/A"), "🎯")

    with col4:
        total_hours = week_summary.get('total_hours', 0)
        UIComponents.stat_card("Study Hours", safe_format(total_hours, "{:.1f}h", "0h"), "⏰")

    with col5:
        UIComponents.stat_card("Tasks Done", week_summary.get('total_tasks', 0), "✅")
else:
    st.info("📊 No data for this week yet. Keep learning!")

st.markdown(f"<div style='margin: {DS.SPACE_10} 0;'></div>", unsafe_allow_html=True)

# Quiz Performance
st.markdown(f"""
<div class="modern-card">
    <h2 style="color: {DS.PRIMARY};">📝 Quiz Performance</h2>
</div>
""", unsafe_allow_html=True)

db = SessionLocal()
try:
    quizzes = db.query(Quiz).filter(
        Quiz.user_id == user_id,
        Quiz.status == 'completed'
    ).order_by(Quiz.created_at.desc()).limit(10).all()

    if quizzes:
        # Create dataframe
        quiz_data = []
        for q in quizzes:
            score = q.score if q.score is not None else 0
            max_score = q.max_score if q.max_score is not None else 1
            percentage = safe_percentage(score, max_score, 0)
            
            # Color based on score
            if percentage >= 80:
                badge = UIComponents.badge("Excellent", "success")
            elif percentage >= 60:
                badge = UIComponents.badge("Good", "primary")
            else:
                badge = UIComponents.badge("Practice", "warning")
            
            quiz_data.append({
                "Topic": q.topic,
                "Score": f"{score}/{max_score}",
                "Percentage": f"{percentage:.0f}%",
                "Date": q.attempted_at.strftime("%b %d") if q.attempted_at else "N/A"
            })

        df = pd.DataFrame(quiz_data)
        st.dataframe(df, use_container_width=True, hide_index=True)

        # Calculate average score safely
        valid_scores = []
        for q in quizzes:
            if q.score is not None and q.max_score is not None and q.max_score > 0:
                percentage = safe_percentage(q.score, q.max_score, 0)
                valid_scores.append(percentage)
        
        avg_percentage = sum(valid_scores) / len(valid_scores) if valid_scores else 0

        col1, col2 = st.columns(2)
        with col1:
            UIComponents.stat_card("Total Quizzes", len(quizzes), "📝")
        with col2:
            UIComponents.stat_card("Average Score", safe_format(avg_percentage, "{:.1f}%", "N/A"), "🎯")
    else:
        st.markdown(f"""
        <div class="glass-card" style="text-align: center; padding: {DS.SPACE_10};">
            <div style="font-size: 4rem; margin-bottom: {DS.SPACE_4};">📝</div>
            <h3 style="color: {DS.PRIMARY};">No Quizzes Yet</h3>
            <p style="color: {DS.TEXT_SECONDARY};">Take your first quiz to see your performance here!</p>
        </div>
        """, unsafe_allow_html=True)
finally:
    db.close()

st.markdown(f"<div style='margin: {DS.SPACE_10} 0;'></div>", unsafe_allow_html=True)

# Study Plan Progress
st.markdown(f"""
<div class="modern-card">
    <h2 style="color: {DS.PRIMARY};">📚 Study Plan Progress</h2>
</div>
""", unsafe_allow_html=True)

db = SessionLocal()
try:
    all_plans = db.query(StudyPlan).filter(
        StudyPlan.user_id == user_id
    ).order_by(StudyPlan.day_number).all()

    if all_plans:
        completed = sum(1 for p in all_plans if p.status == 'completed')
        in_progress = sum(1 for p in all_plans if p.status == 'in_progress')
        pending = sum(1 for p in all_plans if p.status == 'pending')

        col1, col2, col3 = st.columns(3)

        with col1:
            UIComponents.stat_card("Completed", completed, "✅")
        with col2:
            UIComponents.stat_card("In Progress", in_progress, "🔄")
        with col3:
            UIComponents.stat_card("Pending", pending, "⏳")

        st.markdown(f"<div style='margin: {DS.SPACE_6} 0;'></div>", unsafe_allow_html=True)

        # Topics breakdown
        st.markdown(f"<h3 style='color: {DS.PRIMARY};'>Topics Covered</h3>", unsafe_allow_html=True)

        completed_plans = [p for p in all_plans if p.status == 'completed']
        if completed_plans:
            topics = {}
            for plan in completed_plans:
                topic = plan.topic
                if topic in topics:
                    topics[topic] += 1
                else:
                    topics[topic] = 1

            for topic, count in topics.items():
                st.markdown(f"""
                <div style="background: {DS.SURFACE}; padding: {DS.SPACE_3}; border-radius: {DS.RADIUS_MD}; 
                            margin-bottom: {DS.SPACE_2}; border-left: 4px solid {DS.ACCENT};">
                    <strong style="color: {DS.TEXT_PRIMARY};">✅ {topic}</strong>
                    <span style="color: {DS.TEXT_MUTED}; margin-left: {DS.SPACE_2};">
                        ({count} day{'s' if count > 1 else ''})
                    </span>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No topics completed yet. Keep going!")
    else:
        st.markdown(f"""
        <div class="glass-card" style="text-align: center; padding: {DS.SPACE_10};">
            <div style="font-size: 4rem; margin-bottom: {DS.SPACE_4};">📚</div>
            <h3 style="color: {DS.PRIMARY};">No Study Plan Yet</h3>
            <p style="color: {DS.TEXT_SECONDARY};">Complete onboarding to generate your personalized study plan!</p>
        </div>
        """, unsafe_allow_html=True)
finally:
    db.close()

st.markdown(f"<div style='margin: {DS.SPACE_10} 0;'></div>", unsafe_allow_html=True)

# Achievements
st.markdown(f"""
<div class="modern-card">
    <h2 style="color: {DS.PRIMARY};">🏆 Achievements</h2>
</div>
""", unsafe_allow_html=True)

achievements = []

if profile.streak_count >= 7:
    achievements.append(("🔥 Week Warrior", f"Maintained {profile.streak_count}-day streak!"))
elif profile.streak_count >= 3:
    achievements.append(("⭐ Consistency Champion", f"{profile.streak_count}-day streak!"))

db = SessionLocal()
try:
    total_quizzes = db.query(Quiz).filter(
        Quiz.user_id == user_id,
        Quiz.status == 'completed'
    ).count()

    if total_quizzes >= 10:
        achievements.append(("🎓 Quiz Master", f"Completed {total_quizzes} quizzes!"))
    elif total_quizzes >= 5:
        achievements.append(("📝 Quiz Enthusiast", f"Completed {total_quizzes} quizzes!"))

    # Perfect scores
    perfect_quizzes = db.query(Quiz).filter(
        Quiz.user_id == user_id,
        Quiz.status == 'completed',
        Quiz.score == Quiz.max_score
    ).count()

    if perfect_quizzes > 0:
        achievements.append(("💯 Perfect Score", f"Achieved perfection {perfect_quizzes} time{'s' if perfect_quizzes > 1 else ''}!"))

finally:
    db.close()

if achievements:
    cols = st.columns(min(3, len(achievements)))
    for i, (title, desc) in enumerate(achievements):
        with cols[i % 3]:
            st.markdown(f"""
            <div class="glass-card" style="text-align: center;">
                <h3 style="color: {DS.PRIMARY}; margin-bottom: {DS.SPACE_3};">{title}</h3>
                <p style="color: {DS.TEXT_SECONDARY};">{desc}</p>
            </div>
            """, unsafe_allow_html=True)
else:
    st.info("🏆 Keep learning to unlock achievements!")

st.markdown(f"<div style='margin: {DS.SPACE_8} 0;'></div>", unsafe_allow_html=True)

# Motivational message
if summary:
    progress = safe_percentage(
        summary.get('tasks_completed', 0),
        summary.get('total_tasks', 1),
        0
    )
    if progress == 100:
        st.balloons()
        st.success("🎉 Amazing! You completed today's tasks! Keep up the excellent work!")
    elif progress >= 50:
        st.info("💪 You're making great progress today! Keep going!")
    else:
        st.warning("⏰ Don't forget to complete today's tasks!")