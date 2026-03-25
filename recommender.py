from pathlib import Path

import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity


_MODEL_CACHE = None


def _find_db_dir() -> Path:
    """Resolve Database directory in local and cloud runtimes."""
    candidates = [
        Path(__file__).resolve().parent / "Database",
        Path(__file__).resolve().parent.parent / "Database",
        Path("Database").resolve(),
    ]
    for candidate in candidates:
        if (candidate / "ratings.csv").exists() and (candidate / "movies.csv").exists():
            return candidate
    raise FileNotFoundError("Database folder with ratings.csv and movies.csv not found")


def _load_model():
    """Build and cache similarity artifacts once per process."""
    global _MODEL_CACHE
    if _MODEL_CACHE is not None:
        return _MODEL_CACHE

    db_dir = _find_db_dir()
    ratings = pd.read_csv(db_dir / "ratings.csv")
    movies = pd.read_csv(db_dir / "movies.csv")

    matrix = ratings.pivot_table(index="userId", columns="movieId", values="rating").fillna(0)
    movie_similarity = cosine_similarity(matrix.T)
    similarity_df = pd.DataFrame(movie_similarity, index=matrix.columns, columns=matrix.columns)

    _MODEL_CACHE = (movies, similarity_df)
    return _MODEL_CACHE


def recommend(movie_id, top_n=5):
    """Return top-N similar movies with title and genres."""
    movies, similarity_df = _load_model()
    if movie_id not in similarity_df.columns:
        return pd.DataFrame(columns=["title", "genres"])

    similar_scores = similarity_df[movie_id].sort_values(ascending=False)
    top_movies = similar_scores.iloc[1 : top_n + 1].index
    result = movies[movies["movieId"].isin(top_movies)][["title", "genres"]]
    return result.reset_index(drop=True)
