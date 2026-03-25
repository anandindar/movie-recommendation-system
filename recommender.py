import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity

# Load data
ratings = pd.read_csv("Database/ratings.csv")
movies = pd.read_csv("Database/movies.csv")

# Create user-movie matrix
matrix = ratings.pivot_table(
    index="userId",
    columns="movieId",
    values="rating"
).fillna(0)

print("Matrix Ready")

# Movie similarity (transpose for movie-based filtering)
movie_similarity = cosine_similarity(matrix.T)

similarity_df = pd.DataFrame(
    movie_similarity,
    index=matrix.columns,
    columns=matrix.columns
)

print("Similarity Matrix Created")


# ----------- Recommend Function -----------
def recommend(movie_id, top_n=5):
    similar_scores = similarity_df[movie_id].sort_values(ascending=False)
    top_movies = similar_scores.iloc[1:top_n+1].index

    return movies[movies["movieId"].isin(top_movies)][["title", "genres"]]


# ----------- Test Recommendation -----------
print("\nRecommended movies for movieId = 1\n")
print(recommend(1))
