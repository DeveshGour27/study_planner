"""
Reusable UI Components
Modern, production-ready Streamlit components
"""

import streamlit as st
from .design_system import DesignSystem as DS

class UIComponents:
    
    @staticmethod
    def render_custom_css():
        """Inject custom CSS into Streamlit app"""
        st.markdown(f"""
        <style>
        /* ==================== GLOBAL STYLES ==================== */
        
        :root {{
            --primary: {DS.PRIMARY};
            --background: {DS.BACKGROUND};
            --surface: {DS.SURFACE};
            --text-primary: {DS.TEXT_PRIMARY};
            --text-secondary: {DS.TEXT_SECONDARY};
        }}
        
        /* Hide Streamlit branding */
        #MainMenu {{visibility: hidden;}}
        footer {{visibility: hidden;}}
        header {{visibility: hidden;}}
        
        /* Custom scrollbar */
        ::-webkit-scrollbar {{
            width: 8px;
            height: 8px;
        }}
        
        ::-webkit-scrollbar-track {{
            background: {DS.SURFACE};
            border-radius: {DS.RADIUS_FULL};
        }}
        
        ::-webkit-scrollbar-thumb {{
            background: {DS.PRIMARY};
            border-radius: {DS.RADIUS_FULL};
        }}
        
        ::-webkit-scrollbar-thumb:hover {{
            background: {DS.PRIMARY_DARK};
        }}
        
        /* ==================== STREAMLIT OVERRIDES ==================== */
        
        .stApp {{
            background: {DS.BACKGROUND};
            color: {DS.TEXT_PRIMARY};
        }}
        
        /* Buttons */
        .stButton>button {{
            background: {DS.GRADIENT_PRIMARY};
            color: white;
            border: none;
            border-radius: {DS.RADIUS_LG};
            padding: {DS.SPACE_3} {DS.SPACE_6};
            font-weight: 600;
            transition: all {DS.TRANSITION_BASE};
            box-shadow: {DS.SHADOW_MD};
        }}
        
        .stButton>button:hover {{
            transform: translateY(-2px);
            box-shadow: {DS.SHADOW_LG};
        }}
        
        .stButton>button:active {{
            transform: translateY(0);
        }}
        
        /* Inputs */
        .stTextInput>div>div>input,
        .stTextArea>div>div>textarea,
        .stSelectbox>div>div>select {{
            background: {DS.SURFACE};
            color: {DS.TEXT_PRIMARY};
            border: 2px solid {DS.BORDER};
            border-radius: {DS.RADIUS_MD};
            padding: {DS.SPACE_3};
            transition: all {DS.TRANSITION_BASE};
        }}
        
        .stTextInput>div>div>input:focus,
        .stTextArea>div>div>textarea:focus {{
            border-color: {DS.PRIMARY};
            box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1);
        }}
        
        /* Cards */
        .element-container {{
            background: transparent;
        }}
        
        div[data-testid="stMetricValue"] {{
            font-size: {DS.FONT_SIZE_3XL};
            font-weight: 700;
            color: {DS.PRIMARY};
        }}
        
        div[data-testid="stMetricLabel"] {{
            color: {DS.TEXT_SECONDARY};
            font-size: {DS.FONT_SIZE_SM};
            font-weight: 500;
        }}
        
        /* Progress bars */
        .stProgress>div>div>div>div {{
            background: {DS.GRADIENT_PRIMARY};
            border-radius: {DS.RADIUS_FULL};
        }}
        
        /* Expanders */
        .streamlit-expanderHeader {{
            background: {DS.SURFACE};
            border-radius: {DS.RADIUS_MD};
            color: {DS.TEXT_PRIMARY};
            font-weight: 600;
        }}
        
        /* Tabs */
        .stTabs [data-baseweb="tab-list"] {{
            gap: {DS.SPACE_2};
            background: transparent;
        }}
        
        .stTabs [data-baseweb="tab"] {{
            background: {DS.SURFACE};
            border-radius: {DS.RADIUS_MD};
            color: {DS.TEXT_SECONDARY};
            padding: {DS.SPACE_3} {DS.SPACE_6};
            font-weight: 600;
            transition: all {DS.TRANSITION_BASE};
        }}
        
        .stTabs [aria-selected="true"] {{
            background: {DS.GRADIENT_PRIMARY};
            color: white;
        }}
        
        /* Sidebar */
        section[data-testid="stSidebar"] {{
            background: {DS.SURFACE};
            border-right: 1px solid {DS.BORDER};
        }}
        
        section[data-testid="stSidebar"] .stButton>button {{
            width: 100%;
        }}
        
        /* ==================== CUSTOM COMPONENTS ==================== */
        
        .modern-card {{
            background: {DS.SURFACE};
            border-radius: {DS.RADIUS_XL};
            padding: {DS.SPACE_6};
            box-shadow: {DS.SHADOW_MD};
            border: 1px solid {DS.BORDER};
            transition: all {DS.TRANSITION_BASE};
            margin-bottom: {DS.SPACE_4};
        }}
        
        .modern-card:hover {{
            box-shadow: {DS.SHADOW_XL};
            transform: translateY(-4px);
        }}
        
        .glass-card {{
            background: rgba(30, 41, 59, 0.7);
            backdrop-filter: blur(10px);
            border-radius: {DS.RADIUS_XL};
            padding: {DS.SPACE_6};
            border: 1px solid rgba(255, 255, 255, 0.1);
            box-shadow: {DS.SHADOW_LG};
        }}
        
        .stat-card {{
            background: {DS.GRADIENT_CARD};
            border-radius: {DS.RADIUS_LG};
            padding: {DS.SPACE_5};
            text-align: center;
            border: 1px solid {DS.BORDER};
            transition: all {DS.TRANSITION_BASE};
        }}
        
        .stat-card:hover {{
            border-color: {DS.PRIMARY};
            box-shadow: {DS.SHADOW_GLOW};
        }}
        
        .badge {{
            display: inline-block;
            padding: {DS.SPACE_1} {DS.SPACE_3};
            border-radius: {DS.RADIUS_FULL};
            font-size: {DS.FONT_SIZE_XS};
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        
        .badge-success {{
            background: {DS.ACCENT};
            color: white;
        }}
        
        .badge-warning {{
            background: {DS.ACCENT_WARNING};
            color: white;
        }}
        
        .badge-error {{
            background: {DS.ACCENT_ERROR};
            color: white;
        }}
        
        .badge-primary {{
            background: {DS.PRIMARY};
            color: white;
        }}
        
        /* Hero section */
        .hero {{
            text-align: center;
            padding: {DS.SPACE_12} {DS.SPACE_6};
            background: {DS.GRADIENT_PRIMARY};
            border-radius: {DS.RADIUS_2XL};
            margin-bottom: {DS.SPACE_8};
            box-shadow: {DS.SHADOW_2XL};
        }}
        
        .hero h1 {{
            font-size: {DS.FONT_SIZE_4XL};
            font-weight: 800;
            color: white;
            margin-bottom: {DS.SPACE_4};
        }}
        
        .hero p {{
            font-size: {DS.FONT_SIZE_LG};
            color: rgba(255, 255, 255, 0.9);
        }}
        
        /* Feature grid */
        .feature-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: {DS.SPACE_6};
            margin: {DS.SPACE_8} 0;
        }}
        
        .feature-card {{
            background: {DS.SURFACE};
            border-radius: {DS.RADIUS_XL};
            padding: {DS.SPACE_6};
            text-align: center;
            border: 1px solid {DS.BORDER};
            transition: all {DS.TRANSITION_BASE};
        }}
        
        .feature-card:hover {{
            border-color: {DS.PRIMARY};
            transform: translateY(-8px);
            box-shadow: {DS.SHADOW_XL};
        }}
        
        .feature-card h3 {{
            color: {DS.PRIMARY};
            font-size: {DS.FONT_SIZE_XL};
            margin: {DS.SPACE_4} 0;
        }}
        
        /* Loading animation */
        @keyframes pulse {{
            0%, 100% {{ opacity: 1; }}
            50% {{ opacity: 0.5; }}
        }}
        
        .loading {{
            animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
        }}
        
        /* Fade in animation */
        @keyframes fadeIn {{
            from {{ opacity: 0; transform: translateY(20px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}
        
        .fade-in {{
            animation: fadeIn 0.6s ease-out;
        }}
        
        </style>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def modern_card(content, key=None):
        """Render a modern card"""
        st.markdown(f"""
        <div class="modern-card fade-in">
            {content}
        </div>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def glass_card(title, description, icon="🎯"):
        """Render a glassmorphism card"""
        st.markdown(f"""
        <div class="glass-card fade-in">
            <div style="font-size: 3rem; margin-bottom: 1rem;">{icon}</div>
            <h3 style="color: {DS.PRIMARY}; margin-bottom: 0.5rem;">{title}</h3>
            <p style="color: {DS.TEXT_SECONDARY};">{description}</p>
        </div>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def stat_card(label, value, icon="📊", delta=None):
        """Render a stat card"""
        delta_html = f'<div style="color: {DS.ACCENT}; font-size: 0.875rem; margin-top: 0.5rem;">▲ {delta}</div>' if delta else ""
        
        st.markdown(f"""
        <div class="stat-card fade-in">
            <div style="font-size: 2rem; margin-bottom: 0.5rem;">{icon}</div>
            <div style="font-size: 0.75rem; color: {DS.TEXT_MUTED}; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 0.5rem;">{label}</div>
            <div style="font-size: 2rem; font-weight: 700; color: {DS.PRIMARY};">{value}</div>
            {delta_html}
        </div>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def badge(text, type="primary"):
        """Render a badge"""
        return f'<span class="badge badge-{type}">{text}</span>'
    
    @staticmethod
    def hero(title, subtitle):
        """Render hero section"""
        st.markdown(f"""
        <div class="hero fade-in">
            <h1>{title}</h1>
            <p>{subtitle}</p>
        </div>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def feature_card(icon, title, description):
        """Render feature card"""
        st.markdown(f"""
        <div class="feature-card fade-in">
            <div style="font-size: 3rem; margin-bottom: 1rem;">{icon}</div>
            <h3>{title}</h3>
            <p style="color: {DS.TEXT_SECONDARY};">{description}</p>
        </div>
        """, unsafe_allow_html=True)