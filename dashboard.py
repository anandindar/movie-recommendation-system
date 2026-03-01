import requests
import matplotlib.pyplot as plt
import streamlit as st
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
import os
from pathlib import Path
import base64

st.set_page_config(
    page_title="Movie Recommendation System",
    layout="wide"
)

st.markdown("""
<style>
/* Professional Movie Background */
.stApp {
    background: linear-gradient(rgba(10, 10, 20, 0.7), rgba(10, 10, 20, 0.7)), 
                url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 800"><defs><pattern id="movies" x="0" y="0" width="300" height="400" patternUnits="userSpaceOnUse"><rect fill="%23111" width="300" height="400"/><text x="150" y="200" text-anchor="middle" fill="%23666" font-size="12">Movie</text></pattern></defs><rect width="1200" height="800" fill="url(%23movies)"/></svg>');
    background-attachment: fixed;
    background-size: cover;
    color: white;
    min-height: 100vh;
}

/* Top header banner */
.header-banner {
    background: linear-gradient(90deg, #000000 0%, #1a1a1a 50%, #000000 100%);
    padding: 30px 20px;
    margin-bottom: 40px;
    text-align: center;
    box-shadow: 0px 8px 25px rgba(229, 9, 20, 0.5), 
                0px 0px 40px rgba(229, 9, 20, 0.3);
    border-bottom: 4px solid #e50914;
    border-radius: 8px;
}

.header-title {
    font-size: 52px;
    font-weight: 900;
    color: #ffffff;
    text-shadow: 0px 4px 15px rgba(229, 9, 20, 0.9),
                 0px 0px 20px rgba(255, 255, 255, 0.3);
    margin: 0;
    letter-spacing: 3px;
    font-family: 'Arial Black', sans-serif;
}

.header-subtitle {
    font-size: 20px;
    color: #ff6b6b;
    margin-top: 10px;
    font-style: italic;
    text-shadow: 0px 2px 8px rgba(0, 0, 0, 0.8);
    font-weight: 600;
}

/* Center Login */
.login-box {
    background: linear-gradient(135deg, rgba(0,0,0,0.9) 0%, rgba(20,20,30,0.85) 100%);
    padding: 50px;
    border-radius: 20px;
    box-shadow: 0px 0px 50px rgba(229, 9, 20, 0.5), 
                0px 0px 100px rgba(0,0,0,0.9),
                inset 0px 0px 30px rgba(229, 9, 20, 0.1);
    border: 2px solid #e50914;
    backdrop-filter: blur(5px);
}

.login-title {
    font-size: 44px;
    font-weight: bold;
    text-shadow: 0px 2px 15px rgba(229, 9, 20, 0.7);
    color: #ffffff;
}

/* Input fields */
div[data-testid="stTextInput"] > div > div > input {
    background-color: rgba(31, 31, 31, 0.8) !important;
    color: white !important;
    border: 2px solid #e50914 !important;
    border-radius: 10px !important;
    padding: 14px !important;
    font-size: 16px !important;
    box-shadow: 0 0 15px rgba(229, 9, 20, 0.2) !important;
}

div[data-testid="stTextInput"] > div > div > input:focus {
    border-color: #ff6b6b !important;
    box-shadow: 0 0 20px rgba(229, 9, 20, 0.4), 
                0 0 40px rgba(229, 9, 20, 0.2) !important;
}

div[data-testid="stTextInput"] > label {
    color: #cccccc !important;
    font-weight: 600 !important;
    font-size: 15px !important;
}

/* Button */
.stButton>button {
    background: linear-gradient(90deg, #e50914 0%, #ff6b6b 100%) !important;
    color: white !important;
    border-radius: 10px !important;
    width: 100% !important;
    padding: 14px !important;
    font-weight: bold !important;
    border: none !important;
    font-size: 18px !important;
    box-shadow: 0px 4px 20px rgba(229, 9, 20, 0.5) !important;
    transition: all 0.3s ease !important;
}

.stButton>button:hover {
    background: linear-gradient(90deg, #ff6b6b 0%, #ff9999 100%) !important;
    box-shadow: 0px 8px 30px rgba(229, 9, 20, 0.7) !important;
}

/* Login subtitle */
.login-subtitle {
    color: #b0b0b0;
    font-size: 16px;
    font-weight: 500;
}

/* Remove extra spacing */
.stColumn {
    padding: 0 !important;
}
</style>
""", unsafe_allow_html=True)

OMDB_API_KEY =("e09f8ad5")

# Load and encode movie poster images for background
def get_image_backgrounds():
    frontend_path = Path("frontend")
    images = []
    if frontend_path.exists():
        for img_file in sorted(frontend_path.glob("*")):
            if img_file.suffix.lower() in ['.jpg', '.jpeg', '.png', '.webp']:
                try:
                    with open(img_file, 'rb') as f:
                        images.append(base64.b64encode(f.read()).decode())
                except:
                    pass
    return images

# Get all poster images
poster_images = get_image_backgrounds()

# Create background HTML with movie posters
if poster_images:
    background_html = '<div style="position:fixed;top:0;left:0;width:100%;height:100%;z-index:-1;opacity:0.15;">'
    background_html += '<div style="display:grid;grid-template-columns:repeat(3,1fr);gap:0;width:100%;height:100%;">'
    for img_data in poster_images:
        background_html += f'<img src="data:image/jpeg;base64,{img_data}" style="width:100%;height:100%;object-fit:cover;" />'
    background_html += '</div></div>'
    st.markdown(background_html, unsafe_allow_html=True)

# -------- LOGIN SYSTEM --------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "username" not in st.session_state:
    st.session_state.username = ""

if not st.session_state.logged_in:
    # Add Header Banner
    st.markdown("""
    <div class='header-banner'>
        <h1 class='header-title'>🎬 MOVIES RECOMMEND SYSTEM 🎬</h1>
        <p class='header-subtitle'>✨ Discover Your Next Favorite Movie ✨</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1,2,1])

    with col2:
        st.markdown("<div class='login-box'>", unsafe_allow_html=True)
        st.markdown("<h1 class='login-title' style='text-align:center;'>🎬 Welcome Back</h1>", unsafe_allow_html=True)
        st.markdown("<p class='login-subtitle' style='text-align:center;'>Login to continue</p>", unsafe_allow_html=True)

        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if st.button("Login"):
            if username == "anand@0814" and password == "Tamkuhi@274407":
                st.session_state.logged_in = True
                st.session_state.username = username
                st.rerun()
            else:
                st.error("Invalid Credentials ❌")

        st.markdown("</div>", unsafe_allow_html=True)

    st.stop()

st.markdown("<h1 style='text-align:center;'>🎬 Movie Recommendation System</h1>", unsafe_allow_html=True)

# Load data
ratings = pd.read_csv("Database/ratings.csv")
movies = pd.read_csv("Database/movies.csv")
links = pd.read_csv("Database/links.csv")

st.write(f"👤 Logged in as: **{st.session_state.username}**")
# Create matrix
matrix = ratings.pivot_table(
    index="userId",
    columns="movieId",
    values="rating"
).fillna(0)

movie_similarity = cosine_similarity(matrix.T)

similarity_df = pd.DataFrame(
    movie_similarity,
    index=matrix.columns,
    columns=matrix.columns
)

def fetch_poster(imdb_id):
    try:
        url = f"http://www.omdbapi.com/?i={imdb_id}&apikey={OMDB_API_KEY}"
        response = requests.get(url, timeout=5)
        data = response.json()

        if data.get("Response") == "True":
            poster = data.get("Poster")
            if poster and poster != "N/A":
                return poster

    except Exception as e:
        print("Error fetching poster:", e)

    return None

# Recommendation function
def recommend(movie_id, top_n=5):
    similar_scores = similarity_df[movie_id].sort_values(ascending=False)
    top_movies = similar_scores.iloc[1:top_n+1].index
    return movies[movies["movieId"].isin(top_movies)][["title", "genres"]]


# Dropdown for movie selection
movie_dict = dict(zip(movies["title"], movies["movieId"]))
selected_movie = st.selectbox(
    "🔎 Search and Select a Movie",
    sorted(movie_dict.keys())
)
num_recommendations = st.slider(
    "Select number of recommendations",
    min_value=3,
    max_value=15,
    value=5
)
if st.button("Recommend"):
    movie_id = movie_dict[selected_movie]
    recs = recommend(movie_id, top_n=num_recommendations)

    st.subheader("Recommended Movies:")

    DEFAULT_POSTER = "https://via.placeholder.com/300x450?text=No+Poster"

    for index, row in recs.iterrows():
        movie_title = row["title"]

        movie_id_row = movies[movies["title"] == movie_title]["movieId"].values[0]
        imdb_row = links[links["movieId"] == movie_id_row]

        if not imdb_row.empty:
            imdb_value = str(imdb_row["imdbId"].values[0]).strip()

            if not imdb_value.startswith("tt"):
                imdb_id = "tt" + imdb_value.zfill(7)
            else:
                imdb_id = imdb_value

            poster_url = fetch_poster(imdb_id)

        else:
            poster_url = None

        st.markdown(f"### {movie_title}")

        if poster_url:
            st.image(poster_url, use_column_width=True)
        else:
            st.image(DEFAULT_POSTER, use_column_width=True)
    

st.divider()
st.header("📊 Movie Analytics Dashboard")

# -------- Top Rated Movies --------
avg_rating = ratings.groupby("movieId")["rating"].mean().reset_index()
avg_rating = avg_rating.merge(movies, on="movieId")

top_rated = avg_rating.sort_values("rating", ascending=False).head(10)

st.subheader("⭐ Top Rated Movies")

fig, ax = plt.subplots()
ax.barh(top_rated["title"], top_rated["rating"])
ax.invert_yaxis()
st.pyplot(fig)


# -------- Most Rated Movies --------
count_rating = ratings.groupby("movieId").size().reset_index(name="count")
count_rating = count_rating.merge(movies, on="movieId")

most_rated = count_rating.sort_values("count", ascending=False).head(10)

st.subheader("🔥 Most Watched Movies")

fig2, ax2 = plt.subplots()
ax2.barh(most_rated["title"], most_rated["count"])
ax2.invert_yaxis()
st.pyplot(fig2)


# -------- Rating Distribution --------
st.subheader("📈 Rating Distribution")

fig3, ax3 = plt.subplots()
ax3.hist(ratings["rating"], bins=5)
st.pyplot(fig3)
