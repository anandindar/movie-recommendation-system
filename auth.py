"""
User Authentication Module - Handles sign-up, login, and user management
Using SQLite for simplicity (can be upgraded to MySQL later)
"""

import sqlite3
import hashlib
import os
from pathlib import Path

# Database file location
DB_PATH = Path(__file__).parent / "Database" / "users.db"

def init_db():
    """Initialize the database with users table if it doesn't exist"""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    conn.commit()
    conn.close()

def hash_password(password):
    """Hash a password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def user_exists(username):
    """Check if a username already exists"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
    result = cursor.fetchone()
    conn.close()
    return result is not None

def email_exists(email):
    """Check if an email already exists"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
    result = cursor.fetchone()
    conn.close()
    return result is not None

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
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)",
            (username, email, password_hash)
        )
        conn.commit()
        conn.close()
        return True, "Account created successfully! 🎉 Please log in now"
    except sqlite3.IntegrityError:
        return False, "An error occurred during registration"
    except Exception as e:
        return False, f"Database error: {str(e)}"

def authenticate_user(username, password):
    """Authenticate a user. Returns (success, message)"""
    
    if not username or not password:
        return False, "Please enter username and password"
    
    password_hash = hash_password(password)
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, username FROM users WHERE username = ? AND password_hash = ?",
            (username, password_hash)
        )
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return True, "Login successful! 🎉"
        else:
            return False, "Invalid username or password ❌"
    except Exception as e:
        return False, f"Authentication error: {str(e)}"

def get_user_info(username):
    """Get user information by username"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, username, email, created_at FROM users WHERE username = ?",
        (username,)
    )
    result = cursor.fetchone()
    conn.close()
    return result

# Initialize database on module load
init_db()
