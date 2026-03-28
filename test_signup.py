"""Test signup functionality"""
from auth import register_user, get_db_connection, authenticate_user

print("Testing signup...")

# Test 1: Register a user
username = "testuser"
email = "test@example.com"
password = "password123"

print(f"\n✓ Attempting to register: {username}")
success, msg = register_user(username, email, password)
print(f"  Result: {msg}")

if success:
    print(f"\n✓ Testing login with registered user...")
    auth_success, auth_msg = authenticate_user(username, password)
    print(f"  Login Result: {auth_msg}")
    
    # Check database
    print(f"\n✓ Checking database...")
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, username, email FROM users WHERE username = %s", (username,))
        result = cursor.fetchone()
        if result:
            print(f"  ✅ User found in database: {result}")
        else:
            print(f"  ❌ User NOT found in database")
        cursor.close()
        conn.close()
else:
    print(f"  ❌ Registration failed: {msg}")
