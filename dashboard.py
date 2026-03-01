import requests
import matplotlib.pyplot as plt
import streamlit as st
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
import os

OMDB_API_KEY = os.getenv("OMDB_API_KEY")

# -------- LOGIN SYSTEM --------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "username" not in st.session_state:
    st.session_state.username = ""

if not st.session_state.logged_in:
    st.title("🔐 Login to Movie Recommendation System")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if username == "anand@0814" and password == "Tamkuhi@274407":
            st.session_state.logged_in = True
            st.session_state.username = username
            st.success("Login Successful ✅")
            st.rerun()
        else:
            st.error("Invalid Credentials ❌")

    st.stop()

st.title("🎬 Movie Recommendation System")

col1, col2 = st.columns([8, 2])

with col2:
    if st.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.rerun()

st.write(f"👤 Logged in as: **{st.session_state.username}**")

# Load data
ratings = pd.read_csv("Database/ratings.csv")
movies = pd.read_csv("Database/movies.csv")
links = pd.read_csv("Database/links.csv")
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

    for index, row in recs.iterrows():
        movie_title = row["title"]

        # Get movieId
        movie_id_row = movies[movies["title"] == movie_title]["movieId"].values[0]

        # Get imdbId
        imdb_row = links[links["movieId"] == movie_id_row]

        if not imdb_row.empty:
            imdb_value = str(imdb_row["imdbId"].values[0]).strip()

            if not imdb_value.startswith("tt"):
                imdb_id = "tt" + imdb_value.zfill(7)
            else:
                imdb_id = imdb_value

            poster_url = fetch_poster(imdb_id)

            st.markdown(f"### {movie_title}")

            if poster_url:
                st.image(poster_url, width=200)
            else:
                st.write("Poster not available")

    # get movieId
    movie_id_row = movies[movies["title"] == movie_title]["movieId"].values[0]

    # get imdbId
    imdb_row = links[links["movieId"] == movie_id_row]
    

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
