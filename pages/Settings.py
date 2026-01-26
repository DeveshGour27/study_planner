import streamlit as st
from core.auth_manager import AuthManager
from database.models import User, StudentProfile, StudyPlan, Quiz, ChatSession, UploadedResource
from database.db_manager import SessionLocal
from datetime import datetime
from styles.design_system import DesignSystem as DS
from styles.components import UIComponents

st.set_page_config(page_title="Settings", page_icon="⚙️", layout="wide")

# Inject CSS
UIComponents.render_custom_css()

# Get user
user_id = st.session_state.get('user_id')
if not user_id:
    st.error("Please login first")
    st.stop()

user = AuthManager.get_user_by_id(user_id)
profile = AuthManager.get_user_profile(user_id)

if not user or not profile:
    st.error("User not found!")
    st.stop()

# Header
st.markdown(f"""
<div style="text-align: center; margin-bottom: {DS.SPACE_8};">
    <h1 style="color: {DS.PRIMARY};">⚙️ Settings</h1>
    <p style="color: {DS.TEXT_SECONDARY}; font-size: {DS.FONT_SIZE_LG};">
        Manage your account and preferences
    </p>
</div>
""", unsafe_allow_html=True)

# Tabs
tab1, tab2, tab3, tab4 = st.tabs(["👤 Profile", "📚 Study Preferences", "🔒 Security", "⚠️ Danger Zone"])

# ==================== TAB 1: PROFILE ====================
with tab1:
    st.markdown(f"""
    <div class="modern-card">
        <h2 style="color: {DS.PRIMARY};">👤 Profile Information</h2>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown(f"<div style='margin: {DS.SPACE_6} 0;'></div>", unsafe_allow_html=True)
    
    with st.form("profile_form"):
        st.markdown(f"<h3 style='color: {DS.PRIMARY};'>Basic Information</h3>", unsafe_allow_html=True)
        
        new_name = st.text_input("Full Name", value=user.full_name)
        new_email = st.text_input("Email", value=user.email)
        new_username = st.text_input("Username", value=user.username, disabled=True, help="Username cannot be changed")
        
        st.markdown(f"<h3 style='color: {DS.PRIMARY}; margin-top: {DS.SPACE_6};'>Study Information</h3>", unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            UIComponents.stat_card("Current Day", profile.current_day_number, "📅")
        
        with col2:
            UIComponents.stat_card("Streak", f"{profile.streak_count} days", "🔥")
        
        submit_profile = st.form_submit_button("💾 Save Profile", use_container_width=True, type="primary")
        
        if submit_profile:
            db = SessionLocal()
            try:
                db_user = db.query(User).filter(User.user_id == user_id).first()
                
                if db_user:
                    db_user.full_name = new_name
                    db_user.email = new_email
                    db.commit()
                    
                    st.success("✅ Profile updated successfully!")
                    st.rerun()
                else:
                    st.error("User not found")
            except Exception as e:
                db.rollback()
                st.error(f"Error updating profile: {e}")
            finally:
                db.close()
    
    st.markdown("---")
    
    # Display stats
    st.markdown(f"<h3 style='color: {DS.PRIMARY};'>📊 Your Statistics</h3>", unsafe_allow_html=True)
    
    db = SessionLocal()
    try:
        total_plans = db.query(StudyPlan).filter(StudyPlan.user_id == user_id).count()
        completed_plans = db.query(StudyPlan).filter(StudyPlan.user_id == user_id, StudyPlan.status == 'completed').count()
        total_quizzes = db.query(Quiz).filter(Quiz.user_id == user_id, Quiz.status == 'completed').count()
        total_pdfs = db.query(UploadedResource).filter(UploadedResource.user_id == user_id).count()
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            UIComponents.stat_card("Study Plans", total_plans, "📚")
        
        with col2:
            UIComponents.stat_card("Completed", completed_plans, "✅")
        
        with col3:
            UIComponents.stat_card("Quizzes Taken", total_quizzes, "📝")
        
        with col4:
            UIComponents.stat_card("PDFs Uploaded", total_pdfs, "📄")
            
    finally:
        db.close()

# ==================== TAB 2: STUDY PREFERENCES ====================
with tab2:
    st.markdown(f"""
    <div class="modern-card">
        <h2 style="color: {DS.PRIMARY};">📚 Study Preferences</h2>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown(f"<div style='margin: {DS.SPACE_6} 0;'></div>", unsafe_allow_html=True)
    
    with st.form("preferences_form"):
        st.markdown(f"<h3 style='color: {DS.PRIMARY};'>Learning Settings</h3>", unsafe_allow_html=True)
        
        new_hours = st.slider(
            "Hours Available Per Day",
            min_value=1,
            max_value=12,
            value=profile.hours_per_day
        )
        
        # Topics management
        st.markdown(f"<h3 style='color: {DS.PRIMARY}; margin-top: {DS.SPACE_6};'>Your Topics</h3>", unsafe_allow_html=True)
        
        current_topics = profile.topics_to_learn if profile.topics_to_learn else []
        
        if current_topics:
            st.info(f"Current topics: {', '.join(current_topics)}")
        
        new_topic = st.text_input("Add New Topic", placeholder="e.g., Machine Learning")
        
        if current_topics:
            topics_to_remove = st.multiselect("Remove Topics", current_topics)
        else:
            topics_to_remove = []
        
        st.markdown(f"<h3 style='color: {DS.PRIMARY}; margin-top: {DS.SPACE_6};'>Timeline</h3>", unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            UIComponents.stat_card("Days Remaining", profile.days_remaining if profile.days_remaining else "Self-paced", "📅")
        
        with col2:
            UIComponents.stat_card("Total Planned Days", profile.total_planned_days, "📆")
        
        submit_prefs = st.form_submit_button("💾 Save Preferences", use_container_width=True, type="primary")
        
        if submit_prefs:
            db = SessionLocal()
            try:
                db_profile = db.query(StudentProfile).filter(StudentProfile.user_id == user_id).first()
                
                if db_profile:
                    db_profile.hours_per_day = new_hours
                    
                    updated_topics = [t for t in current_topics if t not in topics_to_remove]
                    if new_topic and new_topic.strip():
                        updated_topics.append(new_topic.strip())
                    
                    db_profile.topics_to_learn = updated_topics
                    
                    db.commit()
                    
                    st.success("✅ Preferences updated successfully!")
                    st.balloons()
                    st.rerun()
                else:
                    st.error("Profile not found")
            except Exception as e:
                db.rollback()
                st.error(f"Error updating preferences: {e}")
            finally:
                db.close()
    
    st.markdown("---")
    
    # Current levels
    st.markdown(f"<h3 style='color: {DS.PRIMARY};'>📈 Topic Levels</h3>", unsafe_allow_html=True)
    
    if profile.current_levels:
        for topic, level in profile.current_levels.items():
            progress_val = 0.33 if level == 'beginner' else 0.66 if level == 'intermediate' else 1.0
            color = DS.ACCENT_WARNING if level == 'beginner' else DS.PRIMARY if level == 'intermediate' else DS.ACCENT
            
            st.markdown(f"""
            <div style="margin-bottom: {DS.SPACE_4};">
                <div style="display: flex; justify-content: space-between; margin-bottom: {DS.SPACE_2};">
                    <span style="color: {DS.TEXT_PRIMARY}; font-weight: 600;">{topic}</span>
                    <span style="color: {color}; font-weight: 600;">{level.title()}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            st.progress(progress_val)
    else:
        st.info("No topic levels set yet")

# ==================== TAB 3: SECURITY ====================
with tab3:
    st.markdown(f"""
    <div class="modern-card">
        <h2 style="color: {DS.PRIMARY};">🔒 Security Settings</h2>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown(f"<div style='margin: {DS.SPACE_6} 0;'></div>", unsafe_allow_html=True)
    
    st.markdown(f"<h3 style='color: {DS.PRIMARY};'>Change Password</h3>", unsafe_allow_html=True)
    
    with st.form("password_form"):
        current_password = st.text_input("Current Password", type="password")
        new_password = st.text_input("New Password", type="password")
        confirm_password = st.text_input("Confirm New Password", type="password")
        
        submit_password = st.form_submit_button("🔐 Change Password", use_container_width=True, type="primary")
        
        if submit_password:
            if not current_password or not new_password or not confirm_password:
                st.error("All fields are required")
            elif new_password != confirm_password:
                st.error("New passwords don't match")
            elif len(new_password) < 6:
                st.error("Password must be at least 6 characters")
            else:
                if AuthManager.verify_credentials(user.username, current_password):
                    db = SessionLocal()
                    try:
                        import bcrypt
                        
                        db_user = db.query(User).filter(User.user_id == user_id).first()
                        
                        if db_user:
                            hashed = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
                            db_user.password_hash = hashed.decode('utf-8')
                            
                            db.commit()
                            
                            st.success("✅ Password changed successfully!")
                        else:
                            st.error("User not found")
                    except Exception as e:
                        db.rollback()
                        st.error(f"Error changing password: {e}")
                    finally:
                        db.close()
                else:
                    st.error("Current password is incorrect")
    
    st.markdown("---")
    
    # Account info
    st.markdown(f"<h3 style='color: {DS.PRIMARY};'>📋 Account Information</h3>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"""
        <div class="glass-card">
            <strong style="color: {DS.PRIMARY};">Account Created</strong>
            <p style="color: {DS.TEXT_SECONDARY}; margin-top: {DS.SPACE_2};">
                {user.created_at.strftime('%B %d, %Y')}
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        last_active_text = profile.last_active_date.strftime('%B %d, %Y') if profile.last_active_date else "Today"
        st.markdown(f"""
        <div class="glass-card">
            <strong style="color: {DS.PRIMARY};">Last Active</strong>
            <p style="color: {DS.TEXT_SECONDARY}; margin-top: {DS.SPACE_2};">
                {last_active_text}
            </p>
        </div>
        """, unsafe_allow_html=True)

# ==================== TAB 4: DANGER ZONE ====================
with tab4:
    st.markdown(f"""
    <div style="background: {DS.ACCENT_ERROR}20; padding: {DS.SPACE_6}; border-radius: {DS.RADIUS_XL}; 
                border: 2px solid {DS.ACCENT_ERROR};">
        <h2 style="color: {DS.ACCENT_ERROR};">⚠️ Danger Zone</h2>
        <p style="color: {DS.TEXT_PRIMARY};">
            These actions are irreversible. Please be careful!
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown(f"<div style='margin: {DS.SPACE_8} 0;'></div>", unsafe_allow_html=True)
    
    # Reset Progress
    st.markdown(f"<h3 style='color: {DS.ACCENT_WARNING};'>🔄 Reset Progress</h3>", unsafe_allow_html=True)
    st.markdown("This will reset your day counter, streak, and mark all plans as pending. Your data will NOT be deleted.")
    
    with st.form("reset_progress_form"):
        st.warning("⚠️ Are you sure you want to reset your progress?")
        
        submit_reset = st.form_submit_button("🔄 Reset My Progress", use_container_width=True, type="primary")
        
        if submit_reset:
            db = SessionLocal()
            try:
                db_profile = db.query(StudentProfile).filter(StudentProfile.user_id == user_id).first()
                
                if db_profile:
                    db_profile.current_day_number = 1
                    db_profile.streak_count = 0
                    
                    plans = db.query(StudyPlan).filter(StudyPlan.user_id == user_id).all()
                    for plan in plans:
                        plan.status = 'pending'
                        plan.completed_at = None
                    
                    db.commit()
                    
                    st.success("✅ Progress reset successfully!")
                    st.balloons()
                    st.rerun()
            except Exception as e:
                db.rollback()
                st.error(f"Error resetting progress: {e}")
            finally:
                db.close()
    
    st.markdown("---")
    
    # Delete All Data
    st.markdown(f"<h3 style='color: {DS.ACCENT_ERROR};'>🗑️ Delete All Data</h3>", unsafe_allow_html=True)
    st.markdown("This will delete all your study plans, quizzes, and uploaded PDFs. Your account will remain active.")
    
    with st.form("delete_data_form"):
        st.error("⚠️ This will DELETE all your data permanently!")
        
        confirm_text = st.text_input("Type 'DELETE DATA' to confirm")
        
        submit_delete_data = st.form_submit_button("🗑️ Delete All My Data", use_container_width=True, type="primary")
        
        if submit_delete_data:
            if confirm_text == "DELETE DATA":
                db = SessionLocal()
                try:
                    # Delete all data
                    db.query(StudyPlan).filter(StudyPlan.user_id == user_id).delete()
                    db.query(Quiz).filter(Quiz.user_id == user_id).delete()
                    db.query(ChatSession).filter(ChatSession.user_id == user_id).delete()
                    
                    import os
                    resources = db.query(UploadedResource).filter(UploadedResource.user_id == user_id).all()
                    for resource in resources:
                        if os.path.exists(resource.file_path):
                            os.remove(resource.file_path)
                        embeddings_path = f"data/embeddings/{resource.resource_id}.pkl"
                        if os.path.exists(embeddings_path):
                            os.remove(embeddings_path)
                    
                    db.query(UploadedResource).filter(UploadedResource.user_id == user_id).delete()
                    
                    db_profile = db.query(StudentProfile).filter(StudentProfile.user_id == user_id).first()
                    if db_profile:
                        db_profile.onboarding_completed = False
                        db_profile.current_day_number = 1
                        db_profile.streak_count = 0
                    
                    db.commit()
                    
                    st.success("✅ All data deleted successfully!")
                    st.info("Please complete onboarding again to continue.")
                    st.rerun()
                    
                except Exception as e:
                    db.rollback()
                    st.error(f"Error deleting data: {e}")
                finally:
                    db.close()
            else:
                st.error("Please type 'DELETE DATA' to confirm")
    
    st.markdown("---")
    
    # Delete Account
    st.markdown(f"<h3 style='color: {DS.ACCENT_ERROR};'>💀 Delete Account</h3>", unsafe_allow_html=True)
    st.markdown("This will **permanently delete** your account and all associated data. This action **cannot be undone**!")
    
    with st.form("delete_account_form"):
        st.error("🚨 FINAL WARNING: This will permanently delete your account!")
        
        verification = st.text_input("Type 'DELETE ACCOUNT' to confirm")
        
        submit_delete_account = st.form_submit_button("💀 Delete My Account Forever", use_container_width=True, type="primary")
        
        if submit_delete_account:
            if verification == "DELETE ACCOUNT":
                db = SessionLocal()
                try:
                    # Delete everything
                    db.query(StudyPlan).filter(StudyPlan.user_id == user_id).delete()
                    db.query(Quiz).filter(Quiz.user_id == user_id).delete()
                    db.query(ChatSession).filter(ChatSession.user_id == user_id).delete()
                    
                    import os
                    resources = db.query(UploadedResource).filter(UploadedResource.user_id == user_id).all()
                    for resource in resources:
                        if os.path.exists(resource.file_path):
                            os.remove(resource.file_path)
                        embeddings_path = f"data/embeddings/{resource.resource_id}.pkl"
                        if os.path.exists(embeddings_path):
                            os.remove(embeddings_path)
                    
                    db.query(UploadedResource).filter(UploadedResource.user_id == user_id).delete()
                    db.query(StudentProfile).filter(StudentProfile.user_id == user_id).delete()
                    db.query(User).filter(User.user_id == user_id).delete()
                    
                    db.commit()
                    
                    # Logout
                    st.session_state.authenticated = False
                    st.session_state.user_id = None
                    st.session_state.username = None
                    
                    st.success("Account deleted. Goodbye! 👋")
                    st.balloons()
                    st.stop()
                    
                except Exception as e:
                    db.rollback()
                    st.error(f"Error deleting account: {e}")
                finally:
                    db.close()
            else:
                st.error("Please type 'DELETE ACCOUNT' to confirm")