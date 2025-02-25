import streamlit as st
import google.generativeai as genai
from datetime import datetime
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import base64
import time
import random

# Configure Gemini API
GOOGLE_API_KEY = "AIzaSyC_3S1DnOvip8iBpyhtp1rf08j91Scx8V0"  # Replace with your actual Google Gemini API key
try:
    genai.configure(api_key=GOOGLE_API_KEY)
    model = genai.GenerativeModel(model_name="gemini-1.5-flash")
except Exception as e:
    st.error(f"Error configuring Gemini API: {str(e)}")
    model = None

# Utility Functions
def generate_ai_response(prompt, max_retries=3):
    """Generate AI-driven text content using the Gemini API with retry logic."""
    if not model:
        return "AI model is not available. Please check your API key configuration."
    
    for attempt in range(max_retries):
        try:
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            if attempt == max_retries - 1:
                return f"Error generating response: {str(e)}"
            time.sleep(1)  # Wait before retrying

def generate_ai_insights(data, context, max_tokens=300):
    """Generate insights based on provided data and context."""
    prompt = f"""
    Context: {context}
    
    Data: {data}
    
    Please provide educational insights based on this information. 
    Focus on practical applications and actionable recommendations.
    Keep your response concise and professional.
    """
    return generate_ai_response(prompt)

def generate_flow_diagram(topic):
    """Generate an interactive flow diagram for a specific topic using Plotly."""
    topic = topic.lower()
    if topic == "photosynthesis":
        data = pd.DataFrame({
            'Step': ['Sunlight', 'Chlorophyll', 'CO2', 'Water', 'Glucose', 'Oxygen'],
            'Process': ['Captured', 'Absorbs', 'Taken', 'Taken', 'Produced', 'Released']
        })
        fig = px.line(data, x='Step', y='Process', title='Photosynthesis Flow', text='Process', 
                      line_shape='spline', render_mode='svg', height=300)
        fig.update_traces(textposition='top center')
        return fig
    elif topic == "water cycle":
        data = pd.DataFrame({
            'Step': ['Evaporation', 'Condensation', 'Precipitation', 'Collection'],
            'Process': ['Vaporizes', 'Forms Clouds', 'Falls', 'Gathers']
        })
        fig = px.line(data, x='Step', y='Process', title='Water Cycle Flow', text='Process', 
                      line_shape='spline', render_mode='svg', height=300)
        fig.update_traces(textposition='top center')
        return fig
    else:
        return None  # Placeholder for future topic expansions

# Session State Initialization
def initialize_session_state():
    """Initialize session state variables with default values."""
    defaults = {
        "lesson_plans": [],          # Saved lesson plans
        "grades": {},                # Student grades
        "forum_posts": [],           # Forum posts for collaboration
        "pd_activities": [],         # Professional development activities
        "wellbeing_logs": [],        # Well-being logs
        "observations": [],          # Observation records
        "messages": [],              # Collaboration messages
        "substitute_plans": [],      # Substitute plans
        "attendance": {},            # Attendance records
        "peer_reviews": [],          # Peer reviews
        "live_observations": [],     # Live classroom observations
        "student_analytics": {},     # Student performance analytics
        "dark_mode": False,          # Dark mode toggle
        "current_page": "Home",      # Current page
        "username": "teacher1",      # Default username
        "role": "Teacher",           # User role
        "lesson_planning_session": [], # AI planning session
        "collaborative_notes": [],   # Collaborative notes
        "feedback_log": [],          # Feedback logs
        "live_session_active": False, # Live session status
        "live_content_options": {},  # Live session content
        "current_display": None,     # Displayed content
        "engagement_logs": [],       # Engagement logs
        "full_screen": False,        # Full-screen mode
        "syllabi": {},               # Stored syllabi
        "assessment_logs": [],       # Assessment logs
        "elca_data": {},             # ELCA data
        "voice_history": [],          # History of voice commands
        "ai_insights_cache": {},      # Cache for AI-generated insights
        "integrated_updates": [],     # Tracking content updates integration
        "adopted_trends": [],         # Tracking adopted trends
        "last_ai_interaction": None,  # Timestamp of last AI interaction
        "feedback_responses": {},     # AI-generated feedback responses
        "page_visit_history": [],     # Track user navigation patterns
        "tutorial_completed": {},     # Track completed tutorials by page
        "custom_themes": {},          # User-defined UI themes
        "notification_count": 0,      # Notification counter
        "notifications": [],          # System notifications
        "elca_active": False,         # ELCA active status
        "current_lesson": "Photosynthesis in Plants",  # Current lesson for ELCA
        "content_options": [          # Content options for ELCA
            {
                "type": "Diagram",
                "title": "Photosynthesis Process Flow",
                "description": "Visual breakdown of the photosynthesis stages",
                "impact": 15,
                "icon": "📊"
            },
            {
                "type": "Story",
                "title": "The Plant Chef",
                "description": "Analogy comparing plants to chefs using sunlight as heat",
                "impact": 20,
                "icon": "📚"
            },
            {
                "type": "Video",
                "title": "Photosynthesis Animation",
                "description": "30-second animation showing the chemical process",
                "impact": 18,
                "icon": "🎬"
            },
            {
                "type": "Simplified",
                "title": "Photosynthesis in Simple Terms",
                "description": "Grade-appropriate explanation of the concept",
                "impact": 12,
                "icon": "🔤"
            },
            {
                "type": "Interactive",
                "title": "Label the Plant Cell",
                "description": "Drag and drop activity for identifying cell parts",
                "impact": 25,
                "icon": "🖱️"
            },
            {
                "type": "Picture",
                "title": "Detailed Plant Cell Image",
                "description": "High-resolution labeled diagram of a plant cell",
                "impact": 10,
                "icon": "🖼️"
            }
        ],
        "selected_content": 0,        # Selected content for ELCA
        "metrics": {                  # Metrics for ELCA
            "engagement": 75,
            "comprehension": 68,
            "retention": 72
        },
        "alerts": [                   # Alerts for ELCA
            {"type": "warning", "message": "Pacing is faster than optimal - consider slowing down"},
            {"type": "success", "message": "Student participation is high - good questioning technique"}
        ],
        "content_used": 3,            # Content used for ELCA
        "student_responses": 85,      # Student responses for ELCA
        "teachers": [                 # Teachers for admin dashboard
            {"name": "Sarah Johnson", "subject": "Mathematics", "pd_complete": 85, "observation": 4.2, "student_growth": 12},
            {"name": "Michael Chen", "subject": "Science", "pd_complete": 92, "observation": 4.7, "student_growth": 15},
            {"name": "Emily Rodriguez", "subject": "English", "pd_complete": 78, "observation": 3.9, "student_growth": 8},
            {"name": "David Kim", "subject": "History", "pd_complete": 65, "observation": 3.5, "student_growth": 5},
            {"name": "Lisa Patel", "subject": "Art", "pd_complete": 90, "observation": 4.5, "student_growth": 10},
            {"name": "James Wilson", "subject": "Physical Education", "pd_complete": 72, "observation": 4.0, "student_growth": 7},
            {"name": "Maria Garcia", "subject": "Spanish", "pd_complete": 88, "observation": 4.3, "student_growth": 11},
            {"name": "Robert Taylor", "subject": "Music", "pd_complete": 81, "observation": 4.1, "student_growth": 9}
        ],
        "admin_view": "overview",     # Admin view
        "lesson_sections": [],        # Lesson sections
        "standards_analysis": None,   # Standards analysis
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value
    
    # Track page visits for analytics
    current_page = st.session_state.get("current_page", "Home")
    if not st.session_state.page_visit_history or st.session_state.page_visit_history[-1] != current_page:
        st.session_state.page_visit_history.append(current_page)
        if len(st.session_state.page_visit_history) > 20:  # Limit history length
            st.session_state.page_visit_history.pop(0)

# Dynamic UI Theme
def apply_theme():
    """Apply a dynamic UI theme with custom CSS styling."""
    primary_color = "#2E86C1"
    secondary_color = "#28A745"
    accent_color = "#F59E0B"
    background_dark = "#1A2525"
    background_light = "#F8FAFC"
    
    if st.session_state['dark_mode']:
        bg_color = background_dark
        text_color = "#E2E8F0"
        card_bg = "#2D3748"
        accent = "#FBBF24"
    else:
        bg_color = background_light
        text_color = "#1A2525"
        card_bg = "#FFFFFF"
        accent = accent_color

    css = f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
    @import url('https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css');

    :root {{
        --primary: {primary_color};
        --secondary: {secondary_color};
        --accent: {accent};
        --bg: {bg_color};
        --text: {text_color};
        --card-bg: {card_bg};
        --border: rgba(0, 0, 0, 0.1);
        --text-secondary: rgba(0, 0, 0, 0.6);
    }}

    .stApp {{
        background: var(--bg);
        color: var(--text);
        font-family: 'Inter', sans-serif;
        line-height: 1.6;
    }}

    .custom-card {{
        background: var(--card-bg);
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        margin: 1rem 0;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }}
    .custom-card:hover {{
        transform: translateY(-4px);
        box-shadow: 0 6px 16px rgba(0, 0, 0, 0.15);
    }}

    .stButton>button {{
        background: linear-gradient(45deg, {primary_color}, {secondary_color});
        color: white !important;
        border: none;
        border-radius: 8px;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        transition: all 0.3s ease;
    }}
    .stButton>button:hover {{
        opacity: 0.9;
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.2);
    }}

    .stTabs [data-baseweb="tab-list"] {{
        gap: 1rem;
        background: var(--card-bg);
        padding: 0.5rem;
        border-radius: 8px;
    }}
    .stTabs [data-baseweb="tab"] {{
        padding: 0.75rem 1.5rem;
        border-radius: 8px;
        transition: all 0.3s ease;
        font-weight: 600;
    }}
    .stTabs [aria-selected="true"] {{
        background: var(--primary) !important;
        color: white !important;
    }}

    .divider {{
        margin: 20px 0;
        border-bottom: 2px solid rgba(229, 231, 235, 0.5);
    }}

    .sidebar-header {{
        background: linear-gradient(45deg, {primary_color}, {secondary_color});
        color: white;
        padding: 1.5rem;
        border-radius: 12px 12px 0 0;
        margin-bottom: 1rem;
    }}

    .stRadio > div {{
        display: flex;
        flex-direction: column;
    }}
    .stRadio label {{
        padding: 0.75rem 1rem;
        border-radius: 8px;
        margin-bottom: 0.5rem;
        transition: background 0.3s ease;
        cursor: pointer;
        font-size: 1.1rem;
        font-weight: 600;
    }}
    .stRadio label:hover {{
        background: rgba(46, 134, 193, 0.1);
    }}
    .stRadio input:checked + label {{
        background: var(--primary);
        color: white;
    }}

    .projector-screen {{
        background: #F0F4F8;
        border: 2px dashed var(--primary);
        border-radius: 10px;
        padding: 1rem;
        min-height: 300px;
        transition: all 0.3s ease;
    }}
    .projector-screen.full-screen {{
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        z-index: 999;
        padding: 2rem;
        background: rgba(0, 0, 0, 0.9);
        color: white;
    }}

    .progress-ring {{
        width: 120px;
        height: 120px;
        margin: 20px auto;
    }}
    .progress-ring__circle {{
        transition: stroke-dashoffset 0.5s;
        transform: rotate(-90deg);
        transform-origin: 50% 50%;
    }}
    .standard-match {{ background: #e8f5e9 !important; border-left: 4px solid #4caf50; }}
    .standard-gap {{ background: #ffebee !important; border-left: 4px solid #f44336; }}

    .resource-card {{
        border-radius: 12px;
        padding: 1rem;
        margin: 1rem 0;
        transition: all 0.3s ease;
        cursor: pointer;
        background: var(--card-bg);
    }}
    .resource-card:hover {{
        transform: translateY(-5px);
        box-shadow: 0 5px 15px rgba(0,0,0,0.2);
    }}
    .resource-tag {{
        display: inline-block;
        padding: 0.25rem 0.5rem;
        border-radius: 20px;
        font-size: 0.8rem;
        margin: 0.25rem;
    }}
    .teaching-style-badge {{
        position: absolute;
        top: -10px;
        right: -10px;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-weight: bold;
    }}
    .story-segment {{
        border-left: 4px solid #4CAF50;
        padding: 1rem;
        margin: 1rem 0;
        background: var(--card-bg);
        border-radius: 8px;
        transition: all 0.3s ease;
    }}
    .story-segment:hover {{
        transform: translateX(10px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }}
    .ai-suggestion {{
        background: #fff3e0;
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
        border: 2px dashed #FF9800;
    }}
    .typewriter {{
        font-family: monospace;
        border-right: 3px solid;
        white-space: nowrap;
        overflow: hidden;
        animation: typing 3s steps(40), blink-caret 0.75s step-end infinite;
    }}
    @keyframes typing {{ from {{ width: 0 }} to {{ width: 100% }} }}
    @keyframes blink-caret {{ from, to {{ border-color: transparent }} 50% {{ border-color: orange }} }}

    .performance-card {{
        background: var(--card-bg);
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        transition: all 0.3s ease;
        position: relative;
    }}
    .performance-card:hover {{
        transform: translateY(-3px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }}
    .live-alert {{
        animation: pulse 2s infinite;
        border-left: 4px solid #FF9800;
    }}
    @keyframes pulse {{
        0% {{ opacity: 1; }}
        50% {{ opacity: 0.8; }}
        100% {{ opacity: 1; }}
    }}
    .student-avatar {{
        width: 40px;
        height: 40px;
        border-radius: 50%;
        margin-right: 1rem;
    }}
    .impact-card {{
        background: var(--card-bg);
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        transition: all 0.3s ease;
    }}
    .impact-card:hover {{
        transform: translateY(-3px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }}
    .pulse-alert {{
        animation: pulse 2s infinite;
        border-left: 4px solid #2196F3;
    }}
    @keyframes pulse {{
        0% {{ opacity: 1; }}
        50% {{ opacity: 0.8; }}
        100% {{ opacity: 1; }}
    }}
    .impact-badge {{
        padding: 0.25rem 0.5rem;
        border-radius: 20px;
        font-size: 0.8rem;
        margin-left: 0.5rem;
    }}
    .engagement-card {{
        background: var(--card-bg);
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        transition: all 0.3s ease;
    }}
    .engagement-card:hover {{
        transform: translateY(-3px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }}
    .heatmap-cell {{
        padding: 1rem;
        border-radius: 8px;
        margin: 0.2rem;
        text-align: center;
    }}
    .case-card {{
        background: var(--card-bg);
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        transition: all 0.3s ease;
    }}
    .case-card:hover {{
        transform: translateY(-3px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }}
    .tag-pill {{
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.8rem;
        margin: 0.2rem;
    }}
    .completeness-bar {{
        height: 5px;
        background: #e0e0e0;
        border-radius: 3px;
        margin: 0.5rem 0;
    }}
    .completeness-fill {{
        height: 100%;
        border-radius: 3px;
        background: var(--primary);
        transition: width 0.3s ease;
    }}
    .admin-card {{
        background: var(--card-bg);
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        transition: all 0.3s ease;
        border-left: 4px solid var(--primary);
    }}
    .admin-card:hover {{
        transform: translateY(-3px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }}
    .metric-container {{
        display: flex;
        justify-content: space-between;
        flex-wrap: wrap;
        gap: 1rem;
        margin: 1rem 0;
    }}
    .metric-box {{
        background: var(--card-bg);
        border-radius: 8px;
        padding: 1rem;
        flex: 1;
        min-width: 120px;
        text-align: center;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
    }}
    .metric-value {{
        font-size: 2rem;
        font-weight: bold;
        margin: 0.5rem 0;
    }}
    .metric-label {{
        font-size: 0.9rem;
        color: var(--text-secondary);
    }}
    .alert-box {{
        background: rgba(244, 67, 54, 0.1);
        border-left: 4px solid #F44336;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }}
    .success-box {{
        background: rgba(76, 175, 80, 0.1);
        border-left: 4px solid #4CAF50;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }}
    .warning-box {{
        background: rgba(255, 152, 0, 0.1);
        border-left: 4px solid #FF9800;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }}
    .calendar-item {{
        padding: 0.75rem;
        border-radius: 8px;
        margin: 0.5rem 0;
        background: var(--card-bg);
        border-left: 4px solid;
    }}
    .prediction-card {{
        background: rgba(33, 150, 243, 0.05);
        border-radius: 12px;
        padding: 1rem;
        margin: 0.5rem 0;
        border: 1px solid rgba(33, 150, 243, 0.2);
    }}
    .teacher-row {{
        display: flex;
        align-items: center;
        padding: 0.75rem;
        border-radius: 8px;
        margin: 0.5rem 0;
        background: var(--card-bg);
    }}
    .teacher-avatar {{
        width: 40px;
        height: 40px;
        border-radius: 50%;
        background: var(--primary);
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        margin-right: 1rem;
    }}
    .progress-bar {{
        height: 8px;
        background: #e0e0e0;
        border-radius: 4px;
        margin: 0.5rem 0;
        overflow: hidden;
    }}
    .progress-fill {{
        height: 100%;
        border-radius: 4px;
    }}
    .elca-card {{
        background: var(--card-bg);
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        transition: all 0.3s ease;
    }}
    .elca-card:hover {{
        transform: translateY(-3px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }}
    .status-indicator {{
        display: inline-block;
        width: 12px;
        height: 12px;
        border-radius: 50%;
        margin-right: 8px;
    }}
    .status-active {{
        background: #4CAF50;
        box-shadow: 0 0 8px rgba(76, 175, 80, 0.5);
        animation: pulse 1.5s infinite;
    }}
    .status-inactive {{
        background: #F44336;
    }}
    .status-warning {{
        background: #FF9800;
    }}
    .content-option {{
        border: 1px solid var(--border);
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
        cursor: pointer;
        transition: all 0.2s ease;
    }}
    .content-option:hover {{
        border-color: var(--primary);
        background: rgba(33, 150, 243, 0.05);
    }}
    .content-option.selected {{
        border-color: var(--primary);
        background: rgba(33, 150, 243, 0.1);
        box-shadow: 0 0 0 1px var(--primary);
    }}
    .tutor-display {{
        background: rgba(33, 150, 243, 0.05);
        border: 1px solid rgba(33, 150, 243, 0.2);
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        position: relative;
    }}
    .tutor-avatar {{
        position: absolute;
        top: -20px;
        left: 20px;
        width: 50px;
        height: 50px;
        border-radius: 50%;
        background: var(--primary);
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-size: 24px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }}
    .alert-bar {{
        background: rgba(255, 152, 0, 0.1);
        border-left: 4px solid #FF9800;
        padding: 0.75rem 1rem;
        border-radius: 4px;
        margin: 1rem 0;
        display: flex;
        align-items: center;
        justify-content: space-between;
    }}
    .alert-bar.success {{
        background: rgba(76, 175, 80, 0.1);
        border-left: 4px solid #4CAF50;
    }}
    .alert-bar.warning {{
        background: rgba(255, 152, 0, 0.1);
        border-left: 4px solid #FF9800;
    }}
    .alert-bar.danger {{
        background: rgba(244, 67, 54, 0.1);
        border-left: 4px solid #F44336;
    }}
    .metric-pill {{
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.8rem;
        margin: 0.2rem;
        background: var(--accent);
        color: white;
    }}
    .content-type-icon {{
        width: 40px;
        height: 40px;
        border-radius: 8px;
        background: rgba(33, 150, 243, 0.1);
        display: flex;
        align-items: center;
        justify-content: center;
        margin-right: 12px;
    }}
    .progress-container {{
        height: 8px;
        background: #e0e0e0;
        border-radius: 4px;
        margin: 0.5rem 0;
        overflow: hidden;
    }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)
    st.markdown('<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">', unsafe_allow_html=True)

# Sidebar Navigation
def render_sidebar():
    """Render the sidebar navigation menu with role-based options."""
    with st.sidebar:
        st.markdown(f"""
        <div class="sidebar-header">
            <h1 style="font-size: 1.75rem; margin: 0;">
                <i class="fas fa-graduation-cap" style="margin-right: 0.5rem;"></i>EduGauge
            </h1>
            <div style="display: flex; align-items: center; gap: 0.75rem; margin-top: 0.5rem;">
                <div style="width: 40px; height: 40px; border-radius: 50%; background: #E2E8F0;"></div>
                <div>
                    <p style="margin: 0; font-weight: 600;">{st.session_state['username']}</p>
                    <p style="margin: 0; font-size: 0.875rem;">{st.session_state['role']}</p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        pages = [
            ("🏠 Home", "Home"),
            ("📚 Lesson Planning", "Lesson Planning"),
            ("📊 Student Performance", "Student Performance"),
            ("🎓 Professional Development", "Professional Development"),
                        ("🤝 Collaboration", "Collaboration"),
            ("💖 Well-Being", "Well-Being"),
            ("👁️ Observation and Feedback", "Observation and Feedback"),
            ("🏫 Classroom Management", "Classroom Management"),
            ("📚 Alignment Optimizer", "Alignment Optimizer"),
            ("📚 Resource Hub", "Resource Hub"),
            ("📚 Story Builder", "Story Builder"),
            ("📚 Recap Studio", "Recap Studio"),
            ("📚 Case Study Vault", "Case Study Vault"),
            ("👩‍🏫 Student Engagement Monitor", "Student Engagement Monitor"),
            ("💬 Communication Studio", "Communication Studio"),
            ("🌍 Global Exchange Hub", "Global Exchange Hub"),
            ("🔄 Content Update Center", "Content Update Center"),
            ("🔍 Trend Analyzer Hub", "Trend Analyzer Hub"),
            ("🎓 ELCA Control Center", "ELCA Control Center"),
            ("🔊 Voice Assistant", "Voice Assistant"),
            ("⚙️ Admin Dashboard", "Admin Dashboard")
        ] if st.session_state["role"] == "Teacher" else [
            ("🏠 Home", "Home"),
            ("⚙️ Admin Dashboard", "Admin Dashboard")
        ]

        options = [display for display, _ in pages]
        current_index = next((i for i, (_, p) in enumerate(pages) if p == st.session_state["current_page"]), 0)
        selected_display = st.radio("Navigation", options, index=current_index)
        selected_page = next(p for d, p in pages if d == selected_display)
        if selected_page != st.session_state["current_page"]:
            st.session_state["current_page"] = selected_page
            st.rerun()

        st.markdown('<div class="custom-card">', unsafe_allow_html=True)
        st.markdown('<h3 style="color: var(--primary);"><i class="fas fa-cog"></i> Settings</h3>', unsafe_allow_html=True)
        st.checkbox("Dark Mode", value=st.session_state['dark_mode'], 
                    on_change=lambda: st.session_state.update({'dark_mode': not st.session_state['dark_mode']}), 
                    key="dark_mode_toggle")
        st.markdown('</div>', unsafe_allow_html=True)

        # Notifications
        if st.session_state.get("notification_count", 0) > 0:
            st.markdown(f"""
            <div class="custom-card" style="background: rgba(33, 150, 243, 0.1); border-left: 4px solid #2196F3;">
                <h3><i class="fas fa-bell"></i> Notifications ({st.session_state.notification_count})</h3>
                <p>You have {st.session_state.notification_count} unread notifications</p>
                <button class="stButton">View All</button>
            </div>
            """, unsafe_allow_html=True)

# Main Application
def main():
    """Main function to render the EduGauge application."""
    st.set_page_config(page_title="EduGauge", page_icon="🎓", layout="wide", initial_sidebar_state="expanded")
    
    # Initialize session state
    if "teachers" not in st.session_state:
        st.session_state.teachers = [
            {"name": "Sarah Johnson", "subject": "Math", "pd_complete": 92, "observation": 4.7, "student_growth": 12.5},
            {"name": "Michael Chen", "subject": "Science", "pd_complete": 85, "observation": 4.2, "student_growth": 10.8},
            {"name": "Emily Rodriguez", "subject": "English", "pd_complete": 78, "observation": 3.9, "student_growth": 8.2},
            {"name": "David Kim", "subject": "History", "pd_complete": 65, "observation": 3.5, "student_growth": 6.5},
            {"name": "Lisa Patel", "subject": "Arts", "pd_complete": 90, "observation": 4.5, "student_growth": 11.2},
            {"name": "James Wilson", "subject": "PE", "pd_complete": 72, "observation": 4.0, "student_growth": 7.8},
            {"name": "Maria Garcia", "subject": "Languages", "pd_complete": 88, "observation": 4.3, "student_growth": 9.5}
        ]
    
    initialize_session_state()
    apply_theme()
    render_sidebar()
    page = st.session_state["current_page"]

    ### Home Page
    if page == "Home":
        st.markdown('<h1 style="font-size: 2.5rem; font-weight: 700; color: var(--primary);"><i class="fas fa-home"></i> EduGauge Home</h1>', unsafe_allow_html=True)
        st.markdown('<p style="font-size: 1.25rem; color: var(--text);">Empowering Teachers for Impactful Learning</p>', unsafe_allow_html=True)
        
        # Welcome banner with dynamic greeting
        current_hour = datetime.now().hour
        greeting = "Good morning" if 5 <= current_hour < 12 else "Good afternoon" if 12 <= current_hour < 18 else "Good evening"
        
        st.markdown(f"""
        <div class="custom-card" style="background: linear-gradient(45deg, #2E86C1, #28A745); color: white;">
            <h2>{greeting}, {st.session_state['username']}!</h2>
            <p>Welcome to EduGauge - Your AI-powered teaching assistant</p>
            <p>Today is {datetime.now().strftime('%A, %B %d, %Y')}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Quick stats in a row
        st.markdown('<div class="custom-card">', unsafe_allow_html=True)
        st.markdown('<h3 class="subheader"><i class="fas fa-tachometer-alt" style="color: var(--accent); margin-right: 0.5rem;"></i>Quick Stats</h3>', unsafe_allow_html=True)
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Lesson Plans", len(st.session_state["lesson_plans"]), delta="+2")
        with col2:
            st.metric("PD Hours", f"{sum(a.get('hours', 0) for a in st.session_state['pd_activities']):.1f}", delta="+2.5")
        with col3:
            st.metric("Observations", len(st.session_state["observations"]), delta="+1")
        with col4:
            st.metric("Students Graded", sum(len(g) for g in st.session_state["grades"].values()), delta="+15")
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Three-column layout for quick access
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown('<div class="custom-card">', unsafe_allow_html=True)
            st.markdown("### 📝 Recent Lesson Plans")
            st.markdown("Access your most recent lesson plans.")
            if st.button("Create New Plan", key="home_create_plan"):
                st.session_state.current_page = "Lesson Planning"
                st.experimental_rerun()
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="custom-card">', unsafe_allow_html=True)
            st.markdown("### 🤖 AI Assistant")
            st.markdown("Get help with your teaching tasks.")
            if st.button("Ask AI", key="home_ask_ai"):
                st.session_state.current_page = "Voice Assistant"
                st.experimental_rerun()
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col3:
            st.markdown('<div class="custom-card">', unsafe_allow_html=True)
            st.markdown("### 📊 Trending Now")
            st.markdown("Discover the latest educational trends and innovations.")
            if st.button("Explore Trends", key="home_explore_trends"):
                st.session_state.current_page = "Trend Analyzer Hub"
                st.experimental_rerun()
            st.markdown('</div>', unsafe_allow_html=True)
    
    elif page == "ELCA Control Center":
        elca_page()
    
    elif page == "Content Update Center":
        content_updates_page()
    
    elif page == "Trend Analyzer Hub":
        trend_analyzer_page()
    
    elif page == "Admin Dashboard":
        admin_dashboard_page()
    
    elif page == "Voice Assistant":
        voice_assistant_page()
    
    elif page == "Student Performance":
        student_performance_page()
    
    elif page == "Professional Development":
        professional_development_page()
    
    elif page == "Lesson Planning":
        lesson_planning_page()
    
    elif page == "Collaboration":
        collaboration_page()
    
    elif page == "Well-Being":
        wellbeing_page()
    
    elif page == "Observation and Feedback":
        observation_feedback_page()
    
    elif page == "Classroom Management":
        classroom_management_page()
    
    elif page == "Alignment Optimizer":
        alignment_optimizer_page()
    
    elif page == "Resource Hub":
        resource_hub_page()
    
    elif page == "Story Builder":
        story_builder_page()
    
    elif page == "Recap Studio":
        recap_studio_page()
    
    elif page == "Case Study Vault":
        case_study_vault_page()
    
    elif page == "Student Engagement Monitor":
        student_engagement_page()
    
    elif page == "Communication Studio":
        communication_studio_page()
    
    elif page == "Global Exchange Hub":
        global_exchange_page()

def elca_page():
    """Render the ELCA Control Center page."""
    st.markdown("""
    <style>
    .elca-card {
        background: var(--card-bg);
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        transition: all 0.3s ease;
    }
    .elca-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }
    .status-indicator {
        display: inline-block;
        width: 12px;
        height: 12px;
        border-radius: 50%;
        margin-right: 8px;
    }
    .status-active {
        background: #4CAF50;
        box-shadow: 0 0 8px rgba(76, 175, 80, 0.5);
        animation: pulse 1.5s infinite;
    }
    .status-inactive {
        background: #F44336;
    }
    .status-warning {
        background: #FF9800;
    }
    @keyframes pulse {
        0% { opacity: 0.7; }
        50% { opacity: 1; }
        100% { opacity: 0.7; }
    }
    .content-option {
        border: 1px solid rgba(0,0,0,0.1);
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
        cursor: pointer;
        transition: all 0.2s ease;
    }
    .content-option:hover {
        border-color: var(--primary);
        background: rgba(33, 150, 243, 0.05);
    }
    .content-option.selected {
        border-color: var(--primary);
        background: rgba(33, 150, 243, 0.1);
        box-shadow: 0 0 0 1px var(--primary);
    }
    .metric-container {
        display: flex;
        justify-content: space-between;
        margin: 1rem 0;
    }
    .metric-box {
        text-align: center;
        padding: 1rem;
        border-radius: 8px;
        background: var(--card-bg);
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        flex: 1;
        margin: 0 0.5rem;
    }
    .metric-value {
        font-size: 1.5rem;
        font-weight: bold;
    }
    .metric-label {
        font-size: 0.875rem;
        color: rgba(0,0,0,0.6);
    }
    </style>
    """, unsafe_allow_html=True)

    st.title("🎓 ELCA Control Center")
    
    # Initialize session state for ELCA
    if 'elca_active' not in st.session_state:
        st.session_state.elca_active = False
    if 'current_lesson' not in st.session_state:
        st.session_state.current_lesson = "Photosynthesis in Plants"
    if 'content_options' not in st.session_state:
        st.session_state.content_options = [
            {
                "type": "Diagram",
                "title": "Photosynthesis Process Flow",
                "description": "Visual breakdown of the photosynthesis stages",
                "impact": 15,
                "icon": "📊"
            },
            {
                "type": "Story",
                "title": "The Plant Chef",
                "description": "Analogy comparing plants to chefs using sunlight as heat",
                "impact": 20,
                "icon": "📚"
            },
            {
                "type": "Video",
                "title": "Photosynthesis Animation",
                "description": "30-second animation showing the chemical process",
                "impact": 18,
                "icon": "🎬"
            },
            {
                "type": "Simplified",
                "title": "Photosynthesis in Simple Terms",
                "description": "Grade-appropriate explanation of the concept",
                "impact": 12,
                "icon": "🔤"
            },
            {
                "type": "Interactive",
                "title": "Label the Plant Cell",
                "description": "Drag and drop activity for identifying cell parts",
                "impact": 25,
                "icon": "🖱️"
            },
            {
                "type": "Picture",
                "title": "Detailed Plant Cell Image",
                "description": "High-resolution labeled diagram of a plant cell",
                "impact": 10,
                "icon": "🖼️"
            }
        ]
    if 'selected_content' not in st.session_state:
        st.session_state.selected_content = 0
    if 'metrics' not in st.session_state:
        st.session_state.metrics = {
            "engagement": 75,
            "comprehension": 68,
            "retention": 72
        }
    if 'alerts' not in st.session_state:
        st.session_state.alerts = [
            {"type": "warning", "message": "Pacing is faster than optimal - consider slowing down"},
            {"type": "success", "message": "Student participation is high - good questioning technique"}
        ]
    if 'content_used' not in st.session_state:
        st.session_state.content_used = 3
    if 'student_responses' not in st.session_state:
        st.session_state.student_responses = 85
    
    # Three-column layout
    col1, col2, col3 = st.columns([0.25, 0.5, 0.25])
    
    with col1:  # Activity Capture & Setup
        st.markdown('<div class="custom-card">', unsafe_allow_html=True)
        
        # ELCA Status and Controls
        st.markdown("### 📡 Capture Status")
        
        # Toggle for ELCA activation
        if st.button("🔄 " + ("Stop ELCA" if st.session_state.elca_active else "Start ELCA")):
            st.session_state.elca_active = not st.session_state.elca_active
            if st.session_state.elca_active:
                st.toast("ELCA activated and capturing classroom data")
            else:
                st.toast("ELCA stopped")
        
        # Status indicators
        st.markdown(f"""
            <div class="elca-card">
                <p><span class="status-indicator {'status-active' if st.session_state.elca_active else 'status-inactive'}"></span> 
                <strong>ELCA Status:</strong> {'Active' if st.session_state.elca_active else 'Inactive'}</p>
                
                <p><span class="status-indicator {'status-active' if st.session_state.elca_active else 'status-inactive'}"></span> 
                <strong>Voice Capture:</strong> {'Listening' if st.session_state.elca_active else 'Off'}</p>
                
                <p><span class="status-indicator {'status-active' if st.session_state.elca_active else 'status-inactive'}"></span> 
                <strong>Slide Sync:</strong> {'Connected' if st.session_state.elca_active else 'Disconnected'}</p>
                
                <p><span class="status-indicator {'status-warning' if st.session_state.elca_active else 'status-inactive'}"></span> 
                <strong>Student Devices:</strong> {f'{st.session_state.student_responses}% Connected' if st.session_state.elca_active else 'Not tracking'}</p>
            </div>
        """, unsafe_allow_html=True)
        
        # Lesson setup
        st.markdown("### 🔧 Lesson Setup")
        
        lesson_topic = st.text_input("Current Topic", value=st.session_state.current_lesson)
        if lesson_topic != st.session_state.current_lesson:
            st.session_state.current_lesson = lesson_topic
            st.toast(f"Lesson topic updated to: {lesson_topic}")
        
        grade_level = st.selectbox("Grade Level", ["Elementary (K-5)", "Middle School (6-8)", "High School (9-12)"])
        
        st.selectbox("Input Sources", ["Voice + Slides", "Voice Only", "Slides Only", "Voice + Slides + Student Devices"])
        
        # Quick stats
        st.markdown("### 📊 Live Stats")
        
        st.markdown(f"""
            <div class="metric-container">
                <div class="metric-box">
                    <div class="metric-value">{st.session_state.content_used}</div>
                    <div class="metric-label">Content Used</div>
                </div>
                <div class="metric-box">
                    <div class="metric-value">{st.session_state.metrics['engagement']}%</div>
                    <div class="metric-label">Engagement</div>
                </div>
                <div class="metric-box">
                    <div class="metric-value">{st.session_state.metrics['comprehension']}%</div>
                    <div class="metric-label">Comprehension</div>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        # Action buttons
        st.button("📥 Save Session")
        st.button("📤 Share Insights")
            
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:  # AI Tutor & Content Options
        st.markdown('<div class="custom-card">', unsafe_allow_html=True)
        
        # AI Tutor Display
        st.markdown("### 🤖 AI Tutor")
        
        selected = st.session_state.content_options[st.session_state.selected_content]
        
        # Alert bar based on metrics
        alert_type = "success" if st.session_state.metrics['comprehension'] >= 80 else "warning" if st.session_state.metrics['comprehension'] >= 60 else "danger"
        alert_message = "Students are following well - continue current approach" if alert_type == "success" else "Some confusion detected - consider simplifying" if alert_type == "warning" else "Significant confusion - try a different approach"
        
        st.markdown(f"""
            <div class="alert-bar {alert_type}">
                <span><i class="fas fa-{'check-circle' if alert_type == 'success' else 'exclamation-triangle'}"></i> {alert_message}</span>
            </div>
        """, unsafe_allow_html=True)
        
        # Tutor display with suggestion
        st.markdown(f"""
            <div class="tutor-display">
                <div class="tutor-avatar">🧠</div>
                <h4>AI Suggestion for {st.session_state.current_lesson}</h4>
                <p>I notice student comprehension is at {st.session_state.metrics['comprehension']}%. 
                Consider using the <strong>{selected['type']}: {selected['title']}</strong> to improve understanding.</p>
                <p><small>This content is predicted to increase comprehension by approximately {selected['impact']}%.</small></p>
            </div>
        """, unsafe_allow_html=True)
        
        if st.button("Project to Class"):
            st.toast(f"Projecting {selected['type']}: {selected['title']} to class")
        
        # Content options
        st.markdown("### 📚 Content Options")
        
        for i, option in enumerate(st.session_state.content_options):
            selected_class = "selected" if i == st.session_state.selected_content else ""
            st.markdown(f"""
                <div class="content-option {selected_class}" id="content_{i}">
                    <div style="display: flex; align-items: center;">
                        <div class="content-type-icon">{option['icon']}</div>
                        <div>
                            <strong>{option['type']}: {option['title']}</strong>
                            <span class="impact-badge">+{option['impact']}% impact</span>
                            <p>{option['description']}</p>
                        </div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
            # Since we can't directly make the divs clickable in Streamlit, add hidden buttons
            if st.button(f"Select {option['type']}", key=f"select_{i}", help=f"Use this {option['type']} content"):
                st.session_state.selected_content = i
                st.toast(f"Selected: {option['type']}: {option['title']}")
                st.experimental_rerun()
        
        # Real-time analytics
        st.markdown("### 📈 Live Analytics")
        
        # Engagement meter
        st.markdown("<strong>Engagement</strong>", unsafe_allow_html=True)
        st.markdown(f"""
            <div class="progress-container">
                <div class="progress-bar" style="width: {st.session_state.metrics['engagement']}%; background: {'#4CAF50' if st.session_state.metrics['engagement'] >= 80 else '#FF9800' if st.session_state.metrics['engagement'] >= 60 else '#F44336'}"></div>
            </div>
            <div style="display: flex; justify-content: space-between;">
                <small>Low</small>
                <small>{st.session_state.metrics['engagement']}%</small>
                <small>High</small>
            </div>
        """, unsafe_allow_html=True)
        
        # Comprehension meter
        st.markdown("<strong>Comprehension</strong>", unsafe_allow_html=True)
        st.markdown(f"""
            <div class="progress-container">
                <div class="progress-bar" style="width: {st.session_state.metrics['comprehension']}%; background: {'#4CAF50' if st.session_state.metrics['comprehension'] >= 80 else '#FF9800' if st.session_state.metrics['comprehension'] >= 60 else '#F44336'}"></div>
            </div>
            <div style="display: flex; justify-content: space-between;">
                <small>Low</small>
                <small>{st.session_state.metrics['comprehension']}%</small>
                <small>High</small>
            </div>
        """, unsafe_allow_html=True)
        
        # Retention meter
        st.markdown("<strong>Predicted Retention</strong>", unsafe_allow_html=True)
        st.markdown(f"""
            <div class="progress-container">
                <div class="progress-bar" style="width: {st.session_state.metrics['retention']}%; background: {'#4CAF50' if st.session_state.metrics['retention'] >= 80 else '#FF9800' if st.session_state.metrics['retention'] >= 60 else '#F44336'}"></div>
            </div>
            <div style="display: flex; justify-content: space-between;">
                <small>Low</small>
                <small>{st.session_state.metrics['retention']}%</small>
                <small>High</small>
            </div>
        """, unsafe_allow_html=True)
            
        st.markdown('</div>', unsafe_allow_html=True)

    with col3:  # Insights & Support
        st.markdown('<div class="custom-card">', unsafe_allow_html=True)
        
        # AI Assistant
        st.markdown("### 💬 AI Assistant")
        
        ai_query = st.text_area("Ask for specific content or help", placeholder="E.g., 'Find a video about chloroplasts'")
        if st.button("🔍 Get Suggestions"):
            if ai_query:
                with st.spinner("Generating suggestions..."):
                    response = generate_ai_response(f"As a classroom assistant, provide a brief response to: {ai_query}")
                    st.success("AI Assistant Response:")
                    st.write(response)
            else:
                st.warning("Please enter a query first")
        
        # Voice command option
        st.markdown("""
            <div style="text-align: center; margin: 1rem 0;">
                <button class="stButton">🎤 Voice Command</button>
                <p><small>Press and speak your request</small></p>
            </div>
        """, unsafe_allow_html=True)
        
        # Impact prediction
        st.markdown("### 🔮 Impact Prediction")
        
        # Create a Plotly chart for impact prediction
        selected = st.session_state.content_options[st.session_state.selected_content]
        
        fig = go.Figure()
        
        # Current metrics
        current_metrics = [st.session_state.metrics['engagement'], 
                          st.session_state.metrics['comprehension'], 
                          st.session_state.metrics['retention']]
        
        # Predicted metrics after using selected content
        predicted_metrics = [min(100, m + selected['impact'] * 0.8) for m in current_metrics]
        
        # Add current metrics
        fig.add_trace(go.Bar(
            x=['Engagement', 'Comprehension', 'Retention'],
            y=current_metrics,
            name='Current',
            marker_color='#2196F3'
        ))
        
        # Add predicted metrics
        fig.add_trace(go.Bar(
            x=['Engagement', 'Comprehension', 'Retention'],
            y=predicted_metrics,
            name='Predicted',
            marker_color='#4CAF50'
        ))
        
        fig.update_layout(
            barmode='group',
            margin=dict(l=20, r=20, t=30, b=20),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Historical impact
        st.markdown("### 📊 Historical Impact")
        
        # Create a line chart for historical impact
        hist_fig = go.Figure()
        
        # Sample historical data
        lessons = ['Lesson 1', 'Lesson 2', 'Lesson 3', 'Lesson 4', 'Current']
        engagement_history = [60, 68, 72, 70, st.session_state.metrics['engagement']]
        comprehension_history = [55, 62, 65, 64, st.session_state.metrics['comprehension']]
        
        hist_fig.add_trace(go.Scatter(
            x=lessons,
            y=engagement_history,
            mode='lines+markers',
            name='Engagement',
            line=dict(color='#2196F3')
        ))
        
        hist_fig.add_trace(go.Scatter(
            x=lessons,
            y=comprehension_history,
            mode='lines+markers',
            name='Comprehension',
            line=dict(color='#FF9800')
        ))
        
        hist_fig.update_layout(
            margin=dict(l=20, r=20, t=30, b=20),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        
        st.plotly_chart(hist_fig, use_container_width=True)
            
        st.markdown('</div>', unsafe_allow_html=True)

def content_updates_page():
    """Render the Content Update Center page."""
    st.title("🔄 Content Update Center")
    
    # Initialize content update data if not present
    if 'content_updates' not in st.session_state:
        st.session_state.content_updates = [
            {
                "id": 1,
                "title": "New Research on Learning Styles",
                "category": "Pedagogy",
                "date": "2023-05-10",
                "source": "Journal of Educational Psychology",
                "summary": "Recent research challenges traditional learning style theories, suggesting more flexible approaches.",
                "impact": "High",
                "integrated": False
            },
            {
                "id": 2,
                "title": "Updated Math Standards for Grade 5-8",
                "category": "Curriculum",
                "date": "2023-04-22",
                "source": "National Education Board",
                "summary": "New standards emphasize computational thinking and real-world problem solving.",
                "impact": "Medium",
                "integrated": False
            },
            {
                "id": 3,
                "title": "Digital Literacy Framework",
                "category": "Technology",
                "date": "2023-05-05",
                "source": "International Tech Education Association",
                                "summary": "New framework for teaching digital literacy skills across all subject areas.",
                "impact": "Medium",
                "integrated": False
            },
            {
                "id": 4,
                "title": "Social-Emotional Learning Guidelines",
                "category": "Well-being",
                "date": "2023-05-12",
                "source": "Child Development Institute",
                "summary": "Updated guidelines for incorporating SEL into daily classroom activities.",
                "impact": "High",
                "integrated": False
            },
            {
                "id": 5,
                "title": "Accessibility Standards Update",
                "category": "Inclusion",
                "date": "2023-04-30",
                "source": "Education Accessibility Board",
                "summary": "New requirements for making educational content accessible to all learners.",
                "impact": "Medium",
                "integrated": False
            }
        ]
    
    # Create tabs for different sections
    tabs = st.tabs(["Updates Feed", "Impact Analysis", "Integration Center"])
    
    with tabs[0]:  # Updates Feed
        st.markdown("### 📰 Latest Content Updates")
        
        # Filters
        col1, col2, col3 = st.columns(3)
        with col1:
            category_filter = st.selectbox("Filter by Category", ["All Categories", "Pedagogy", "Curriculum", "Technology", "Well-being", "Inclusion"])
        with col2:
            impact_filter = st.selectbox("Filter by Impact", ["All Impacts", "High", "Medium", "Low"])
        with col3:
            integration_filter = st.selectbox("Integration Status", ["All", "Integrated", "Not Integrated"])
        
        # Apply filters
        filtered_updates = st.session_state.content_updates
        if category_filter != "All Categories":
            filtered_updates = [u for u in filtered_updates if u["category"] == category_filter]
        if impact_filter != "All Impacts":
            filtered_updates = [u for u in filtered_updates if u["impact"] == impact_filter]
        if integration_filter == "Integrated":
            filtered_updates = [u for u in filtered_updates if u["integrated"]]
        elif integration_filter == "Not Integrated":
            filtered_updates = [u for u in filtered_updates if not u["integrated"]]
        
        # Display updates
        for update in filtered_updates:
            with st.container():
                st.markdown(f"""
                <div class="custom-card">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <h3 style="margin: 0;">{update["title"]}</h3>
                        <span class="tag-pill" style="background: {'#4CAF50' if update['impact'] == 'High' else '#FF9800' if update['impact'] == 'Medium' else '#9E9E9E'}; color: white;">
                            {update["impact"]} Impact
                        </span>
                    </div>
                    <p><strong>Category:</strong> {update["category"]} | <strong>Source:</strong> {update["source"]} | <strong>Date:</strong> {update["date"]}</p>
                    <p>{update["summary"]}</p>
                    <div style="display: flex; gap: 1rem;">
                        <button class="stButton">View Details</button>
                        <button class="stButton">{'✓ Integrated' if update['integrated'] else 'Integrate Now'}</button>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Since we can't make the buttons work directly in markdown, add functional buttons
                col1, col2 = st.columns(2)
                with col1:
                    if st.button(f"View Details for {update['id']}", key=f"view_{update['id']}"):
                        st.session_state.selected_update = update
                        st.toast(f"Viewing details for: {update['title']}")
                with col2:
                    if not update["integrated"]:
                        if st.button(f"Integrate {update['id']}", key=f"integrate_{update['id']}"):
                            # Find and update the item in the session state
                            for i, u in enumerate(st.session_state.content_updates):
                                if u["id"] == update["id"]:
                                    st.session_state.content_updates[i]["integrated"] = True
                                    st.session_state.integrated_updates.append(update["id"])
                                    st.toast(f"Successfully integrated: {update['title']}")
                                    st.experimental_rerun()
                                    break
    
    with tabs[1]:  # Impact Analysis
        st.markdown("### 📊 Content Update Impact Analysis")
        
        # Create metrics for integration stats
        integrated_count = sum(1 for u in st.session_state.content_updates if u["integrated"])
        total_count = len(st.session_state.content_updates)
        integration_rate = integrated_count / total_count * 100 if total_count > 0 else 0
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Updates", total_count)
        with col2:
            st.metric("Integrated Updates", integrated_count)
        with col3:
            st.metric("Integration Rate", f"{integration_rate:.1f}%")
        
        # Create a pie chart for category distribution
        category_counts = {}
        for update in st.session_state.content_updates:
            category = update["category"]
            if category in category_counts:
                category_counts[category] += 1
            else:
                category_counts[category] = 1
        
        fig = go.Figure(data=[go.Pie(
            labels=list(category_counts.keys()),
            values=list(category_counts.values()),
            hole=.4,
            marker_colors=['#4CAF50', '#2196F3', '#FF9800', '#F44336', '#9C27B0']
        )])
        
        fig.update_layout(
            title_text="Updates by Category",
            annotations=[dict(text='Categories', x=0.5, y=0.5, font_size=20, showarrow=False)]
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Create a bar chart for impact distribution
        impact_counts = {"High": 0, "Medium": 0, "Low": 0}
        for update in st.session_state.content_updates:
            impact = update["impact"]
            impact_counts[impact] += 1
        
        impact_fig = go.Figure(data=[
            go.Bar(
                x=list(impact_counts.keys()),
                y=list(impact_counts.values()),
                marker_color=['#4CAF50', '#FF9800', '#F44336']
            )
        ])
        
        impact_fig.update_layout(
            title_text="Updates by Impact Level",
            xaxis_title="Impact Level",
            yaxis_title="Number of Updates"
        )
        
        st.plotly_chart(impact_fig, use_container_width=True)
        
        # Integration timeline
        if st.session_state.integrated_updates:
            st.markdown("### 📅 Integration Timeline")
            
            # Create a dummy timeline for demonstration
            timeline_data = []
            for i, update_id in enumerate(st.session_state.integrated_updates):
                update = next((u for u in st.session_state.content_updates if u["id"] == update_id), None)
                if update:
                    # Create a fake integration date (for demo purposes)
                    integration_date = datetime.now() - pd.Timedelta(days=i*3)
                    timeline_data.append({
                        "title": update["title"],
                        "date": integration_date.strftime("%Y-%m-%d"),
                        "impact": update["impact"]
                    })
            
            # Sort by date
            timeline_data.sort(key=lambda x: x["date"], reverse=True)
            
            for item in timeline_data:
                st.markdown(f"""
                <div class="custom-card" style="border-left: 4px solid #4CAF50;">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <h4 style="margin: 0;">{item["title"]}</h4>
                        <span>{item["date"]}</span>
                    </div>
                    <p>Successfully integrated into curriculum</p>
                </div>
                """, unsafe_allow_html=True)
    
    with tabs[2]:  # Integration Center
        st.markdown("### 🔄 Integration Center")
        
        # Select an update to integrate
        non_integrated = [u for u in st.session_state.content_updates if not u["integrated"]]
        if non_integrated:
            selected_update_title = st.selectbox(
                "Select an update to integrate",
                options=[u["title"] for u in non_integrated],
                index=0
            )
            
            selected_update = next((u for u in non_integrated if u["title"] == selected_update_title), None)
            
            if selected_update:
                st.markdown(f"""
                <div class="custom-card">
                    <h3>{selected_update["title"]}</h3>
                    <p><strong>Category:</strong> {selected_update["category"]} | <strong>Impact:</strong> {selected_update["impact"]}</p>
                    <p>{selected_update["summary"]}</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Integration steps
                st.markdown("#### Integration Steps")
                
                step1 = st.checkbox("1. Review content update details", value=True)
                step2 = st.checkbox("2. Identify affected curriculum areas")
                step3 = st.checkbox("3. Modify lesson plans")
                step4 = st.checkbox("4. Update assessment methods")
                step5 = st.checkbox("5. Communicate changes to stakeholders")
                
                # Progress bar
                steps_completed = sum([step1, step2, step3, step4, step5])
                progress = steps_completed / 5
                
                st.progress(progress)
                st.write(f"Integration Progress: {int(progress * 100)}%")
                
                # AI-generated integration plan
                if st.button("Generate Integration Plan"):
                    with st.spinner("Generating integration plan..."):
                        prompt = f"""
                        Create a detailed integration plan for the following educational content update:
                        
                        Title: {selected_update["title"]}
                        Category: {selected_update["category"]}
                        Summary: {selected_update["summary"]}
                        Impact: {selected_update["impact"]}
                        
                        Include:
                        1. Specific steps for teachers to implement this update
                        2. Timeline recommendations
                        3. Resources needed
                        4. Assessment modifications
                        5. Professional development needs
                        
                        Keep it concise and practical.
                        """
                        
                        integration_plan = generate_ai_response(prompt)
                        
                        st.markdown(f"""
                        <div class="custom-card" style="background: rgba(76, 175, 80, 0.1);">
                            <h4>AI-Generated Integration Plan</h4>
                            <p>{integration_plan}</p>
                        </div>
                        """, unsafe_allow_html=True)
                
                # Complete integration button
                if st.button("Complete Integration"):
                    # Find and update the item in the session state
                    for i, u in enumerate(st.session_state.content_updates):
                        if u["id"] == selected_update["id"]:
                            st.session_state.content_updates[i]["integrated"] = True
                            st.session_state.integrated_updates.append(selected_update["id"])
                            st.success(f"Successfully integrated: {selected_update['title']}")
                            st.experimental_rerun()
                            break
        else:
            st.info("All updates have been integrated! Check back later for new content updates.")

def trend_analyzer_page():
    """Render the Trend Analyzer Hub page."""
    st.title("🔍 Trend Analyzer Hub")
    
    # Initialize trends data if not present
    if 'trends' not in st.session_state:
        st.session_state.trends = [
            {
                "id": 1,
                "title": "Project-Based Learning",
                "category": "Pedagogy",
                "adoption_rate": 68,
                "growth_rate": 12,
                "description": "Approach that allows students to gain knowledge and skills by working on projects that engage them in real-world problems.",
                "adopted": False
            },
            {
                "id": 2,
                "title": "Microlearning",
                "category": "Content Delivery",
                "adoption_rate": 42,
                "growth_rate": 28,
                "description": "Learning strategy that involves delivering content in small, focused units.",
                "adopted": False
            },
            {
                "id": 3,
                "title": "Gamification",
                "category": "Engagement",
                "adoption_rate": 55,
                "growth_rate": 15,
                "description": "Using game design elements in non-game contexts to increase engagement and motivation.",
                "adopted": False
            },
            {
                "id": 4,
                "title": "AI-Powered Personalization",
                "category": "Technology",
                "adoption_rate": 35,
                "growth_rate": 45,
                "description": "Using artificial intelligence to personalize learning experiences for individual students.",
                "adopted": False
            },
            {
                "id": 5,
                "title": "Social-Emotional Learning Integration",
                "category": "Well-being",
                "adoption_rate": 62,
                "growth_rate": 18,
                "description": "Incorporating social and emotional skill development into academic curriculum.",
                "adopted": False
            }
        ]
    
    # Create tabs for different sections
    tabs = st.tabs(["Trending Now", "Adoption Analysis", "Implementation Planner"])
    
    with tabs[0]:  # Trending Now
        st.markdown("### 📈 Current Educational Trends")
        
        # Filters
        col1, col2, col3 = st.columns(3)
        with col1:
            category_filter = st.selectbox("Filter by Category", ["All Categories", "Pedagogy", "Content Delivery", "Engagement", "Technology", "Well-being"])
        with col2:
            adoption_filter = st.selectbox("Filter by Adoption Rate", ["All", "High (>60%)", "Medium (30-60%)", "Low (<30%)"])
        with col3:
            growth_filter = st.selectbox("Filter by Growth Rate", ["All", "High (>25%)", "Medium (10-25%)", "Low (<10%)"])
        
        # Apply filters
        filtered_trends = st.session_state.trends
        if category_filter != "All Categories":
            filtered_trends = [t for t in filtered_trends if t["category"] == category_filter]
        if adoption_filter != "All":
            if adoption_filter == "High (>60%)":
                filtered_trends = [t for t in filtered_trends if t["adoption_rate"] > 60]
            elif adoption_filter == "Medium (30-60%)":
                filtered_trends = [t for t in filtered_trends if 30 <= t["adoption_rate"] <= 60]
            elif adoption_filter == "Low (<30%)":
                filtered_trends = [t for t in filtered_trends if t["adoption_rate"] < 30]
        if growth_filter != "All":
            if growth_filter == "High (>25%)":
                filtered_trends = [t for t in filtered_trends if t["growth_rate"] > 25]
            elif growth_filter == "Medium (10-25%)":
                filtered_trends = [t for t in filtered_trends if 10 <= t["growth_rate"] <= 25]
            elif growth_filter == "Low (<10%)":
                filtered_trends = [t for t in filtered_trends if t["growth_rate"] < 10]
        
        # Display trends
        for trend in filtered_trends:
            with st.container():
                st.markdown(f"""
                <div class="custom-card">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <h3 style="margin: 0;">{trend["title"]}</h3>
                        <span class="tag-pill" style="background: {'#4CAF50' if trend['growth_rate'] > 25 else '#FF9800' if trend['growth_rate'] > 10 else '#9E9E9E'}; color: white;">
                            {trend["growth_rate"]}% Growth
                        </span>
                    </div>
                    <p><strong>Category:</strong> {trend["category"]} | <strong>Adoption Rate:</strong> {trend["adoption_rate"]}%</p>
                    <p>{trend["description"]}</p>
                    <div style="display: flex; gap: 1rem;">
                        <button class="stButton">View Details</button>
                        <button class="stButton">{'✓ Adopted' if trend['adopted'] else 'Adopt This Trend'}</button>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Since we can't make the buttons work directly in markdown, add functional buttons
                col1, col2 = st.columns(2)
                with col1:
                    if st.button(f"View Details for {trend['id']}", key=f"view_trend_{trend['id']}"):
                        st.session_state.selected_trend = trend
                        st.toast(f"Viewing details for: {trend['title']}")
                with col2:
                    if not trend["adopted"]:
                        if st.button(f"Adopt {trend['id']}", key=f"adopt_{trend['id']}"):
                            # Find and update the item in the session state
                            for i, t in enumerate(st.session_state.trends):
                                if t["id"] == trend["id"]:
                                    st.session_state.trends[i]["adopted"] = True
                                    st.session_state.adopted_trends.append(trend["id"])
                                    st.toast(f"Successfully adopted: {trend['title']}")
                                    st.experimental_rerun()
                                    break
    
    with tabs[1]:  # Adoption Analysis
        st.markdown("### 📊 Trend Adoption Analysis")
        
        # Create metrics for adoption stats
        adopted_count = sum(1 for t in st.session_state.trends if t["adopted"])
        total_count = len(st.session_state.trends)
        adoption_rate = adopted_count / total_count * 100 if total_count > 0 else 0
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Trends", total_count)
        with col2:
            st.metric("Adopted Trends", adopted_count)
        with col3:
            st.metric("Your Adoption Rate", f"{adoption_rate:.1f}%")
        
        # Create a scatter plot for trend analysis
        fig = go.Figure()
        
        # Add data points for each trend
        for trend in st.session_state.trends:
            fig.add_trace(go.Scatter(
                x=[trend["adoption_rate"]],
                y=[trend["growth_rate"]],
                mode="markers+text",
                marker=dict(
                    size=trend["adoption_rate"] / 3 + 10,
                    color='#4CAF50' if trend["adopted"] else '#2196F3',
                    opacity=0.7,
                    line=dict(width=2, color='white')
                ),
                text=[trend["title"]],
                textposition="top center",
                name=trend["title"]
            ))
        
        # Add quadrant lines
        fig.add_shape(
            type="line",
            x0=50, y0=0,
            x1=50, y1=50,
            line=dict(color="gray", width=1, dash="dash")
        )
        
        fig.add_shape(
            type="line",
            x0=0, y0=20,
            x1=100, y1=20,
            line=dict(color="gray", width=1, dash="dash")
        )
        
        # Add quadrant labels
        fig.add_annotation(x=25, y=10, text="Low Adoption, Low Growth", showarrow=False)
        fig.add_annotation(x=75, y=10, text="High Adoption, Low Growth", showarrow=False)
        fig.add_annotation(x=25, y=35, text="Low Adoption, High Growth", showarrow=False)
        fig.add_annotation(x=75, y=35, text="High Adoption, High Growth", showarrow=False)
        
        fig.update_layout(
            title="Trend Analysis Matrix",
            xaxis_title="Adoption Rate (%)",
            yaxis_title="Growth Rate (%)",
            showlegend=False,
            xaxis=dict(range=[0, 100]),
            yaxis=dict(range=[0, 50])
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Adoption rate over time
        st.markdown("### 📈 Adoption Rate Over Time")
        
        # Create a line chart for adoption rate over time (simulated data)
        adoption_fig = go.Figure()
        
        # Sample data for demonstration
        months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun"]
        
        # Generate simulated adoption rates for each trend
        for trend in st.session_state.trends:
            # Create a simulated growth curve
            base_rate = max(5, trend["adoption_rate"] - 20)  # Starting point
            rates = [base_rate]
            
            for i in range(1, len(months)):
                # Add some randomness to the growth
                growth = trend["growth_rate"] / 6 * (1 + 0.2 * random.random())
                new_rate = min(100, rates[-1] + growth)
                rates.append(new_rate)
            
            adoption_fig.add_trace(go.Scatter(
                x=months,
                y=rates,
                mode="lines+markers",
                name=trend["title"],
                line=dict(width=3)
            ))
        
        adoption_fig.update_layout(
            title="Adoption Rate Over Time",
            xaxis_title="Month",
            yaxis_title="Adoption Rate (%)",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        
        st.plotly_chart(adoption_fig, use_container_width=True)
    
    with tabs[2]:  # Implementation Planner
        st.markdown("### 🔄 Implementation Planner")
        
        # Select a trend to implement
        non_adopted = [t for t in st.session_state.trends if not t["adopted"]]
        if non_adopted:
            selected_trend_title = st.selectbox(
                "Select a trend to implement",
                options=[t["title"] for t in non_adopted],
                index=0
            )
            
            selected_trend = next((t for t in non_adopted if t["title"] == selected_trend_title), None)
            
            if selected_trend:
                st.markdown(f"""
                <div class="custom-card">
                    <h3>{selected_trend["title"]}</h3>
                    <p><strong>Category:</strong> {selected_trend["category"]} | <strong>Adoption Rate:</strong> {selected_trend["adoption_rate"]}% | <strong>Growth Rate:</strong> {selected_trend["growth_rate"]}%</p>
                    <p>{selected_trend["description"]}</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Implementation steps
                st.markdown("#### Implementation Steps")
                
                step1 = st.checkbox("1. Research trend details and best practices", value=True)
                step2 = st.checkbox("2. Identify curriculum areas for implementation")
                step3 = st.checkbox("3. Develop implementation strategy")
                step4 = st.checkbox("4. Create assessment methods")
                step5 = st.checkbox("5. Train staff and communicate with stakeholders")
                
                # Progress bar
                steps_completed = sum([step1, step2, step3, step4, step5])
                progress = steps_completed / 5
                
                st.progress(progress)
                st.write(f"Implementation Progress: {int(progress * 100)}%")
                
                # AI-generated implementation plan
                if st.button("Generate Implementation Plan"):
                    with st.spinner("Generating implementation plan..."):
                        prompt = f"""
                        Create a detailed implementation plan for adopting the following educational trend:
                        
                        Trend: {selected_trend["title"]}
                        Category: {selected_trend["category"]}
                        Description: {selected_trend["description"]}
                        
                        Include:
                        1. Specific steps for teachers to implement this trend
                        2. Timeline recommendations
                        3. Resources needed
                        4. Assessment methods
                        5. Professional development needs
                        
                        Keep it concise and practical.
                        """
                        
                        implementation_plan = generate_ai_response(prompt)
                        
                        st.markdown(f"""
                        <div class="custom-card" style="background: rgba(76, 175, 80, 0.1);">
                            <h4>AI-Generated Implementation Plan</h4>
                            <p>{implementation_plan}</p>
                        </div>
                        """, unsafe_allow_html=True)
                
                # Complete implementation button
                if st.button("Complete Implementation"):
                    # Find and update the item in the session state
                    for i, t in enumerate(st.session_state.trends):
                        if t["id"] == selected_trend["id"]:
                            st.session_state.trends[i]["adopted"] = True
                            st.session_state.adopted_trends.append(selected_trend["id"])
                            st.success(f"Successfully adopted: {selected_trend['title']}")
                            st.experimental_rerun()
                            break
        else:
            st.info("You've adopted all current trends! Check back later for new educational trends.")

def voice_assistant_page():
    """Render the Voice Assistant page."""
    st.title("🔊 Voice Assistant")
    
    # Initialize voice history if not present
    if 'voice_history' not in st.session_state:
        st.session_state.voice_history = [
            {"role": "assistant", "content": "Hello! I'm your EduGauge Voice Assistant. How can I help you today?"}
        ]
    
    # Display chat history
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    for message in st.session_state.voice_history:
        if message["role"] == "user":
            st.markdown(f"""
            <div class="chat-message user-message">
                <div class="chat-bubble user-bubble">
                    <p>{message["content"]}</p>
                </div>
                <div class="chat-avatar user-avatar">👤</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="chat-message assistant-message">
                <div class="chat-avatar assistant-avatar">🤖</div>
                <div class="chat-bubble assistant-bubble">
                    <p>{message["content"]}</p>
                </div>
            </div>
            """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Voice input section
    st.markdown("### 🎤 Speak to Assistant")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        user_input = st.text_input("Type your question or command", key="voice_input")
    
    with col2:
        st.markdown('<div style="height: 38px; display: flex; align-items: center;">', unsafe_allow_html=True)
        voice_button = st.button("🎤 Speak", key="voice_button")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Process input
    if user_input:
        # Add user message to history
        st.session_state.voice_history.append({"role": "user", "content": user_input})
        
        # Generate response
        prompt = f"""
        You are an educational voice assistant. The teacher has asked: "{user_input}"
        
        Provide a helpful, concise response focused on educational needs.
        If they're asking for a specific educational resource or tool, suggest options.
        If they're asking about student data or metrics, provide a sample response.
        Keep your response under 100 words.
        """
        
        response = generate_ai_response(prompt)
        
        # Add assistant response to history
        st.session_state.voice_history.append({"role": "assistant", "content": response})
        
        # Clear input and rerun to update chat
        st.session_state.voice_input = ""
        st.experimental_rerun()
    
    # Voice commands section
    st.markdown("### 📋 Available Voice Commands")
    
    commands = [
        {"command": "Show my schedule", "description": "Displays your teaching schedule for today"},
        {"command": "Create a lesson plan", "description": "Starts the lesson planning wizard"},
        {"command": "Check student progress", "description": "Shows student performance metrics"},
        {"command": "Generate quiz questions", "description": "Creates quiz questions for current topic"},
        {"command": "Find resources for [topic]", "description": "Searches for teaching resources on a topic"},
        {"command": "Summarize today's lesson", "description": "Creates a summary of the current lesson"},
        {"command": "Start classroom timer", "description": "Begins a countdown timer for activities"},
        {"command": "Take attendance", "description": "Opens the attendance tracking tool"}
    ]
    
    for command in commands:
        st.markdown(f"""
        <div class="command-card">
            <strong>"{command["command"]}"</strong>
            <p>{command["description"]}</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Settings
    st.markdown("### ⚙️ Voice Assistant Settings")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.selectbox("Voice Type", ["Female (Default)", "Male", "Neutral"])
        st.slider("Speaking Rate", min_value=0.5, max_value=2.0, value=1.0, step=0.1)
    
    with col2:
        st.selectbox("Language", ["English (US)", "English (UK)", "Spanish", "French", "German"])
        st.checkbox("Enable wake word detection", value=False)
    
    # JavaScript for voice recognition
    st.markdown("""
        <script>
    const startRecognition = () => {
        const recognition = new webkitSpeechRecognition();
        recognition.continuous = false;
        recognition.interimResults = false;

        recognition.onresult = (event) => {
            const transcript = event.results[0][0].transcript;
            window.parent.postMessage({
                type: 'transcript',
                data: transcript
            }, '*');
        };
        
        recognition.start();
    };

    window.addEventListener('message', (event) => {
        if (event.data.type === 'trigger_recognition') {
            startRecognition();
        }
    });
    </script>
    """, unsafe_allow_html=True)

def trend_analyzer_page():
    """Render the Trend Analyzer Hub page."""
    st.title("🔍 Trend Analyzer Hub")
    
    # Initialize trends data if not present
    if 'trends' not in st.session_state:
        st.session_state.trends = [
            {
                "id": 1,
                "title": "AI-Enhanced Personalized Learning",
                "category": "Technology",
                "adoption_rate": 68,
                "impact_score": 4.2,
                "description": "Using AI to create personalized learning paths for each student based on their performance, preferences, and learning style.",
                "implementation_difficulty": "Medium",
                "resources_required": ["AI platform subscription", "Teacher training", "Data integration"],
                "adopted": False
            },
            {
                "id": 2,
                "title": "Microlearning Modules",
                "category": "Pedagogy",
                "adoption_rate": 72,
                "impact_score": 3.8,
                "description": "Breaking down complex topics into small, focused learning units that can be completed in 5-10 minutes.",
                "implementation_difficulty": "Low",
                "resources_required": ["Content creation tools", "Learning management system"],
                "adopted": False
            },
            {
                "id": 3,
                "title": "Project-Based Assessment",
                "category": "Assessment",
                "adoption_rate": 65,
                "impact_score": 4.5,
                "description": "Replacing traditional tests with comprehensive projects that demonstrate mastery of multiple skills and concepts.",
                "implementation_difficulty": "Medium",
                "resources_required": ["Assessment rubrics", "Project templates", "Collaboration tools"],
                "adopted": False
            },
            {
                "id": 4,
                "title": "Social-Emotional Learning Integration",
                "category": "Well-being",
                "adoption_rate": 78,
                "impact_score": 4.7,
                "description": "Embedding social-emotional learning objectives into academic content across all subjects.",
                "implementation_difficulty": "Medium",
                "resources_required": ["SEL curriculum", "Teacher training", "Assessment tools"],
                "adopted": False
            },
            {
                "id": 5,
                "title": "Gamification Elements",
                "category": "Engagement",
                "adoption_rate": 81,
                "impact_score": 4.0,
                "description": "Incorporating game mechanics like points, badges, and leaderboards to increase student motivation and engagement.",
                "implementation_difficulty": "Low",
                "resources_required": ["Gamification platform", "Digital badge system"],
                "adopted": False
            }
        ]
    
    # Initialize adopted trends if not present
    if 'adopted_trends' not in st.session_state:
        st.session_state.adopted_trends = []
    
    # Create tabs for different sections
    tabs = st.tabs(["Trend Explorer", "Impact Analysis", "Implementation Planner", "My Adopted Trends"])
    
    with tabs[0]:  # Trend Explorer
        st.markdown("### 🔎 Explore Educational Trends")
        
        # Filters
        col1, col2, col3 = st.columns(3)
        with col1:
            category_filter = st.selectbox("Filter by Category", ["All Categories", "Technology", "Pedagogy", "Assessment", "Well-being", "Engagement"])
        with col2:
            difficulty_filter = st.selectbox("Implementation Difficulty", ["All", "Low", "Medium", "High"])
        with col3:
            adoption_filter = st.slider("Minimum Adoption Rate", 0, 100, 50)
        
        # Apply filters
        filtered_trends = st.session_state.trends
        if category_filter != "All Categories":
            filtered_trends = [t for t in filtered_trends if t["category"] == category_filter]
        if difficulty_filter != "All":
            filtered_trends = [t for t in filtered_trends if t["implementation_difficulty"] == difficulty_filter]
        filtered_trends = [t for t in filtered_trends if t["adoption_rate"] >= adoption_filter]
        
        # Sort options
        sort_option = st.selectbox("Sort by", ["Impact Score (High to Low)", "Adoption Rate (High to Low)", "Implementation Difficulty (Easy to Hard)"])
        
        if sort_option == "Impact Score (High to Low)":
            filtered_trends = sorted(filtered_trends, key=lambda x: x["impact_score"], reverse=True)
        elif sort_option == "Adoption Rate (High to Low)":
            filtered_trends = sorted(filtered_trends, key=lambda x: x["adoption_rate"], reverse=True)
        elif sort_option == "Implementation Difficulty (Easy to Hard)":
            difficulty_order = {"Low": 1, "Medium": 2, "High": 3}
            filtered_trends = sorted(filtered_trends, key=lambda x: difficulty_order[x["implementation_difficulty"]])
        
        # Display trends
        for trend in filtered_trends:
            with st.container():
                st.markdown(f"""
                <div class="custom-card">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <h3 style="margin: 0;">{trend["title"]}</h3>
                        <span class="tag-pill" style="background: {'#4CAF50' if trend['impact_score'] >= 4.5 else '#FF9800' if trend['impact_score'] >= 4.0 else '#2196F3'}; color: white;">
                            Impact: {trend["impact_score"]}/5
                        </span>
                    </div>
                    <p><strong>Category:</strong> {trend["category"]} | <strong>Adoption Rate:</strong> {trend["adoption_rate"]}% | 
                    <strong>Difficulty:</strong> <span style="color: {'#4CAF50' if trend['implementation_difficulty'] == 'Low' else '#FF9800' if trend['implementation_difficulty'] == 'Medium' else '#F44336'}">
                        {trend["implementation_difficulty"]}
                    </span></p>
                    <p>{trend["description"]}</p>
                    <div>
                        <strong>Resources Required:</strong>
                        <ul style="margin-top: 0.5rem;">
                            {' '.join(f'<li>{resource}</li>' for resource in trend["resources_required"])}
                        </ul>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button(f"View Details for {trend['id']}", key=f"view_trend_{trend['id']}"):
                        st.session_state.selected_trend = trend
                        st.toast(f"Viewing details for: {trend['title']}")
                with col2:
                    if trend["id"] not in st.session_state.adopted_trends:
                        if st.button(f"Adopt Trend {trend['id']}", key=f"adopt_{trend['id']}"):
                            # Find and update the item in the session state
                            for i, t in enumerate(st.session_state.trends):
                                if t["id"] == trend["id"]:
                                    st.session_state.trends[i]["adopted"] = True
                                    st.session_state.adopted_trends.append(trend["id"])
                                    st.success(f"Successfully adopted: {trend['title']}")
                                    st.experimental_rerun()
                                    break
                    else:
                        st.success("✓ Already Adopted")
    
    with tabs[1]:  # Impact Analysis
        st.markdown("### 📊 Impact Analysis")
        
        # Create a scatter plot of trends
        fig = px.scatter(
            pd.DataFrame(st.session_state.trends),
            x="adoption_rate",
            y="impact_score",
            size="impact_score",
            color="category",
            hover_name="title",
            size_max=15,
            title="Trend Impact vs. Adoption Rate"
        )
        
        fig.update_layout(
            xaxis_title="Adoption Rate (%)",
            yaxis_title="Impact Score (1-5)",
            legend_title="Category"
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # AI-generated insights
        st.markdown("### 🧠 AI-Generated Insights")
        
        if st.button("Generate Trend Insights"):
            with st.spinner("Analyzing educational trends..."):
                prompt = """
                Based on these educational trends:
                1. AI-Enhanced Personalized Learning (Technology, 68% adoption, 4.2/5 impact)
                2. Microlearning Modules (Pedagogy, 72% adoption, 3.8/5 impact)
                3. Project-Based Assessment (Assessment, 65% adoption, 4.5/5 impact)
                4. Social-Emotional Learning Integration (Well-being, 78% adoption, 4.7/5 impact)
                5. Gamification Elements (Engagement, 81% adoption, 4.0/5 impact)
                
                Provide 3 key insights about these trends and what they suggest about the future of education.
                Format as bullet points and keep each insight under 50 words.
                """
                insights = generate_ai_response(prompt)
                st.markdown(f"""
                <div class="custom-card" style="background: rgba(33, 150, 243, 0.05);">
                    <h4>Trend Analysis Insights</h4>
                    {insights}
                </div>
                """, unsafe_allow_html=True)
    
    with tabs[2]:  # Implementation Planner
        st.markdown("### 📝 Implementation Planner")
        
        # Select a trend to implement
        trend_options = [t["title"] for t in st.session_state.trends]
        selected_trend_title = st.selectbox("Select a trend to implement", trend_options)
        selected_trend = next((t for t in st.session_state.trends if t["title"] == selected_trend_title), None)
        
        if selected_trend:
            st.markdown(f"""
            <div class="custom-card">
                <h3>{selected_trend["title"]}</h3>
                <p>{selected_trend["description"]}</p>
                <p><strong>Implementation Difficulty:</strong> {selected_trend["implementation_difficulty"]}</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Implementation timeline
            st.markdown("### 📅 Implementation Timeline")
            
            col1, col2 = st.columns(2)
            with col1:
                start_date = st.date_input("Start Date")
            with col2:
                implementation_duration = st.selectbox("Implementation Duration", ["2 weeks", "1 month", "3 months", "6 months"])
            
            # Implementation steps
            st.markdown("### 🔄 Implementation Steps")
            
            if st.button("Generate Implementation Plan"):
                with st.spinner("Creating implementation plan..."):
                    prompt = f"""
                    Create a step-by-step implementation plan for adopting "{selected_trend["title"]}" in a school.
                    The implementation difficulty is {selected_trend["implementation_difficulty"]}.
                    Resources required: {', '.join(selected_trend["resources_required"])}.
                    
                    Create a 5-step implementation plan with timeline, resources needed, and success metrics for each step.
                    Format as a numbered list with clear headings for each section.
                    """
                    implementation_plan = generate_ai_response(prompt)
                    st.markdown(f"""
                    <div class="custom-card" style="background: rgba(76, 175, 80, 0.05);">
                        <h4>Implementation Plan</h4>
                        {implementation_plan}
                    </div>
                    """, unsafe_allow_html=True)
            
            # Resource calculator
            st.markdown("### 💰 Resource Calculator")
            
            col1, col2 = st.columns(2)
            with col1:
                num_teachers = st.number_input("Number of Teachers", min_value=1, value=10)
            with col2:
                num_students = st.number_input("Number of Students", min_value=1, value=200)
            
            if st.button("Calculate Resource Needs"):
                with st.spinner("Calculating resources..."):
                    prompt = f"""
                    Calculate the resources needed to implement "{selected_trend["title"]}" for {num_teachers} teachers and {num_students} students.
                    Required resources include: {', '.join(selected_trend["resources_required"])}.
                    
                    Provide estimated costs, time commitments, and training needs.
                    Format as a bulleted list with clear categories.
                    """
                    resource_calculation = generate_ai_response(prompt)
                    st.markdown(f"""
                    <div class="custom-card" style="background: rgba(255, 152, 0, 0.05);">
                        <h4>Resource Calculation</h4>
                        {resource_calculation}
                    </div>
                    """, unsafe_allow_html=True)
    
    with tabs[3]:  # My Adopted Trends
        st.markdown("### ✅ My Adopted Trends")
        
        # Get adopted trends
        adopted_trend_ids = st.session_state.adopted_trends
        adopted_trends = [t for t in st.session_state.trends if t["id"] in adopted_trend_ids]
        
        if adopted_trends:
            for trend in adopted_trends:
                st.markdown(f"""
                <div class="custom-card" style="border-left: 4px solid #4CAF50;">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <h3 style="margin: 0;">{trend["title"]}</h3>
                        <span class="tag-pill" style="background: #4CAF50; color: white;">
                            Adopted
                        </span>
                    </div>
                    <p><strong>Category:</strong> {trend["category"]} | <strong>Impact Score:</strong> {trend["impact_score"]}/5</p>
                    <p>{trend["description"]}</p>
                    <div style="display: flex; gap: 1rem;">
                        <button class="stButton">Implementation Progress</button>
                        <button class="stButton">Resources</button>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Since we can't make the buttons work directly in markdown, add functional buttons
                col1, col2 = st.columns(2)
                with col1:
                    if st.button(f"Track Progress for {trend['id']}", key=f"progress_{trend['id']}"):
                        st.toast(f"Tracking progress for: {trend['title']}")
                with col2:
                    if st.button(f"Access Resources for {trend['id']}", key=f"resources_{trend['id']}"):
                        st.toast(f"Accessing resources for: {trend['title']}")
        else:
            st.info("You've not adopted any trends yet. Explore the Trend Explorer tab to find and adopt educational trends.")

def admin_dashboard_page():
    """Render the Admin Dashboard page."""
    st.title("⚙️ Admin Dashboard")
    
    # Create tabs for different admin sections
    tabs = st.tabs(["User Management", "System Analytics", "Content Management", "Settings"])
    
    with tabs[0]:  # User Management
        st.markdown("### 👥 User Management")
        
        # Sample user data
        if 'users' not in st.session_state:
            st.session_state.users = [
                {"id": 1, "name": "Sarah Johnson", "email": "sarah.j@eduschool.org", "role": "Teacher", "department": "Math", "status": "Active"},
                {"id": 2, "name": "Michael Chen", "email": "m.chen@eduschool.org", "role": "Teacher", "department": "Science", "status": "Active"},
                {"id": 3, "name": "Emily Rodriguez", "email": "e.rodriguez@eduschool.org", "role": "Teacher", "department": "English", "status": "Active"},
                {"id": 4, "name": "David Kim", "email": "d.kim@eduschool.org", "role": "Teacher", "department": "History", "status": "Inactive"},
                {"id": 5, "name": "Lisa Patel", "email": "l.patel@eduschool.org", "role": "Admin", "department": "Administration", "status": "Active"}
            ]
        
        # User filters
        col1, col2, col3 = st.columns(3)
        with col1:
            role_filter = st.selectbox("Filter by Role", ["All Roles", "Teacher", "Admin", "Student"])
        with col2:
            department_filter = st.selectbox("Filter by Department", ["All Departments", "Math", "Science", "English", "History", "Administration"])
        with col3:
            status_filter = st.selectbox("Filter by Status", ["All Statuses", "Active", "Inactive"])
        
        # Apply filters
        filtered_users = st.session_state.users
        if role_filter != "All Roles":
            filtered_users = [u for u in filtered_users if u["role"] == role_filter]
        if department_filter != "All Departments":
            filtered_users = [u for u in filtered_users if u["department"] == department_filter]
        if status_filter != "All Statuses":
            filtered_users = [u for u in filtered_users if u["status"] == status_filter]
        
        # Display users
        for user in filtered_users:
            st.markdown(f"""
            <div class="custom-card">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <h3 style="margin: 0;">{user["name"]}</h3>
                    <span class="tag-pill" style="background: {'#4CAF50' if user['status'] == 'Active' else '#F44336'}; color: white;">
                        {user["status"]}
                    </span>
                </div>
                <p><strong>Email:</strong> {user["email"]} | <strong>Role:</strong> {user["role"]} | <strong>Department:</strong> {user["department"]}</p>
                <div style="display: flex; gap: 1rem;">
                    <button class="stButton">Edit User</button>
                    <button class="stButton">Reset Password</button>
                    <button class="stButton">{'Deactivate' if user['status'] == 'Active' else 'Activate'}</button>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        # Add new user
        st.markdown("### ➕ Add New User")
        
        with st.form(key="add_user_form"):
            col1, col2 = st.columns(2)
            with col1:
                new_name = st.text_input("Full Name")
                new_email = st.text_input("Email")
                new_role = st.selectbox("Role", ["Teacher", "Admin", "Student"])
            with col2:
                new_department = st.selectbox("Department", ["Math", "Science", "English", "History", "Administration"])
                new_password = st.text_input("Initial Password", type="password")
                new_confirm_password = st.text_input("Confirm Password", type="password")
            
            submit = st.form_submit_button("Add User")
            if submit:
                if new_password != new_confirm_password:
                    st.error("Passwords do not match!")
                elif not new_name or not new_email:
                    st.error("Name and email are required!")
                else:
                    new_id = max([u["id"] for u in st.session_state.users]) + 1
                    st.session_state.users.append({
                        "id": new_id,
                        "name": new_name,
                        "email": new_email,
                        "role": new_role,
                        "department": new_department,
                        "status": "Active"
                    })
                    st.success(f"User {new_name} added successfully!")
    
    with tabs[1]:  # System Analytics
        st.markdown("### 📊 System Analytics")
        
        # Usage metrics
        st.markdown("#### 📈 Usage Metrics")
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Active Users", "42", delta="↑ 5")
        with col2:
            st.metric("Lesson Plans Created", "156", delta="↑ 23")
        with col3:
            st.metric("AI Interactions", "1,248", delta="↑ 312")
        with col4:
            st.metric("Resources Shared", "89", delta="↑ 12")
        
        # Create a usage chart
        usage_data = pd.DataFrame({
            'Date': pd.date_range(start='2023-01-01', periods=12, freq='M'),
            'Active Users': [25, 28, 30, 32, 35, 38, 40, 42, 45, 48, 50, 52],
            'Lesson Plans': [80, 95, 110, 120, 125, 130, 135, 140, 145, 150, 155, 160],
            'AI Interactions': [300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400]
        })
        
        usage_fig = go.Figure()
        
        usage_fig.add_trace(go.Scatter(
            x=usage_data['Date'],
            y=usage_data['Active Users'],
            mode='lines+markers',
            name='Active Users',
            line=dict(color='#2196F3')
        ))
        
        usage_fig.add_trace(go.Scatter(
            x=usage_data['Date'],
            y=usage_data['Lesson Plans'],
            mode='lines+markers',
            name='Lesson Plans',
            line=dict(color='#4CAF50')
        ))
        
        usage_fig.add_trace(go.Scatter(
            x=usage_data['Date'],
            y=usage_data['AI Interactions'] / 10,  # Scale down for better visualization
            mode='lines+markers',
            name='AI Interactions (÷10)',
            line=dict(color='#FF9800')
        ))
        
        usage_fig.update_layout(
            title='System Usage Trends',
            xaxis_title='Month',
            yaxis_title='Count',
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        
        st.plotly_chart(usage_fig, use_container_width=True)
        
        # Feature usage
        st.markdown("#### 🔍 Feature Usage")
        
        feature_data = pd.DataFrame({
            'Feature': ['Lesson Planning', 'Student Performance', 'Professional Development', 'Collaboration', 'Well-Being', 
                       'Observation', 'Classroom Management', 'Alignment Optimizer', 'Resource Hub', 'Voice Assistant'],
            'Usage': [85, 72, 65, 58, 45, 62, 70, 48, 75, 40]
        })
        
        feature_fig = px.bar(
            feature_data,
            x='Feature',
            y='Usage',
            title='Feature Usage (%)',
            color='Usage',
            color_continuous_scale='Viridis'
        )
        
        feature_fig.update_layout(
            xaxis_title='Feature',
            yaxis_title='Usage (%)',
            coloraxis_showscale=False
        )
        
        st.plotly_chart(feature_fig, use_container_width=True)
        
        # System performance
        st.markdown("#### ⚡ System Performance")
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Response Time (ms)**")
            st.progress(0.2)
            st.text("Average: 120ms (Good)")
        with col2:
            st.markdown("**Error Rate (%)**")
            st.progress(0.05)
            st.text("Average: 0.5% (Excellent)")
    
    with tabs[2]:  # Content Management
        st.markdown("### 📚 Content Management")
        
        # Content categories
        content_categories = ["Lesson Templates", "Assessment Resources", "Professional Development", "Educational Videos", "Interactive Activities"]
        selected_category = st.selectbox("Select Content Category", content_categories)
        
        # Display content items
        st.markdown(f"#### {selected_category}")
        
        # Sample content items
        content_items = [
            {"title": f"{selected_category} Item 1", "author": "Content Team", "date": "2023-05-01", "status": "Published"},
            {"title": f"{selected_category} Item 2", "author": "Sarah Johnson", "date": "2023-04-15", "status": "Published"},
            {"title": f"{selected_category} Item 3", "author": "Michael Chen", "date": "2023-05-10", "status": "Draft"},
            {"title": f"{selected_category} Item 4", "author": "Content Team", "date": "2023-03-22", "status": "Published"},
            {"title": f"{selected_category} Item 5", "author": "Emily Rodriguez", "date": "2023-05-05", "status": "Review"}
        ]
        
        for item in content_items:
            st.markdown(f"""
            <div class="custom-card">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <h3 style="margin: 0;">{item["title"]}</h3>
                    <span class="tag-pill" style="background: {'#4CAF50' if item['status'] == 'Published' else '#FF9800' if item['status'] == 'Review' else '#9E9E9E'}; color: white;">
                        {item["status"]}
                    </span>
                </div>
                <p><strong>Author:</strong> {item["author"]} | <strong>Date:</strong> {item["date"]}</p>
                <div style="display: flex; gap: 1rem;">
                    <button class="stButton">Edit</button>
                    <button class="stButton">Preview</button>
                    <button class="stButton">{'Unpublish' if item['status'] == 'Published' else 'Publish'}</button>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        # Add new content
        st.markdown("### ➕ Add New Content")
        
        with st.form(key="add_content_form"):
            new_title = st.text_input("Content Title")
            new_category = st.selectbox("Category", content_categories)
            new_description = st.text_area("Description")
            new_file = st.file_uploader("Upload Content File")
            
            submit = st.form_submit_button("Add Content")
            if submit:
                if not new_title or not new_description:
                    st.error("Title and description are required!")
                else:
                    st.success(f"Content '{new_title}' added successfully!")
    
    with tabs[3]:  # Settings
        st.markdown("### ⚙️ System Settings")
        
        # General settings
        st.markdown("#### 🔧 General Settings")
        
        col1, col2 = st.columns(2)
        with col1:
            st.text_input("School Name", value="EduGauge Academy")
            st.text_input("Administrator Email", value="admin@eduschool.org")
            st.selectbox("Default Language", ["English", "Spanish", "French", "German"])
        with col2:
            st.selectbox("Academic Year", ["2023-2024", "2024-2025"])
            st.selectbox("Grade System", ["A-F", "Percentage", "1-10", "Custom"])
            st.selectbox("Time Zone", ["Eastern Time (ET)", "Central Time (CT)", "Mountain Time (MT)", "Pacific Time (PT)"])
        
        # API settings
        st.markdown("#### 🔌 API Settings")
        
        st.text_input("Google Gemini API Key", value="••••••••••••••••••••••••", type="password")
        st.text_input("OpenAI API Key (Optional)", value="", type="password")
        st.checkbox("Enable API Usage Tracking", value=True)
        st.slider("API Rate Limit (requests per minute)", min_value=10, max_value=100, value=60, step=10)
        
        # Backup settings
        st.markdown("#### 💾 Backup & Recovery")
        
        col1, col2 = st.columns(2)
        with col1:
            st.selectbox("Backup Frequency", ["Daily", "Weekly", "Monthly"])
            st.selectbox("Backup Storage", ["Cloud Storage", "Local Server", "Both"])
        with col2:
            st.date_input("Last Backup Date", value=datetime.now())
            st.button("Backup Now")
        
        # Save settings
        if st.button("Save All Settings"):
            st.success("Settings saved successfully!")

def student_performance_page():
    """Render the Student Performance page."""
    st.title("📊 Student Performance")
    
    # Create tabs for different views
    tabs = st.tabs(["Class Overview", "Individual Students", "Performance Trends", "Assessments"])
    
    with tabs[0]:  # Class Overview
        st.markdown("### 📚 Class Overview")
        st.write("This is the Student Performance page. Class overview content will appear here.")
        
    with tabs[1]:  # Individual Students
        st.markdown("### 👨‍🎓 Individual Student Performance")
        st.write("Individual student performance data will appear here.")
        
    with tabs[2]:  # Performance Trends
        st.markdown("### 📈 Performance Trends")
        st.write("Performance trend analysis will appear here.")
        
    with tabs[3]:  # Assessments
        st.markdown("### 📝 Assessments")
        st.write("Assessment data and tools will appear here.")

def professional_development_page():
    """Render the Professional Development page."""
    st.title("🎓 Professional Development")
    st.write("This is the Professional Development page. Content will appear here.")

def collaboration_page():
    """Render the Collaboration page."""
    st.title("🤝 Collaboration")
    st.write("This is the Collaboration page. Content will appear here.")

def wellbeing_page():
    """Render the Well-Being page."""
    st.title("💖 Well-Being")
    st.write("This is the Well-Being page. Content will appear here.")

def observation_feedback_page():
    """Render the Observation and Feedback page."""
    st.title("👁️ Observation and Feedback")
    st.write("This is the Observation and Feedback page. Content will appear here.")

def classroom_management_page():
    """Render the Classroom Management page."""
    st.title("🏫 Classroom Management")
    st.write("This is the Classroom Management page. Content will appear here.")

def alignment_optimizer_page():
    """Render the Alignment Optimizer page."""
    st.title("📚 Alignment Optimizer")
    st.write("This is the Alignment Optimizer page. Content will appear here.")

def resource_hub_page():
    """Render the Resource Hub page."""
    st.title("📚 Resource Hub")
    st.write("This is the Resource Hub page. Content will appear here.")

def story_builder_page():
    """Render the Story Builder page."""
    st.title("📚 Story Builder")
    st.write("This is the Story Builder page. Content will appear here.")

def recap_studio_page():
    """Render the Recap Studio page."""
    st.title("📚 Recap Studio")
    st.write("This is the Recap Studio page. Content will appear here.")

def case_study_vault_page():
    """Render the Case Study Vault page."""
    st.title("📚 Case Study Vault")
    st.write("This is the Case Study Vault page. Content will appear here.")

def student_engagement_monitor_page():
    """Render the Student Engagement Monitor page."""
    st.title("👩‍🏫 Student Engagement Monitor")
    st.write("This is the Student Engagement Monitor page. Content will appear here.")

def communication_studio_page():
    """Render the Communication Studio page."""
    st.title("💬 Communication Studio")
    st.write("This is the Communication Studio page. Content will appear here.")

def global_exchange_hub_page():
    """Render the Global Exchange Hub page."""
    st.title("🌍 Global Exchange Hub")
    st.write("This is the Global Exchange Hub page. Content will appear here.")

# Main application routing
def main():
    """Main function to render the EduGauge application."""
    st.set_page_config(page_title="EduGauge", page_icon="🎓", layout="wide", initial_sidebar_state="expanded")
    initialize_session_state()
    apply_theme()
    render_sidebar()
    page = st.session_state["current_page"]

    if page == "Home":
        st.markdown('<h1 style="font-size: 2.5rem; font-weight: 700; color: var(--primary);"><i class="fas fa-home"></i> EduGauge Home</h1>', unsafe_allow_html=True)
        st.markdown('<p style="font-size: 1.25rem; color: var(--text);">Empowering Teachers for Impactful Learning</p>', unsafe_allow_html=True)
        
                # Dashboard layout
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("### 📊 Your Dashboard")
            
            # Quick stats
            stats_cols = st.columns(4)
            with stats_cols[0]:
                st.metric("Lesson Plans", "12", "+2")
            with stats_cols[1]:
                st.metric("Student Progress", "78%", "+5%")
            with stats_cols[2]:
                st.metric("PD Hours", "24.5", "+2.5")
            with stats_cols[3]:
                st.metric("Well-being Score", "85%", "+3%")
            
            # Recent activity
            st.markdown("### 🔔 Recent Activity")
            
            activities = [
                {"type": "lesson", "title": "Photosynthesis Lesson Plan", "time": "2 hours ago"},
                {"type": "feedback", "title": "Observation Feedback Received", "time": "Yesterday"},
                {"type": "assessment", "title": "Math Quiz Graded", "time": "2 days ago"},
                {"type": "resource", "title": "Shared Science Lab Resources", "time": "3 days ago"}
            ]
            
            for activity in activities:
                icon = "📝" if activity["type"] == "lesson" else "💬" if activity["type"] == "feedback" else "📊" if activity["type"] == "assessment" else "📚"
                st.markdown(f"""
                <div class="activity-card">
                    <div class="activity-icon">{icon}</div>
                    <div class="activity-content">
                        <strong>{activity["title"]}</strong>
                        <p>{activity["time"]}</p>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            # Upcoming deadlines
            st.markdown("### ⏰ Upcoming Deadlines")
            
            deadlines = [
                {"title": "Submit Q3 Grades", "date": "May 15, 2023", "days_left": 3, "status": "Not Started"},
                {"title": "Professional Development Workshop", "date": "May 20, 2023", "days_left": 8, "status": "Registered"},
                {"title": "Parent-Teacher Conferences", "date": "May 25-26, 2023", "days_left": 13, "status": "Scheduled"}
            ]
            
            for deadline in deadlines:
                status_color = "#4CAF50" if deadline["status"] == "Completed" else "#FF9800" if deadline["status"] == "In Progress" or deadline["status"] == "Registered" or deadline["status"] == "Scheduled" else "#F44336"
                st.markdown(f"""
                <div class="deadline-card">
                    <div class="deadline-header">
                        <h4>{deadline["title"]}</h4>
                        <span class="deadline-status" style="background: {status_color};">{deadline["status"]}</span>
                    </div>
                    <p>Due: {deadline["date"]} <span class="deadline-days">({deadline["days_left"]} days left)</span></p>
                </div>
                """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("### 🔮 AI Insights")
            
            # AI-generated insights
            insights = [
                "Students showed 15% improvement in engagement when using interactive simulations in science lessons.",
                "Consider scheduling challenging topics earlier in the day when student focus is highest.",
                "Your assessment variety has increased by 30% this semester, correlating with better student outcomes."
            ]
            
            for insight in insights:
                st.markdown(f"""
                <div class="insight-card">
                    <i class="fas fa-lightbulb" style="color: #FFC107;"></i>
                    <p>{insight}</p>
                </div>
                """, unsafe_allow_html=True)
            
            # Quick actions
            st.markdown("### ⚡ Quick Actions")
            
            actions = [
                {"title": "Create New Lesson Plan", "icon": "fas fa-plus-circle", "color": "#4CAF50"},
                {"title": "Grade Assignments", "icon": "fas fa-check-circle", "color": "#2196F3"},
                {"title": "Schedule Observation", "icon": "fas fa-calendar-plus", "color": "#9C27B0"},
                {"title": "Access Resource Hub", "icon": "fas fa-book", "color": "#FF9800"}
            ]
            
            action_cols = st.columns(2)
            for i, action in enumerate(actions):
                with action_cols[i % 2]:
                    st.markdown(f"""
                    <div class="action-button" style="background: {action['color']};">
                        <i class="{action['icon']}"></i>
                        <span>{action['title']}</span>
                    </div>
                    """, unsafe_allow_html=True)
                    st.button(action["title"], key=f"action_{i}")
            
            # Professional development progress
            st.markdown("### 🎓 PD Progress")
            
            pd_progress = 65  # Percentage complete
            st.progress(pd_progress / 100)
            st.markdown(f"<p>{pd_progress}% complete - 24.5/40 hours</p>", unsafe_allow_html=True)
            
            # Recommended PD
            st.markdown("### 📚 Recommended for You")
            
            recommendations = [
                {"title": "Data-Driven Instruction Workshop", "type": "Workshop", "duration": "3 hours"},
                {"title": "Inclusive Classroom Strategies", "type": "Course", "duration": "8 hours"},
                {"title": "EdTech Tools for Engagement", "type": "Webinar", "duration": "1 hour"}
            ]
            
            for rec in recommendations:
                st.markdown(f"""
                <div class="recommendation-card">
                    <h4>{rec["title"]}</h4>
                    <p><span class="rec-type">{rec["type"]}</span> • {rec["duration"]}</p>
                    <button class="stButton">Explore</button>
                </div>
                """, unsafe_allow_html=True)
    
    elif page == "Lesson Planning":
        st.markdown('<h1 style="font-size: 2.5rem; font-weight: 700; color: var(--primary);"><i class="fas fa-book-open"></i> Lesson Planning</h1>', unsafe_allow_html=True)
        
        # Create tabs for different lesson planning tools
        tabs = st.tabs(["AI Lesson Creator", "Template Library", "My Lesson Plans", "Curriculum Mapper"])
        
        with tabs[0]:  # AI Lesson Creator
            st.markdown("### 🤖 AI-Powered Lesson Creator")
            
            # Lesson parameters
            col1, col2 = st.columns(2)
            
            with col1:
                subject = st.selectbox("Subject", ["Science", "Math", "English", "Social Studies", "Art", "Physical Education"])
                grade_level = st.selectbox("Grade Level", ["K-2", "3-5", "6-8", "9-12"])
                duration = st.selectbox("Lesson Duration", ["30 minutes", "45 minutes", "60 minutes", "90 minutes"])
            
            with col2:
                topic = st.text_input("Lesson Topic", placeholder="e.g., Photosynthesis, Fractions, Shakespeare...")
                standards = st.multiselect("Standards Alignment", ["Common Core", "NGSS", "State Standards", "IB", "AP"])
                learning_styles = st.multiselect("Learning Styles to Include", ["Visual", "Auditory", "Kinesthetic", "Reading/Writing"])
            
            # Advanced options
            with st.expander("Advanced Options"):
                col1, col2 = st.columns(2)
                with col1:
                    st.checkbox("Include differentiation strategies", value=True)
                    st.checkbox("Include assessment tools", value=True)
                    st.checkbox("Include digital resources", value=True)
                with col2:
                    st.checkbox("Focus on critical thinking", value=False)
                    st.checkbox("Include group activities", value=True)
                    st.checkbox("Add extension activities", value=False)
            
            # Generate button
            if st.button("🔮 Generate Lesson Plan"):
                if not topic:
                    st.error("Please enter a lesson topic")
                else:
                    with st.spinner("Creating your lesson plan..."):
                        # Simulate AI generation with a delay
                        time.sleep(2)
                        
                        # Generate lesson plan using AI
                        prompt = f"""
                        Create a detailed lesson plan for a {duration} {subject} lesson for {grade_level} students on the topic of {topic}.
                        Include the following components:
                        - Learning objectives
                        - Standards alignment with {', '.join(standards)}
                        - Materials needed
                        - Warm-up activity (5-10 minutes)
                        - Main instruction (including teacher and student activities)
                        - Practice/Application
                        - Assessment
                        - Closure
                        - Differentiation strategies
                        
                        The lesson should accommodate {', '.join(learning_styles)} learning styles.
                        Format the response as a structured lesson plan with clear headings and bullet points.
                        """
                        
                        lesson_plan = generate_ai_response(prompt)
                        
                        # Display the generated lesson plan
                        st.markdown("### 📝 Your Generated Lesson Plan")
                        st.markdown(lesson_plan)
                        
                        # Save options
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.button("💾 Save Lesson Plan")
                        with col2:
                            st.button("🖨️ Print Lesson Plan")
                        with col3:
                            st.button("✏️ Edit Lesson Plan")
        
        with tabs[1]:  # Template Library
            st.markdown("### 📚 Lesson Template Library")
            
            # Search and filter
            col1, col2, col3 = st.columns(3)
            with col1:
                template_subject = st.selectbox("Filter by Subject", ["All Subjects", "Science", "Math", "English", "Social Studies", "Art", "Physical Education"], key="template_subject")
            with col2:
                template_grade = st.selectbox("Filter by Grade", ["All Grades", "K-2", "3-5", "6-8", "9-12"], key="template_grade")
            with col3:
                template_search = st.text_input("Search Templates", placeholder="Search by keyword...", key="template_search")
            
            # Template gallery
            st.markdown("### Browse Templates")
            
            templates = [
                {"title": "5E Science Investigation", "subject": "Science", "grade": "6-8", "rating": 4.8, "downloads": 1245},
                {"title": "Math Problem-Based Learning", "subject": "Math", "grade": "3-5", "rating": 4.6, "downloads": 987},
                {"title": "Literature Circle Discussion", "subject": "English", "grade": "9-12", "rating": 4.7, "downloads": 1102},
                {"title": "Historical Document Analysis", "subject": "Social Studies", "grade": "9-12", "rating": 4.5, "downloads": 876},
                {"title": "Art Critique Workshop", "subject": "Art", "grade": "6-8", "rating": 4.4, "downloads": 654},
                {"title": "Physical Fitness Circuit", "subject": "Physical Education", "grade": "K-2", "rating": 4.9, "downloads": 1432}
            ]
            
            # Filter templates based on selections
            if template_subject != "All Subjects":
                templates = [t for t in templates if t["subject"] == template_subject]
            if template_grade != "All Grades":
                templates = [t for t in templates if t["grade"] == template_grade]
            if template_search:
                templates = [t for t in templates if template_search.lower() in t["title"].lower()]
            
            # Display templates in a grid
            template_cols = st.columns(3)
            for i, template in enumerate(templates):
                with template_cols[i % 3]:
                    st.markdown(f"""
                    <div class="template-card">
                        <h4>{template["title"]}</h4>
                        <p><strong>Subject:</strong> {template["subject"]} | <strong>Grade:</strong> {template["grade"]}</p>
                        <p>⭐ {template["rating"]} | 📥 {template["downloads"]} downloads</p>
                        <button class="stButton">Use Template</button>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Since we can't make the buttons work directly in markdown, add functional buttons
                    st.button(f"Use {template['title']}", key=f"use_template_{i}")
        
        with tabs[2]:  # My Lesson Plans
            st.markdown("### 📂 My Lesson Plans")
            
            # Sample lesson plans
            if not st.session_state.get("lesson_plans"):
                st.session_state.lesson_plans = [
                    {"title": "Photosynthesis Process", "subject": "Science", "grade": "6-8", "created": "2023-04-15", "last_used": "2023-05-01"},
                    {"title": "Shakespeare's Sonnets", "subject": "English", "grade": "9-12", "created": "2023-03-22", "last_used": "2023-04-12"},
                    {"title": "Fractions and Decimals", "subject": "Math", "grade": "3-5", "created": "2023-05-02", "last_used": "2023-05-03"},
                    {"title": "Civil Rights Movement", "subject": "Social Studies", "grade": "6-8", "created": "2023-02-18", "last_used": "2023-04-05"}
                ]
            
            # Search and sort
            col1, col2 = st.columns(2)
            with col1:
                lesson_search = st.text_input("Search My Lessons", placeholder="Search by title or subject...", key="lesson_search")
            with col2:
                sort_by = st.selectbox("Sort By", ["Recently Created", "Recently Used", "Alphabetical"], key="sort_by")
            
            # Filter and sort lesson plans
            filtered_lessons = st.session_state.lesson_plans
            if lesson_search:
                filtered_lessons = [l for l in filtered_lessons if lesson_search.lower() in l["title"].lower() or lesson_search.lower() in l["subject"].lower()]
            
            if sort_by == "Recently Created":
                filtered_lessons.sort(key=lambda x: x["created"], reverse=True)
            elif sort_by == "Recently Used":
                filtered_lessons.sort(key=lambda x: x["last_used"], reverse=True)
            else:  # Alphabetical
                filtered_lessons.sort(key=lambda x: x["title"])
            
            # Display lesson plans
            for lesson in filtered_lessons:
                st.markdown(f"""
                <div class="lesson-card">
                    <div class="lesson-header">
                        <h4>{lesson["title"]}</h4>
                        <span class="lesson-subject">{lesson["subject"]} ({lesson["grade"]})</span>
                    </div>
                    <p><strong>Created:</strong> {lesson["created"]} | <strong>Last Used:</strong> {lesson["last_used"]}</p>
                    <div class="lesson-actions">
                        <button class="stButton">View</button>
                        <button class="stButton">Edit</button>
                        <button class="stButton">Duplicate</button>
                        <button class="stButton">Delete</button>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            # Add new lesson plan button
            st.button("➕ Create New Lesson Plan", key="create_new_lesson")
        
        with tabs[3]:  # Curriculum Mapper
            st.markdown("### 🗺️ Curriculum Mapper")
            
            # Term selection
            term = st.selectbox("Select Term", ["Fall 2023", "Spring 2024", "Fall 2024"])
            
            # Subject and grade selection
            col1, col2 = st.columns(2)
            with col1:
                map_subject = st.selectbox("Subject", ["Science", "Math", "English", "Social Studies"], key="map_subject")
            with col2:
                map_grade = st.selectbox("Grade Level", ["K-2", "3-5", "6-8", "9-12"], key="map_grade")
            
            # Display curriculum map
            st.markdown("### Curriculum Overview")
            
            # Sample curriculum data
            curriculum_data = {
                "Science": {
                    "6-8": [
                        {"unit": "Unit 1: Scientific Method", "weeks": "Weeks 1-3", "standards": "NGSS MS-PS1-1, MS-PS1-2", "status": "Complete"},
                        {"unit": "Unit 2: Matter and Energy", "weeks": "Weeks 4-7", "standards": "NGSS MS-PS1-3, MS-PS1-4", "status": "In Progress"},
                        {"unit": "Unit 3: Earth Systems", "weeks": "Weeks 8-11", "standards": "NGSS MS-ESS2-1, MS-ESS2-2", "status": "Not Started"},
                        {"unit": "Unit 4: Life Sciences", "weeks": "Weeks 12-15", "standards": "NGSS MS-LS1-1, MS-LS1-2", "status": "Not Started"},
                        {"unit": "Unit 5: Engineering Design", "weeks": "Weeks 16-18", "standards": "NGSS MS-ETS1-1, MS-ETS1-2", "status": "Not Started"}
                    ]
                },
                "Math": {
                    "3-5": [
                        {"unit": "Unit 1: Place Value", "weeks": "Weeks 1-3", "standards": "CCSS.MATH.3.NBT.A.1", "status": "Complete"},
                        {"unit": "Unit 2: Addition and Subtraction", "weeks": "Weeks 4-6", "standards": "CCSS.MATH.3.NBT.A.2", "status": "Complete"},
                        {"unit": "Unit 3: Multiplication", "weeks": "Weeks 7-10", "standards": "CCSS.MATH.3.OA.A.1", "status": "In Progress"},
                        {"unit": "Unit 4: Division", "weeks": "Weeks 11-14", "standards": "CCSS.MATH.3.OA.A.2", "status": "Not Started"},
                        {"unit": "Unit 5: Fractions", "weeks": "Weeks 15-18", "standards": "CCSS.MATH.3.NF.A.1", "status": "Not Started"}
                    ]
                }
            }
            
            # Display curriculum units
            if map_subject in curriculum_data and map_grade in curriculum_data[map_subject]:
                units = curriculum_data[map_subject][map_grade]
                
                for unit in units:
                    status_color = "#4CAF50" if unit["status"] == "Complete" else "#FF9800" if unit["status"] == "In Progress" else "#9E9E9E"
                    st.markdown(f"""
                    <div class="curriculum-unit">
                        <div class="unit-header">
                            <h4>{unit["unit"]}</h4>
                            <span class="unit-status" style="background: {status_color};">{unit["status"]}</span>
                        </div>
                        <p><strong>Timeline:</strong> {unit["weeks"]}</p>
                        <p><strong>Standards:</strong> {unit["standards"]}</p>
                        <div class="unit-actions">
                            <button class="stButton">View Details</button>
                            <button class="stButton">Edit Unit</button>
                            <button class="stButton">Add Lessons</button>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("No curriculum data available for the selected subject and grade level.")
            
            # Add new unit button
            st.button("➕ Add New Unit", key="add_new_unit")
    
    elif page == "Student Performance":
        student_performance_page()
    
    elif page == "Professional Development":
        professional_development_page()
    
    elif page == "Collaboration":
        collaboration_page()
    
    elif page == "Well-Being":
        wellbeing_page()
    
    elif page == "Observation and Feedback":
        observation_feedback_page()
    
    elif page == "Classroom Management":
        classroom_management_page()
    
    elif page == "Alignment Optimizer":
        alignment_optimizer_page()
    
    elif page == "Resource Hub":
        resource_hub_page()
    
    elif page == "Story Builder":
        story_builder_page()
    
    elif page == "Recap Studio":
        recap_studio_page()
    
    elif page == "Case Study Vault":
        case_study_vault_page()
    
    elif page == "Student Engagement Monitor":
        student_engagement_monitor_page()
    
    elif page == "Communication Studio":
        communication_studio_page()
    
    elif page == "Global Exchange Hub":
        global_exchange_hub_page()
    
    elif page == "Content Update Center":
        content_updates_page()
    
    elif page == "Trend Analyzer Hub":
        trend_analyzer_page()
    
    elif page == "ELCA Control Center":
        elca_page()
    
    elif page == "Voice Assistant":
        voice_assistant_page()
    
    elif page == "Admin Dashboard":
        admin_dashboard_page()

# Run the application
if __name__ == "__main__":
    main()