import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.express as px
from utils import VALID_USERNAME, VALID_PASSWORD
from pathlib import Path
import os

# NOTE: st.set_page_config is intentionally NOT called here.
# It is already set once in dashboard.py (the entry point).
# Calling it again causes a StreamlitAPIException.

# ── Auth guard ───────────────────────────────────────────────────────────────
# When accessed directly while logged out, send user to login page.
if not st.session_state.get("logged_in", False):
    st.switch_page("dashboard.py")
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
        display: flex; align-items: center; gap: 3px;
    }

    /* ── genre tags inside overlay ── */
    .genre-row {
        display: flex; flex-wrap: wrap; gap: 4px;
        margin-bottom: 5px;
    }
    .genre-tag {
        background: rgba(229,9,20,.85); color: #fff;
        font-size: 9px; font-weight: 600;
        padding: 2px 6px; border-radius: 20px;
        text-transform: uppercase; letter-spacing: .3px;
    }

    /* ── card title & meta below poster ── */
    .card-body { padding: 8px 8px 10px; }
    .card-title {
        color: #f0f0f0; font-size: 13px; font-weight: 700;
        white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
        margin-bottom: 4px;
    }
    .card-meta { color: #888; font-size: 11px; }

    /* ── loading skeleton pulse ── */
    @keyframes pulse {
        0%   { opacity: .5; }
        50%  { opacity: 1; }
        100% { opacity: .5; }
    }
    .skeleton {
        background: #252525; border-radius: 10px;
        height: 270px;
        animation: pulse 1.4s ease-in-out infinite;
    }

    /* ── section headers ── */
    h1, h2, h3 { color: #fff !important; }

    /* ── Recommendation section inputs & controls ── */
    /* Text inputs visible */
    [data-testid="stTextInput"] input {
        background: #1a1a1a !important;
        color: #ffffff !important;
        border: 1.5px solid #444 !important;
        border-radius: 10px !important;
        padding: 12px 16px !important;
        font-size: 15px !important;
    }
    [data-testid="stTextInput"] input:focus {
        border-color: #e50914 !important;
        box-shadow: 0 0 0 2px rgba(229,9,20,0.3) !important;
    }
    [data-testid="stTextInput"] input::placeholder {
        color: #888 !important;
    }

    /* Selectbox visible */
    [data-testid="stSelectbox"] > div > div {
        background: #1a1a1a !important;
        border: 1.5px solid #444 !important;
        border-radius: 10px !important;
        color: #fff !important;
    }
    [data-testid="stSelectbox"] [data-baseweb="select"] > div {
        background: #1a1a1a !important;
        color: #fff !important;
    }
    [data-testid="stSelectbox"] svg { fill: #fff !important; }

    /* Slider visible */
    [data-testid="stSlider"] {
        padding-top: 8px !important;
        padding-bottom: 16px !important;
    }
    [data-testid="stSlider"] label p {
        color: #ddd !important;
        font-weight: 600 !important;
    }
    [data-testid="stSlider"] [data-baseweb="slider"] > div > div {
        background: #e50914 !important;
    }
    [data-testid="stSlider"] [data-baseweb="slider"] [role="slider"] {
        background: #e50914 !important;
        border-color: #fff !important;
    }

    /* Button visible & styled */
    .stButton > button {
        background: linear-gradient(90deg, #e50914 0%, #ff4b5c 100%) !important;
        color: #ffffff !important;
        border-radius: 10px !important;
        padding: 12px 24px !important;
        font-weight: 700 !important;
        font-size: 15px !important;
        border: 2px solid rgba(255,120,130,0.5) !important;
        box-shadow: 0 4px 16px rgba(229,9,20,0.4) !important;
        transition: transform 0.2s, box-shadow 0.2s !important;
    }
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 24px rgba(229,9,20,0.6) !important;
    }

    /* Caption text */
    .stCaption, [data-testid="stCaption"] {
        color: #aaa !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ── Session state initialization ──────────────────────────────────────────
if "logged_in" not in st.session_state:
    st.session_state.logged_in = True
if "username" not in st.session_state:
    st.session_state.username = "Guest User"

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

# ── Load links data for poster images ──────────────────────────────────────
@st.cache_data
def load_links():
    try:
        links = pd.read_csv("Database/links.csv")
        return links
    except:
        return pd.DataFrame()

links_df = load_links()

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
    <h1 style='font-size:48px; font-family:"Bebas Neue", sans-serif; color:#ffffff; 
               text-shadow:0 3px 15px rgba(229,9,20,0.8); letter-spacing:2px; margin:0;'>
        🎬 MOVIE ENTERTAINMENT HUB 🎬
    </h1>
    <p style='color:#ff74a8; font-size:16px; font-weight:600; margin-top:8px;'>
        Discover. Rate. Enjoy. Your Personal Movie Journey Starts Here.
    </p>
</div>
""", unsafe_allow_html=True)

# ── Sidebar Navigation ────────────────────────────────────────────────────
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
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### ⭐ Rating Distribution")
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
            
            cols = st.columns(3)
            for idx, (_, rec) in enumerate(rec_with_id.iterrows()):
                with cols[idx % 3]:
                    try:
                        movie_id = int(rec['movieId']) if pd.notna(rec['movieId']) else 0
                        poster_url = get_poster_url(movie_id) if movie_id > 0 else "https://via.placeholder.com/200x300?text=No+Poster"
                    except:
                        poster_url = "https://via.placeholder.com/200x300?text=No+Poster"
                    
                    st.image(poster_url, use_column_width=True)
                    st.markdown(f"""
                    <div style='text-align:center;'>
                        <h4 style='color:#ffffff; font-family:"Bebas Neue", sans-serif; margin:8px 0 4px 0;'>{rec['title']}</h4>
                        <p style='color:#ff74a8; font-size:12px; margin:0;'>{rec['genres']}</p>
                    </div>
                    """, unsafe_allow_html=True)

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
        cols = st.columns(3)
        for idx, (_, movie) in enumerate(filtered_df.head(12).iterrows()):
            with cols[idx % 3]:
                try:
                    movie_id = int(movie['movieId'])
                    poster_url = get_poster_url(movie_id)
                except:
                    poster_url = "https://via.placeholder.com/200x300?text=No+Poster"
                
                st.image(poster_url, use_column_width=True)
                st.markdown(f"""
                <div style='text-align:center;'>
                    <h4 style='color:#ffffff; font-family:"Bebas Neue", sans-serif; margin:8px 0 4px 0;'>{movie['title']}</h4>
                    <p style='color:#ff74a8; font-size:12px; margin:0;'>{movie['genres']}</p>
                </div>
                """, unsafe_allow_html=True)
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
    
    # Display
    cols = st.columns(3)
    for idx, (_, movie) in enumerate(top_rated.iterrows()):
        with cols[idx % 3]:
            try:
                movie_id = int(movie['movieId'])
                poster_url = get_poster_url(movie_id)
            except:
                poster_url = "https://via.placeholder.com/200x300?text=No+Poster"
            
            st.image(poster_url, use_column_width=True)
            st.markdown(f"""
            <div style='text-align:center;'>
                <h4 style='color:#ffffff; font-family:"Bebas Neue", sans-serif; margin:8px 0 4px 0;'>{movie['title']}</h4>
                <p style='color:#ff74a8; font-size:12px; margin-bottom:8px;'>{movie['genres']}</p>
                <div class='rating-badge'>⭐ {movie['avg_rating']:.1f}</div>
                <p style='color:#a0aec0; font-size:11px; margin-top:8px;'>Based on {int(movie['num_ratings'])} ratings</p>
            </div>
            """, unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════
# PAGE: PROFILE
# ════════════════════════════════════════════════════════════════════════════
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
