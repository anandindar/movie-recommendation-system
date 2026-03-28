"""Minimize dashboard to test basic functionality"""
import streamlit as st
from auth import authenticate_user, register_user, init_db

st.set_page_config(page_title="Movie Recommendation System", layout="wide")

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

# PAGE CONTENT
st.title("🎬 MOVIE RECOMMENDATION SYSTEM 🎬")

col1, col2 = st.columns(2)
with col1:
    if st.button("🔐 LOGIN", use_container_width=True):
        st.session_state.auth_tab = "LOGIN"
        st.rerun()

with col2:
    if st.button("📝 SIGN UP", use_container_width=True):
        st.session_state.auth_tab = "SIGNUP"
        st.rerun()

st.divider()

if st.session_state.auth_tab == "LOGIN":
    st.write("## Login Form")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    
    if st.button("🔐 Login", use_container_width=True):
        if not username or not password:
            st.error("Please enter username and password")
        else:
            success, msg = authenticate_user(username, password)
            if success:
                st.session_state.logged_in = True
                st.session_state.username = username
                st.success(msg)
                st.balloons()
                st.switch_page("pages/app.py")
            else:
                st.error(msg)
else:
    st.write("## Sign Up Form")
    username = st.text_input("Username", key="su_username")
    email = st.text_input("Email", key="su_email")
    password = st.text_input("Password", key="su_password", type="password")
    confirm = st.text_input("Confirm Password", key="su_confirm", type="password")
    
    if st.button("Sign Up", use_container_width=True):
        if not username or not email or not password:
            st.error("Please fill in all fields")
        elif password != confirm:
            st.error("Passwords don't match")
        elif len(password) < 6:
            st.error("Password must be at least 6 characters")
        else:
            success, msg = register_user(username, email, password)
            if success:
                st.success(msg)
                st.balloons()
                # Auto-login after signup
                st.session_state.logged_in = True
                st.session_state.username = username
                st.info("Redirecting to dashboard...")
                st.switch_page("pages/app.py")
            else:
                st.error(msg)
