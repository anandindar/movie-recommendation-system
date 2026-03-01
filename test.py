import pandas as pd

# load dataset from Database folder
ratings = pd.read_csv("Database/ratings.csv")
movies = pd.read_csv("Database/movies.csv")

print("Ratings Data ✅")
print(ratings.head())

print("\nMovies Data ✅")
print(movies.head())