import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.express as px
from pathlib import Path
import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from utils import VALID_USERNAME, VALID_PASSWORD

# Page configuration
st.set_page_config(
    page_title="Movie Analytics Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Auth guard ───────────────────────────────────────────────────────────────
if not st.session_state.get("logged_in", False):
    st.switch_page("../../dashboard.py")
    st.stop()

# ── Enhanced CSS Styling ──────────────────────────────────────────────────
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

# ── Session state initialization ──────────────────────────────────────────
if "logged_in" not in st.session_state:
    st.session_state.logged_in = True
if "username" not in st.session_state:
    st.session_state.username = "Guest User"
if "user_ratings" not in st.session_state:
    st.session_state.user_ratings = {}
    # Load user ratings from MongoDB on startup
    user_ratings = get_user_ratings(st.session_state.username)
    if user_ratings:
        st.session_state.user_ratings = {int(k): v for k, v in user_ratings.items()}

# ── MongoDB User Functions ────────────────────────────────────────────────
def get_mongo_db():
    """Get MongoDB database instance"""
    try:
        from auth import get_mongo_db as auth_get_mongo_db
        return auth_get_mongo_db()
    except:
        return None

def save_user_rating(username, movie_id, rating):
    """Save user's movie rating to MongoDB"""
    try:
        db = get_mongo_db()
        if not db:
            return False
        
        users_col = db['users']
        users_col.update_one(
            {"username": username},
            {"$set": {f"ratings.{movie_id}": rating, "last_updated": datetime.now()}},
            upsert=True
        )
        st.session_state.user_ratings[int(movie_id)] = rating
        return True
    except Exception as e:
        st.warning(f"Could not save rating: {e}")
        return False

def get_user_ratings(username):
    """Get all user ratings from MongoDB"""
    try:
        db = get_mongo_db()
        if not db:
            return {}
        
        users_col = db['users']
        user = users_col.find_one({"username": username})
        if user and "ratings" in user:
            return user["ratings"]
        return {}
    except Exception as e:
        return {}

def get_user_stats(username):
    """Get user's viewing statistics"""
    try:
        ratings = get_user_ratings(username)
        if not ratings:
            return {"rated": 0, "avg_rating": 0, "top_genre": "None"}
        
        rated_count = len(ratings)
        avg_rating = sum(ratings.values()) / rated_count if rated_count > 0 else 0
        
        # Find top genre
        rated_ids = [int(mid) for mid in ratings.keys() if int(mid) in movies_df['movieId'].values]
        if rated_ids:
            rated_movies = movies_df[movies_df['movieId'].isin(rated_ids)]
            genres = rated_movies['genres'].str.split('|').explode()
            top_genre = genres.value_counts().index[0] if len(genres) > 0 else "None"
        else:
            top_genre = "None"
        
        return {
            "rated": rated_count,
            "avg_rating": round(avg_rating, 1),
            "top_genre": top_genre
        }
    except Exception as e:
        return {"rated": 0, "avg_rating": 0, "top_genre": "None"}

def get_user_recommendations(username, n=6):
    """Get personalized recommendations based on user's ratings"""
    try:
        ratings = get_user_ratings(username)
        if not ratings or len(ratings) < 2:
            return pd.DataFrame(columns=['title', 'genres'])
        
        # Get top-rated movie from user's ratings
        top_rated_movie_id = max(ratings, key=ratings.get)
        from recommender import recommend
        return recommend(int(top_rated_movie_id), top_n=n)
    except Exception as e:
        return pd.DataFrame(columns=['title', 'genres'])

# ── Load Data ─────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    try:
        movies = pd.read_csv("../../Database/movies.csv")
        ratings = pd.read_csv("../../Database/ratings.csv")
        tags = pd.read_csv("../../Database/tags.csv")
        return movies, ratings, tags
    except FileNotFoundError:
        try:
            movies = pd.read_csv("Database/movies.csv")
            ratings = pd.read_csv("Database/ratings.csv")
            tags = pd.read_csv("Database/tags.csv")
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
        if "__file__" in dir():
            project_root = Path(__file__).parent.parent.parent
        else:
            project_root = Path(".")
        if str(project_root) not in sys.path:
            sys.path.insert(0, str(project_root))
        from recommender import recommend
        return recommend(movie_id, top_n=n)
    except Exception as e:
        st.warning(f"Could not load recommendations: {e}")
        return pd.DataFrame(columns=['title', 'genres'])

# ── Load links data for poster images ──────────────────────────────────────
@st.cache_data
def load_links():
    try:
        links = pd.read_csv("../../Database/links.csv")
        return links
    except:
        try:
            links = pd.read_csv("Database/links.csv")
            return links
        except:
            return pd.DataFrame()

links_df = load_links()

# ── Netflix-style Grid Display Function ───────────────────────────────────
def display_netflix_grid(movies_list, columns=6, show_rating=False):
    """Display movies in a Netflix-style grid layout
    
    Args:
        movies_list: DataFrame with movie data
        columns: Number of columns in grid
        show_rating: Show rating badge if True
    """
    if not movies_list:
        st.info("No movies to display")
        return
    
    # Custom CSS for Netflix-style grid
    st.markdown("""
    <style>
    .netflix-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
        gap: 15px;
        padding: 15px 0;
    }
    
    .netflix-card {
        position: relative;
        border-radius: 10px;
        overflow: hidden;
        background: #1a1f35;
        cursor: pointer;
        transition: all 0.3s ease;
        border: 2px solid rgba(229, 9, 20, 0.3);
    }
    
    .netflix-card:hover {
        transform: scale(1.08) translateY(-8px);
        box-shadow: 0 8px 30px rgba(229, 9, 20, 0.6);
        border-color: rgba(229, 9, 20, 1);
        z-index: 100;
    }
    
    .netflix-poster {
        width: 100%;
        height: 220px;
        object-fit: cover;
        display: block;
    }
    
    .netflix-info {
        padding: 10px;
        background: rgba(5, 8, 20, 0.95);
        min-height: 70px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }
    
    .netflix-title {
        font-size: 12px;
        font-weight: 700;
        color: #ffffff;
        font-family: 'Poppins', sans-serif;
        line-height: 1.2;
        margin: 0;
        display: -webkit-box;
        -webkit-line-clamp: 2;
        -webkit-box-orient: vertical;
        overflow: hidden;
    }
    
    .netflix-genre {
        font-size: 10px;
        color: #ff74a8;
        font-weight: 600;
        margin-top: 4px;
        margin-bottom: 0;
        display: -webkit-box;
        -webkit-line-clamp: 1;
        -webkit-box-orient: vertical;
        overflow: hidden;
    }
    
    .netflix-rating {
        display: inline-block;
        background: linear-gradient(90deg, #e50914 0%, #ff4b5c 100%);
        color: white;
        padding: 3px 8px;
        border-radius: 10px;
        font-weight: 700;
        font-size: 9px;
        margin-top: 5px;
    }
    </style>
    
    <div class="netflix-grid">
    """, unsafe_allow_html=True)
    
    # Create HTML cards for each movie
    for _, movie in movies_list.iterrows():
        try:
            movie_id = int(movie['movieId'])
            poster_url = get_poster_url(movie_id)
        except:
            poster_url = "https://via.placeholder.com/180x270?text=No+Poster"
        
        genres = movie['genres'][:40] + "..." if len(str(movie['genres'])) > 40 else movie['genres']
        
        # Build rating badge HTML if show_rating is True
        rating_html = ""
        if show_rating and 'avg_rating' in movie:
            rating_html = f'<div class="netflix-rating">⭐ {movie["avg_rating"]:.1f}</div>'
        
        st.markdown(f"""
        <div class="netflix-card">
            <img src="{poster_url}" alt="{movie['title']}" class="netflix-poster" onerror="this.src='https://via.placeholder.com/180x270?text=No+Poster'">
            <div class="netflix-info">
                <div>
                    <p class="netflix-title">{movie['title']}</p>
                    <p class="netflix-genre">{genres}</p>
                    {rating_html}
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)

# ── Fetch posters from OMDB API ────────────────────────────────────────────
@st.cache_data
def get_poster_url(movie_id):
    """Fetch poster URL from OMDB API"""
    if links_df.empty:
        return "https://via.placeholder.com/200x300?text=No+Poster"
    
    try:
        from utils import OMDB_API_KEY
        imdb_data = links_df[links_df['movieId'] == movie_id]
        if imdb_data.empty:
            return "https://via.placeholder.com/200x300?text=No+Poster"
        
        imdb_id = str(imdb_data['imdbId'].values[0]).strip()
        if not imdb_id.startswith('tt'):
            imdb_id = 'tt' + imdb_id.zfill(7)
        
        import requests
        url = f"http://www.omdbapi.com/?i={imdb_id}&apikey={OMDB_API_KEY}"
        response = requests.get(url, timeout=5)
        data = response.json()
        
        if data.get("Response") == "True" and data.get("Poster"):
            poster = data.get("Poster")
            if poster != "N/A":
                return poster
    except:
        pass
    
    return "https://via.placeholder.com/200x300?text=No+Poster"

# ── Header Section ────────────────────────────────────────────────────────
st.markdown("""
<div style='text-align:center; margin-bottom:32px;'>
    <h1 style='font-size:48px; font-family:"Bebas Neue", sans-serif; color:#F5F1E8; 
               background: #000000; padding: 20px 30px; border-radius: 12px;
               text-shadow:0 2px 8px rgba(0,0,0,0.8); letter-spacing:2px; margin:0;'>
        🎬 MOVIE ENTERTAINMENT HUB 🎬
    </h1>
    <p style='color:#F5F1E8; font-size:16px; font-weight:600; margin-top:16px; background: #1a1a1a; padding: 12px 20px; border-radius: 8px; display: inline-block;'>
        Discover. Rate. Enjoy. Your Personal Movie Journey Starts Here.
    </p>
</div>
""", unsafe_allow_html=True)

# Personalized Welcome Section
user_stats = get_user_stats(st.session_state.username)
st.markdown(f"""
<div style='background: #000000; 
            border-left: 4px solid #F5F1E8; padding: 16px; border-radius: 8px; margin-bottom: 24px;'>
    <h3 style='color:#F5F1E8; margin: 0 0 8px 0; font-family:"Bebas Neue", sans-serif;'>
        👋 Welcome Back, <span style='color:#F5F1E8;'>{st.session_state.username.upper()}</span>!
    </h3>
    <p style='color:#DDD8D0; margin: 4px 0; font-size: 14px;'>
        ⭐ Movies Rated: <strong>{user_stats["rated"]}</strong> | 
        📊 Average Rating: <strong>{user_stats["avg_rating"]}</strong> | 
        🎭 Top Genre: <strong>{user_stats["top_genre"]}</strong>
    </p>
</div>
""", unsafe_allow_html=True)

# ── Sidebar Navigation ────────────────────────────────────────────────────
st.sidebar.markdown("### 🎬 Navigation")
page = st.sidebar.radio("Choose View", ["📊 Dashboard", "🎯 Recommendations", "🔍 Search", "⭐ Top Rated", "👤 Profile"])

st.sidebar.markdown("---")
user_stats = get_user_stats(st.session_state.username)
st.sidebar.markdown(f"### 👤 {st.session_state.username.upper()}")
st.sidebar.markdown(f"**⭐ Ratings:** {user_stats['rated']}")
st.sidebar.markdown(f"**⭐ Avg Rating:** {user_stats['avg_rating']}")
st.sidebar.markdown(f"**🎭 Top Genre:** {user_stats['top_genre']}")
st.sidebar.markdown(f"**📅 Date:** {datetime.now().strftime('%B %d, %Y')}")
st.sidebar.markdown(f"**🎬 Total Movies:** {len(movies_df)}")

if st.sidebar.button("🚪 Logout"):
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.switch_page("../../dashboard.py")

# ════════════════════════════════════════════════════════════════════════════
# PAGE: DASHBOARD
# ════════════════════════════════════════════════════════════════════════════
if page == "📊 Dashboard":
    st.markdown('<h2 class="section-header">📊 Your Personal Dashboard</h2>', unsafe_allow_html=True)
    
    # User's Personal Stats
    col1, col2, col3, col4 = st.columns(4)
    
    user_ratings = get_user_ratings(st.session_state.username)
    avg_user_rating = sum(user_ratings.values()) / len(user_ratings) if user_ratings else 0
    
    with col1:
        st.markdown(f"""
        <div class='stat-card'>
            <div class='stat-number'>⭐ {len(user_ratings)}</div>
            <div class='stat-label'>Your Ratings</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class='stat-card'>
            <div class='stat-number'>{avg_user_rating:.1f}</div>
            <div class='stat-label'>Avg Rating</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class='stat-card'>
            <div class='stat-number'>{len(movies_df)}</div>
            <div class='stat-label'>Total Movies</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        fav_genre = get_user_stats(st.session_state.username)["top_genre"]
        st.markdown(f"""
        <div class='stat-card'>
            <div class='stat-number'>🎭</div>
            <div class='stat-label'>{fav_genre}</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("")
    
    # Your Personalized Recommendations
    if len(user_ratings) >= 2:
        st.markdown('<h3 class="section-header" style="font-size:20px;">✨ Recommended For You</h3>', unsafe_allow_html=True)
        user_recommendations = get_user_recommendations(st.session_state.username, n=6)
        if not user_recommendations.empty:
            display_netflix_grid(user_recommendations, columns=6)
        else:
            st.info("Rate more movies to get personalized recommendations!")
    else:
        st.info("💡 Rate at least 2 movies to get personalized recommendations!")
    
    st.markdown("")
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### ⭐ Community Rating Distribution")
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
        movie_id = movies_df[movies_df['title'] == movie_title]['movieId'].values[0]
        recommendations = get_recommendations(movie_id, n=num_recommendations)
        
        if not recommendations.empty:
            # Merge with movies_df to get movieId
            rec_with_id = recommendations.merge(movies_df[['movieId', 'title']], on='title', how='left')
            
            st.markdown('<h3 class="section-header" style="font-size:20px;">✨ Similar Movies You Might Like</h3>', unsafe_allow_html=True)
            
            # Create columns for rating display
            cols = st.columns(6)
            for idx, (_, rec) in enumerate(rec_with_id.head(6).iterrows()):
                with cols[idx]:
                    try:
                        rec_movie_id = int(rec['movieId']) if pd.notna(rec['movieId']) else 0
                    except:
                        rec_movie_id = 0
                    
                    poster_url = get_poster_url(rec_movie_id) if rec_movie_id > 0 else "https://via.placeholder.com/150x220?text=No+Poster"
                    st.image(poster_url, use_column_width=True)
                    
                    st.markdown(f"""
                    <div style='text-align:center;'>
                        <h4 style='color:#ffffff; font-family:"Bebas Neue", sans-serif; margin:8px 0 4px 0; font-size:12px;'>{rec['title'][:25]}</h4>
                        <p style='color:#ff74a8; font-size:10px; margin:0;'>{rec['genres'][:20]}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Rating system
                    your_rating = st.session_state.user_ratings.get(rec_movie_id, 0)
                    rating = st.select_slider(f"Rate:", options=[0, 1, 2, 3, 4, 5], value=int(your_rating), key=f"rate_{rec_movie_id}")
                    
                    if rating > 0:
                        if st.button("💾 Save", key=f"save_{rec_movie_id}", use_container_width=True):
                            if save_user_rating(st.session_state.username, rec_movie_id, rating):
                                st.success(f"Rated ⭐ {rating}", icon="✅")
                            else:
                                st.error("Failed to save rating")

# ════════════════════════════════════════════════════════════════════════════
# PAGE: SEARCH
# ════════════════════════════════════════════════════════════════════════════
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
        # Display in grid with rating capability
        cols = st.columns(6)
        for idx, (_, movie) in enumerate(filtered_df.head(30).iterrows()):
            with cols[idx % 6]:
                try:
                    movie_id = int(movie['movieId'])
                    poster_url = get_poster_url(movie_id)
                except:
                    poster_url = "https://via.placeholder.com/150x220?text=No+Poster"
                
                st.image(poster_url, use_column_width=True)
                st.markdown(f"""
                <div style='text-align:center;'>
                    <h4 style='color:#ffffff; font-family:"Bebas Neue", sans-serif; margin:8px 0 4px 0; font-size:12px;'>{movie['title'][:25]}</h4>
                    <p style='color:#ff74a8; font-size:10px; margin:0;'>{movie['genres'][:20]}</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Quick rating
                your_rating = st.session_state.user_ratings.get(int(movie_id), 0)
                rating = st.select_slider(f"Rate:", options=[0, 1, 2, 3, 4, 5], value=int(your_rating), key=f"search_rate_{movie_id}")
                
                if rating > 0 and st.button("💾", key=f"search_save_{movie_id}", use_container_width=True):
                    if save_user_rating(st.session_state.username, movie_id, rating):
                        st.success(f"⭐ {rating}", icon="✅")
    else:
        st.info("No movies found. Try a different search term.")

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
    
    # Calculate average ratings
    movie_ratings = ratings_df.groupby('movieId').agg({
        'rating': ['mean', 'count']
    }).reset_index()
    movie_ratings.columns = ['movieId', 'avg_rating', 'num_ratings']
    
    # Filter by minimum ratings and merge with movies
    movie_ratings_filtered = movie_ratings[movie_ratings['num_ratings'] >= min_ratings]
    top_rated = movie_ratings_filtered.nlargest(top_n, 'avg_rating')
    top_rated = top_rated.merge(movies_df, on='movieId')
    
    # Display with rating option
    cols = st.columns(6)
    for idx, (_, movie) in enumerate(top_rated.iterrows()):
        with cols[idx % 6]:
            try:
                movie_id = int(movie['movieId'])
                poster_url = get_poster_url(movie_id)
            except:
                poster_url = "https://via.placeholder.com/150x220?text=No+Poster"
            
            st.image(poster_url, use_column_width=True)
            
            st.markdown(f"""
            <div style='text-align:center;'>
                <h4 style='color:#ffffff; font-family:"Bebas Neue", sans-serif; margin:8px 0 4px 0; font-size:12px;'>{movie['title'][:25]}</h4>
                <p style='color:#ff74a8; font-size:10px; margin:0;'>{movie['genres'][:20]}</p>
                <div class='rating-badge'>⭐ {movie['avg_rating']:.1f}</div>
                <p style='color:#a0aec0; font-size:10px; margin-top:4px;'>{int(movie['num_ratings'])} ratings</p>
            </div>
            """, unsafe_allow_html=True)
            
            # User rating option
            your_rating = st.session_state.user_ratings.get(int(movie_id), 0)
            rating = st.select_slider(f"Your rating:", options=[0, 1, 2, 3, 4, 5], value=int(your_rating), key=f"top_rate_{movie_id}")
            
            if rating > 0 and st.button("💾", key=f"top_save_{movie_id}", use_container_width=True):
                if save_user_rating(st.session_state.username, movie_id, rating):
                    st.success(f"⭐ {rating}", icon="✅")

# ════════════════════════════════════════════════════════════════════════════
# PAGE: PROFILE
# ════════════════════════════════════════════════════════════════════════════
elif page == "👤 Profile":
    st.markdown('<h2 class="section-header">👤 Your Personal Profile</h2>', unsafe_allow_html=True)
    
    user_ratings = get_user_ratings(st.session_state.username)
    user_stats = get_user_stats(st.session_state.username)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 👤 Account Information")
        st.markdown(f"""
        <div class='stat-card'>
            <div style='text-align:left;'>
                <p><strong>👤 Username:</strong> {st.session_state.username}</p>
                <p><strong>⭐ Movies Rated:</strong> {user_stats["rated"]}</p>
                <p><strong>📊 Average Rating:</strong> {user_stats["avg_rating"]}</p>
                <p><strong>🎭 Top Genre:</strong> {user_stats["top_genre"]}</p>
                <p><strong>🔐 Member Since:</strong> 2024</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("#### 🎯 Your Stats")
        st.markdown(f"""
        <div class='stat-card'>
            <p><strong>⭐ Total Ratings:</strong> {user_stats["rated"]}</p>
            <p><strong>🎬 Community Size:</strong> {ratings_df['userId'].nunique():,} users</p>
            <p><strong>📚 Movie Library:</strong> {len(movies_df):,} movies</p>
            <p><strong>🏆 Your Rank:</strong> Active Rater</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Your Ratings
    if user_ratings:
        st.markdown("#### ⭐ Your Recent Ratings")
        
        # Get top-rated movies
        sorted_ratings = sorted(user_ratings.items(), key=lambda x: x[1], reverse=True)
        top_ratings = sorted_ratings[:6]
        
        rated_movie_ids = [int(mid) for mid in [r[0] for r in top_ratings] if int(mid) in movies_df['movieId'].values]
        if rated_movie_ids:
            rated_movies_df = movies_df[movies_df['movieId'].isin(rated_movie_ids)].copy()
            
            # Add user ratings to dataframe
            rated_movies_df['user_rating'] = rated_movies_df['movieId'].map(lambda x: user_ratings.get(str(x), 0))
            
            display_netflix_grid(rated_movies_df, columns=6, show_rating=False)
            
            st.markdown("")
            st.markdown("**Your Rating Summary:**")
            rating_summary = pd.Series(user_ratings.values()).value_counts().sort_index(ascending=False)
            col1, col2, col3, col4, col5 = st.columns(5)
            
            for idx, (rating_val, count) in enumerate(rating_summary.items()):
                with [col1, col2, col3, col4, col5][idx]:
                    st.metric(f"⭐ {rating_val}", count)
    else:
        st.info("💡 Start rating movies to build your profile and get personalized recommendations!")
    
    st.markdown("---")
    st.markdown("#### 🎬 Recommendation Engine")
    st.markdown("""
    **How Your Recommendations Work:**
    - 🤖 Uses Collaborative Filtering
    - 📊 Analyzes your ratings and preferences
    - 🎯 Compares with similar users
    - 🚀 Gets smarter with more ratings
    - 💡 Based on MovieLens Database
    """)
    
    st.markdown("---")
    with st.expander("⚙️ Preferences & Settings"):
        st.markdown("### Coming Soon!")
        st.info("Advanced preference settings and customization options will be available in future updates.")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align:center; color:#a0aec0; font-size:12px; margin-top:32px;'>
    <p>🎬 Movie Entertainment Hub © 2024 | Built with Streamlit & Collaborative Filtering</p>
    <p style='margin-top:8px;'>Data Source: MovieLens Database | Privacy: Your data is secure and never shared</p>
</div>
""", unsafe_allow_html=True)

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
