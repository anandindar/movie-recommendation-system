"""
User Authentication Module - Handles sign-up, login, and user management
Using MongoDB for data storage
"""

from pymongo import MongoClient
from pymongo.errors import PyMongoError, ServerSelectionTimeoutError, ConnectionFailure
import hashlib
import streamlit as st
import os
from datetime import datetime

# Load MongoDB configuration - Priority: Streamlit secrets > Environment variables > config.py (local)
MONGODB_CONFIG = {
    'connection_string': 'mongodb+srv://YOUR_USERNAME:YOUR_PASSWORD@cluster0.xxxxx.mongodb.net/?retryWrites=true&w=majority',
    'database': 'movie_recommendation_db',
    'users_collection': 'users'
}

# Try Streamlit Cloud connection string first
try:
    if st.secrets and 'MONGODB_CONNECTION_STRING' in st.secrets:
        MONGODB_CONFIG['connection_string'] = st.secrets['MONGODB_CONNECTION_STRING']
        if 'MONGODB_DATABASE' in st.secrets:
            MONGODB_CONFIG['database'] = st.secrets['MONGODB_DATABASE']
except Exception:
    pass

# Try environment variables
if 'MONGODB_CONNECTION_STRING' in os.environ:
    MONGODB_CONFIG['connection_string'] = os.getenv('MONGODB_CONNECTION_STRING')
    if 'MONGODB_DATABASE' in os.environ:
        MONGODB_CONFIG['database'] = os.getenv('MONGODB_DATABASE')

# Try config.py (local development)
try:
    from config import MONGODB_CONFIG as CONFIG_FILE
    # Only use config.py if environment variables weren't set
    if 'MONGODB_CONNECTION_STRING' not in os.environ:
        MONGODB_CONFIG = CONFIG_FILE
except ImportError:
    pass

# MongoDB client instance
_mongo_client = None
_mongo_db = None

def get_mongo_db():
    """Get MongoDB database instance"""
    global _mongo_client, _mongo_db
    
    try:
        if _mongo_client is None:
            # Check if connection string contains placeholder values
            if 'YOUR_USERNAME' in MONGODB_CONFIG['connection_string'] or 'xxxxx' in MONGODB_CONFIG['connection_string']:
                raise ConnectionFailure(
                    "MongoDB Atlas credentials not configured in config.py. "
                    "Please follow the setup instructions in config.py to get your MongoDB Atlas connection string."
                )
            
            # Create connection with proper timeouts for Streamlit Cloud
            _mongo_client = MongoClient(
                MONGODB_CONFIG['connection_string'], 
                serverSelectionTimeoutMS=15000,
                connectTimeoutMS=20000,
                socketTimeoutMS=20000,
                maxIdleTimeMS=45000
            )
            # Test connection
            _mongo_client.admin.command('ping')
        
        if _mongo_db is None:
            _mongo_db = _mongo_client[MONGODB_CONFIG['database']]
        
        return _mongo_db
    except (ServerSelectionTimeoutError, ConnectionFailure) as e:
        error_msg = str(e)
        if 'YOUR_USERNAME' in error_msg or 'Atlas' in error_msg:
            print(f"❌ MongoDB Configuration Error: {error_msg}")
        else:
            print(f"❌ MongoDB Connection Error: {error_msg}")
        return None
    except PyMongoError as e:
        print(f"❌ MongoDB Error: {str(e)}")
        return None

def close_mongo_connection():
    """Close MongoDB connection"""
    global _mongo_client
    if _mongo_client:
        _mongo_client.close()
        _mongo_client = None

def init_db():
    """Initialize MongoDB with users collection and indexes if it doesn't exist"""
    try:
        db = get_mongo_db()
        if db is None:
            return False
        
        # Get the users collection
        users_collection = db[MONGODB_CONFIG['users_collection']]
        
        # Create unique indexes on username and email
        users_collection.create_index('username', unique=True)
        users_collection.create_index('email', unique=True)
        
        return True
    except PyMongoError as e:
        print(f"Error initializing MongoDB: {e}")
        return False

def hash_password(password):
    """Hash a password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def user_exists(username):
    """Check if a username already exists"""
    try:
        db = get_mongo_db()
        if db is None:
            return False
        
        users_collection = db[MONGODB_CONFIG['users_collection']]
        return users_collection.find_one({'username': username}) is not None
    except PyMongoError as e:
        print(f"Error checking user: {e}")
        return False

def email_exists(email):
    """Check if an email already exists"""
    try:
        db = get_mongo_db()
        if db is None:
            return False
        
        users_collection = db[MONGODB_CONFIG['users_collection']]
        return users_collection.find_one({'email': email}) is not None
    except PyMongoError as e:
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
    
    try:
        db = get_mongo_db()
        if db is None:
            return False, "Database connection error. Please try again."
        
        users_collection = db[MONGODB_CONFIG['users_collection']]
        
        user_document = {
            'username': username,
            'email': email,
            'password_hash': password_hash,
            'created_at': datetime.utcnow()
        }
        
        users_collection.insert_one(user_document)
        return True, "Account created successfully! 🎉 Please log in now"
    except PyMongoError as e:
        return False, f"Registration error: {str(e)}"

def authenticate_user(username, password):
    """Authenticate a user. Returns (success, message)"""
    
    if not username or not password:
        return False, "Please enter username and password"
    
    password_hash = hash_password(password)
    
    try:
        db = get_mongo_db()
        if db is None:
            return False, "Database connection error. Please try again."
        
        users_collection = db[MONGODB_CONFIG['users_collection']]
        
        user = users_collection.find_one({
            'username': username,
            'password_hash': password_hash
        })
        
        if user:
            return True, "Login successful! 🎉"
        else:
            return False, "Invalid username or password ❌"
    except PyMongoError as e:
        return False, f"Authentication error: {str(e)}"

def get_user_info(username):
    """Get user information by username"""
    try:
        db = get_mongo_db()
        if db is None:
            return None
        
        users_collection = db[MONGODB_CONFIG['users_collection']]
        
        user = users_collection.find_one(
            {'username': username},
            {'password_hash': 0}  # Exclude password hash from results
        )
        
        if user:
            # Convert ObjectId to string for JSON serialization
            user['_id'] = str(user['_id'])
            return user
        return None
    except PyMongoError as e:
        print(f"Error getting user info: {e}")
        return None

