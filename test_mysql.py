"""Test MySQL connection"""
from auth import init_db

try:
    init_db()
    print("✅ MySQL Connection Successful!")
    print("✅ Database initialized!")
    print("✅ You can now run: streamlit run dashboard.py")
except Exception as e:
    print(f"❌ Error: {e}")
