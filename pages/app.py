import re
import requests
import matplotlib.pyplot as plt
import streamlit as st
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from utils import OMDB_API_KEY

# NOTE: st.set_page_config is intentionally NOT called here.
# It is already set once in dashboard.py (the entry point).
# Calling it again causes a StreamlitAPIException.

# ── Auth guard ───────────────────────────────────────────────────────────────
# When accessed directly while logged out, send user to login page.
if not st.session_state.get("logged_in", False):
    st.switch_page("dashboard.py")
    st.stop()

# ── Global CSS (Netflix-style cards + hover + badges + genre tags) ───────────
st.markdown(
    """
    <style>
    /* ── page background ── */
    [data-testid="stAppViewContainer"] { background: #0e0e0e; }
    [data-testid="stSidebar"]          { background: #141414; }

    /* ── search bar ── */
    .search-wrapper {
        display: flex; align-items: center; gap: 10px;
        background: #1f1f1f; border-radius: 8px;
        padding: 6px 14px; margin-bottom: 8px;
        border: 1px solid #333;
    }
    .search-wrapper input { background: transparent; border: none; color: #fff; font-size: 15px; flex: 1; outline: none; }
    .suggestion-box {
        background: #1f1f1f; border: 1px solid #333; border-radius: 8px;
        max-height: 220px; overflow-y: auto; margin-bottom: 12px;
    }
    .suggestion-item {
        padding: 8px 14px; color: #ccc; font-size: 14px; cursor: pointer;
        border-bottom: 1px solid #2a2a2a;
        transition: background 0.2s;
    }
    .suggestion-item:hover { background: #e50914; color: #fff; }

    /* ── Netflix movie grid ── */
    .movie-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
        gap: 20px;
        padding: 20px 0;
    }
    .movie-card {
        position: relative;
        border-radius: 10px;
        overflow: hidden;
        background: #1a1a1a;
        cursor: pointer;
        transition: transform 0.35s cubic-bezier(.25,.46,.45,.94),
                    box-shadow  0.35s ease;
        box-shadow: 0 4px 12px rgba(0,0,0,.5);
    }
    .movie-card:hover {
        transform: scale(1.08) translateY(-4px);
        box-shadow: 0 16px 40px rgba(0,0,0,.8);
        z-index: 20;
    }
    .movie-card img {
        width: 100%; height: 240px;
        object-fit: cover; display: block;
    }

    /* ── hover overlay (genres visible on hover) ── */
    .card-overlay {
        position: absolute; inset: 0;
        background: linear-gradient(to top, rgba(0,0,0,.95) 0%, transparent 55%);
        display: flex; flex-direction: column;
        justify-content: flex-end; padding: 10px 8px 8px;
        opacity: 0; transition: opacity 0.35s ease;
    }
    .movie-card:hover .card-overlay { opacity: 1; }

    /* ── year badge (top-left) ── */
    .year-badge {
        position: absolute; top: 8px; left: 8px;
        background: rgba(0,0,0,.72); color: #d4d4d4;
        font-size: 11px; font-weight: 600;
        padding: 2px 7px; border-radius: 5px;
        letter-spacing: .4px;
    }
    /* ── IMDb rating badge (top-right) ── */
    .rating-badge {
        position: absolute; top: 8px; right: 8px;
        background: #f5c518; color: #000;
        font-size: 11px; font-weight: 800;
        padding: 2px 7px; border-radius: 5px;
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

# ── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(f"### 👤 {st.session_state.get('username', '')}")
    st.divider()
    if st.button("🚪 Logout"):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.switch_page("dashboard.py")

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown(
    "<h1 style='text-align:center; letter-spacing:1px;'>🎬 Movie Recommendation System</h1>",
    unsafe_allow_html=True,
)
st.caption(f"Logged in as **{st.session_state.username}**")

# ── Load data ──────────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    ratings = pd.read_csv("Database/ratings.csv")
    movies  = pd.read_csv("Database/movies.csv")
    links   = pd.read_csv("Database/links.csv")
    return ratings, movies, links

@st.cache_data
def build_similarity(ratings):
    matrix = ratings.pivot_table(
        index="userId", columns="movieId", values="rating"
    ).fillna(0)
    sim = cosine_similarity(matrix.T)
    return pd.DataFrame(sim, index=matrix.columns, columns=matrix.columns)

ratings, movies, links = load_data()
similarity_df = build_similarity(ratings)

# ── Helpers ────────────────────────────────────────────────────────────────────
DEFAULT_POSTER = "https://placehold.co/300x450/1a1a1a/555?text=No+Poster"

@st.cache_data(show_spinner=False)
def fetch_movie_data(imdb_id: str) -> dict:
    """Fetch poster URL + IMDb rating from OMDB API."""
    result = {"poster": None, "rating": None}
    try:
        url  = f"http://www.omdbapi.com/?i={imdb_id}&apikey={OMDB_API_KEY}"
        data = requests.get(url, timeout=5).json()
        if data.get("Response") == "True":
            poster = data.get("Poster", "")
            if poster and poster != "N/A":
                result["poster"] = poster
            rating = data.get("imdbRating", "")
            if rating and rating != "N/A":
                result["rating"] = rating
    except Exception as e:
        print("OMDB error:", e)
    return result


def extract_year(title: str) -> str:
    """Pull the (YYYY) year from a movie title string."""
    m = re.search(r"\((\d{4})\)\s*$", title)
    return m.group(1) if m else ""


def clean_title(title: str) -> str:
    """Remove trailing (year) from display title."""
    return re.sub(r"\s*\(\d{4}\)\s*$", "", title).strip()


def recommend(movie_id, top_n=5):
    scores  = similarity_df[movie_id].sort_values(ascending=False)
    top_ids = scores.iloc[1 : top_n + 1].index
    return movies[movies["movieId"].isin(top_ids)][["movieId", "title", "genres"]]


def build_movie_card(title: str, genres: str, year: str,
                     poster_url: str, rating: str) -> str:
    """Return an HTML snippet for one Netflix-style movie card."""
    safe_title = title.replace('"', "&quot;").replace("'", "&#39;")
    genre_list = genres.split("|") if genres else []
    genre_tags = "".join(
        f'<span class="genre-tag">{g}</span>' for g in genre_list[:4]
    )
    year_badge   = f'<span class="year-badge">{year}</span>' if year else ""
    rating_badge = (
        f'<span class="rating-badge">⭐ {rating}</span>' if rating else ""
    )
    return f"""
    <div class="movie-card">
      <img src="{poster_url}" alt="{safe_title}" loading="lazy"
           onerror="this.src='{DEFAULT_POSTER}'" />
      {year_badge}
      {rating_badge}
      <div class="card-overlay">
        <div class="genre-row">{genre_tags}</div>
      </div>
      <div class="card-body">
        <div class="card-title" title="{safe_title}">{clean_title(title)}</div>
      </div>
    </div>"""


# ════════════════════════════════════════════════════════════════════════════
# SECTION 1 – Recommendations
# ════════════════════════════════════════════════════════════════════════════
st.markdown("## 🔎 Movie Recommendations")

# ── Search with live suggestions ─────────────────────────────────────────────
all_titles = sorted(movies["title"].tolist())

search_query = st.text_input(
    "🔍  Search a movie...",
    placeholder="e.g. Toy Story, The Matrix, Inception...",
    label_visibility="collapsed",
)

# Suggestion dropdown (shows up to 8 matches while typing)
selected_movie = None
if search_query.strip():
    q_lower = search_query.lower()
    suggestions = [t for t in all_titles if q_lower in t.lower()][:8]
    if suggestions:
        # Show a compact selectbox acting as suggestion list
        selected_movie = st.selectbox(
            "Suggestions",
            suggestions,
            label_visibility="collapsed",
        )
    else:
        st.caption("No matching movies found.")
else:
    selected_movie = st.selectbox(
        "Or pick from full list",
        all_titles,
        label_visibility="collapsed",
    )

num_recommendations = st.slider(
    "Number of recommendations", min_value=3, max_value=15, value=8
)

if st.button("🎬  Get Recommendations", use_container_width=True):
    if selected_movie:
        movie_id_val = movies[movies["title"] == selected_movie]["movieId"].values
        if len(movie_id_val) == 0:
            st.warning("Movie not found in database.")
        else:
            movie_id = movie_id_val[0]
            recs = recommend(movie_id, top_n=num_recommendations)

            st.markdown("### Recommended Movies")

            # ── Loading skeleton while fetching OMDB data ──────────────────
            skeleton_html = "".join(
                f'<div class="skeleton"></div>' for _ in range(min(len(recs), 8))
            )
            skeleton_holder = st.empty()
            skeleton_holder.markdown(
                f'<div class="movie-grid">{skeleton_html}</div>',
                unsafe_allow_html=True,
            )

            # ── Fetch OMDB data with spinner ──────────────────────────────
            cards_html = []
            with st.spinner("Fetching movie details…"):
                for _, row in recs.iterrows():
                    mid      = row["movieId"]
                    title    = row["title"]
                    genres   = row["genres"]
                    year     = extract_year(title)
                    imdb_row = links[links["movieId"] == mid]

                    poster_url = DEFAULT_POSTER
                    rating     = None
                    if not imdb_row.empty:
                        raw = str(imdb_row["imdbId"].values[0]).strip()
                        imdb_id = raw if raw.startswith("tt") else "tt" + raw.zfill(7)
                        data    = fetch_movie_data(imdb_id)
                        if data["poster"]:
                            poster_url = data["poster"]
                        rating = data["rating"]

                    cards_html.append(
                        build_movie_card(title, genres, year, poster_url, rating)
                    )

            # ── Replace skeleton with real grid ───────────────────────────
            skeleton_holder.markdown(
                f'<div class="movie-grid">{"".join(cards_html)}</div>',
                unsafe_allow_html=True,
            )

# ════════════════════════════════════════════════════════════════════════════
# SECTION 2 – Analytics Dashboard
# ════════════════════════════════════════════════════════════════════════════
st.divider()
st.markdown("## 📊 Movie Analytics Dashboard")

# ── Key metrics row ───────────────────────────────────────────────────────
m1, m2, m3, m4 = st.columns(4)
m1.metric("🎬 Total Movies",   f"{len(movies):,}")
m2.metric("👥 Total Users",    f"{ratings['userId'].nunique():,}")
m3.metric("⭐ Total Ratings",  f"{len(ratings):,}")
m4.metric("📈 Avg Rating",     f"{ratings['rating'].mean():.2f}")

st.markdown("")   # spacer

# ── Helper: dark-themed figure ────────────────────────────────────────────
BG   = "#0e0e0e"
TILE = "#1a1a1a"
RED  = "#e50914"
GOLD = "#f5c518"
TEAL = "#00b4d8"

def dark_fig(w=10, h=5):
    fig, ax = plt.subplots(figsize=(w, h), facecolor=BG)
    ax.set_facecolor(TILE)
    for spine in ax.spines.values():
        spine.set_edgecolor("#333")
    ax.tick_params(colors="#bbb", labelsize=10)
    ax.xaxis.label.set_color("#aaa")
    ax.yaxis.label.set_color("#aaa")
    return fig, ax

# ── Top + Most Watched side by side ──────────────────────────────────────
avg_rating = (
    ratings.groupby("movieId")["rating"]
    .mean()
    .reset_index()
    .merge(movies, on="movieId")
)
top_rated = avg_rating.sort_values("rating", ascending=False).head(10)

count_rating = (
    ratings.groupby("movieId")
    .size()
    .reset_index(name="count")
    .merge(movies, on="movieId")
)
most_rated = count_rating.sort_values("count", ascending=False).head(10)

col_a, col_b = st.columns(2)

with col_a:
    st.markdown("### ⭐ Top Rated Movies")
    fig, ax = dark_fig()
    bars = ax.barh(top_rated["title"], top_rated["rating"],
                   color=RED, edgecolor="none", height=0.65)
    ax.bar_label(bars, fmt="%.2f", color="#fff", fontsize=9, padding=4)
    ax.set_xlim(0, 5.8)
    ax.invert_yaxis()
    ax.set_xlabel("Average Rating")
    ax.tick_params(axis="y", labelsize=9)
    plt.tight_layout()
    st.pyplot(fig)
    plt.close(fig)

with col_b:
    st.markdown("### 🔥 Most Watched Movies")
    fig2, ax2 = dark_fig()
    bars2 = ax2.barh(most_rated["title"], most_rated["count"],
                     color=GOLD, edgecolor="none", height=0.65)
    ax2.bar_label(bars2, fmt="%d", color="#fff", fontsize=9, padding=4)
    ax2.invert_yaxis()
    ax2.set_xlabel("Number of Ratings")
    ax2.tick_params(axis="y", labelsize=9)
    plt.tight_layout()
    st.pyplot(fig2)
    plt.close(fig2)

# ── Rating distribution + Genre breakdown side by side ───────────────────
col_c, col_d = st.columns(2)

with col_c:
    st.markdown("### 📈 Rating Distribution")
    fig3, ax3 = dark_fig(7, 4)
    counts, edges, patches = ax3.hist(ratings["rating"], bins=10,
                                      color=RED, edgecolor=BG, linewidth=0.6)
    ax3.set_xlabel("Rating")
    ax3.set_ylabel("Count")
    plt.tight_layout()
    st.pyplot(fig3)
    plt.close(fig3)

with col_d:
    st.markdown("### 🎭 Top Genres")
    genre_counts = (
        movies["genres"]
        .str.split("|")
        .explode()
        .value_counts()
        .head(10)
    )
    fig4, ax4 = dark_fig(7, 4)
    ax4.barh(genre_counts.index[::-1], genre_counts.values[::-1],
             color=TEAL, edgecolor="none", height=0.65)
    ax4.set_xlabel("Number of Movies")
    ax4.tick_params(axis="y", labelsize=9)
    plt.tight_layout()
    st.pyplot(fig4)
    plt.close(fig4)
