#!/usr/bin/env python
import sys
import traceback

try:
    print("Starting import test...")
    import streamlit as st
    print("✅ Streamlit imported")
    
    from utils import load_frontend_images, build_background, background_css
    print("✅ Utils imported")
    
    from auth import authenticate_user, register_user, init_db
    print("✅ Auth imported")
    
    print("\n✅ All imports successful! No issues found.")
    
except Exception as e:
    print(f"❌ Error: {str(e)}")
    print(f"\nFull traceback:")
    traceback.print_exc()
    sys.exit(1)
