"""Test to diagnose the dashboard loading issue"""

import traceback
import sys

try:
    print("Step 1: Importing utils...")
    from utils import load_frontend_images, build_background, background_css
    print("✅ Utils imported")
    
    print("\nStep 2: Loading frontend images...")
    try:
        movie_images = load_frontend_images()
        print(f"✅ Loaded {len(movie_images) if movie_images else 0} movie images")
    except Exception as e:
        print(f"⚠️  Error loading images: {e}")
        movie_images = []
    
    print("\nStep 3: Building background...")
    try:
        grid_layout_css, background_html = build_background(movie_images)
        print("✅ Background built successfully")
    except Exception as e:
        print(f"❌ Error building background: {e}")
        traceback.print_exc()
        sys.exit(1)
    
    print("\nStep 4: Building background CSS...")
    try:
        css = background_css(grid_layout_css)
        print("✅ Background CSS built successfully")
    except Exception as e:
        print(f"❌ Error building CSS: {e}")
        traceback.print_exc()
        sys.exit(1)
    
    print("\n✅ All utilities working correctly!")
    
except Exception as e:
    print(f"❌ Unexpected error: {e}")
    traceback.print_exc()
    sys.exit(1)
