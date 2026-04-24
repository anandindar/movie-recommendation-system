# MongoDB Atlas Setup Guide

## Quick Start (5 minutes)

### Step 1: Create MongoDB Atlas Account
1. Go to https://www.mongodb.com/cloud/atlas
2. Click **"Sign Up"** (free tier available - 512MB storage)
3. Enter your email and create password
4. Verify your email

### Step 2: Create a Cluster
1. Log in to MongoDB Atlas
2. Click **"Create"** or **"Build a Database"**
3. Select **"Shared"** tier (FREE - $0/month)
4. Choose region closest to your location
5. Click **"Create Cluster"**
6. Wait 1-2 minutes for cluster to initialize

### Step 3: Create Database User
1. In left sidebar, click **"Database Access"**
2. Click **"Add New Database User"**
3. Enter:
   - **Username:** `moviesapp` (or your choice)
   - **Password:** Create a strong password (save it!)
   - Example: `MySecurePass123!`
4. Under "Database User Privileges," select **"Atlas Admin"**
5. Click **"Add User"**

### Step 4: Whitelist Your IP
1. In left sidebar, click **"Network Access"**
2. Click **"Add IP Address"**
3. Click **"Allow Access from Anywhere"** (for development)
   - Or add your specific IP address for production
4. Click **"Confirm"**

### Step 5: Get Connection String
1. Go to **"Clusters"** tab
2. Click **"Connect"** button on your cluster
3. Choose **"Drivers"** tab
4. Select **"Python"** → **"3.12 or later"**
5. Copy the connection string

**Example Connection String:**
```
mongodb+srv://moviesapp:MySecurePass123!@cluster0.a1b2c.mongodb.net/?retryWrites=true&w=majority
```

⚠️ **Important:** Replace `moviesapp` with your username and `MySecurePass123!` with your actual password!

### Step 6: Update config.py
1. Open `config.py` in your project
2. Find this line:
   ```python
   'connection_string': 'mongodb+srv://YOUR_USERNAME:YOUR_PASSWORD@cluster0.xxxxx.mongodb.net/?retryWrites=true&w=majority',
   ```
3. Replace with your connection string from Step 5
4. Save the file

### Step 7: Test Connection
Run this command:
```bash
python -c "import auth; result = auth.init_db(); print('✅ Connection successful!' if result else '❌ Connection failed')"
```

### Step 8: Restart Your App
```bash
streamlit run dashboard_minimal.py
```

---

## Troubleshooting

### Error: "Lost connection to MySQL"
- ✅ This is expected! You've switched from MySQL to MongoDB
- Make sure you've completed all steps above

### Error: "Connection timeout"
- Check that your IP is whitelisted in Network Access
- Verify username and password are correct in connection string
- Try disabling VPN/firewall temporarily

### Error: "Authentication failed"
- Verify username and password match exactly (case-sensitive!)
- Make sure you copied the entire connection string correctly
- Check that database user was created successfully

### Connection string doesn't work
- Go back to MongoDB Atlas > Clusters > Connect
- Copy the connection string again
- Make sure you replaced YOUR_USERNAME and YOUR_PASSWORD with actual values

---

## What's Now Stored in MongoDB

User credentials are now stored in MongoDB Atlas instead of MySQL:
- **Database:** `movie_recommendation_db`
- **Collection:** `users`
- **Fields:**
  - `username` (unique, indexed)
  - `email` (unique, indexed)
  - `password_hash` (SHA-256 encrypted)
  - `created_at` (timestamp)

---

## Security Notes

⚠️ **Never share your connection string!**
- Add `config.py` to `.gitignore`
- Don't commit passwords to GitHub
- For production, use environment variables
- For Streamlit Cloud, add secret to app settings

---

## Free Tier Limits

- **Storage:** 512MB (free)
- **Databases:** Up to 100
- **Concurrent connections:** 100
- **Upgrade anytime** if you need more

This is plenty for development and testing!
