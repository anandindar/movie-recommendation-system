#!/usr/bin/env python
"""Quick test to see if dashboard.py can execute the init_db call"""

import sys
import traceback

try:
    from auth import init_db
    
    print("Testing init_db()...")
    result = init_db()
    
    if result:
        print("✅ Database initialized successfully")
    else:
        print("⚠️  Database initialization returned False")
        print("Possible causes:")
        print("  1. MySQL server not running")
        print("  2. Wrong credentials in config.py")
        print("  3. Cannot create/access database")
        
except Exception as e:
    print(f"❌ Error during init_db(): {str(e)}")
    traceback.print_exc()
    sys.exit(1)
