import streamlit as st
from styles.design_system import DesignSystem as DS
from styles.components import UIComponents

st.set_page_config(
    page_title="Adaptive Study Planner",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Inject custom CSS
UIComponents.render_custom_css()

# Check if user is logged in
if 'user_id' in st.session_state:
    from core.auth_manager import AuthManager
    
    profile = AuthManager.get_user_profile(st.session_state['user_id'])
    
    if profile and profile.onboarding_completed:
        st.switch_page("pages/Dashboard.py")
    else:
        st.switch_page("pages/onboarding.py")
else:
    # Modern Landing Page
    
    # Hero Section
    UIComponents.hero(
        "🎓 Adaptive Study Planner",
        "Your AI-Powered Learning Companion | Personalized Plans • Smart Quizzes • Progress Tracking"
    )
    
    # CTA Buttons
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        col_a, col_b = st.columns(2)
        with col_a:
            if st.button("🚀 Get Started Free", use_container_width=True, type="primary"):
                st.switch_page("pages/Signup.py")
        with col_b:
            if st.button("🔐 Login", use_container_width=True):
                st.switch_page("pages/Login.py")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Features Grid
    st.markdown(f"""
    <div style="text-align: center; margin: {DS.SPACE_12} 0;">
        <h2 style="color: {DS.PRIMARY};">✨ Why Choose Us?</h2>
        <p style="color: {DS.TEXT_SECONDARY};">Everything you need to master your learning goals</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        UIComponents.feature_card(
            "🎯",
            "Personalized Plans",
            "AI generates custom study schedules tailored to your goals, pace, and learning style"
        )
    
    with col2:
        UIComponents.feature_card(
            "🤖",
            "AI Assistant",
            "24/7 intelligent chat support for doubts, explanations, and motivation when you need it"
        )
    
    with col3:
        UIComponents.feature_card(
            "📝",
            "Smart Quizzes",
            "AI-powered assessments with instant feedback and detailed performance analysis"
        )
    
    with col4:
        UIComponents.feature_card(
            "📊",
            "Progress Tracking",
            "Comprehensive analytics, streaks, achievements, and insights into your learning journey"
        )
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    # How it Works
    st.markdown(f"""
    <div style="text-align: center; margin: {DS.SPACE_12} 0;">
        <h2 style="color: {DS.PRIMARY};">🚀 How It Works</h2>
        <p style="color: {DS.TEXT_SECONDARY};">Get started in 3 simple steps</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
        <div class="glass-card fade-in">
            <div style="font-size: 3rem; margin-bottom: 1rem;">1️⃣</div>
            <h3 style="color: {DS.PRIMARY};">Sign Up Free</h3>
            <p style="color: {DS.TEXT_SECONDARY};">Create your account in seconds. No credit card required.</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="glass-card fade-in">
            <div style="font-size: 3rem; margin-bottom: 1rem;">2️⃣</div>
            <h3 style="color: {DS.PRIMARY};">Set Your Goals</h3>
            <p style="color: {DS.TEXT_SECONDARY};">Tell us what you want to learn and your timeline. AI does the rest.</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="glass-card fade-in">
            <div style="font-size: 3rem; margin-bottom: 1rem;">3️⃣</div>
            <h3 style="color: {DS.PRIMARY};">Start Learning</h3>
            <p style="color: {DS.TEXT_SECONDARY};">Follow your personalized plan and track your amazing progress!</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    # Stats Section
    st.markdown(f"""
    <div style="text-align: center; padding: {DS.SPACE_12} {DS.SPACE_6}; 
                background: {DS.GRADIENT_PRIMARY}; border-radius: {DS.RADIUS_2XL}; 
                margin: {DS.SPACE_8} 0; box-shadow: {DS.SHADOW_2XL};">
        <h2 style="color: white; margin-bottom: {DS.SPACE_6};">Join Thousands of Learners</h2>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        UIComponents.stat_card("Active Users", "10,000+", "👥")
    
    with col2:
        UIComponents.stat_card("Study Plans", "50,000+", "📚")
    
    with col3:
        UIComponents.stat_card("Quizzes Taken", "100,000+", "📝")
    
    with col4:
        UIComponents.stat_card("Avg Success Rate", "87%", "🏆")
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    # Final CTA
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown(f"""
        <div style="text-align: center; padding: {DS.SPACE_10}; 
                    background: {DS.GRADIENT_CARD}; border-radius: {DS.RADIUS_2XL}; 
                    border: 1px solid {DS.BORDER};">
            <h2 style="color: {DS.PRIMARY};">Ready to Transform Your Learning?</h2>
            <p style="color: {DS.TEXT_SECONDARY}; margin: {DS.SPACE_4} 0;">
                Join thousands of students achieving their goals with AI-powered personalization
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        if st.button("🎓 Start Learning Today - It's Free!", use_container_width=True, type="primary", key="cta_bottom"):
            st.switch_page("pages/Signup.py")
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    # Footer
    st.markdown(f"""
    <div style="text-align: center; padding: {DS.SPACE_8} {DS.SPACE_4}; 
                color: {DS.TEXT_MUTED}; border-top: 1px solid {DS.BORDER};">
        <p><strong>✨ 100% Free</strong> • <strong>🔒 Privacy First</strong> • <strong>🌍 Learn Anywhere</strong></p>
        <p style="margin-top: {DS.SPACE_4};">Made with ❤️ for learners worldwide | © 2024 Adaptive Study Planner</p>
    </div>
    """, unsafe_allow_html=True)