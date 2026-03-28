import streamlit as st
from auth import authenticate_user, register_user, init_db

st.set_page_config(page_title="Test", layout="wide")

st.write("Testing dashboard...")

# ── Initialize database ─────────────────────────────────────────────────────
if "db_initialized" not in st.session_state:
    st.write("Initializing database...")
    success = init_db()
    st.session_state.db_initialized = True
    if not success:
        st.error("❌ Cannot connect to MySQL")
    else:
        st.success("✅ Database connected")

# ── Test form ─────────────────────────────────────────────────────────────
st.title("Test Login Form")

col1, col2 = st.columns(2)

with col1:
    if st.button("🔐 LOGIN"):
        st.write("LOGIN pressed")

with col2:
    if st.button("📝 SIGN UP"):
        st.write("SIGN UP pressed")

st.divider()

username = st.text_input("Username")
password = st.text_input("Password", type="password")

if st.button("Test Auth"):
    if username and password:
        success, msg = authenticate_user(username, password)
        if success:
            st.success(msg)
        else:
            st.error(msg)
    else:
        st.warning("Enter username and password")
