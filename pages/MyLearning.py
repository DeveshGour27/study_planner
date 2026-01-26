import streamlit as st
from core.auth_manager import AuthManager
from core.pdf_processor import PDFProcessor
from llm.rag_engine import rag_engine
from database.models import StudyPlan
from database.db_manager import SessionLocal
from utils import Validators
from styles.design_system import DesignSystem as DS
from styles.components import UIComponents

st.set_page_config(page_title="My Learning", page_icon="📚", layout="wide")

# Inject CSS
UIComponents.render_custom_css()

# Get user
user_id = st.session_state.get('user_id')
if not user_id:
    st.error("Please login first")
    st.stop()

profile = AuthManager.get_user_profile(user_id)

if not profile or not profile.onboarding_completed:
    st.warning("Please complete onboarding first!")
    st.stop()

# Header
st.markdown(f"""
<div style="text-align: center; margin-bottom: {DS.SPACE_8};">
    <h1 style="color: {DS.PRIMARY};">📚 My Learning Resources</h1>
    <p style="color: {DS.TEXT_SECONDARY}; font-size: {DS.FONT_SIZE_LG};">
        Manage your study materials and track your learning journey
    </p>
</div>
""", unsafe_allow_html=True)

# Tabs
tab1, tab2, tab3 = st.tabs(["📖 Learning Path", "📄 My Documents", "➕ Upload Material"])

# ==================== TAB 1: LEARNING PATH ====================
with tab1:
    st.markdown(f"""
    <div class="modern-card">
        <h2 style="color: {DS.PRIMARY};">🎯 Your Learning Journey</h2>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown(f"<div style='margin: {DS.SPACE_6} 0;'></div>", unsafe_allow_html=True)
    
    # Show topics
    if profile.topics_to_learn:
        st.markdown(f"<h3 style='color: {DS.PRIMARY};'>Topics You're Learning</h3>", unsafe_allow_html=True)
        
        for topic in profile.topics_to_learn:
            level = profile.current_levels.get(topic, 'beginner') if profile.current_levels else 'beginner'
            level_color = DS.ACCENT if level == 'advanced' else DS.PRIMARY if level == 'intermediate' else DS.ACCENT_WARNING
            
            st.markdown(f"""
            <div style="background: {DS.SURFACE}; padding: {DS.SPACE_4}; border-radius: {DS.RADIUS_MD}; 
                        margin-bottom: {DS.SPACE_3}; border-left: 4px solid {level_color};">
                <strong style="color: {DS.TEXT_PRIMARY};">{topic}</strong>
                <span style="color: {DS.TEXT_MUTED}; margin-left: {DS.SPACE_3};">
                    {level.title()}
                </span>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown(f"<div style='margin: {DS.SPACE_6} 0;'></div>", unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Study plan progress
    st.markdown(f"<h3 style='color: {DS.PRIMARY};'>📅 Study Plan Progress</h3>", unsafe_allow_html=True)
    
    db = SessionLocal()
    try:
        all_plans = db.query(StudyPlan).filter(
            StudyPlan.user_id == user_id
        ).order_by(StudyPlan.day_number).all()
        
        if all_plans:
            # Group by status
            completed = [p for p in all_plans if p.status == 'completed']
            in_progress = [p for p in all_plans if p.status == 'in_progress']
            pending = [p for p in all_plans if p.status == 'pending']
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                UIComponents.stat_card("Completed", len(completed), "✅")
            with col2:
                UIComponents.stat_card("In Progress", len(in_progress), "🔄")
            with col3:
                UIComponents.stat_card("Pending", len(pending), "⏳")
            
            st.markdown(f"<div style='margin: {DS.SPACE_8} 0;'></div>", unsafe_allow_html=True)
            
            # Show completed topics
            if completed:
                st.markdown(f"<h3 style='color: {DS.ACCENT};'>✅ Completed Topics</h3>", unsafe_allow_html=True)
                
                for plan in completed[-5:]:  # Show last 5
                    completion_date = plan.completed_at.strftime("%b %d, %Y") if plan.completed_at else "N/A"
                    st.markdown(f"""
                    <div style="background: {DS.SURFACE}; padding: {DS.SPACE_4}; border-radius: {DS.RADIUS_MD}; 
                                margin-bottom: {DS.SPACE_3}; border-left: 4px solid {DS.ACCENT};">
                        <strong style="color: {DS.TEXT_PRIMARY};">✅ {plan.topic}</strong>
                        <span style="color: {DS.TEXT_MUTED}; margin-left: {DS.SPACE_3};">
                            Day {plan.day_number} • {completion_date}
                        </span>
                    </div>
                    """, unsafe_allow_html=True)
            
            # Show current topic
            if in_progress:
                st.markdown(f"<h3 style='color: {DS.PRIMARY};'>🔄 Currently Learning</h3>", unsafe_allow_html=True)
                for plan in in_progress:
                    st.markdown(f"""
                    <div style="background: {DS.SURFACE}; padding: {DS.SPACE_4}; border-radius: {DS.RADIUS_MD}; 
                                margin-bottom: {DS.SPACE_3}; border-left: 4px solid {DS.PRIMARY};">
                        <strong style="color: {DS.TEXT_PRIMARY};">🔄 {plan.topic}</strong>
                        <span style="color: {DS.TEXT_MUTED}; margin-left: {DS.SPACE_3};">
                            Day {plan.day_number}
                        </span>
                    </div>
                    """, unsafe_allow_html=True)
            
            # Show upcoming
            if pending:
                st.markdown(f"<h3 style='color: {DS.ACCENT_WARNING};'>⏳ Coming Up Next</h3>", unsafe_allow_html=True)
                for plan in pending[:3]:  # Show next 3
                    st.markdown(f"""
                    <div style="background: {DS.SURFACE}; padding: {DS.SPACE_4}; border-radius: {DS.RADIUS_MD}; 
                                margin-bottom: {DS.SPACE_3}; border-left: 4px solid {DS.ACCENT_WARNING};">
                        <strong style="color: {DS.TEXT_PRIMARY};">⏳ {plan.topic}</strong>
                        <span style="color: {DS.TEXT_MUTED}; margin-left: {DS.SPACE_3};">
                            Day {plan.day_number}
                        </span>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            UIComponents.glass_card(
                "No Study Plan Yet",
                "Complete onboarding to generate your personalized plan!",
                "📚"
            )
    finally:
        db.close()

# ========== TAB 2: MY RESOURCES ==========
with tab2:
    st.markdown("### 📄 Uploaded Study Materials")
    
    pdfs = PDFProcessor.get_user_pdfs(user_id)
    
    if pdfs:
        st.info(f"📚 You have {len(pdfs)} uploaded document(s)")
        
        for pdf in pdfs:
            # Document card - SIMPLIFIED WITHOUT COMPLEX HTML
            st.markdown("---")
            
            col1, col2 = st.columns([4, 1])
            
            with col1:
                st.markdown(f"### 📄 {pdf.filename}")
                
                # Metadata in simple text (not HTML)
                metadata_parts = []
                if pdf.topic:
                    metadata_parts.append(f"📌 {pdf.topic}")
                metadata_parts.append(f"📅 {pdf.uploaded_at.strftime('%b %d, %Y')}")
                metadata_parts.append(f"📏 {len(pdf.extracted_text) if pdf.extracted_text else 0:,} characters")
                
                st.caption(" • ".join(metadata_parts))
                
                # Status
                if pdf.embeddings_generated:
                    st.success("✅ Processed - Available for AI search")
                else:
                    st.warning("⚠️ Not yet processed for AI search")
            
            with col2:
                # Action buttons
                if not pdf.embeddings_generated:
                    if st.button("🔄 Process", key=f"process_{pdf.resource_id}", use_container_width=True):
                        with st.spinner("Processing PDF..."):
                            success, message = rag_engine.generate_embeddings(pdf.resource_id)
                            if success:
                                st.success(message)
                                st.rerun()
                            else:
                                st.error(message)
                
                if st.button("🗑️ Delete", key=f"delete_{pdf.resource_id}", use_container_width=True, type="secondary"):
                    st.session_state[f'confirm_delete_{pdf.resource_id}'] = True
                    st.rerun()
            
            # Delete confirmation
            if st.session_state.get(f'confirm_delete_{pdf.resource_id}', False):
                st.warning("⚠️ Are you sure you want to delete this document?")
                col_a, col_b = st.columns(2)
                with col_a:
                    if st.button("✅ Yes, Delete", key=f"confirm_del_{pdf.resource_id}", type="primary", use_container_width=True):
                        success, message = PDFProcessor.delete_pdf(pdf.resource_id)
                        if success:
                            st.success(message)
                            del st.session_state[f'confirm_delete_{pdf.resource_id}']
                            st.rerun()
                        else:
                            st.error(message)
                with col_b:
                    if st.button("❌ Cancel", key=f"cancel_del_{pdf.resource_id}", use_container_width=True):
                        del st.session_state[f'confirm_delete_{pdf.resource_id}']
                        st.rerun()
            
            # Preview expander
            with st.expander("👁️ Preview"):
                if pdf.extracted_text:
                    preview = pdf.extracted_text[:1000] + "..." if len(pdf.extracted_text) > 1000 else pdf.extracted_text
                    st.text_area("Content Preview", preview, height=200, disabled=True, key=f"preview_{pdf.resource_id}", label_visibility="collapsed")
                else:
                    st.info("No text extracted")
    else:
        st.info("📭 No documents yet. Upload your study materials in the next tab!")
# ==================== TAB 3: UPLOAD MATERIAL ====================
with tab3:
    st.markdown(f"""
    <div class="modern-card">
        <h2 style="color: {DS.PRIMARY};">➕ Upload Study Material</h2>
        <p style="color: {DS.TEXT_SECONDARY};">Add PDFs of textbooks, notes, or any study material for AI-powered Q&A</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown(f"<div style='margin: {DS.SPACE_6} 0;'></div>", unsafe_allow_html=True)
    
    # Upload form
    with st.form("upload_form"):
        uploaded_file = st.file_uploader(
            "Choose a PDF file",
            type=['pdf'],
            help="Upload textbooks, notes, or any study material in PDF format (Max 50MB)"
        )
        
        topic = st.selectbox(
            "Related Topic (optional)",
            ["General"] + (profile.topics_to_learn if profile.topics_to_learn else [])
        )
        
        submit = st.form_submit_button("📤 Upload & Process", use_container_width=True, type="primary")
        
        if submit:
            if uploaded_file:
                # Validate file
                valid_file, file_error = Validators.validate_file_upload(
                    uploaded_file,
                    allowed_types=['pdf'],
                    max_size_mb=50
                )
                
                if not valid_file:
                    st.error(f"❌ {file_error}")
                else:
                    with st.spinner("📤 Uploading and processing PDF..."):
                        # Upload PDF
                        success, message, resource_id = PDFProcessor.upload_pdf(
                            user_id=user_id,
                            uploaded_file=uploaded_file,
                            topic=topic if topic != "General" else None
                        )
                        
                        if success:
                            st.success(message)
                            
                            # Generate embeddings
                            with st.spinner("🤖 Generating embeddings for AI search..."):
                                success_emb, message_emb = rag_engine.generate_embeddings(resource_id)
                                
                                if success_emb:
                                    st.success(message_emb)
                                    st.balloons()
                                    st.info("✨ Your PDF is now ready! Go to Chat and ask questions about it!")
                                    st.rerun()
                                else:
                                    st.warning(f"⚠️ PDF uploaded but embeddings failed: {message_emb}")
                        else:
                            st.error(message)
            else:
                st.warning("⚠️ Please select a PDF file to upload")
    
    st.markdown("---")
    
    # Tips section
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"""
        <div class="glass-card">
            <h3 style="color: {DS.PRIMARY};">💡 Best Practices</h3>
            <ul style="color: {DS.TEXT_SECONDARY};">
                <li>Upload clear, text-based PDFs</li>
                <li>Keep files under 50MB</li>
                <li>Organize by topic for tracking</li>
                <li>Test AI search after upload</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="glass-card">
            <h3 style="color: {DS.PRIMARY};">💬 Ask AI Questions Like:</h3>
            <ul style="color: {DS.TEXT_SECONDARY};">
                <li>"What does my textbook say about recursion?"</li>
                <li>"Explain the concept from my notes"</li>
                <li>"Find information about algorithms"</li>
                <li>"Summarize my uploaded document"</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)