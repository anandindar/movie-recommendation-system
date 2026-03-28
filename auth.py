"""
User Authentication Module - Handles sign-up, login, and user management
Using MySQL Workbench for data storage
"""

import mysql.connector
from mysql.connector import Error
import hashlib
import streamlit as st
import os

# Load configuration - Priority: Streamlit secrets > Environment variables > config.py (local)
MYSQL_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'movie_recommendation_db',
    'port': 3306
}

# Try Streamlit Cloud connection string first (better for Railway)
try:
    if st.secrets and 'MYSQL_CONNECTION_STRING' in st.secrets:
        conn_str = st.secrets['MYSQL_CONNECTION_STRING']
        # Parse: mysql://user:password@host:port/database
        import urllib.parse
        parsed = urllib.parse.urlparse(conn_str)
        MYSQL_CONFIG = {
            'host': parsed.hostname,
            'user': parsed.username,
            'password': parsed.password,
            'database': parsed.path.lstrip('/'),
            'port': parsed.port or 3306
        }
except Exception:
    pass

# Try Streamlit Cloud individual secrets if connection string not available
try:
    if st.secrets and 'MYSQL_HOST' in st.secrets:
        MYSQL_CONFIG = {
            'host': st.secrets['MYSQL_HOST'],
            'user': st.secrets['MYSQL_USER'],
            'password': st.secrets['MYSQL_PASSWORD'],
            'database': st.secrets['MYSQL_DATABASE'],
            'port': st.secrets.get('MYSQL_PORT', 3306)
        }
except Exception:
    pass

# Try environment variables
if 'MYSQL_HOST' in os.environ:
    MYSQL_CONFIG = {
        'host': os.getenv('MYSQL_HOST'),
        'user': os.getenv('MYSQL_USER'),
        'password': os.getenv('MYSQL_PASSWORD'),
        'database': os.getenv('MYSQL_DATABASE'),
        'port': int(os.getenv('MYSQL_PORT', 3306))
    }

# Try config.py (local development)
try:
    from config import MYSQL_CONFIG as CONFIG_FILE
    # Only use config.py if environment variables weren't set
    if 'MYSQL_HOST' not in os.environ:
        MYSQL_CONFIG = CONFIG_FILE
except ImportError:
    pass

def init_db():
    """Initialize the MySQL database with users table if it doesn't exist"""
    try:
        # Connect to MySQL without specifying database first
        conn = mysql.connector.connect(
            host=MYSQL_CONFIG['host'],
            user=MYSQL_CONFIG['user'],
            password=MYSQL_CONFIG['password'],
            port=MYSQL_CONFIG.get('port', 3306)
        )
        cursor = conn.cursor()
        
        # Create database if it doesn't exist
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {MYSQL_CONFIG['database']}")
        
        # Switch to the database
        cursor.execute(f"USE {MYSQL_CONFIG['database']}")
        
        # Create users table if it doesn't exist
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(50) UNIQUE NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.commit()
        cursor.close()
        conn.close()
        
    except Error as e:
        print(f"❌ Error initializing database: {e}")
        print(f"Please ensure MySQL is running and credentials in config.py are correct.")
        return False
    return True

def hash_password(password):
    """Hash a password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def get_db_connection():
    """Get MySQL database connection"""
    try:
        return mysql.connector.connect(
            host=MYSQL_CONFIG['host'],
            user=MYSQL_CONFIG['user'],
            password=MYSQL_CONFIG['password'],
            database=MYSQL_CONFIG['database'],
            port=MYSQL_CONFIG.get('port', 3306)
        )
    except Error as e:
        st.error(f"❌ Database Connection Error: {str(e)}")
        return None

def user_exists(username):
    """Check if a username already exists"""
    conn = get_db_connection()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM users WHERE username = %s", (username,))
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        return result is not None
    except Error as e:
        print(f"Error checking user: {e}")
        return False

def email_exists(email):
    """Check if an email already exists"""
    conn = get_db_connection()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        return result is not None
    except Error as e:
        print(f"Error checking email: {e}")
        return False

def register_user(username, email, password):
    """Register a new user. Returns (success, message)"""
    
    # Validate inputs
    if not username or len(username) < 3:
        return False, "Username must be at least 3 characters long"
    
    if not email or "@" not in email:
        return False, "Please enter a valid email address"
    
    if not password or len(password) < 6:
        return False, "Password must be at least 6 characters long"
    
    # Check if username exists
    if user_exists(username):
        return False, "Username already exists! Try a different one"
    
    # Check if email exists
    if email_exists(email):
        return False, "Email already registered! Try logging in"
    
    # Hash password and store user
    password_hash = hash_password(password)
    
    conn = get_db_connection()
    if not conn:
        return False, "Database connection error. Please try again."
    
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO users (username, email, password_hash) VALUES (%s, %s, %s)",
            (username, email, password_hash)
        )
        conn.commit()
        cursor.close()
        conn.close()
        return True, "Account created successfully! 🎉 Please log in now"
    except Error as e:
        return False, f"Registration error: {str(e)}"

def authenticate_user(username, password):
    """Authenticate a user. Returns (success, message)"""
    
    if not username or not password:
        return False, "Please enter username and password"
    
    password_hash = hash_password(password)
    
    conn = get_db_connection()
    if not conn:
        return False, "Database connection error. Please try again."
    
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, username FROM users WHERE username = %s AND password_hash = %s",
            (username, password_hash)
        )
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if result:
            return True, "Login successful! 🎉"
        else:
            return False, "Invalid username or password ❌"
    except Error as e:
        return False, f"Authentication error: {str(e)}"

def get_user_info(username):
    """Get user information by username"""
    conn = get_db_connection()
    if not conn:
        return None
    
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, username, email, created_at FROM users WHERE username = %s",
            (username,)
        )
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        return result
    except Error as e:
        print(f"Error getting user info: {e}")
        return None
