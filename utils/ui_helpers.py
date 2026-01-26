"""UI helper functions for better UX"""
import streamlit as st

class UIHelpers:
    
    @staticmethod
    def show_success(message, icon="✅"):
        """Show success message with icon"""
        st.success(f"{icon} {message}")
    
    @staticmethod
    def show_error(message, icon="❌"):
        """Show error message with icon"""
        st.error(f"{icon} {message}")
    
    @staticmethod
    def show_warning(message, icon="⚠️"):
        """Show warning message with icon"""
        st.warning(f"{icon} {message}")
    
    @staticmethod
    def show_info(message, icon="ℹ️"):
        """Show info message with icon"""
        st.info(f"{icon} {message}")
    
    @staticmethod
    def confirm_action(message, confirm_text="Confirm", cancel_text="Cancel"):
        """Show confirmation dialog - returns True/False/None"""
        st.warning(f"⚠️ {message}")
        col1, col2 = st.columns(2)
        confirmed = None
        with col1:
            if st.button(confirm_text, type="primary", use_container_width=True):
                confirmed = True
        with col2:
            if st. button(cancel_text, use_container_width=True):
                confirmed = False
        return confirmed
    
    @staticmethod
    def show_loading(message="Processing... "):
        """Show loading spinner"""
        return st.spinner(message)
    
    @staticmethod
    def empty_state(title, description, icon="📭", button_text=None, button_callback=None):
        """Show empty state with optional action button"""
        st.markdown(f"""
        <div style="text-align: center; padding: 3rem; color: #666;">
            <div style="font-size: 4rem; margin-bottom: 1rem;">{icon}</div>
            <h3 style="color: #333; margin-bottom:  0.5rem;">{title}</h3>
            <p style="color: #666;">{description}</p>
        </div>
        """, unsafe_allow_html=True)
        
        if button_text and button_callback:
            col1, col2, col3 = st.columns([1, 1, 1])
            with col2:
                if st.button(button_text, use_container_width=True, type="primary"):
                    button_callback()
    
    @staticmethod
    def progress_bar(current, total, label="Progress"):
        """Show progress bar with label"""
        percentage = (current / total * 100) if total > 0 else 0
        st.progress(percentage / 100, text=f"{label}: {current}/{total} ({percentage:.0f}%)")
        return percentage
    
    @staticmethod
    def metric_card(label, value, delta=None, icon="📊"):
        """Show metric card"""
        st.metric(f"{icon} {label}", value, delta)
    
    @staticmethod
    def section_header(title, icon="", description=""):
        """Show section header"""
        if icon:
            st.markdown(f"### {icon} {title}")
        else:
            st.markdown(f"### {title}")
        if description:
            st.caption(description)
        st.markdown("---")