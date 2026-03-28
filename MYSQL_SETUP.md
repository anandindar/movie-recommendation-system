# MySQL Setup Guide for Movie Recommendation System

## Prerequisites

You need to have MySQL Server and MySQL Workbench installed. If not:
- [Download MySQL Community Server](https://dev.mysql.com/downloads/mysql/)
- [Download MySQL Workbench](https://dev.mysql.com/downloads/workbench/)

---

## Quick Setup (2 Steps)

### Step 1: Get Your MySQL Password

1. Open **MySQL Workbench**
2. Click on your local connection (usually `localhost:3306`)
3. Enter your MySQL password (set during MySQL installation)
4. You're connected! ✅

### Step 2: Update config.py

1. Open `config.py` in VS Code
2. Replace `'password': 'your_password_here'` with your actual MySQL password
3. Save the file

Example:
```python
MYSQL_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'MySecurePassword123',  # ← Your MySQL password here
    'database': 'movie_recommendation_db'
}
```

---

## How It Works

When you start the app:
- ✅ Database `movie_recommendation_db` is created automatically
- ✅ `users` table is created automatically
- ✅ All user sign-ups are stored in MySQL Workbench

---

## Manual Setup (Optional)

If you prefer to create the database manually in MySQL Workbench:

### Option A: Using SQL Script

1. Open MySQL Workbench
2. Click **File → Open SQL Script**
3. Create a new file with this content:

```sql
-- Create Database
CREATE DATABASE IF NOT EXISTS movie_recommendation_db;

-- Use the database
USE movie_recommendation_db;

-- Create Users Table
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create Index for faster lookups
CREATE INDEX idx_username ON users(username);
CREATE INDEX idx_email ON users(email);
```

4. Click **Query → Execute All** (or press `Ctrl+Shift+Enter`)

### Option B: Using MySQL Command Line

```bash
mysql -u root -p
Enter password: [your MySQL password]

CREATE DATABASE movie_recommendation_db;
USE movie_recommendation_db;

CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## Testing the Connection

To verify everything works:

1. Update `config.py` with your MySQL password
2. Run the app: `streamlit run dashboard.py`
3. Try signing up a test account
4. Check MySQL Workbench → your database → users table → you should see your new account! ✅

---

## Troubleshooting

### Error: "Can't connect to MySQL server"
- ✅ Ensure MySQL Server is running
- ✅ Check your password in `config.py` is correct
- ✅ Verify host is `localhost` (not an IP address)

### Error: "Access denied for user 'root'"
- ✅ Wrong password in `config.py`
- ✅ Reset MySQL password and update `config.py`

### Error: "Unknown database"
- ✅ Let the app create it automatically (just needs first sign-up)
- ✅ Or manually create using SQL script above

---

## View User Data in Workbench

1. Open MySQL Workbench
2. Click your local connection
3. Navigate: **SCHEMAS → movie_recommendation_db → Tables → users**
4. Right-click `users` → **Select Rows**
5. View all registered users! 📊

---

## Security Notes

⚠️ **IMPORTANT:**
- `config.py` contains your database password
- Add `config.py` to `.gitignore` (already done)
- Never commit `config.py` with real passwords to GitHub
- Passwords are hashed (SHA-256) before storing in database

---

## Next Steps

Once configured:
1. All new user sign-ups automatically save to MySQL
2. Login validation queries the MySQL database
3. User profiles can be extended with preferences, ratings, watchlist, etc.
4. Can generate reports/analytics from user data

Enjoy! 🎬
