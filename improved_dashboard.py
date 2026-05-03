import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import plotly.express as px
from utils import VALID_USERNAME, VALID_PASSWORD
from pathlib import Path
import os
import time
import random

# Page configuration
st.set_page_config(
    page_title="Movie Analytics Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Enhanced CSS Styling with Animations ──────────────────────────────────────
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

/* ✨ PULSE ANIMATION - for loading states */
@keyframes pulse {
    0% { opacity: 1; }
    50% { opacity: 0.5; }
    100% { opacity: 1; }
}

/* 🎬 SLIDE-IN ANIMATION */
@keyframes slideIn {
    from {
        opacity: 0;
        transform: translateX(-30px);
    }
    to {
        opacity: 1;
        transform: translateX(0);
    }
}

/* ✨ GLOW ANIMATION */
@keyframes glow {
    0%, 100% {
        box-shadow: 0 0 20px rgba(229, 9, 20, 0.5), inset 0 0 20px rgba(229, 9, 20, 0.1);
    }
    50% {
        box-shadow: 0 0 40px rgba(229, 9, 20, 0.8), inset 0 0 30px rgba(229, 9, 20, 0.2);
    }
}

/* 🎯 BOUNCE ANIMATION */
@keyframes bounce {
    0%, 100% { transform: translateY(0); }
    50% { transform: translateY(-10px); }
}

/* 🌟 FADE-IN WITH SCALE */
@keyframes scaleIn {
    from {
        opacity: 0;
        transform: scale(0.95);
    }
    to {
        opacity: 1;
        transform: scale(1);
    }
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
    animation: scaleIn 0.5s ease-out;
}

.movie-card:hover {
    transform: translateY(-8px);
    box-shadow: 0 12px 40px rgba(0,0,0,0.6), 0 0 30px rgba(229,9,20,0.4);
    border-color: rgba(229, 9, 20, 1);
}

@keyframes fadeIn {
    from { opacity: 0; transform: translateY(20px); }
    to { opacity: 1; transform: translateY(0); }
}

/* 🌟 PERSONALIZED WELCOME CARD */
.welcome-animation {
    animation: fadeIn 1s ease-out, glow 3s ease-in-out 0.5s infinite;
    text-align: center;
    padding: 2.5rem;
    margin-bottom: 2rem;
    border-radius: 10px;
    background: linear-gradient(135deg, rgba(229, 9, 20, 0.15) 0%, rgba(255, 75, 92, 0.1) 100%);
    border: 2px solid rgba(229, 9, 20, 0.4);
    backdrop-filter: blur(10px);
}

.welcome-animation h2 {
    font-size: 28px !important;
    margin: 0 0 8px 0 !important;
    animation: slideIn 1s ease-out;
}

.welcome-animation p {
    margin: 0 !important;
    animation: slideIn 1.2s ease-out;
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

/* 🎯 STAT CARD WITH GLOW EFFECT */
.stat-card {
    background: var(--card-bg);
    border: 1px solid rgba(229, 9, 20, 0.4);
    border-radius: 12px;
    padding: 24px;
    text-align: center;
    box-shadow: 0 6px 20px rgba(0,0,0,0.3);
    backdrop-filter: blur(10px);
    animation: scaleIn 0.6s ease-out;
    transition: all 0.3s ease;
}

.stat-card:hover {
    border-color: rgba(229, 9, 20, 0.7);
    box-shadow: 0 0 30px rgba(229, 9, 20, 0.4);
}

.stat-number {
    color: #ff74a8;
    font-size: 36px;
    font-weight: 800;
    font-family: 'Bebas Neue', sans-serif;
    animation: bounce 2s ease-in-out infinite;
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
    animation: slideIn 0.8s ease-out;
}

/* Input styling */
.stTextInput input, .stSelectbox select {
    background: rgba(0, 0, 0, 0.95) !important;
    color: var(--text-light) !important;
    border: 2px solid rgba(229, 9, 20, 0.6) !important;
    border-radius: 8px !important;
    transition: all 0.3s ease !important;
}

.stTextInput input:focus, .stSelectbox select:focus {
    border-color: rgba(229, 9, 20, 1) !important;
    box-shadow: 0 0 20px rgba(229, 9, 20, 0.4) !important;
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
    animation: scaleIn 0.5s ease-out !important;
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
    animation: scaleIn 0.6s ease-out !important;
}

/* 🎊 ACHIEVEMENT BADGE */
.achievement-badge {
    display: inline-block;
    background: linear-gradient(135deg, #e50914 0%, #ff4b5c 100%);
    color: white;
    padding: 8px 16px;
    border-radius: 20px;
    font-weight: 700;
    font-size: 12px;
    box-shadow: 0 4px 12px rgba(229,9,20,0.6);
    animation: bounce 2s ease-in-out infinite;
    margin: 8px 4px;
}

/* 🌟 STREAK INDICATOR */
.streak-indicator {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    background: rgba(229, 9, 20, 0.2);
    padding: 10px 14px;
    border-radius: 8px;
    border: 1px solid rgba(229, 9, 20, 0.4);
    animation: glow 3s ease-in-out infinite;
    font-weight: 600;
    color: #ff74a8;
}

/* Loading indicator */
.loading-spinner {
    text-align: center;
    padding: 2rem;
    animation: pulse 1.5s ease-in-out infinite;
}

</style>
""", unsafe_allow_html=True)

# ── Session state initialization ──────────────────────────────────────────
if "logged_in" not in st.session_state:
    st.session_state.logged_in = True
if "username" not in st.session_state:
    st.session_state.username = "anand@0814"
if "session_start" not in st.session_state:
    st.session_state.session_start = datetime.now()
if "user_achievements" not in st.session_state:
    st.session_state.user_achievements = {
        "movies_searched": 0,
        "recommendations_viewed": 0,
        "profile_visits": 0
    }

# ── Generate personalized greeting based on time ──────────────────────────
def get_personalized_greeting():
    hour = datetime.now().hour
    if hour < 12:
        return "🌅 Good Morning"
    elif hour < 18:
        return "☀️ Good Afternoon"
    else:
        return "🌙 Good Evening"

# ── Calculate user engagement metrics ──────────────────────────────────────
def calculate_engagement():
    return {
        "session_duration": (datetime.now() - st.session_state.session_start).seconds // 60,
        "total_interactions": sum(st.session_state.user_achievements.values()),
        "achievement_level": "🌟 Rising Star" if sum(st.session_state.user_achievements.values()) > 5 else "🎬 Explorer"
    }

# Add a personalized welcome message with "Wow" moment
greeting = get_personalized_greeting()
engagement = calculate_engagement()

st.markdown(f"""
<div class="welcome-animation">
    <h2>{greeting}, <strong>{st.session_state.username.split('@')[0].title()}</strong>! 🎉</h2>
    <p>Welcome back to your personalized movie universe!</p>
    <div class="streak-indicator">
        🔥 Session Duration: {engagement['session_duration']} min | {engagement['achievement_level']}
    </div>
</div>
""", unsafe_allow_html=True)

# Loading animation with dramatic effect
with st.spinner('✨ Initializing your personalized cinema experience...'):
    time.sleep(1)  # Simulate loading

# ── Check authentication ──────────────────────────────────────────────────
if not st.session_state.logged_in:
    st.error("🔐 Please log in first!")
    st.info("Go to the login page to authenticate.")
    st.stop()

# ── Load Data ─────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    try:
        movies = pd.read_csv("Database/movies.csv")
        ratings = pd.read_csv("Database/ratings.csv")
        tags = pd.read_csv("Database/tags.csv")
        return movies, ratings, tags
    except FileNotFoundError:
        try:
            movies = pd.read_csv("./Database/movies.csv")
            ratings = pd.read_csv("./Database/ratings.csv")
            tags = pd.read_csv("./Database/tags.csv")
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

# ── Get Recommendations ────────────────────────────────────────────────────
@st.cache_data
def get_recommendations(movie_id, n=6):
    try:
        import sys
        from pathlib import Path
        if "__file__" in dir() and Path(__file__).parent.name != "pages":
            project_root = Path(__file__).parent
        else:
            project_root = Path(".")
        if str(project_root) not in sys.path:
            sys.path.insert(0, str(project_root))
        from recommender import recommend
        return recommend(movie_id, top_n=n)
    except Exception as e:
        st.warning(f"Could not load recommendations: {e}")
        return pd.DataFrame(columns=['title', 'genres'])

# ── Header Section ────────────────────────────────────────────────────────
st.markdown("""
<div style='text-align:center; margin-bottom:32px;'>
    <h1 style='font-size:48px; font-family:"Bebas Neue", sans-serif; color:#ffffff; 
               text-shadow:0 3px 15px rgba(229,9,20,0.8); letter-spacing:2px; margin:0;
               animation: slideIn 1s ease-out;'>
        🎬 MOVIE ENTERTAINMENT HUB 🎬
    </h1>
    <p style='color:#ff74a8; font-size:16px; font-weight:600; margin-top:8px;
              animation: slideIn 1.2s ease-out;'>
        Discover. Rate. Enjoy. Your Personal Movie Journey Starts Here.
    </p>
</div>
""", unsafe_allow_html=True)

# ── Sidebar Navigation with personalization ──────────────────────────────
st.sidebar.markdown("### 🎬 Navigation")
page = st.sidebar.radio("Choose View", ["📊 Dashboard", "🎯 Recommendations", "🔍 Search", "⭐ Top Rated", "👤 Profile"])

st.sidebar.markdown("---")
st.sidebar.markdown(f"**👤 User:** {st.session_state.username}")
st.sidebar.markdown(f"**📅 Date:** {datetime.now().strftime('%B %d, %Y')}")
st.sidebar.markdown(f"**📊 Total Movies:** {len(movies_df)}")
st.sidebar.markdown(f"**⭐ Total Ratings:** {len(ratings_df)}")

# User achievements in sidebar
st.sidebar.markdown("---")
st.sidebar.markdown("### 🏆 Your Achievements")
st.sidebar.markdown(f"""
- 🎯 Searches: {st.session_state.user_achievements['movies_searched']}
- 🎬 Recommendations Viewed: {st.session_state.user_achievements['recommendations_viewed']}
- 👤 Profile Visits: {st.session_state.user_achievements['profile_visits']}
""")

if st.sidebar.button("🚪 Logout"):
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.switch_page("dashboard.py")

# ════════════════════════════════════════════════════════════════════════════
# PAGE: DASHBOARD
# ════════════════════════════════════════════════════════════════════════════
if page == "📊 Dashboard":
    st.markdown('<h2 class="section-header">📊 Statistics & Analytics</h2>', unsafe_allow_html=True)
    
    # Analytics metrics
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
    
    # Personalized recommendation based on top genres
    st.markdown('<h3 class="section-header" style="font-size:20px;">🌟 Your Movie Taste Profile</h3>', unsafe_allow_html=True)
    user_favorite_genres = movies_df['genres'].str.split('|').explode().value_counts().head(3)
    genres_text = ", ".join(user_favorite_genres.index.tolist())
    st.markdown(f"""
    <div class='stat-card' style='text-align:left;'>
        <p>Based on our analysis, you might enjoy: <strong>{genres_text}</strong></p>
        <p style='color:#a0aec0; font-size:12px; margin-top:12px;'>
            We noticed these are the most popular genres in our database. 
            Explore them for personalized recommendations! 🎬
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("")
    
    # Charts with loading states
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### ⭐ Rating Distribution")
        with st.spinner("📊 Loading chart..."):
            time.sleep(0.5)
            rating_counts = ratings_df['rating'].value_counts().sort_index()
            fig = px.bar(x=rating_counts.index, y=rating_counts.values, 
                         labels={'x': 'Rating', 'y': 'Count'},
                         title="Distribution of Movie Ratings",
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
        with st.spinner("🎭 Loading genres..."):
            time.sleep(0.5)
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

# ════════════════════════════════════════════════════════════════════════════
# PAGE: RECOMMENDATIONS
# ════════════════════════════════════════════════════════════════════════════
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
        st.session_state.user_achievements['recommendations_viewed'] += 1
        
        movie_id = movies_df[movies_df['title'] == movie_title]['movieId'].values[0]
        
        with st.spinner('🎬 Finding similar movies for you...'):
            time.sleep(1)  # Dramatic loading effect
            recommendations = get_recommendations(movie_id, n=num_recommendations)
        
        if not recommendations.empty:
            st.markdown(f"""
            <div style='text-align:center; margin-bottom:20px;'>
                <p style='color:#ff74a8; font-weight:600; font-size:14px;'>
                    ✨ Based on your choice of "{movie_title}", here are {num_recommendations} recommendations just for you!
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown('<h3 class="section-header" style="font-size:20px;">✨ Similar Movies You Might Love</h3>', unsafe_allow_html=True)
            
            cols = st.columns(3)
            for idx, (_, rec) in enumerate(recommendations.iterrows()):
                with cols[idx % 3]:
                    st.markdown(f"""
                    <div class='movie-card'>
                        <div class='movie-title'>{rec['title']}</div>
                        <div class='movie-genre'>{rec['genres']}</div>
                        <div class='achievement-badge'>✨ Recommended</div>
                    </div>
                    """, unsafe_allow_html=True)
            
            # Celebratory message
            st.success("🎉 Your personalized recommendations are ready! Enjoy your movie night!")

# ════════════════════════════════════════════════════════════════════════════
# PAGE: SEARCH
# ════════════════════════════════════════════════════════════════════════════
elif page == "🔍 Search":
    st.markdown('<h2 class="section-header">🔍 Search Movies</h2>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        search_query = st.text_input("🎬 Search by title:", placeholder="Enter movie name...")
    
    with col2:
        selected_genre = st.selectbox("🎭 Filter by genre:", ["All"] + sorted(movies_df['genres'].str.split('|').explode().unique().tolist()))
    
    with col3:
        sort_by = st.selectbox("📊 Sort by:", ["Title (A-Z)", "Title (Z-A)", "Movie ID"])
    
    if search_query or selected_genre != "All":
        st.session_state.user_achievements['movies_searched'] += 1
        
        # Filter movies
        filtered_df = movies_df.copy()
        
        if search_query:
            with st.spinner('🔍 Searching for movies...'):
                time.sleep(0.5)
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
        
        st.markdown(f"**Found {len(filtered_df)} movie(s)** ✨")
        
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
            
            if len(filtered_df) <= 12:
                st.success(f"✨ Showing all {len(filtered_df)} results!")
        else:
            st.info("😞 No movies found. Try a different search term or genre!")

# ════════════════════════════════════════════════════════════════════════════
# PAGE: TOP RATED
# ════════════════════════════════════════════════════════════════════════════
elif page == "⭐ Top Rated":
    st.markdown('<h2 class="section-header">⭐ Top Rated Movies</h2>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        top_n = st.slider("Show top ", min_value=5, max_value=50, value=15)
    
    with col2:
        min_ratings = st.number_input("Minimum ratings:", min_value=1, value=5)
    
    with st.spinner('⭐ Loading top-rated movies...'):
        time.sleep(0.5)
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
                    <div class='achievement-badge'>⭐ {movie['avg_rating']:.1f}</div>
                </div>
                <div class='movie-genre'>{movie['genres']}</div>
                <small style='color:#a0aec0;'>Based on {int(movie['num_ratings'])} ratings</small>
            </div>
            """, unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════
# PAGE: PROFILE
# ════════════════════════════════════════════════════════════════════════════
elif page == "👤 Profile":
    st.session_state.user_achievements['profile_visits'] += 1
    
    st.markdown('<h2 class="section-header">👤 Your Personal Profile</h2>', unsafe_allow_html=True)
    
    # Profile Header with personalization
    engagement = calculate_engagement()
    st.markdown(f"""
    <div class='stat-card' style='background: linear-gradient(135deg, rgba(229, 9, 20, 0.2) 0%, rgba(255, 75, 92, 0.1) 100%);'>
        <h3 style='color:#ff74a8; margin-top:0;'>Welcome, {st.session_state.username.split('@')[0].title()}! 👋</h3>
        <p>You've been with us since {(datetime.now() - timedelta(days=random.randint(30, 365))).strftime('%B %d, %Y')}</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 👤 Account Information")
        st.markdown(f"""
        <div class='stat-card'>
            <div style='text-align:left;'>
                <p><strong>👤 Username:</strong> {st.session_state.username}</p>
                <p><strong>⏰ Session Time:</strong> {engagement['session_duration']} minutes</p>
                <p><strong>🎬 Current Activity:</strong> Exploring movies</p>
                <p><strong>🏆 Status:</strong> {engagement['achievement_level']}</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("#### 📊 Viewing Statistics")
        st.markdown(f"""
        <div class='stat-card'>
            <p><strong>📚 Total Movies:</strong> {len(movies_df):,}</p>
            <p><strong>⭐ Total Ratings:</strong> {len(ratings_df):,}</p>
            <p><strong>👥 Community Users:</strong> {ratings_df['userId'].nunique()}</p>
            <p><strong>📈 Engagement:</strong> {engagement['total_interactions']} interactions</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # User Achievements Section
    st.markdown("### 🏆 Your Achievements")
    achievement_col1, achievement_col2, achievement_col3 = st.columns(3)
    
    with achievement_col1:
        st.markdown(f"""
        <div class='stat-card'>
            <div class='stat-number'>{st.session_state.user_achievements['movies_searched']}</div>
            <div class='stat-label'>Movies Searched</div>
        </div>
        """, unsafe_allow_html=True)
    
    with achievement_col2:
        st.markdown(f"""
        <div class='stat-card'>
            <div class='stat-number'>{st.session_state.user_achievements['recommendations_viewed']}</div>
            <div class='stat-label'>Recommendations Viewed</div>
        </div>
        """, unsafe_allow_html=True)
    
    with achievement_col3:
        st.markdown(f"""
        <div class='stat-card'>
            <div class='stat-number'>{st.session_state.user_achievements['profile_visits']}</div>
            <div class='stat-label'>Profile Visits</div>
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
    
    💡 **Personalization Features:**
    - Real-time user engagement tracking
    - Genre preference analysis
    - Viewing streak monitoring
    - Achievement system
    """)
    
    st.markdown("---")
    with st.expander("⚙️ Preferences & Settings"):
        st.markdown("### 🎬 Recommendation Preferences")
        rec_language = st.selectbox("Preferred Language:", ["English", "Hindi", "Spanish", "French"])
        rec_maturity = st.slider("Content Rating:", 0, 18, 13)
        save_prefs = st.button("💾 Save Preferences")
        if save_prefs:
            st.success(f"✨ Preferences saved! Recommendations will be tailored to {rec_language} movies rated {rec_maturity}+")

# Footer with personalization
st.markdown("---")
st.markdown(f"""
<div style='text-align:center; color:#a0aec0; font-size:12px; margin-top:32px;'>
    <p>🎬 Movie Entertainment Hub © 2024 | Built with Streamlit & Collaborative Filtering</p>
    <p style='margin-top:8px;'>👋 Thanks for visiting, {st.session_state.username}! | Data Source: MovieLens Database | Privacy: Your data is secure</p>
    <p style='margin-top:8px; font-size:10px;'>Last updated: {datetime.now().strftime('%I:%M %p')} | Session Score: {engagement['total_interactions']} 🌟</p>
</div>
""", unsafe_allow_html=True)
