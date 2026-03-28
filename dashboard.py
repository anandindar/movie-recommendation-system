"""Movie Recommendation System - Login/Signup Dashboard"""
import streamlit as st
from auth import authenticate_user, register_user, init_db
import base64
import os
from pathlib import Path

st.set_page_config(page_title="Movie Recommendation System", layout="wide")

# ── Load and encode background image ──────────────────────────────────────────
def get_image_as_base64(image_path):
    """Convert image to base64 for CSS background"""
    try:
        if os.path.exists(image_path):
            with open(image_path, "rb") as image_file:
                return base64.b64encode(image_file.read()).decode()
    except Exception as e:
        pass
    return None

# Try multiple paths to find the image
possible_paths = [
    "frontend/Avenger.jpg",
    "./frontend/Avenger.jpg",
    os.path.join(os.path.dirname(__file__), "frontend", "Avenger.jpg"),
]

image_base64 = None
for path in possible_paths:
    if os.path.exists(path):
        image_base64 = get_image_as_base64(path)
        if image_base64:
            break

# ── Build CSS with or without background image ──────────────────────────────
if image_base64:
    bg_style = f"""
    background: linear-gradient(135deg, rgba(5, 8, 20, 0.92) 0%, rgba(26, 31, 53, 0.92) 50%, rgba(45, 27, 78, 0.92) 100%), 
                url('data:image/jpeg;base64,{image_base64}');
    background-size: cover;
    background-position: center;
    background-attachment: fixed;
    """
else:
    bg_style = "background: linear-gradient(135deg, #050814 0%, #1a1f35 50%, #2d1b4e 100%);"

# ── Build CSS with or without background image ──────────────────────────────
if image_base64:
    bg_style = f"""
    background: linear-gradient(135deg, rgba(5, 8, 20, 0.92) 0%, rgba(26, 31, 53, 0.92) 50%, rgba(45, 27, 78, 0.92) 100%), 
                url('data:image/jpeg;base64,{image_base64}');
    background-size: cover;
    background-position: center;
    background-attachment: fixed;
    """
else:
    bg_style = "background: linear-gradient(135deg, #050814 0%, #1a1f35 50%, #2d1b4e 100%);"

css_template = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Poppins:wght@400;500;600;700;800&display=swap');

/* Main background */
body, html, [data-testid="stAppViewContainer"], [data-testid="stSidebarNav"] {{
    {bg_style} !important;
}}

.main {{
    {bg_style} !important;
}}

[data-testid="stAppViewContainer"] {{
    background-attachment: fixed !important;
}}

/* Hide sidebar */
[data-testid="stSidebarNav"] {{
    display: none !important;
}}

/* Main title styling */
.main-title {{
    font-size: 48px;
    font-weight: 800;
    font-family: 'Bebas Neue', sans-serif;
    color: #e50914;
    text-align: center;
    text-shadow: 0 4px 12px rgba(229, 9, 20, 0.6);
    letter-spacing: 2px;
    margin-bottom: 10px;
    text-transform: uppercase;
}}

/* Form container */
.form-container {{
    background: rgba(10, 15, 35, 0.85);
    border: 2px solid rgba(229, 9, 20, 0.5);
    border-radius: 16px;
    padding: 40px;
    backdrop-filter: blur(10px);
    box-shadow: 0 8px 40px rgba(0, 0, 0, 0.6), 0 0 40px rgba(229, 9, 20, 0.2);
    max-width: 500px;
    margin: 20px auto;
}}

/* Form title */
.form-title {{
    font-size: 28px;
    font-weight: 800;
    font-family: 'Bebas Neue', sans-serif;
    color: #ffffff;
    text-align: center;
    margin-bottom: 30px;
    letter-spacing: 1px;
}}

/* Input styling */
.stTextInput > div > div > input,
.stTextInput input {{
    background: rgba(0, 0, 0, 0.9) !important;
    color: #ffffff !important;
    border: 2px solid rgba(229, 9, 20, 0.4) !important;
    border-radius: 8px !important;
    padding: 12px 16px !important;
    font-family: 'Poppins', sans-serif !important;
    font-size: 14px !important;
}}

.stTextInput > div > div > input:focus,
.stTextInput input:focus {{
    border-color: rgba(229, 9, 20, 0.8) !important;
    box-shadow: 0 0 12px rgba(229, 9, 20, 0.3) !important;
}}

/* Label styling */
.stTextInput > label, label {{
    color: #b8c5d6 !important;
    font-family: 'Poppins', sans-serif !important;
    font-weight: 600 !important;
    font-size: 13px !important;
    text-transform: uppercase !important;
    letter-spacing: 0.5px !important;
}}

/* Button styling */
.stButton > button {{
    background: linear-gradient(90deg, #e50914 0%, #ff4b5c 100%) !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 8px !important;
    padding: 12px 24px !important;
    font-weight: 700 !important;
    font-family: 'Poppins', sans-serif !important;
    text-transform: uppercase !important;
    letter-spacing: 0.5px !important;
    box-shadow: 0 4px 16px rgba(229, 9, 20, 0.5) !important;
    transition: all 0.3s ease !important;
    width: 100% !important;
    font-size: 14px !important;
}}

.stButton > button:hover {{
    background: linear-gradient(90deg, #ff4b5c 0%, #e50914 100%) !important;
    box-shadow: 0 8px 24px rgba(229, 9, 20, 0.7) !important;
    transform: translateY(-2px) !important;
}}

/* Tab buttons styling */
.tab-button {{
    background: rgba(229, 9, 20, 0.8) !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    padding: 10px 20px !important;
    margin: 5px !important;
    font-weight: 700 !important;
    font-family: 'Poppins', sans-serif !important;
}}

/* Divider styling */
hr {{
    border: 1px solid rgba(229, 9, 20, 0.3) !important;
    margin: 30px 0 !important;
}}

/* Success/Error messages */
.stSuccess {{
    background: rgba(0, 200, 100, 0.15) !important;
    border: 1px solid rgba(0, 200, 100, 0.5) !important;
    border-radius: 8px !important;
    color: #00ff7f !important;
}}

.stError {{
    background: rgba(229, 9, 20, 0.15) !important;
    border: 1px solid rgba(229, 9, 20, 0.5) !important;
    border-radius: 8px !important;
    color: #ff6b9d !important;
}}

.stInfo {{
    background: rgba(100, 150, 255, 0.15) !important;
    border: 1px solid rgba(100, 150, 255, 0.5) !important;
    border-radius: 8px !important;
    color: #88ccff !important;
}}

/* Responsive */
@media (max-width: 768px) {{
    .main-title {{
        font-size: 32px !important;
    }}
    .form-container {{
        padding: 24px !important;
        margin: 10px !important;
    }}
}}

</style>
"""

st.markdown(css_template, unsafe_allow_html=True)

# Init DB
if "db_initialized" not in st.session_state:
    init_db()
    st.session_state.db_initialized = True

# Session state
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "auth_tab" not in st.session_state:
    st.session_state.auth_tab = "LOGIN"

# Check login
if st.session_state.logged_in:
    st.switch_page("pages/app.py")
    st.stop()

# ── PAGE CONTENT ──────────────────────────────────────────────────────────────
st.markdown('<h1 class="main-title">🎬 Movie Recommendation System 🎬</h1>', unsafe_allow_html=True)
st.markdown('<p style="text-align: center; color: #b8c5d6; font-size: 16px; font-family: Poppins;">Discover your next favorite movie</p>', unsafe_allow_html=True)

# Tab selector
col1, col2 = st.columns(2)
with col1:
    if st.button("🔐 LOGIN", use_container_width=True, key="btn_login"):
        st.session_state.auth_tab = "LOGIN"
        st.rerun()

with col2:
    if st.button("📝 SIGN UP", use_container_width=True, key="btn_signup"):
        st.session_state.auth_tab = "SIGNUP"
        st.rerun()

# Form content
form_col1, form_col2, form_col3 = st.columns([1, 1.2, 1])

with form_col2:
    st.markdown('<div class="form-container">', unsafe_allow_html=True)
    
    if st.session_state.auth_tab == "LOGIN":
        st.markdown('<h2 class="form-title">🔐 LOGIN</h2>', unsafe_allow_html=True)
        
        username = st.text_input("Username", placeholder="Enter your username")
        password = st.text_input("Password", type="password", placeholder="Enter your password")
        
        if st.button("🔐 Login", use_container_width=True):
            if not username or not password:
                st.error("❌ Please enter username and password")
            else:
                success, msg = authenticate_user(username, password)
                if success:
                    st.session_state.logged_in = True
                    st.session_state.username = username
                    st.success(f"✅ {msg}")
                    st.balloons()
                    st.switch_page("pages/app.py")
                else:
                    st.error(f"❌ {msg}")
    else:
        st.markdown('<h2 class="form-title">📝 SIGN UP</h2>', unsafe_allow_html=True)
        
        username = st.text_input("Username", placeholder="Choose a username", key="su_username")
        email = st.text_input("Email", placeholder="Enter your email", key="su_email")
        password = st.text_input("Password", type="password", placeholder="Create a password (min 6 chars)", key="su_password")
        confirm = st.text_input("Confirm Password", type="password", placeholder="Confirm your password", key="su_confirm")
        
        if st.button("📝 Sign Up", use_container_width=True):
            if not username or not email or not password:
                st.error("❌ Please fill in all fields")
            elif password != confirm:
                st.error("❌ Passwords don't match")
            elif len(password) < 6:
                st.error("❌ Password must be at least 6 characters")
            else:
                success, msg = register_user(username, email, password)
                if success:
                    st.success(f"✅ {msg}")
                    st.balloons()
                    st.session_state.logged_in = True
                    st.session_state.username = username
                    st.info("🎬 Redirecting to dashboard...")
                    st.switch_page("pages/app.py")
                else:
                    st.error(f"❌ {msg}")
    
    st.markdown('</div>', unsafe_allow_html=True)
