"""Minimize dashboard to test basic functionality"""
import streamlit as st

# MUST be first Streamlit command
st.set_page_config(page_title="Movie Recommendation System", layout="wide")

# Now import auth module
from auth import authenticate_user, register_user, init_db, MONGODB_CONFIG, get_mongo_db

# Check MongoDB Configuration
def check_mongodb_configured():
    """Check if MongoDB is properly configured"""
    if 'YOUR_USERNAME' in MONGODB_CONFIG['connection_string'] or 'xxxxx' in MONGODB_CONFIG['connection_string']:
        return False, "MongoDB not configured"
    return True, "MongoDB configured"

# Check if MongoDB is configured
is_configured, config_msg = check_mongodb_configured()

if not is_configured:
    st.error("🔧 MongoDB Configuration Required")
    st.markdown("""
    ### Setup MongoDB Atlas (Free)
    
    1. **Go to** https://www.mongodb.com/cloud/atlas
    2. **Sign Up** for free (512MB storage - enough for development)
    3. **Create a Cluster** (Shared tier, free)
    4. **Create Database User** with username & password
    5. **Whitelist IP** (Network Access)
    6. **Get Connection String** from "Connect" button
    7. **Update config.py** with your connection string:
       - Replace `YOUR_USERNAME` with your username
       - Replace `YOUR_PASSWORD` with your password  
       - Replace `cluster0.xxxxx` with your cluster name
    
    **Example Connection String:**
    ```
    mongodb+srv://moviesapp:MyPassword123@cluster0.a1b2c.mongodb.net/?retryWrites=true&w=majority
    ```
    
    After updating config.py, refresh this page.
    """)
    st.stop()

# Init DB
if "db_initialized" not in st.session_state:
    db_result = init_db()
    if not db_result:
        st.error("❌ MongoDB Connection Failed")
        st.info("Please verify:")
        st.write("- MongoDB Atlas connection string is correct in config.py")
        st.write("- Username and password are correct")
        st.write("- Your IP is whitelisted in MongoDB Atlas Network Access")
        st.write("- The database credentials have been created")
        st.stop()
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
    st.write("## 🔐 Login Form")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔓 Login", use_container_width=True, key="login_btn"):
            success, msg = authenticate_user(username, password)
            if success:
                st.session_state.logged_in = True
                st.success(msg)
                st.rerun()
            else:
                st.error(msg)
    
    with col2:
        if st.button("↩️ Back", use_container_width=True, key="back_login"):
            st.session_state.auth_tab = "SIGNUP"
            st.rerun()
    
    st.divider()
    st.markdown("**Don't have an account?**")
    if st.button("📝 Create Account", use_container_width=True, key="create_account"):
        st.session_state.auth_tab = "SIGNUP"
        st.rerun()
else:
    st.write("## 📝 Sign Up Form")
    username = st.text_input("Username", key="su_username")
    email = st.text_input("Email", key="su_email")
    password = st.text_input("Password", key="su_password", type="password")
    confirm = st.text_input("Confirm Password", key="su_confirm", type="password")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("✅ Sign Up", use_container_width=True, key="signup_btn"):
            if password != confirm:
                st.error("❌ Passwords don't match")
            else:
                success, msg = register_user(username, email, password)
                if success:
                    st.success(msg)
                    st.session_state.auth_tab = "LOGIN"
                    st.rerun()
                else:
                    st.error(msg)
    
    with col2:
        if st.button("↩️ Back", use_container_width=True, key="back_signup"):
            st.session_state.auth_tab = "LOGIN"
            st.rerun()
    
    st.divider()
    st.markdown("**Already have an account?**")
    if st.button("🔐 Sign In", use_container_width=True, key="sign_in"):
        st.session_state.auth_tab = "LOGIN"
        st.rerun()
