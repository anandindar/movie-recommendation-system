import streamlit as st
from utils import load_frontend_images, build_background, background_css, VALID_USERNAME, VALID_PASSWORD

st.set_page_config(page_title="Movie Recommendation System – Login", layout="wide")

# ── Build background ────────────────────────────────────────────────────────
movie_images = load_frontend_images()
grid_layout_css, background_html = build_background(movie_images)

# ── Inject CSS ──────────────────────────────────────────────────────────────
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Poppins:wght@400;500;600;700;800&display=swap');

:root {{
    --primary-red: #e50914;
}}

{background_css(grid_layout_css)}

/* ── Header title ── */
.header-title {{
    font-size: clamp(34px, 4.6vw, 54px);
    font-weight: 900;
    margin: 0;
    letter-spacing: 2px;
    line-height: 1;
    font-family: 'Poppins', sans-serif;
    color: #ffffff !important;
    -webkit-text-fill-color: #ffffff !important;
    text-shadow: 0 3px 15px rgba(0,0,0,1), 0 0 20px rgba(229,9,20,0.8);
    animation: titleGlow 2.2s ease-in-out infinite alternate;
}}

@keyframes titleGlow {{
    from {{ text-shadow: 0 2px 14px rgba(0,0,0,1), 0 0 10px rgba(255,255,255,0.22), 0 0 22px rgba(229,9,20,0.35); }}
    to   {{ text-shadow: 0 2px 14px rgba(0,0,0,1), 0 0 18px rgba(255,255,255,0.35), 0 0 40px rgba(229,9,20,0.6), 0 0 58px rgba(229,9,20,0.4); }}
}}

/* ── Login card ── */
.login-box {{
    background: transparent !important;
    padding: 0 !important;
    margin: 0 auto;
    max-width: 760px;
    box-shadow: none !important;
    border: none !important;
    position: relative;
    z-index: 4;
}}

.welcome-box {{
    background: rgba(10, 14, 28, 0.68) !important;
    border: 2px solid rgba(229, 9, 20, 0.8) !important;
    border-radius: 18px;
    padding: 28px 24px 22px 24px;
    margin-bottom: 16px;
    box-shadow: 0 8px 32px rgba(0,0,0,0.5), 0 0 24px rgba(229,9,20,0.3) !important;
    backdrop-filter: blur(5px);
}}

.login-title {{
    font-size: clamp(46px, 6vw, 64px);
    font-family: 'Bebas Neue', sans-serif;
    letter-spacing: 1.6px;
    font-weight: 700;
    color: #ffffff !important;
    -webkit-text-fill-color: #ffffff !important;
    text-shadow: 0 3px 15px rgba(0,0,0,1), 0 0 15px rgba(229,9,20,0.9);
}}

.login-subtitle {{
    color: #ffffff !important;
    -webkit-text-fill-color: #ffffff !important;
    font-size: 16px;
    font-weight: 700;
    text-shadow: 0 2px 10px rgba(0,0,0,1);
}}

.field-label {{
    color: #ffffff !important;
    -webkit-text-fill-color: #ffffff !important;
    font-size: 16px;
    font-weight: 900;
    letter-spacing: 0.5px;
    text-shadow: 0 2px 8px rgba(0,0,0,0.8);
    background: rgba(6, 10, 20, 0.24);
    padding: 4px 8px;
    border-radius: 8px;
    display: inline-block;
}}

/* ── Input fields ── */
div[data-testid="stTextInput"] {{ background: transparent !important; margin-bottom: 14px !important; }}

div[data-testid="stTextInput"] > div,
div[data-testid="stTextInput"] > div > div,
div[data-testid="stTextInput"] [data-baseweb="form-control"],
div[data-testid="stTextInput"] [data-baseweb="input"],
div[data-testid="stTextInput"] [data-baseweb="base-input"] {{
    background: transparent !important; border: none !important;
    box-shadow: none !important; outline: none !important;
    padding: 0 !important; margin: 0 !important;
    min-height: 0 !important; height: auto !important;
}}

div[data-testid="stTextInput"] [data-testid="stWidgetLabel"],
div[data-testid="stTextInput"] label,
div[data-testid="stTextInput"] label p,
div[data-testid="stTextInput"] label span,
div[data-testid="stTextInput"] [data-testid="stWidgetInstructions"],
div[data-testid="stTextInput"] small,
[data-testid="stWidgetLabel"] p,
[data-testid="stWidgetLabel"] span,
.stTextInput label {{
    display: none !important; height: 0 !important;
    margin: 0 !important; padding: 0 !important; overflow: hidden !important;
    background: transparent !important; border: none !important;
}}

div[data-testid="stTextInput"] [data-baseweb="form-control"] > *:not([data-baseweb="base-input"]) {{
    display: none !important; height: 0 !important;
    margin: 0 !important; padding: 0 !important; overflow: hidden !important;
}}

div[data-testid="stTextInput"] [data-baseweb="form-control"]::before,
div[data-testid="stTextInput"] [data-baseweb="form-control"]::after,
div[data-testid="stTextInput"] [data-baseweb="base-input"]::before,
div[data-testid="stTextInput"] [data-baseweb="base-input"]::after {{
    display: none !important; content: none !important;
    background: transparent !important; border: none !important; height: 0 !important;
}}

div[data-testid="stTextInput"] input {{
    background: rgba(14, 20, 42, 0.85) !important;
    color: #ffffff !important;
    -webkit-text-fill-color: #ffffff !important;
    caret-color: #ffffff !important;
    border: 1.5px solid rgba(255, 180, 200, 0.75) !important;
    border-radius: 12px !important;
    padding: 13px 16px !important;
    font-size: 16px !important;
    font-family: 'Poppins', sans-serif !important;
    width: 100% !important;
    box-shadow: 0 4px 18px rgba(0,0,0,0.35) !important;
    transition: border-color 0.2s ease, box-shadow 0.2s ease !important;
    display: block !important;
}}

div[data-testid="stTextInput"] input:focus {{
    background: rgba(18, 26, 52, 0.90) !important;
    border-color: rgba(255, 220, 230, 0.95) !important;
    box-shadow: 0 0 0 2px rgba(229,9,20,0.30), 0 4px 20px rgba(0,0,0,0.40) !important;
    outline: none !important;
}}

div[data-testid="stTextInput"] input::placeholder {{
    color: rgba(220, 220, 240, 0.55) !important;
    opacity: 1 !important;
}}

/* ── Login button ── */
.stButton > button {{
    background: linear-gradient(90deg, #e50914 0%, #ff4b5c 100%) !important;
    color: #ffffff !important;
    -webkit-text-fill-color: #ffffff !important;
    border-radius: 12px !important;
    width: 100% !important;
    padding: 13px 14px !important;
    font-weight: 900 !important;
    border: 2px solid rgba(255, 209, 213, 0.7) !important;
    font-size: 17px !important;
    font-family: 'Poppins', sans-serif !important;
    letter-spacing: 0.6px !important;
    box-shadow: 0 6px 24px rgba(229,9,20,0.55), inset 0 1px 0 rgba(255,255,255,0.25) !important;
    transition: transform 0.2s ease, box-shadow 0.2s ease !important;
    text-transform: uppercase;
    position: relative;
    z-index: 5;
    text-shadow: 0 1px 6px rgba(0,0,0,0.9) !important;
    opacity: 1 !important;
}}

.stButton > button:hover {{
    background: linear-gradient(90deg, #ff4b5c 0%, #ff7a84 100%) !important;
    box-shadow: 0 9px 28px rgba(229,9,20,0.7), 0 0 20px rgba(255,209,213,0.4) !important;
    transform: translateY(-2px) !important;
    border-color: rgba(255,209,213,1.0) !important;
}}

[data-testid="column"] {{ padding: 0 !important; }}

/* ── Responsive ── */
@media (max-width: 1024px) {{
    .login-box {{ max-width: 100%; }}
    .welcome-box {{ padding: 24px 20px 18px 20px !important; }}
}}
@media (max-width: 768px) {{
    section.main > div {{ padding-left: 0.8rem !important; padding-right: 0.8rem !important; }}
    .welcome-box {{ padding: 22px 16px 16px 16px !important; border-radius: 16px !important; }}
    .login-title {{ font-size: clamp(34px, 10vw, 46px) !important; }}
    .login-subtitle {{ font-size: 14px !important; }}
    .stButton > button {{ font-size: 16px !important; padding: 12px 14px !important; }}
}}
@media (max-width: 480px) {{
    .welcome-box {{ padding: 18px 14px 14px 14px !important; }}
    div[data-testid="stTextInput"] input {{ font-size: 15px !important; padding: 12px 14px !important; }}
}}

/* ── Mobile viewport / scroll fix ── */
html {{
    background: #050814 !important;
    overflow-y: auto !important;
}}
body {{
    background: #050814 !important;
    overflow-y: auto !important;
    min-height: 100dvh !important;
}}

/* Fill the full visible height including mobile browser chrome */
#root,
.stApp,
[data-testid="stApp"],
[data-testid="stAppViewContainer"],
[data-testid="stMain"],
section.main {{
    background: #050814 !important;
}}

.stApp {{
    min-height: 100dvh !important;
    overflow-y: auto !important;
}}

/* Streamlit's inner scroll container – must not clip */
section[data-testid="stMain"],
section.main {{
    overflow-y: auto !important;
    overflow-x: hidden !important;
}}

/* Main content block – add safe-area bottom padding so nothing hides behind
   the home-indicator / nav bar on iOS & Android */
[data-testid="stMainBlockContainer"],
section.main > div,
section.main > div > div {{
    padding-bottom: max(env(safe-area-inset-bottom, 0px), 80px) !important;
    overflow: visible !important;
}}

/* Prevent the background overlay/grid from eating pointer events or scroll */
.page-bg-grid,
.page-bg-overlay {{
    pointer-events: none !important;
    touch-action: none !important;
}}

/* On very small screens collapse the side columns so the form is full width */
@media (max-width: 600px) {{
    [data-testid="stColumns"] > div:first-child,
    [data-testid="stColumns"] > div:last-child {{
        display: none !important;
        flex: 0 !important;
        min-width: 0 !important;
        max-width: 0 !important;
        padding: 0 !important;
    }}
    [data-testid="stColumns"] > div:nth-child(2) {{
        flex: 1 1 100% !important;
        max-width: 100% !important;
        padding: 0 12px !important;
    }}
}}
</style>
""", unsafe_allow_html=True)

# ── Session state defaults ──────────────────────────────────────────────────
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""

# Already logged in → go straight to the app
if st.session_state.logged_in:
    st.switch_page("pages/app.py")

# ── Render background ───────────────────────────────────────────────────────
if background_html:
    st.markdown(background_html, unsafe_allow_html=True)

# ── Page heading ────────────────────────────────────────────────────────────
st.markdown(
    "<h1 class='header-title' style='text-align:center; margin: 14px 0 18px 0;'>"
    "🎬 MOVIES RECOMMENDATION SYSTEM 🎬</h1>",
    unsafe_allow_html=True,
)

# ── Login form ──────────────────────────────────────────────────────────────
col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    st.markdown("<div class='login-box'>", unsafe_allow_html=True)
    st.markdown("""
    <div class='welcome-box'>
        <h1 class='login-title' style='text-align:center;'>🎬 LOGIN 🎬</h1>
        <p class='login-subtitle' style='text-align:center;'>Welcome back! Please enter your credentials</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div class='field-label' style='margin-bottom:8px;'>👤 USERNAME</div>", unsafe_allow_html=True)
    username = st.text_input("", key="login_username", label_visibility="collapsed")

    st.markdown("<div class='field-label' style='margin-bottom:8px; margin-top:14px;'>🔑 PASSWORD</div>", unsafe_allow_html=True)
    password = st.text_input("", key="login_password", type="password", label_visibility="collapsed")

    if st.button("Login"):
        if username == VALID_USERNAME and password == VALID_PASSWORD:
            st.session_state.logged_in = True
            st.session_state.username = username
            st.switch_page("pages/app.py")
        else:
            st.error("Invalid Credentials ❌")

    st.markdown("</div>", unsafe_allow_html=True)
