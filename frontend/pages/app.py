import streamlit as st
from utils import VALID_USERNAME, VALID_PASSWORD
from datetime import datetime
import pandas as pd
import plotly.express as px
from pathlib import Path
import sys

# Page configuration
st.set_page_config(
    page_title="Movie Analytics Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Import enhanced CSS styling (same as improved_dashboard.py)
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Poppins:wght@400;500;600;700;800&display=swap');

:root {
    --primary-red: #e50914;
    --primary-dark: #050814;
    --card-bg: rgba(16, 24, 46, 0.88);
    --text-light: #ffffff;
}

/* Main background */
body, html, [data-testid="stAppViewContainer"] {
    background: linear-gradient(135deg, #050814 0%, #1a1f35 100%) !important;
}

.main {
    background: linear-gradient(135deg, #050814 0%, #1a1f35 100%) !important;
}

/* Movie Card */
.movie-card {
    background: var(--card-bg);
    border: 2px solid rgba(229, 9, 20, 0.6);
    border-radius: 16px;
    padding: 20px;
    margin-bottom: 16px;
    box-shadow: 0 8px 32px rgba(0,0,0,0.4), 0 0 20px rgba(229,9,20,0.2);
    transition: all 0.3s ease;
    backdrop-filter: blur(10px);
}

.movie-card:hover {
    transform: translateY(-8px);
    box-shadow: 0 12px 40px rgba(0,0,0,0.6), 0 0 30px rgba(229,9,20,0.4);
    border-color: rgba(229, 9, 20, 1);
}

.movie-title {
    color: var(--text-light);
    font-size: 20px;
    font-weight: 800;
    font-family: 'Bebas Neue', sans-serif;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-bottom: 8px;
    text-shadow: 0 2px 8px rgba(0,0,0,0.8);
}

.movie-genre {
    color: #ff74a8;
    font-size: 14px;
    font-weight: 600;
    margin-bottom: 12px;
}

.rating-badge {
    display: inline-block;
    background: linear-gradient(90deg, #e50914 0%, #ff4b5c 100%);
    color: white;
    padding: 6px 14px;
    border-radius: 20px;
    font-weight: 700;
    font-size: 12px;
    box-shadow: 0 4px 12px rgba(229,9,20,0.5);
}

/* Stat Card */
.stat-card {
    background: var(--card-bg);
    border: 1px solid rgba(229, 9, 20, 0.4);
    border-radius: 12px;
    padding: 24px;
    text-align: center;
    box-shadow: 0 6px 20px rgba(0,0,0,0.3);
    backdrop-filter: blur(10px);
}

.stat-number {
    color: #ff74a8;
    font-size: 36px;
    font-weight: 800;
    font-family: 'Bebas Neue', sans-serif;
}

.stat-label {
    color: #b8c5d6;
    font-size: 14px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-top: 8px;
}

/* Section Header */
.section-header {
    font-size: 28px;
    font-weight: 800;
    font-family: 'Bebas Neue', sans-serif;
    color: var(--text-light);
    text-transform: uppercase;
    letter-spacing: 2px;
    margin-bottom: 24px;
    padding-bottom: 12px;
    border-bottom: 3px solid var(--primary-red);
    text-shadow: 0 2px 8px rgba(0,0,0,0.8);
}

/* Input styling */
.stTextInput input, .stSelectbox select {
    background: rgba(0, 0, 0, 0.95) !important;
    color: var(--text-light) !important;
    border: 2px solid rgba(229, 9, 20, 0.6) !important;
    border-radius: 8px !important;
}

/* Button styling */
.stButton > button {
    background: linear-gradient(90deg, #e50914 0%, #ff4b5c 100%) !important;
    color: var(--text-light) !important;
    border-radius: 8px !important;
    border: none !important;
    font-weight: 700 !important;
    font-family: 'Poppins', sans-serif !important;
    text-transform: uppercase !important;
    letter-spacing: 0.5px !important;
    box-shadow: 0 4px 16px rgba(229,9,20,0.5) !important;
    transition: all 0.2s ease !important;
}

.stButton > button:hover {
    background: linear-gradient(90deg, #ff4b5c 0%, #ff7a84 100%) !important;
    box-shadow: 0 6px 24px rgba(229,9,20,0.7) !important;
    transform: translateY(-2px) !important;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0a0d15 0%, #1a1f35 100%) !important;
    border-right: 2px solid rgba(229, 9, 20, 0.3) !important;
}

/* Overall text color */
.stMarkdown, .stText {
    color: var(--text-light) !important;
}

/* Metric styling */
[data-testid="metric-container"] {
    background: var(--card-bg) !important;
    border: 1px solid rgba(229, 9, 20, 0.3) !important;
    border-radius: 12px !important;
}

</style>
""", unsafe_allow_html=True)

# Session state initialization
if "logged_in" not in st.session_state:
    st.session_state.logged_in = True
if "username" not in st.session_state:
    st.session_state.username = "User"

# Check authentication
if not st.session_state.logged_in:
    st.error("🔐 Please log in first!")

# Load Data
@st.cache_data(show_spinner=True)
def load_data():
    try:
        from pathlib import Path
        base_path = Path(__file__).parent.parent.parent
        movies = pd.read_csv(base_path / "Database" / "movies.csv")
        ratings = pd.read_csv(base_path / "Database" / "ratings.csv")
        tags = pd.read_csv(base_path / "Database" / "tags.csv")
        return movies, ratings, tags
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None, None, None

movies_df, ratings_df, tags_df = load_data()

if movies_df is None:
    st.stop()

recommendable_movie_ids = set(ratings_df["movieId"].unique())
recommendable_titles = movies_df.loc[
    movies_df["movieId"].isin(recommendable_movie_ids), "title"
].sort_values().tolist()

# Get Recommendations
@st.cache_data
def get_recommendations(movie_id, n=6):
    try:
        import sys
        from pathlib import Path
        project_root = Path(__file__).parent.parent.parent
        if str(project_root) not in sys.path:
            sys.path.insert(0, str(project_root))
        from recommender import recommend
        return recommend(movie_id, top_n=n)
    except Exception as e:
        st.warning(f"Could not load recommendations: {e}")
        return pd.DataFrame(columns=['title', 'genres'])

# Header Section
st.markdown("""
<div style='text-align:center; margin-bottom:32px;'>
    <h1 style='font-size:48px; font-family:"Bebas Neue", sans-serif; color:#ffffff; 
               text-shadow:0 3px 15px rgba(229,9,20,0.8); letter-spacing:2px; margin:0;'>
        🎬 MOVIE ENTERTAINMENT HUB 🎬
    </h1>
    <p style='color:#ff74a8; font-size:16px; font-weight:600; margin-top:8px;'>
        Discover. Rate. Enjoy. Your Personal Movie Journey Starts Here.
    </p>
</div>
""", unsafe_allow_html=True)

# Sidebar Navigation
st.sidebar.markdown("### 🎬 Navigation")
page = st.sidebar.radio("Choose View", ["📊 Dashboard", "🎯 Recommendations", "🔍 Search", "⭐ Top Rated", "👤 Profile"])

st.sidebar.markdown("---")
st.sidebar.markdown(f"**👤 User:** {st.session_state.username}")
st.sidebar.markdown(f"**📅 Date:** {datetime.now().strftime('%B %d, %Y')}")
st.sidebar.markdown(f"**📊 Total Movies:** {len(movies_df)}")
st.sidebar.markdown(f"**⭐ Total Ratings:** {len(ratings_df)}")

if st.sidebar.button("🚪 Logout"):
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.switch_page("../../dashboard.py")

# PAGE: DASHBOARD
if page == "📊 Dashboard":
    st.markdown('<h2 class="section-header">📊 Statistics & Analytics</h2>', unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class='stat-card'>
            <div class='stat-number'>{len(movies_df)}</div>
            <div class='stat-label'>Total Movies</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        avg_rating = ratings_df['rating'].mean()
        st.markdown(f"""
        <div class='stat-card'>
            <div class='stat-number'>⭐ {avg_rating:.2f}</div>
            <div class='stat-label'>Avg Rating</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class='stat-card'>
            <div class='stat-number'>{len(ratings_df)}</div>
            <div class='stat-label'>Total Ratings</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        unique_users = ratings_df['userId'].nunique()
        st.markdown(f"""
        <div class='stat-card'>
            <div class='stat-number'>{unique_users}</div>
            <div class='stat-label'>Active Users</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### ⭐ Rating Distribution")
        rating_counts = ratings_df['rating'].value_counts().sort_index()
        fig = px.bar(x=rating_counts.index, y=rating_counts.values, 
                     labels={'x': 'Rating', 'y': 'Count'},
                     color_discrete_sequence=["#e50914"])
        fig.update_layout(
            template="plotly_dark",
            hovermode="x unified",
            plot_bgcolor='rgba(16,24,46,0.5)',
            paper_bgcolor='rgba(5,8,20,0.8)',
            font=dict(family="Poppins", color="#ffffff")
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("#### 🎭 Top 10 Genres")
        genre_data = movies_df['genres'].str.split('|').explode().value_counts().head(10)
        fig = px.bar(
            x=genre_data.values,
            y=genre_data.index,
            orientation='h',
            color_discrete_sequence=["#ff4b5c"],
            labels={'x': 'Count', 'y': 'Genre'}
        )
        fig.update_layout(
            template="plotly_dark",
            plot_bgcolor='rgba(16,24,46,0.5)',
            paper_bgcolor='rgba(5,8,20,0.8)',
            font=dict(family="Poppins", color="#ffffff"),
            yaxis={'categoryorder': 'total ascending'}
        )
        st.plotly_chart(fig, use_container_width=True)

# PAGE: RECOMMENDATIONS
elif page == "🎯 Recommendations":
    st.markdown('<h2 class="section-header">🎯 Get Movie Recommendations</h2>', unsafe_allow_html=True)
    
    st.caption(
        f"Recommendations are available for {len(recommendable_titles):,} titles with rating history."
    )
    col1, col2 = st.columns([3, 1])
    with col1:
        movie_title = st.selectbox("Select a movie you like:", recommendable_titles)
    with col2:
        num_recommendations = st.number_input("How many?", min_value=3, max_value=12, value=6)
    
    if movie_title:
        movie_id = movies_df[movies_df['title'] == movie_title]['movieId'].values[0]
        recommendations = get_recommendations(movie_id, n=num_recommendations)
        
        if not recommendations.empty:
            st.markdown('<h3 class="section-header" style="font-size:20px;">✨ Similar Movies You Might Like</h3>', unsafe_allow_html=True)
            
            cols = st.columns(3)
            for idx, (_, rec) in enumerate(recommendations.iterrows()):
                with cols[idx % 3]:
                    st.markdown(f"""
                    <div class='movie-card'>
                        <div class='movie-title'>{rec['title']}</div>
                        <div class='movie-genre'>{rec['genres']}</div>
                        <div class='rating-badge'>✨ Recommended</div>
                    </div>
                    """, unsafe_allow_html=True)

# PAGE: SEARCH
elif page == "🔍 Search":
    st.markdown('<h2 class="section-header">🔍 Search Movies</h2>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        search_query = st.text_input("🎬 Search by title:", placeholder="Enter movie name...")
    
    with col2:
        selected_genre = st.selectbox("🎭 Filter by genre:", ["All"] + movies_df['genres'].str.split('|').explode().unique().tolist())
    
    with col3:
        sort_by = st.selectbox("📊 Sort by:", ["Title (A-Z)", "Title (Z-A)", "Movie ID"])
    
    # Filter movies
    filtered_df = movies_df.copy()
    
    if search_query:
        filtered_df = filtered_df[filtered_df['title'].str.contains(search_query, case=False, na=False)]
    
    if selected_genre != "All":
        filtered_df = filtered_df[filtered_df['genres'].str.contains(selected_genre, na=False)]
    
    # Sort
    if sort_by == "Title (A-Z)":
        filtered_df = filtered_df.sort_values('title')
    elif sort_by == "Title (Z-A)":
        filtered_df = filtered_df.sort_values('title', ascending=False)
    elif sort_by == "Movie ID":
        filtered_df = filtered_df.sort_values('movieId', ascending=False)
    
    st.markdown(f"**Found {len(filtered_df)} movie(s)**")
    
    if len(filtered_df) > 0:
        cols = st.columns(3)
        for idx, (_, movie) in enumerate(filtered_df.head(12).iterrows()):
            with cols[idx % 3]:
                st.markdown(f"""
                <div class='movie-card'>
                    <div class='movie-title'>{movie['title']}</div>
                    <div class='movie-genre'>{movie['genres']}</div>
                    <small style='color:#a0aec0;'>ID: {movie['movieId']}</small>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info("No movies found. Try a different search term.")

# PAGE: TOP RATED
elif page == "⭐ Top Rated":
    st.markdown('<h2 class="section-header">⭐ Top Rated Movies</h2>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        top_n = st.slider("Show top ", min_value=5, max_value=50, value=15)
    
    with col2:
        min_ratings = st.number_input("Minimum ratings:", min_value=1, value=5)
    
    # Calculate average ratings
    movie_ratings = ratings_df.groupby('movieId').agg({
        'rating': ['mean', 'count']
    }).reset_index()
    movie_ratings.columns = ['movieId', 'avg_rating', 'num_ratings']
    
    # Filter by minimum ratings and merge with movies
    movie_ratings_filtered = movie_ratings[movie_ratings['num_ratings'] >= min_ratings]
    top_rated = movie_ratings_filtered.nlargest(top_n, 'avg_rating')
    top_rated = top_rated.merge(movies_df, on='movieId')
    
    # Display
    cols = st.columns(3)
    for idx, (_, movie) in enumerate(top_rated.iterrows()):
        with cols[idx % 3]:
            st.markdown(f"""
            <div class='movie-card'>
                <div style='display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;'>
                    <div class='movie-title' style='margin-bottom:0; flex:1;'>{movie['title']}</div>
                    <div class='rating-badge'>⭐ {movie['avg_rating']:.1f}</div>
                </div>
                <div class='movie-genre'>{movie['genres']}</div>
                <small style='color:#a0aec0;'>Based on {int(movie['num_ratings'])} ratings</small>
            </div>
            """, unsafe_allow_html=True)

# PAGE: PROFILE
elif page == "👤 Profile":
    st.markdown('<h2 class="section-header">👤 Your Profile</h2>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 👤 Account Information")
        st.markdown(f"""
        <div class='stat-card'>
            <div style='text-align:left;'>
                <p><strong>Username:</strong> {st.session_state.username}</p>
                <p><strong>Login Time:</strong> {datetime.now().strftime('%I:%M %p')}</p>
                <p><strong>Last Activity:</strong> Just now</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("#### 📊 Viewing Statistics")
        st.markdown(f"""
        <div class='stat-card'>
            <p><strong>📚 Total Movies:</strong> {len(movies_df)}</p>
            <p><strong>⭐ Total Ratings:</strong> {len(ratings_df)}</p>
            <p><strong>👥 Community Users:</strong> {ratings_df['userId'].nunique()}</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("#### 🎬 Recommendations Engine")
    st.markdown("""
    **Collaborative Filtering Algorithm**
    - Uses: Cosine Similarity Matrix
    - Dataset: MovieLens Database
    - Accuracy: Continuously improving
    - Your recommendations are personalized based on similar viewing patterns
    """)
    
    st.markdown("---")
    with st.expander("⚙️ Preferences & Settings"):
        st.markdown("### Coming Soon!")
        st.info("Additional preference settings and customization options will be available in future updates.")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align:center; color:#a0aec0; font-size:12px; margin-top:32px;'>
    <p>🎬 Movie Entertainment Hub © 2024 | Built with Streamlit & Collaborative Filtering</p>
    <p style='margin-top:8px;'>Data Source: MovieLens Database | Privacy: Your data is secure and never shared</p>
</div>
""", unsafe_allow_html=True)
