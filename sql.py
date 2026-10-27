import pandas as pd
import sqlite3

conn = sqlite3.connect("tmdb_movies.db")
print("Reading cleaned CSV files...")
df_movies = pd.read_csv("cleaned_movies.csv")
df_genres = pd.read_csv("cleaned_genres.csv")
df_movie_genres = pd.read_csv("cleaned_movie_genres.csv")
df_cast = pd.read_csv("cleaned_cast.csv")
df_crew = pd.read_csv("cleaned_crew.csv")
df_keywords = pd.read_csv("cleaned_movie_keywords.csv")

print("Exporting tables into SQL database...")
df_movies.to_sql("movies", conn, if_exists="replace", index=False)
df_genres.to_sql("genres", conn, if_exists="replace", index=False)
df_movie_genres.to_sql("movie_genres", conn, if_exists="replace", index=False)
df_cast.to_sql("cast", conn, if_exists="replace", index=False)
df_crew.to_sql("crew", conn, if_exists="replace", index=False)
df_keywords.to_sql("movie_keywords", conn, if_exists="replace", index=False)
print("All 6 tables loaded successfully into 'tmdb_movies.db'!")

test_query = """
SELECT 
    m.title,
    m.release_date,
    g.genre_name
FROM movies m
JOIN movie_genres mg ON m.movie_id = mg.movie_id
JOIN genres g ON mg.genre_id = g.genre_id
LIMIT 5;
"""

df_test = pd.read_sql_query(test_query, conn)
print("\n--- Verification Query Result ---")
print(df_test)

conn.close()