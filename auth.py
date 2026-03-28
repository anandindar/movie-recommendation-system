"""
User Authentication Module - Handles sign-up, login, and user management
Using MySQL Workbench for data storage
"""

import mysql.connector
from mysql.connector import Error
import hashlib
import streamlit as st
import os

# Load configuration from environment variables or config.py
try:
    from config import MYSQL_CONFIG
except ImportError:
    # Use environment variables if config.py doesn't exist (for Streamlit Cloud)
    MYSQL_CONFIG = {
        'host': os.getenv('MYSQL_HOST', 'localhost'),
        'user': os.getenv('MYSQL_USER', 'root'),
        'password': os.getenv('MYSQL_PASSWORD', ''),
        'database': os.getenv('MYSQL_DATABASE', 'movie_recommendation_db')
    }

def init_db():
    """Initialize the MySQL database with users table if it doesn't exist"""
    try:
        # Connect to MySQL without specifying database first
        conn = mysql.connector.connect(
            host=MYSQL_CONFIG['host'],
            user=MYSQL_CONFIG['user'],
            password=MYSQL_CONFIG['password']
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
            database=MYSQL_CONFIG['database']
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
