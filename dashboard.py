import streamlit as st
from utils import load_frontend_images, build_background, background_css, VALID_USERNAME, VALID_PASSWORD

st.set_page_config(page_title="Movie Recommendation System – Login", layout="wide")

# ── Build background ────────────────────────────────────────────────────────
try:
    movie_images = load_frontend_images()
    grid_layout_css, background_html = build_background(movie_images)
except Exception:
    # Never crash login page due to heavy/invalid poster assets.
    movie_images = []
    grid_layout_css, background_html = build_background([])

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
    font-size: clamp(20px, 2.6vw, 38px);
    font-weight: 900;
    margin: 0 auto 32px auto;
    letter-spacing: 4px;
    line-height: 1.2;
    font-family: 'Bebas Neue', sans-serif;
    color: #ffffff !important;
    -webkit-text-fill-color: #ffffff !important;
    text-shadow: 0 3px 15px rgba(0,0,0,1), 0 0 20px rgba(229,9,20,0.8);
    animation: titleGlow 2.2s ease-in-out infinite alternate;
    /* ── Border box ── */
    display: inline-block;
    padding: 16px 40px;
    border: 3px solid rgba(229, 9, 20, 0.85);
    border-radius: 16px;
    background: rgba(8, 12, 24, 0.75);
    backdrop-filter: blur(8px);
    -webkit-backdrop-filter: blur(8px);
    box-shadow: 0 6px 30px rgba(0,0,0,0.6), 0 0 25px rgba(229,9,20,0.35);
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
    max-width: 420px;
    width: 100%;
    box-shadow: none !important;
    border: none !important;
    position: relative;
    z-index: 4;
}}

.welcome-box {{
    background: rgba(16, 24, 46, 0.88) !important;
    border: 2px solid rgba(255, 116, 132, 0.90) !important;
    border-radius: 20px;
    padding: 30px 32px 24px 32px;
    margin-bottom: 20px;
    box-shadow: 0 8px 40px rgba(0,0,0,0.65), 0 0 32px rgba(229,9,20,0.3) !important;
    backdrop-filter: blur(10px);
    -webkit-backdrop-filter: blur(10px);
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
    color: #f8fbff !important;
    -webkit-text-fill-color: #ffffff !important;
    font-size: 16px;
    font-weight: 900;
    letter-spacing: 0.5px;
    text-shadow: 0 2px 8px rgba(0,0,0,0.8);
    background: rgba(34, 48, 84, 0.74);
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
    background: rgba(0, 0, 0, 0.95) !important;
    color: #ffffff !important;
    -webkit-text-fill-color: #ffffff !important;
    caret-color: #ffffff !important;
    border: 2px solid rgba(229, 9, 20, 0.9) !important;
    border-radius: 12px !important;
    padding: 14px 16px !important;
    font-size: 16px !important;
    font-family: 'Poppins', sans-serif !important;
    width: 100% !important;
    box-shadow: 0 8px 28px rgba(0,0,0,0.6), inset 0 1px 0 rgba(255,255,255,0.15) !important;
    transition: border-color 0.2s ease, box-shadow 0.2s ease !important;
    display: block !important;
}}

div[data-testid="stTextInput"] input:focus {{
    background: rgba(10, 10, 20, 0.98) !important;
    border-color: rgba(255, 220, 226, 1) !important;
    box-shadow: 0 0 0 3px rgba(229,9,20,0.4), 0 10px 30px rgba(0,0,0,0.7) !important;
    outline: none !important;
}}

div[data-testid="stTextInput"] input::placeholder {{
    color: #e0e0e0 !important;
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

/* ── Centre the entire login form on all screens ── */
[data-testid="stMainBlockContainer"] {{
    min-height: 100dvh !important;
    display: flex !important;
    flex-direction: column !important;
    align-items: center !important;
    justify-content: center !important;
    padding: 32px 16px !important;
    /* override conflicting bottom-padding from mobile fix below */
    padding-bottom: max(env(safe-area-inset-bottom, 16px), 32px) !important;
}}
/* Every direct child in the block container gets auto centred */
[data-testid="stMainBlockContainer"] > div,
[data-testid="stMainBlockContainer"] > div > div {{
    width: 100%;
    max-width: 480px;
    padding-bottom: 0 !important;
}}
/* but the header stretches full width */
[data-testid="stMainBlockContainer"] > div:first-child,
[data-testid="stMainBlockContainer"] > div:first-child > div {{
    max-width: 100% !important;
}}

[data-testid="column"] {{ padding: 0 !important; }}

/* ── Responsive ── */
@media (max-width: 768px) {{
    .welcome-box {{ padding: 22px 18px 16px 18px !important; border-radius: 16px !important; }}
    .login-title {{ font-size: clamp(36px, 10vw, 52px) !important; }}
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

/* Main content block – safe-area bottom padding */
[data-testid="stMainBlockContainer"],
section.main > div,
section.main > div > div {{
    overflow: visible !important;
}}

/* Prevent the background overlay/grid from eating pointer events or scroll */
.page-bg-grid,
.page-bg-overlay {{
    pointer-events: none !important;
    touch-action: none !important;
}}

/* On very small screens ensure form is full-width */
@media (max-width: 600px) {{
    [data-testid="stMainBlockContainer"] > div,
    [data-testid="stMainBlockContainer"] > div > div {{
        max-width: 100% !important;
        padding: 0 4px !important;
    }}
}}
</style>
""", unsafe_allow_html=True)

# ── Session state defaults ──────────────────────────────────────────────────
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""

# ── Already logged in → go to app page ─────────────────────────────────────
if st.session_state.logged_in:
    st.switch_page("pages/app.py")
    st.stop()

# ── Render background ───────────────────────────────────────────────────────
if background_html:
    st.markdown(background_html, unsafe_allow_html=True)

# ── Page heading ────────────────────────────────────────────────────────────
st.markdown(
    "<div style='text-align:center; width:100%; margin-bottom:36px;'>"
    "<h1 class='header-title'>"
    "🎬 MOVIES RECOMMENDATION SYSTEM 🎬</h1></div>",
    unsafe_allow_html=True,
)

# ── Login form (CSS handles centering – no st.columns needed) ──────────────
st.markdown("<div class='login-box'>", unsafe_allow_html=True)
st.markdown("""
<div class='welcome-box'>
    <h1 class='login-title' style='text-align:center;'>🎬 LOGIN 🎬</h1>
    <p class='login-subtitle' style='text-align:center;'>Welcome back! Please enter your credentials</p>
</div>
""", unsafe_allow_html=True)

st.markdown("<div class='field-label' style='margin-bottom:8px; color:#ffffff !important; font-size:18px; font-weight:900; text-shadow:0 2px 8px rgba(0,0,0,0.8);'>👤 USERNAME</div>", unsafe_allow_html=True)
username = st.text_input("", key="login_username", label_visibility="collapsed")

st.markdown("<div class='field-label' style='margin-bottom:8px; margin-top:14px; color:#ffffff !important; font-size:18px; font-weight:900; text-shadow:0 2px 8px rgba(0,0,0,0.8);'>🔑 PASSWORD</div>", unsafe_allow_html=True)
password = st.text_input("", key="login_password", type="password", label_visibility="collapsed")

if st.button("Login"):
    if username == VALID_USERNAME and password == VALID_PASSWORD:
        st.session_state.logged_in = True
        st.session_state.username = username
        st.switch_page("pages/app.py")
    else:
        st.error("Invalid Credentials ❌")

st.markdown("</div>", unsafe_allow_html=True)
