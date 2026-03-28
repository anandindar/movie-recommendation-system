import streamlit as st

st.write("✅ Streamlit is working!")
st.write("Testing basic connectivity...")

try:
    from auth import init_db
    st.write("✅ Auth module imported")
    
    result = init_db()
    if result:
        st.success("✅ Database initialized!")
    else:
        st.error("❌ Database initialization failed")
        st.info("Check that MySQL is running and your credentials in config.py are correct")
except Exception as e:
    st.error(f"❌ Error: {str(e)}")
    st.write(f"Details: {type(e).__name__}")
