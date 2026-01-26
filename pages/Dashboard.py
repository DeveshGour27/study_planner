import streamlit as st
from core.auth_manager import AuthManager
from core.plan_generator import PlanGenerator
from core.day_manager import DayManager
from database.models import StudentProfile, StudyPlan
from database.db_manager import SessionLocal
from datetime import date, datetime

st.title("🏠 Dashboard")

# Get user info
user_id = st.session_state.get('user_id')
if not user_id:
    st.error("Please login first")
    st.stop()

# ✅ CRITICAL: Check and update day automatically
day_changed, new_day, message = DayManager.check_and_update_day(user_id)

if day_changed and message:
    st.success(f"🌅 {message}")
    st.balloons()

# Get user and profile
user = AuthManager.get_user_by_id(user_id)
profile = AuthManager.get_user_profile(user_id)

if not profile:
    st.error("Profile not found")
    st.stop()

# Check if onboarding is complete
if not profile.onboarding_completed:
    st.warning("⚠️ Please complete onboarding first!")
    st.info("👉 You need to set up your learning preferences and generate your study plan.")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🚀 Start Onboarding", use_container_width=True, type="primary"):
            st.switch_page("pages/onboarding.py")
    st.stop()

# ========== DEBUG SECTION (Optional - Remove in Production) ==========
with st.expander("🔧 Debug Controls", expanded=False):
    st.warning("**Developer Tools** - For testing day progression")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Current Day", profile.current_day_number)
        st.caption(f"Last Active: {profile.last_active_date}")
    
    with col2:
        st.metric("Total Days", profile.total_planned_days)
        st.caption(f"Days Remaining: {profile.days_remaining or 'Self-paced'}")
    
    with col3:
        st.metric("Streak", profile.streak_count)
    
    st.markdown("---")
    
    col_a, col_b = st.columns(2)
    
    with col_a:
        if st.button("⏭️ Force Move to Next Day", use_container_width=True, type="primary"):
            db = SessionLocal()
            try:
                db_profile = db.query(StudentProfile).filter(StudentProfile.user_id == user_id).first()
                
                if db_profile:
                    # Move to next day
                    db_profile.current_day_number += 1
                    db_profile.last_active_date = date.today()
                    db_profile.streak_count += 1
                    
                    if db_profile.days_remaining:
                        db_profile.days_remaining = max(0, db_profile.days_remaining - 1)
                    
                    # Mark current day's plan as completed
                    today_plan = db.query(StudyPlan).filter(
                        StudyPlan.user_id == user_id,
                        StudyPlan.day_number == db_profile.current_day_number - 1
                    ).first()
                    
                    if today_plan:
                        today_plan.status = 'completed'
                        today_plan.completed_at = datetime.now()
                    
                    db.commit()
                    
                    st.success(f"✅ Moved to Day {db_profile.current_day_number}!")
                    st.rerun()
            finally:
                db.close()
    
    with col_b:
        if st.button("🔄 Reset to Day 1", use_container_width=True):
            db = SessionLocal()
            try:
                db_profile = db.query(StudentProfile).filter(StudentProfile.user_id == user_id).first()
                
                if db_profile:
                    db_profile.current_day_number = 1
                    db_profile.last_active_date = date.today()
                    db.commit()
                    
                    st.success("✅ Reset to Day 1!")
                    st.rerun()
            finally:
                db.close()

st.markdown("---")
# ========== END DEBUG ==========

# Header with stats
col1, col2, col3 = st.columns([2, 1, 1])
with col1:
    st.markdown(f"### Hi {user.full_name}! 👋")
with col2:
    st.metric("Day", f"{profile.current_day_number}", f"of {profile.total_planned_days}")
with col3:
    st.metric("Streak", f"🔥 {profile.streak_count}", "days")

st.markdown("---")

# Get today's plan
today_plan = PlanGenerator.get_today_plan(user_id)

if not today_plan:
    st.error("📅 No plan for today.")
    
    # Debug section
    with st.expander("🔍 Debug Information", expanded=True):
        st.write(f"**User ID:** `{user_id}`")
        st.write(f"**Current Day Number:** {profile.current_day_number}")
        st.write(f"**Onboarding Completed:** {profile.onboarding_completed}")
        st.write(f"**Study Start Date:** {profile.study_start_date}")
        st.write(f"**Total Planned Days:** {profile.total_planned_days}")
        st.write(f"**Topics:** {profile.topics_to_learn}")
        
        # Check database
        db = SessionLocal()
        try:
            all_plans = db.query(StudyPlan).filter(
                StudyPlan.user_id == user_id
            ).order_by(StudyPlan.day_number).all()
            
            st.write(f"**Total Plans in DB:** {len(all_plans)}")
            
            if all_plans:
                st.success(f"✅ Found {len(all_plans)} plans in database")
                st.write("**First 5 plans:**")
                for plan in all_plans[:5]:
                    st.write(f"- Day {plan.day_number}: {plan.topic} ({plan.status})")
                    
                # Check Day 1 specifically
                day1 = [p for p in all_plans if p.day_number == 1]
                if day1:
                    st.success(f"✅ Day 1 plan exists: {day1[0].topic}")
                else:
                    st.error("❌ Day 1 plan not found!")
                    
                # Check current day
                current_day_plans = [p for p in all_plans if p.day_number == profile.current_day_number]
                if current_day_plans:
                    st.success(f"✅ Day {profile.current_day_number} plan exists: {current_day_plans[0].topic}")
                else:
                    st.error(f"❌ Day {profile.current_day_number} plan not found!")
            else:
                st.error("❌ No plans found in database!")
                st.warning("The plan generation might have failed silently. Check console/terminal for errors.")
        finally:
            db.close()
    
    # Regenerate button
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🔄 Regenerate Study Plan", use_container_width=True, type="primary"):
            with st.spinner("Regenerating your study plan..."):
                success = PlanGenerator.generate_full_plan(user_id)
                if success:
                    st.success("✅ Plan regenerated successfully!")
                    import time
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("❌ Failed to generate plan. Check terminal/console for errors.")
    
    st.stop()

# Today's Focus
st.markdown(f"## 📅 Today's Focus: {today_plan.topic}")
st.markdown(f"⏰ Estimated Time: **{today_plan.estimated_hours} hours**")

# Progress calculation
total_tasks = len(today_plan.tasks)
completed_tasks = sum(1 for task in today_plan.tasks if task.get('completed', False))
progress = (completed_tasks / total_tasks) * 100 if total_tasks > 0 else 0

st.progress(progress / 100, text=f"Progress: {completed_tasks}/{total_tasks} tasks ({progress:.0f}%)")

st.markdown("---")

# Display tasks
col_left, col_right = st.columns(2)

with col_left:
    st.markdown("### ✅ Completed")
    completed_shown = False
    for i, task in enumerate(today_plan.tasks):
        if task.get('completed', False):
            completed_shown = True
            task_type = task.get('type', 'task')
            task_title = task.get('title', 'Untitled')
            
            if task_type == 'video':
                st.success(f"🎥 {task_title} ({task.get('duration_min', 0)} min)")
            elif task_type == 'reading':
                st.success(f"📖 {task_title} ({task.get('duration_min', 0)} min)")
            elif task_type == 'practice':
                st.success(f"💻 {task_title} ({task.get('count', 0)} problems)")
            elif task_type == 'quiz':
                st.success(f"📝 {task_title} ({task.get('duration_min', 0)} min)")
            else:
                st.success(f"✓ {task_title}")
    
    if not completed_shown:
        st.info("No tasks completed yet. Keep going!")

with col_right:
    st.markdown("### 📝 Pending")
    pending_shown = False
    for i, task in enumerate(today_plan.tasks):
        if not task.get('completed', False):
            pending_shown = True
            task_type = task.get('type', 'task')
            task_title = task.get('title', 'Untitled')
            
            # Create a container for each task
            col_task, col_btn = st.columns([4, 1])
            
            with col_task:
                if task_type == 'video':
                    st.info(f"🎥 {task_title} ({task.get('duration_min', 0)} min)")
                elif task_type == 'reading':
                    st.info(f"📖 {task_title} ({task.get('duration_min', 0)} min)")
                elif task_type == 'practice':
                    st.info(f"💻 {task_title} ({task.get('count', 0)} problems)")
                elif task_type == 'quiz':
                    st.info(f"📝 {task_title}")
                else:
                    st.info(f"• {task_title}")
            
            with col_btn:
                if st.button("✓", key=f"complete_task_{today_plan.plan_id}_{i}", help="Mark as complete"):
                    success, message = PlanGenerator.mark_task_complete(today_plan.plan_id, i)
                    if success:
                        st.success("Task completed! ✅")
                        st.rerun()
                    else:
                        st.error(f"Error: {message}")
    
    if not pending_shown:
        st.success("🎉 All tasks completed! Great job!")

st.markdown("---")

# Quick Stats
st.markdown("### 📈 Quick Stats")

# Calculate real stats from database
db = SessionLocal()
try:
    # Completed plans count
    completed_plans_count = db.query(StudyPlan).filter(
        StudyPlan.user_id == user_id,
        StudyPlan.status == 'completed'
    ).count()
    
    # Quiz stats
    from database.models import Quiz
    quizzes = db.query(Quiz).filter(
        Quiz.user_id == user_id,
        Quiz.status == 'completed'
    ).all()
    
    avg_score = 0
    if quizzes:
        valid_scores = []
        for q in quizzes:
            if q.score is not None and q.max_score is not None and q.max_score > 0:
                valid_scores.append((q.score / q.max_score) * 100)
        avg_score = sum(valid_scores) / len(valid_scores) if valid_scores else 0
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Topics Covered", completed_plans_count)
    with col2:
        st.metric("Avg Quiz Score", f"{avg_score:.0f}%" if avg_score > 0 else "N/A")
    with col3:
        st.metric("Days Remaining", profile.days_remaining or "Self-paced")
    with col4:
        st.metric("Total Quizzes", len(quizzes))

finally:
    db.close()

# Action Buttons
st.markdown("---")
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("💬 Chat with AI", use_container_width=True):
        st.switch_page("pages/Chat.py")

with col2:
    if st.button("📝 Take Quiz", use_container_width=True):
        st.switch_page("pages/Quiz.py")

with col3:
    if st.button("📊 View Progress", use_container_width=True):
        st.switch_page("pages/Progress.py")

# Upcoming section
st.markdown("---")
st.markdown("### 🎯 Upcoming")

db = SessionLocal()
try:
    upcoming_plans = db.query(StudyPlan).filter(
        StudyPlan.user_id == user_id,
        StudyPlan.day_number > profile.current_day_number,
        StudyPlan.status == 'pending'
    ).order_by(StudyPlan.day_number).limit(3).all()
    
    if upcoming_plans:
        for plan in upcoming_plans:
            day_label = "Tomorrow" if plan.day_number == profile.current_day_number + 1 else f"Day {plan.day_number}"
            st.info(f"📅 **{day_label}:** {plan.topic}")
    else:
        st.info("📅 **All caught up!** No upcoming plans yet.")
finally:
    db.close()