import requests
import matplotlib.pyplot as plt
import streamlit as st
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
import os

st.set_page_config(
    page_title="Movie Recommendation System",
    layout="wide"
)

st.markdown("""
<style>
.stApp {
    background: linear-gradient(to right, #141e30, #243b55);
    color: white;
}

/* Center Login */
.login-box {
    background-color: rgba(0,0,0,0.7);
    padding: 40px;
    border-radius: 15px;
    box-shadow: 0px 0px 25px rgba(0,0,0,0.8);
}

/* Input fields */
div[data-testid="stTextInput"] > div > div > input {
    background-color: #1f1f1f;
    color: white;
}

/* Button */
.stButton>button {
    background-color: #e50914;
    color: white;
    border-radius: 8px;
    width: 100%;
}
</style>
""", unsafe_allow_html=True)

OMDB_API_KEY =("e09f8ad5")

# -------- LOGIN SYSTEM --------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "username" not in st.session_state:
    st.session_state.username = ""

if not st.session_state.logged_in:

    col1, col2, col3 = st.columns([1,2,1])

    with col2:
        st.markdown("<div class='login-box'>", unsafe_allow_html=True)
        st.markdown("<h1 style='text-align:center;'>🎬 Welcome Back</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align:center;'>Login to continue</p>", unsafe_allow_html=True)

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
