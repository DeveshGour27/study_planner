import streamlit as st
from core.chat_engine import ChatEngine
from core.auth_manager import AuthManager
from datetime import datetime
from styles.design_system import DesignSystem as DS
from styles.components import UIComponents

st.set_page_config(page_title="Chat", page_icon="💬", layout="wide")

# Inject CSS
UIComponents.render_custom_css()

# Check authentication
if 'user_id' not in st.session_state:
    st.warning("⚠️ Please login first")
    st.stop()

user_id = st.session_state['user_id']

# Initialize session state
if 'current_chat_session_id' not in st.session_state:
    st.session_state.current_chat_session_id = None
if 'chat_view' not in st.session_state:
    st.session_state.chat_view = 'chat'

# Sidebar for chat sessions
with st.sidebar:
    st.markdown(f"<h3 style='color: {DS.PRIMARY};'>💬 Chat Sessions</h3>", unsafe_allow_html=True)
    
    # New Chat button
    if st.button("➕ New Chat", use_container_width=True, type="primary"):
        # End current session if exists
        if st.session_state.current_chat_session_id:
            from database.models import ChatSession
            from database.db_manager import SessionLocal
            db = SessionLocal()
            try:
                session = db.query(ChatSession).filter(
                    ChatSession.session_id == st.session_state.current_chat_session_id
                ).first()
                if session and not session.ended_at:
                    session.ended_at = datetime.utcnow()
                    db.commit()
            finally:
                db.close()
        
        # Create new session
        st.session_state.current_chat_session_id = None
        st.session_state.chat_view = 'chat'
        st.rerun()
    
    st.markdown("---")
    
    # Get all user chat sessions
    from database.models import ChatSession, ChatMessage
    from database.db_manager import SessionLocal
    
    db = SessionLocal()
    try:
        all_sessions = db.query(ChatSession).filter(
            ChatSession.user_id == user_id
        ).order_by(ChatSession.started_at.desc()).limit(20).all()
        
        if all_sessions:
            st.markdown(f"<p style='color: {DS.TEXT_SECONDARY};'><strong>Recent Chats:</strong></p>", unsafe_allow_html=True)
            
            for session in all_sessions:
                # Determine session label
                if session.ended_at:
                    status = "📝"
                else:
                    status = "💬"
                
                # Get first message topic hint
                first_msg = db.query(ChatMessage).filter(
                    ChatMessage.session_id == session.session_id,
                    ChatMessage.role == 'user'
                ).first()
                
                topic_hint = first_msg.content[:30] + "..." if first_msg and len(first_msg.content) > 30 else (first_msg.content if first_msg else "New chat")
                
                # Check if this is the active session
                is_active = st.session_state.current_chat_session_id == session.session_id
                
                # Create button for session
                if st.button(
                    f"{status} {topic_hint}",
                    key=f"session_{session.session_id}",
                    use_container_width=True,
                    type="secondary" if not is_active else "primary"
                ):
                    st.session_state.current_chat_session_id = session.session_id
                    st.session_state.chat_view = 'chat'
                    st.rerun()
                
                st.caption(f"🕐 {session.started_at.strftime('%b %d, %I:%M %p')} | 💬 {session.message_count} msgs")
                st.markdown("---")
        else:
            st.info("No chat history yet")
    finally:
        db.close()

# Main chat area
st.markdown(f"""
<div style="text-align: center; margin-bottom: {DS.SPACE_8};">
    <h1 style="color: {DS.PRIMARY};">💬 AI Study Assistant</h1>
    <p style="color: {DS.TEXT_SECONDARY};">Your 24/7 learning companion</p>
</div>
""", unsafe_allow_html=True)

# Get or create session
if not st.session_state.current_chat_session_id:
    session = ChatEngine.get_or_create_session(user_id)
    st.session_state.current_chat_session_id = session.session_id
    
    # Send greeting for new session
    greeting = ChatEngine.send_daily_greeting(user_id, session.session_id)

# Display current session info
db = SessionLocal()
try:
    from database.models import ChatSession
    current_session = db.query(ChatSession).filter(
        ChatSession.session_id == st.session_state.current_chat_session_id
    ).first()
    
    if current_session:
        col1, col2, col3 = st.columns([3, 1, 1])
        with col1:
            if current_session.ended_at:
                st.info("📝 Viewing past chat session")
            else:
                st.success("💬 Active chat session")
        with col2:
            st.metric("Messages", current_session.message_count)
        with col3:
            st.caption(f"Started: {current_session.started_at.strftime('%b %d, %I:%M %p')}")
finally:
    db.close()

st.markdown("---")

# Chat history display
chat_history = ChatEngine.get_chat_history(st.session_state.current_chat_session_id, limit=50)

if chat_history:
    for msg in chat_history:
        if msg.role == 'user':
            st.markdown(f"""
            <div style="background: {DS.PRIMARY}; color: white; padding: {DS.SPACE_4}; 
                        border-radius: {DS.RADIUS_LG}; margin: {DS.SPACE_3} 0; 
                        margin-left: 20%; box-shadow: {DS.SHADOW_MD};">
                <strong>You:</strong><br>{msg.content}
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div style="background: {DS.SURFACE}; color: {DS.TEXT_PRIMARY}; 
                        padding: {DS.SPACE_4}; border-radius: {DS.RADIUS_LG}; 
                        margin: {DS.SPACE_3} 0; margin-right: 20%; 
                        border-left: 4px solid {DS.ACCENT}; box-shadow: {DS.SHADOW_MD};">
                <strong style="color: {DS.ACCENT};">🤖 AI Assistant:</strong><br>{msg.content}
            </div>
            """, unsafe_allow_html=True)
else:
    UIComponents.glass_card(
        "Start a Conversation",
        "Ask me anything about your studies!",
        "👋"
    )

st.markdown("---")

# Chat input
db = SessionLocal()
try:
    from database.models import ChatSession
    current_session = db.query(ChatSession).filter(
        ChatSession.session_id == st.session_state.current_chat_session_id
    ).first()
    
    session_ended = current_session.ended_at is not None if current_session else False
finally:
    db.close()

if session_ended:
    st.warning("⚠️ This chat session has ended. Start a new chat to continue!")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("➕ Start New Chat", use_container_width=True, type="primary"):
            st.session_state.current_chat_session_id = None
            st.rerun()
else:
    # Active session - allow input
    with st.form("chat_form", clear_on_submit=True):
        user_input = st.text_area(
            "Your message:",
            placeholder="Ask me about your studies, current topic, or uploaded materials...",
            height=100,
            key="chat_input"
        )
        
        col1, col2, col3 = st.columns([2, 1, 2])
        with col2:
            submit = st.form_submit_button("Send 📤", use_container_width=True, type="primary")
        
        if submit and user_input and user_input.strip():
            # Add user message
            ChatEngine.add_message(
                st.session_state.current_chat_session_id,
                'user',
                user_input.strip()
            )
            
            # Generate AI response
            with st.spinner("🤔 Thinking..."):
                ai_response = ChatEngine.generate_ai_response(
                    user_id,
                    user_input.strip(),
                    st.session_state.current_chat_session_id
                )
            
            # Add AI response
            ChatEngine.add_message(
                st.session_state.current_chat_session_id,
                'ai',
                ai_response
            )
            
            st.rerun()

# Tips section
with st.expander("💡 Tips for better conversations"):
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"""
        <div style="background: {DS.SURFACE}; padding: {DS.SPACE_4}; border-radius: {DS.RADIUS_MD};">
            <h4 style="color: {DS.PRIMARY};">You can ask me about:</h4>
            <ul>
                <li>📚 Your current study topic</li>
                <li>📄 Content from your uploaded PDFs</li>
                <li>❓ Doubts and clarifications</li>
                <li>💪 Motivation and study tips</li>
                <li>📝 Quiz preparation</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div style="background: {DS.SURFACE}; padding: {DS.SPACE_4}; border-radius: {DS.RADIUS_MD};">
            <h4 style="color: {DS.PRIMARY};">Example questions:</h4>
            <ul>
                <li>"What's in my uploaded document?"</li>
                <li>"Explain recursion in simple terms"</li>
                <li>"I'm struggling with today's topic, help!"</li>
                <li>"What should I focus on for the quiz?"</li>
                <li>"Summarize the key points from my notes"</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

# End session button (for active sessions)
if not session_ended:
    st.markdown("---")
    col1, col2, col3 = st.columns([2, 1, 2])
    with col2:
        if st.button("🔚 End This Chat", use_container_width=True):
            db = SessionLocal()
            try:
                from database.models import ChatSession
                session = db.query(ChatSession).filter(
                    ChatSession.session_id == st.session_state.current_chat_session_id
                ).first()
                if session:
                    session.ended_at = datetime.utcnow()
                    db.commit()
                    st.success("Chat session ended!")
                    st.rerun()
            finally:
                db.close()