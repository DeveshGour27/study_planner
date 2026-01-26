import streamlit as st
from core.onboarding import OnboardingManager
from core.plan_generator import PlanGenerator
from datetime import datetime, timedelta
from utils import Validators, UIHelpers

st.set_page_config(page_title="Onboarding", page_icon="🎓", layout="centered")

st.title("🎓 Welcome to Your Learning Journey!")

# Initialize session state for onboarding
if 'onboarding_step' not in st.session_state:
    st.session_state.onboarding_step = 1
    st.session_state.topics = []
    st.session_state.levels = {}
    st.session_state.target_date = None
    st.session_state.hours_per_day = 3

user_id = st.session_state.get('user_id')
if not user_id:
    st.error("Please login first")
    st.stop()

# Progress indicator - SIMPLIFIED VERSION
steps = ["📚 Topics", "📊 Levels", "📅 Timeline", "⏰ Hours"]
current_step = st.session_state.onboarding_step

# Display progress
col1, col2, col3, col4 = st.columns(4)
for i, (col, step) in enumerate(zip([col1, col2, col3, col4], steps), 1):
    with col:
        if i < current_step:
            st.success(f"✅ Step {i}")
            st.caption(step)
        elif i == current_step:
            st.info(f"🔹 Step {i}")
            st.caption(f"**{step}**")
        else:
            st.write(f"⚪ Step {i}")
            st.caption(step)

# Progress bar
progress = (current_step - 1) / (len(steps) - 1)
st.progress(progress)

st.markdown("---")

# Step 1: Topics
if st.session_state.onboarding_step == 1:
    st.markdown("### 📚 What would you like to learn?")
    
    # Show AI greeting
    if 'ai_greeting' not in st.session_state:
        greeting = OnboardingManager.start_onboarding(user_id)
        st.session_state.ai_greeting = greeting
    
    st.info(f"🤖 AI: {st.session_state.ai_greeting}")
    
    st.markdown("---")
    
    # Topic selection
    available_topics = ["Data Structures", "Algorithms", "DBMS", "Operating Systems", 
                       "Computer Networks", "Python", "Java", "Web Development", 
                       "Machine Learning", "System Design"]
    
    selected_topics = st.multiselect(
        "Select topics (choose one or more):",
        available_topics,
        default=st.session_state.topics,
        help="Choose 1-10 topics you want to learn"
    )
    
    # Validate topics
    if selected_topics:
        valid_topics, error = Validators.validate_topics(selected_topics)
        if not valid_topics:
            st.error(f"❌ {error}")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("Next →", disabled=len(selected_topics) == 0, use_container_width=True, type="primary"):
            valid_topics, error = Validators.validate_topics(selected_topics)
            if valid_topics:
                st.session_state.topics = selected_topics
                st.session_state.onboarding_step = 2
                st.rerun()
            else:
                st.error(error)

# Step 2: Skill Levels
elif st.session_state.onboarding_step == 2:
    st.markdown("### 📊 What's your current skill level?")
    
    st.info(f"🤖 AI: Great choice! Let me know your current level in these topics.")
    
    st.markdown("---")
    
    levels = {}
    for topic in st.session_state.topics:
        st.markdown(f"**{topic}**")
        level = st.select_slider(
            f"Level for {topic}",
            options=["Beginner", "Intermediate", "Advanced"],
            value=st.session_state.levels.get(topic, "Beginner"),
            key=f"level_{topic}",
            label_visibility="collapsed"
        )
        levels[topic] = level.lower()
        st.markdown("<br>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("← Back", use_container_width=True):
            st.session_state.onboarding_step = 1
            st.rerun()
    with col2:
        if st.button("Next →", use_container_width=True, type="primary"):
            st.session_state.levels = levels
            st.session_state.onboarding_step = 3
            st.rerun()

# Step 3: Timeline
elif st.session_state.onboarding_step == 3:
    st.markdown("### 📅 Do you have a target date?")
    
    st.info(f"🤖 AI: When do you want to complete these topics?")
    
    st.markdown("---")
    
    has_deadline = st.radio(
        "Choose your learning pace:",
        ["I have a specific deadline", "I want to learn at my own pace"],
        index=0 if st.session_state.target_date else 1
    )
    
    target_date = None
    if has_deadline == "I have a specific deadline":
        target_date = st.date_input(
            "Target completion date:",
            value=st.session_state.target_date or (datetime.now() + timedelta(days=30)).date(),
            min_value=datetime.now().date(),
            help="Choose a realistic target date"
        )
        
        # Validate target date
        if target_date:
            valid_date, error = Validators.validate_target_date(target_date)
            if not valid_date:
                st.error(f"❌ {error}")
            else:
                st.session_state.target_date = target_date
                days_left = (target_date - datetime.now().date()).days
                st.success(f"📅 You have {days_left} days to complete your learning goals!")
    else:
        st.session_state.target_date = None
        st.success("📌 Perfect! We'll create a flexible plan that adapts to your pace.")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("← Back", use_container_width=True):
            st.session_state.onboarding_step = 2
            st.rerun()
    with col2:
        # Check if target date is valid before allowing next
        can_proceed = True
        if has_deadline == "I have a specific deadline" and target_date:
            valid_date, _ = Validators.validate_target_date(target_date)
            can_proceed = valid_date
        
        if st.button("Next →", disabled=not can_proceed, use_container_width=True, type="primary"):
            st.session_state.onboarding_step = 4
            st.rerun()

# Step 4: Time Commitment
elif st.session_state.onboarding_step == 4:
    st.markdown("### ⏰ How much time can you dedicate?")
    
    st.info(f"🤖 AI: How many hours per day can you study?")
    
    st.markdown("---")
    
    hours = st.slider(
        "Hours per day:",
        min_value=1,
        max_value=16,
        value=st.session_state.hours_per_day,
        help="Be realistic! Quality over quantity."
    )
    
    # Validate hours
    valid_hours, warning = Validators.validate_hours_per_day(hours)
    if valid_hours and warning:
        st.warning(warning)
    
    st.session_state.hours_per_day = hours
    
    # Show realistic feedback
    if hours <= 2:
        st.info(f"💡 With {hours} hours/day, you'll make steady progress. Consistency is key!")
    elif hours <= 4:
        st.success(f"💡 With {hours} hours/day, you can make great progress!")
    elif hours <= 8:
        st.success(f"💪 With {hours} hours/day, you're committed to intensive learning!")
    else:
        st.warning(f"⚠️ {hours} hours/day is very intensive. Remember to take breaks!")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("← Back", use_container_width=True):
            st.session_state.onboarding_step = 3
            st.rerun()
    with col2:
        if st.button("🚀 Generate My Plan!", use_container_width=True, type="primary"):
            st.session_state.onboarding_step = 5
            st.rerun()

# Step 5: Summary & Plan Generation
elif st.session_state.onboarding_step == 5:
    st.markdown("### 🎉 Your Learning Plan is Ready!")
    
    with st.spinner("🤖 AI is creating your personalized study plan..."):
        # Save onboarding data
        try:
            OnboardingManager.save_onboarding_data(
                user_id=user_id,
                topics=st.session_state.topics,
                levels=st.session_state.levels,
                target_date=st.session_state.target_date,
                hours=st.session_state.hours_per_day
            )
            
            # Generate study plan
            PlanGenerator.generate_full_plan(user_id)
            
            # Get AI summary
            user = st.session_state.get('username', 'Student')
            summary = OnboardingManager.create_summary(
                name=user,
                topics=st.session_state.topics,
                levels=st.session_state.levels,
                hours=st.session_state.hours_per_day,
                target_date=str(st.session_state.target_date) if st.session_state.target_date else "Self-paced"
            )
        except Exception as e:
            st.error(f"Error generating plan: {str(e)}")
            if st.button("← Try Again"):
                st.session_state.onboarding_step = 1
                st.rerun()
            st.stop()
    
    st.balloons()
    st.success("✅ Plan generated successfully!")
    
    st.markdown("---")
    
    st.info(f"🤖 AI: {summary}")
    
    st.markdown("---")
    
    # Summary
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**📚 Your Topics:**")
        for topic in st.session_state.topics:
            st.write(f"• {topic} ({st.session_state.levels[topic]})")
    
    with col2:
        st.markdown("**📊 Plan Details:**")
        st.write(f"• Hours/day: {st.session_state.hours_per_day}h")
        if st.session_state.target_date:
            days_left = (st.session_state.target_date - datetime.now().date()).days
            st.write(f"• Target: {st.session_state.target_date}")
            st.write(f"• Days: {days_left}")
        else:
            st.write(f"• Pace: Self-paced")
    
    st.markdown("---")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🏠 Go to Dashboard", use_container_width=True, type="primary"):
            # Clear onboarding state
            for key in ['onboarding_step', 'topics', 'levels', 'target_date', 'hours_per_day', 'ai_greeting']:
                if key in st.session_state:
                    del st.session_state[key]
            st.switch_page("pages/Dashboard.py")