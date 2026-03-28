"""Movie Recommendation System - Login/Signup Dashboard"""
import streamlit as st
from auth import authenticate_user, register_user, init_db
import base64
import os
from pathlib import Path
from math import ceil
from PIL import Image, ImageOps

st.set_page_config(page_title="Movie Recommendation System", layout="wide")


def get_image_as_base64(image: Image.Image) -> str:
    """Encode a PIL image to base64 string."""
    from io import BytesIO

    buffer = BytesIO()
    image.save(buffer, format="JPEG", quality=85)
    return base64.b64encode(buffer.getvalue()).decode("utf-8")


@st.cache_resource(show_spinner=False)
def build_collage_base64(tile_width: int = 220, tile_height: int = 320) -> str | None:
    """Build a collage from all images in the frontend folder and return base64.

    This uses every poster you placed in the frontend/ directory and
    arranges them in a grid so the background is rich and works on both
    laptop and mobile (background-size: cover handles responsiveness).
    """
    frontend_dir = Path(__file__).resolve().parent / "frontend"
    if not frontend_dir.exists():
        return None

    image_paths: list[Path] = []
    for pattern in ("*.jpg", "*.jpeg", "*.png", "*.webp"):
        image_paths.extend(frontend_dir.glob(pattern))

    if not image_paths:
        return None

    # More columns so more posters are visible at once
    cols = min(6, max(3, len(image_paths)))
    rows = ceil(len(image_paths) / cols)

    collage = Image.new("RGB", (cols * tile_width, rows * tile_height), (5, 8, 20))

    for idx, path in enumerate(image_paths):
        try:
            img = Image.open(path).convert("RGB")
        except Exception:
            continue

        # Fill the tile completely (no gaps) while keeping aspect ratio
        tile = ImageOps.fit(img, (tile_width, tile_height), Image.LANCZOS)
        x = (idx % cols) * tile_width
        y = (idx // cols) * tile_height
        collage.paste(tile, (x, y))

    return get_image_as_base64(collage)


# Build collage once and reuse it
image_base64 = build_collage_base64()

if image_base64:
    bg_style = f"""
    background: linear-gradient(135deg, rgba(5, 8, 20, 0.80) 0%, rgba(26, 31, 53, 0.80) 50%, rgba(45, 27, 78, 0.80) 100%),
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

/* Center content area */
.block-container {{
    padding-top: 60px !important;
    padding-bottom: 60px !important;
    max-width: 900px !important;
    margin-left: auto !important;
    margin-right: auto !important;
}}

/* Main title styling */
.main-title {{
    font-size: 48px;
    font-weight: 800;
    font-family: 'Bebas Neue', sans-serif;
    color: #b794ff;
    text-align: center;
    text-shadow: 0 4px 16px rgba(107, 70, 193, 0.7);
    letter-spacing: 2px;
    margin-bottom: 10px;
    text-transform: uppercase;
}}

/* Form container */
.form-container {{
    background: transparent;
    border: none;
    border-radius: 0;
    padding: 0;
    backdrop-filter: none;
    box-shadow: none;
    max-width: 500px;
    margin: 24px auto 12px auto;
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
    border: 1px solid rgba(139, 92, 246, 0.6) !important;
    border-radius: 8px !important;
    padding: 12px 16px !important;
    font-family: 'Poppins', sans-serif !important;
    font-size: 14px !important;
}}

.stTextInput > div > div > input:focus,
.stTextInput input:focus {{
    border-color: rgba(167, 139, 250, 1) !important;
    box-shadow: 0 0 14px rgba(129, 140, 248, 0.55) !important;
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
    background: rgba(15, 23, 42, 0.95) !important;
    color: #a855f7 !important;
    border: none !important;
    border-radius: 8px !important;
    padding: 12px 24px !important;
    font-weight: 700 !important;
    font-family: 'Poppins', sans-serif !important;
    text-transform: uppercase !important;
    letter-spacing: 0.5px !important;
    border: 1px solid rgba(139, 92, 246, 0.8) !important;
    box-shadow: 0 4px 14px rgba(15, 23, 42, 0.8) !important;
    transition: all 0.3s ease !important;
    width: 100% !important;
    font-size: 14px !important;
}}

.stButton > button:hover {{
    background: rgba(15, 23, 42, 1) !important;
    box-shadow: 0 8px 24px rgba(15, 23, 42, 0.95) !important;
    transform: translateY(-2px) !important;
}}

/* Tab buttons styling */
.tab-button {{
    background: rgba(124, 58, 237, 0.9) !important;
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
    border: 1px solid rgba(139, 92, 246, 0.35) !important;
    margin: 30px 0 !important;
}}

/* Success/Error messages */
.stSuccess {{
    background: rgba(16, 185, 129, 0.08) !important;
    border-left: 3px solid rgba(16, 185, 129, 0.9) !important;
    border-radius: 4px !important;
    color: #bbf7d0 !important;
}}

.stError {{
    background: rgba(248, 113, 113, 0.08) !important;
    border-left: 3px solid rgba(248, 113, 113, 0.9) !important;
    border-radius: 4px !important;
    color: #fecaca !important;
}}

.stInfo {{
    background: rgba(59, 130, 246, 0.08) !important;
    border-left: 3px solid rgba(59, 130, 246, 0.9) !important;
    border-radius: 4px !important;
    color: #bfdbfe !important;
}}

/* Responsive */
@media (max-width: 768px) {{
    .main-title {{
        font-size: 32px !important;
    }}
    .form-container {{
        padding: 24px 20px !important;
        margin: 16px !important;
    }}
    .form-title {{
        font-size: 22px !important;
        margin-bottom: 20px !important;
    }}
    .block-container {{
        padding-top: 32px !important;
        padding-bottom: 40px !important;
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
st.markdown('<h1 class="main-title">Movie Recommendation System</h1>', unsafe_allow_html=True)
st.markdown('<p style="text-align: center; color: #d1d5db; font-size: 15px; font-family: Poppins;">Sign in to continue to your personalized recommendations</p>', unsafe_allow_html=True)

# Form content
form_col1, form_col2, form_col3 = st.columns([1, 1.2, 1])

with form_col2:
    st.markdown('<div class="form-container">', unsafe_allow_html=True)
    
    if st.session_state.auth_tab == "LOGIN":
        st.markdown('<h2 class="form-title">Login</h2>', unsafe_allow_html=True)
        
        username = st.text_input("Username", placeholder="Enter your username")
        password = st.text_input("Password", type="password", placeholder="Enter your password")
        
        if st.button("Login", use_container_width=True):
            if not username or not password:
                st.error("❌ Please enter username and password")
            else:
                success, msg = authenticate_user(username, password)
                if success:
                    st.session_state.logged_in = True
                    st.session_state.username = username
                    st.success(msg)
                    st.switch_page("pages/app.py")
                else:
                    st.error(f"❌ {msg}")
    else:
        st.markdown('<h2 class="form-title">Create account</h2>', unsafe_allow_html=True)
        
        username = st.text_input("Username", placeholder="Choose a username", key="su_username")
        email = st.text_input("Email", placeholder="Enter your email", key="su_email")
        password = st.text_input("Password", type="password", placeholder="Create a password (min 6 chars)", key="su_password")
        confirm = st.text_input("Confirm Password", type="password", placeholder="Confirm your password", key="su_confirm")
        
        if st.button("Create account", use_container_width=True):
            if not username or not email or not password:
                st.error("❌ Please fill in all fields")
            elif password != confirm:
                st.error("❌ Passwords don't match")
            elif len(password) < 6:
                st.error("❌ Password must be at least 6 characters")
            else:
                success, msg = register_user(username, email, password)
                if success:
                    st.success(msg)
                    st.session_state.logged_in = True
                    st.session_state.username = username
                    st.info("Redirecting to dashboard...")
                    st.switch_page("pages/app.py")
                else:
                    st.error(f"❌ {msg}")

    st.markdown('</div>', unsafe_allow_html=True)

# Bottom "Sign up" toggle button (only shown on login view)
st.markdown("<div style='height: 24px;'></div>", unsafe_allow_html=True)
if st.session_state.auth_tab == "LOGIN":
    if st.button("Sign up", use_container_width=True, key="btn_signup_bottom"):
        st.session_state.auth_tab = "SIGNUP"
        st.rerun()
