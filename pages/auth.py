import streamlit as st
from core.auth_manager import AuthManager
import re

# Custom CSS for auth page
st.markdown("""
<style>
    /* Auth page specific styles */
    .auth-container {
        max-width: 500px;
        margin: 0 auto;
        padding: 2rem;
    }
    
    .auth-header {
        font-size: 3rem;
        font-weight:  bold;
        text-align: center;
        background: linear-gradient(120deg, #1f77b4, #2ca02c);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 1rem;
    }
    
    .auth-subheader {
        font-size: 1.2rem;
        text-align:  center;
        color: #666;
        margin-bottom: 2rem;
    }
    
    /* Make form buttons more prominent */
    .stForm button[type="submit"] {
        background: linear-gradient(120deg, #1f77b4, #2ca02c) !important;
        color: white !important;
        border: none !important;
        padding: 0.75rem 2rem !important;
        font-size: 1.1rem ! important;
        font-weight: bold !important;
        border-radius: 10px !important;
        width: 100% !important;
        margin-top: 1rem !important;
        transition: transform 0.2s ! important;
    }
    
    .stForm button[type="submit"]:hover {
        transform: scale(1.05) !important;
        box-shadow: 0 5px 15px rgba(31, 119, 180, 0.3) !important;
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
        justify-content: center;
    }
    
    .stTabs [data-baseweb="tab"] {
        font-size: 1.2rem;
        font-weight:  600;
        padding: 1rem 2rem;
        border-radius: 10px 10px 0 0;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #1f77b4 !important;
        color: white !important;
    }
    
    /* Input field styling */
    .stTextInput input {
        border-radius: 8px ! important;
        border: 2px solid #e0e0e0 !important;
        padding: 0.75rem ! important;
        font-size:  1rem !important;
    }
    
    .stTextInput input:focus {
        border-color: #1f77b4 !important;
        box-shadow: 0 0 0 0.2rem rgba(31, 119, 180, 0.25) !important;
    }
    
    /* Footer styling */
    .auth-footer {
        text-align: center;
        margin-top: 3rem;
        padding: 1rem;
        color: #888;
        border-top: 1px solid #e0e0e0;
    }
    
    /* Feature cards */
    .feature-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        margin:  0.5rem 0;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<div class="auth-header">🎓 Adaptive Study Planner</div>', unsafe_allow_html=True)
st.markdown('<div class="auth-subheader">Your AI-Powered Learning Companion</div>', unsafe_allow_html=True)

# Feature highlights
col1, col2, col3 = st.columns(3)
with col1:
    st. markdown("""
    <div class="feature-card">
        <h3>🤖 AI-Powered</h3>
        <p>Smart study plans</p>
    </div>
    """, unsafe_allow_html=True)
with col2:
    st. markdown("""
    <div class="feature-card">
        <h3>📊 Adaptive</h3>
        <p>Learns your pace</p>
    </div>
    """, unsafe_allow_html=True)
with col3:
    st.markdown("""
    <div class="feature-card">
        <h3>🎯 Personalized</h3>
        <p>Just for you</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Tabs for Login and Signup
tab1, tab2 = st. tabs(["🔑 Login", "✨ Sign Up"])

# Helper function for email validation
def is_valid_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

# ========== LOGIN TAB ==========
with tab1:
    st.markdown("### Welcome Back!  👋")
    st.markdown("Login to continue your learning journey")
    st.markdown("<br>", unsafe_allow_html=True)
    
    with st.form("login_form", clear_on_submit=False):
        login_username = st.text_input("📧 Username or Email", placeholder="Enter your username or email")
        login_password = st.text_input("🔒 Password", type="password", placeholder="Enter your password")
        
        col1, col2 = st. columns([3, 1])
        with col1:
            login_submit = st.form_submit_button("🚀 Login", use_container_width=True)
        
        if login_submit:
            if not login_username or not login_password: 
                st.error("⚠️ Please fill in all fields")
            else:
                with st.spinner("Logging in... "):
                    success, message, token, user = AuthManager.login_user(login_username, login_password)
                    
                    if success:
                        st. session_state.authenticated = True
                        st.session_state. user_id = user. user_id
                        st.session_state.username = user.username
                        st.session_state.token = token
                        st.success(f"✅ {message}")
                        st.balloons()
                        st.rerun()
                    else: 
                        st.error(f"❌ {message}")

# ========== SIGNUP TAB ==========
with tab2:
    st.markdown("### Create Your Account ✨")
    st.markdown("Start your personalized learning journey today!")
    st.markdown("<br>", unsafe_allow_html=True)
    
    with st.form("signup_form", clear_on_submit=False):
        signup_fullname = st.text_input("👤 Full Name", placeholder="John Doe")
        signup_username = st.text_input("🏷️ Username", placeholder="johndoe123")
        signup_email = st.text_input("📧 Email", placeholder="john@example.com")
        
        col1, col2 = st.columns(2)
        with col1:
            signup_password = st.text_input("🔒 Password", type="password", placeholder="Min.  6 characters")
        with col2:
            signup_password_confirm = st.text_input("🔒 Confirm Password", type="password", placeholder="Re-enter password")
        
        signup_age_group = st.selectbox(
            "🎓 I am a.. .",
            ["School Student", "College Student", "Professional", "Other"]
        )
        
        signup_submit = st.form_submit_button("✨ Create Account", use_container_width=True)
        
        if signup_submit:
            # Validation
            errors = []
            
            if not all([signup_fullname, signup_username, signup_email, signup_password, signup_password_confirm]):
                errors.append("Please fill in all fields")
            
            if signup_email and not is_valid_email(signup_email):
                errors.append("Please enter a valid email address")
            
            if signup_username and len(signup_username) < 3:
                errors.append("Username must be at least 3 characters")
            
            if signup_password and len(signup_password) < 6:
                errors.append("Password must be at least 6 characters")
            
            if signup_password != signup_password_confirm:
                errors.append("Passwords do not match")
            
            if errors:
                for error in errors:
                    st.error(f"⚠️ {error}")
            else:
                with st.spinner("Creating your account..."):
                    age_group_map = {
                        "School Student": "school",
                        "College Student":  "college",
                        "Professional": "professional",
                        "Other": "other"
                    }
                    
                    success, message, user_id = AuthManager.register_user(
                        username=signup_username,
                        email=signup_email,
                        password=signup_password,
                        full_name=signup_fullname,
                        age_group=age_group_map[signup_age_group]
                    )
                    
                    if success:
                        st.success(f"✅ {message}")
                        st.info("👉 Please switch to the Login tab to sign in")
                        st.balloons()
                    else:
                        st.error(f"❌ {message}")

# Footer
st.markdown("---")
st.markdown("""
<div class="auth-footer">
    <p><strong>Why Choose Adaptive Study Planner? </strong></p>
    <p>✨ AI-powered personalization • 📊 Real-time progress tracking • 🎯 Adaptive learning paths</p>
    <p>🔒 100% Free • 🌍 Learn at your own pace • 🏆 Achieve your goals</p>
    <p style='margin-top: 1rem; font-size: 0.9rem; color: #aaa;'>Made with ❤️ for learners worldwide</p>
</div>
""", unsafe_allow_html=True)