import streamlit as st
from core.auth_manager import AuthManager
from utils import Validators
from styles.design_system import DesignSystem as DS
from styles.components import UIComponents

st.set_page_config(page_title="Sign Up", page_icon="✨", layout="centered")

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
        ✨ Create Your Account
    </h1>
    <p style="color: {DS.TEXT_SECONDARY}; font-size: {DS.FONT_SIZE_LG};">
        Start your personalized learning journey today!
    </p>
</div>
""", unsafe_allow_html=True)

# Signup Card
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.markdown(f"""
    <div class="modern-card">
    """, unsafe_allow_html=True)
    
    with st.form("signup_form"):
        st.markdown(f"<h3 style='color: {DS.PRIMARY}; margin-bottom: {DS.SPACE_4};'>👤 Your Information</h3>", unsafe_allow_html=True)
        
        full_name = st.text_input(
            "Full Name *",
            placeholder="John Doe",
            help="Your full name (letters and spaces only)",
            max_chars=100
        )
        
        st.markdown(f"<h3 style='color: {DS.PRIMARY}; margin-top: {DS.SPACE_6}; margin-bottom: {DS.SPACE_4};'>🔐 Account Credentials</h3>", unsafe_allow_html=True)
        
        username = st.text_input(
            "Username *",
            placeholder="johndoe123",
            help="3-50 characters: letters, numbers, underscore, and hyphen only",
            max_chars=50
        )
        
        email = st.text_input(
            "Email Address *",
            placeholder="john@example.com",
            help="Valid email address",
            max_chars=255
        )
        
        col_a, col_b = st.columns(2)
        
        with col_a:
            password = st.text_input(
                "Password *",
                type="password",
                placeholder="Min 6 characters",
                help="Minimum 6 characters",
                max_chars=128
            )
        
        with col_b:
            confirm_password = st.text_input(
                "Confirm Password *",
                type="password",
                placeholder="Re-enter password",
                max_chars=128
            )
        
        st.markdown("---")
        st.caption("* Required fields")
        
        submit = st.form_submit_button("🚀 Create Account", use_container_width=True, type="primary")
        
        if submit:
            # Collect all validation errors
            errors = []
            
            # Validate full name
            if not full_name or not full_name.strip():
                errors.append("Full name is required")
            else:
                valid_name, name_error = Validators.validate_full_name(full_name.strip())
                if not valid_name:
                    errors.append(name_error)
            
            # Validate username
            if not username or not username.strip():
                errors.append("Username is required")
            else:
                valid_username, username_error = Validators.validate_username(username.strip())
                if not valid_username:
                    errors.append(username_error)
            
            # Validate email
            if not email or not email.strip():
                errors.append("Email is required")
            else:
                valid_email, email_error = Validators.validate_email(email.strip())
                if not valid_email:
                    errors.append(email_error)
            
            # Validate password
            if not password:
                errors.append("Password is required")
            else:
                valid_password, password_error = Validators.validate_password(password)
                if not valid_password:
                    errors.append(password_error)
            
            # Check password match
            if password and confirm_password:
                if password != confirm_password:
                    errors.append("Passwords do not match")
            elif not confirm_password:
                errors.append("Please confirm your password")
            
            # Show all errors or proceed
            if errors:
                st.markdown("### ❌ Please fix the following errors:")
                for error in errors:
                    st.error(f"• {error}")
            else:
                # All validation passed - register user
                with st.spinner("Creating your account..."):
                    success, message, user_id = AuthManager.register_user(
                        username=username.strip().lower(),
                        email=email.strip().lower(),
                        password=password,
                        full_name=full_name.strip()
                    )
                
                if success:
                    st.balloons()
                    st.success(message)
                    st.success("🎉 Account created successfully!")
                    st.info("✨ Please login to start your learning journey")
                    
                    # Auto-redirect after 2 seconds
                    import time
                    time.sleep(2)
                    st.switch_page("pages/Login.py")
                else:
                    st.error(message)
    
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Login link
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.markdown(f"""
    <div style="text-align: center; padding: {DS.SPACE_4}; 
                background: {DS.SURFACE}; border-radius: {DS.RADIUS_LG}; 
                border: 1px solid {DS.BORDER};">
        <p style="color: {DS.TEXT_SECONDARY}; margin-bottom: {DS.SPACE_3};">
            Already have an account?
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    if st.button("🔐 Login Here", use_container_width=True):
        st.switch_page("pages/Login.py")

# Features section
st.markdown("<br><br>", unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

with col1:
    UIComponents.glass_card(
        "Personalized Plans",
        "AI-generated study schedules tailored to you",
        "🎯"
    )

with col2:
    UIComponents.glass_card(
        "Track Progress",
        "Monitor your learning with detailed analytics",
        "📊"
    )

with col3:
    UIComponents.glass_card(
        "AI Assistant",
        "24/7 study companion for instant help",
        "🤖"
    )