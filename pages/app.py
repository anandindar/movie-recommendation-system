import requests
import matplotlib.pyplot as plt
import streamlit as st
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from utils import OMDB_API_KEY

st.set_page_config(page_title="Movie Recommendations", layout="wide")

# ── Auth guard: redirect to login if not authenticated ──────────────────────
if not st.session_state.get("logged_in", False):
    st.switch_page("login.py")

# ── Sidebar ─────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(f"### 👤 {st.session_state.get('username', '')}")
    st.divider()
    if st.button("🚪 Logout"):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.switch_page("login.py")

# ── Header ───────────────────────────────────────────────────────────────────
st.markdown(
    "<h1 style='text-align:center;'>🎬 Movie Recommendation System</h1>",
    unsafe_allow_html=True,
)
st.caption(f"Logged in as **{st.session_state.username}**")

# ── Load data ─────────────────────────────────────────────────────────────────
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

# ── Helpers ───────────────────────────────────────────────────────────────────
def fetch_poster(imdb_id: str):
    try:
        url = f"http://www.omdbapi.com/?i={imdb_id}&apikey={OMDB_API_KEY}"
        data = requests.get(url, timeout=5).json()
        if data.get("Response") == "True":
            poster = data.get("Poster")
            if poster and poster != "N/A":
                return poster
    except Exception as e:
        print("Error fetching poster:", e)
    return None


def recommend(movie_id, top_n=5):
    scores = similarity_df[movie_id].sort_values(ascending=False)
    top_ids = scores.iloc[1 : top_n + 1].index
    return movies[movies["movieId"].isin(top_ids)][["title", "genres"]]


# ════════════════════════════════════════════════════════════════════════════
# SECTION 1 – Recommendations
# ════════════════════════════════════════════════════════════════════════════
st.header("🔎 Movie Recommendations")

movie_dict = dict(zip(movies["title"], movies["movieId"]))
selected_movie = st.selectbox("Search and select a movie", sorted(movie_dict.keys()))
num_recommendations = st.slider("Number of recommendations", min_value=3, max_value=15, value=5)

if st.button("Recommend"):
    movie_id = movie_dict[selected_movie]
    recs = recommend(movie_id, top_n=num_recommendations)

    st.subheader("Recommended Movies")
    DEFAULT_POSTER = "https://via.placeholder.com/300x450?text=No+Poster"

    cols = st.columns(min(len(recs), 5))
    for col_idx, (_, row) in enumerate(recs.iterrows()):
        movie_title = row["title"]
        movie_id_row = movies[movies["title"] == movie_title]["movieId"].values[0]
        imdb_row = links[links["movieId"] == movie_id_row]

        poster_url = None
        if not imdb_row.empty:
            imdb_value = str(imdb_row["imdbId"].values[0]).strip()
            imdb_id = imdb_value if imdb_value.startswith("tt") else "tt" + imdb_value.zfill(7)
            poster_url = fetch_poster(imdb_id)

        with cols[col_idx % len(cols)]:
            st.image(poster_url or DEFAULT_POSTER, use_column_width=True)
            st.caption(f"**{movie_title}**")
            st.caption(f"🎭 {row['genres']}")

# ════════════════════════════════════════════════════════════════════════════
# SECTION 2 – Analytics Dashboard
# ════════════════════════════════════════════════════════════════════════════
st.divider()
st.header("📊 Movie Analytics Dashboard")

# Top Rated Movies
avg_rating = (
    ratings.groupby("movieId")["rating"]
    .mean()
    .reset_index()
    .merge(movies, on="movieId")
)
top_rated = avg_rating.sort_values("rating", ascending=False).head(10)

st.subheader("⭐ Top Rated Movies")
fig, ax = plt.subplots()
ax.barh(top_rated["title"], top_rated["rating"])
ax.invert_yaxis()
ax.set_xlabel("Average Rating")
st.pyplot(fig)

# Most Watched Movies
count_rating = (
    ratings.groupby("movieId")
    .size()
    .reset_index(name="count")
    .merge(movies, on="movieId")
)
most_rated = count_rating.sort_values("count", ascending=False).head(10)

st.subheader("🔥 Most Watched Movies")
fig2, ax2 = plt.subplots()
ax2.barh(most_rated["title"], most_rated["count"])
ax2.invert_yaxis()
ax2.set_xlabel("Number of Ratings")
st.pyplot(fig2)

# Rating Distribution
st.subheader("📈 Rating Distribution")
fig3, ax3 = plt.subplots()
ax3.hist(ratings["rating"], bins=5, color="#e50914", edgecolor="white")
ax3.set_xlabel("Rating")
ax3.set_ylabel("Count")
st.pyplot(fig3)
