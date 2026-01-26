import streamlit as st
from core.auth_manager import AuthManager
from styles.design_system import DesignSystem as DS
from styles.components import UIComponents
from utils import UIHelpers
st.set_page_config(page_title="Login", page_icon="🔐", layout="centered")

# Inject CSS
UIComponents.render_custom_css()

# Check if already logged in
if 'user_id' in st.session_state:
    st.success("✅ You're already logged in!")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("Go to Dashboard", use_container_width=True, type="primary"):
            st.switch_page("pages/Dashboard.py")
    st.stop()

# Header
st.markdown(f"""
<div style="text-align: center; margin-bottom: {DS.SPACE_10};">
    <h1 style="color: {DS.PRIMARY}; font-size: {DS.FONT_SIZE_4XL}; margin-bottom: {DS.SPACE_2};">
        🔐 Welcome Back!
    </h1>
    <p style="color: {DS.TEXT_SECONDARY}; font-size: {DS.FONT_SIZE_LG};">
        Login to continue your learning journey
    </p>
</div>
""", unsafe_allow_html=True)

# Login Card
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.markdown(f"""
    <div class="modern-card">
    """, unsafe_allow_html=True)
    
    with st.form("login_form"):
        st.markdown(f"<h3 style='color: {DS.PRIMARY}; margin-bottom: {DS.SPACE_4};'>👤 Enter Your Credentials</h3>", unsafe_allow_html=True)
        
        username = st.text_input(
            "Username or Email",
            placeholder="Enter your username or email",
            help="The username or email you used to sign up"
        )
        
        password = st.text_input(
            "Password",
            type="password",
            placeholder="Enter your password",
            help="Your account password"
        )
        
        remember_me = st.checkbox("Remember me", value=True)
        
        submit = st.form_submit_button("🚀 Login", use_container_width=True, type="primary")
        
        if submit:
            if not username or not username.strip():
                st.error("❌ Please enter your username or email")
            elif not password:
                st.error("❌ Please enter your password")
            else:
                with st.spinner("🔐 Logging you in..."):
                    success, message, token, user = AuthManager.login_user(username.strip(), password)
                
                if success:
                    # Store in session
                    st.session_state['user_id'] = user.user_id
                    st.session_state['username'] = user.username
                    st.session_state['email'] = user.email
                    st.session_state['full_name'] = user.full_name
                    st.session_state['token'] = token
                    st.session_state['logged_in'] = True
                    
                    st.balloons()
                    st.success(f"✅ Welcome back, {user.username}!")
                    
                    # Check onboarding
                    profile = AuthManager.get_user_profile(user.user_id)
                    
                    if profile and profile.onboarding_completed:
                        st.success("Redirecting to Dashboard...")
                        import time
                        time.sleep(1)
                        st.switch_page("pages/Dashboard.py")
                    else:
                        st.info("Let's complete your onboarding first!")
                        import time
                        time.sleep(1)
                        st.switch_page("pages/onboarding.py")
                else:
                    st.error(f"❌ {message}")
    
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Signup link
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.markdown(f"""
    <div style="text-align: center; padding: {DS.SPACE_4}; 
                background: {DS.SURFACE}; border-radius: {DS.RADIUS_LG}; 
                border: 1px solid {DS.BORDER};">
        <p style="color: {DS.TEXT_SECONDARY}; margin-bottom: {DS.SPACE_3};">
            Don't have an account?
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    if st.button("✨ Create New Account", use_container_width=True):
        st.switch_page("pages/Signup.py")

# Features reminder
st.markdown("<br><br>", unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

with col1:
    UIComponents.glass_card(
        "AI-Powered",
        "Smart study plans adapted to you",
        "🤖"
    )

with col2:
    UIComponents.glass_card(
        "Track Progress",
        "Monitor your learning journey",
        "📊"
    )

with col3:
    UIComponents.glass_card(
        "Stay Motivated",
        "Streaks, achievements & more",
        "🔥"
    )