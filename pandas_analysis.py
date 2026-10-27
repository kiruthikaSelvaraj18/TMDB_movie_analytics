import sqlite3
import pandas as pd

# =============================================================
# 0. Load Data from SQLite Database
# =============================================================
conn = sqlite3.connect("tmdb_movies.db")

df_movies = pd.read_sql_query("SELECT * FROM movies", conn)
df_genres = pd.read_sql_query("SELECT * FROM genres", conn)
df_movie_genres = pd.read_sql_query("SELECT * FROM movie_genres", conn)
df_cast = pd.read_sql_query("SELECT * FROM cast", conn)
df_crew = pd.read_sql_query("SELECT * FROM crew", conn)
df_keywords = pd.read_sql_query("SELECT * FROM movie_keywords", conn)

conn.close()

# Ensure numbers are treated as numbers
df_movies["budget"] = pd.to_numeric(df_movies["budget"], errors="coerce").fillna(0)
df_movies["revenue"] = pd.to_numeric(df_movies["revenue"], errors="coerce").fillna(0)
df_movies["runtime"] = pd.to_numeric(df_movies["runtime"], errors="coerce").fillna(0)

# =============================================================
# Question 1: Count Unique Entities Across All Tables
# =============================================================
print("=" * 60)
print("--- Question 1: Unique Entity Counts ---")
print("=" * 60)
# Find keyword column dynamically (keyword_id or keyword)
kw_col = "keyword_id" if "keyword_id" in df_keywords.columns else df_keywords.columns[1]

print("Unique Movies       :", df_movies["movie_id"].nunique())
print("Unique Genres       :", df_genres["genre_id"].nunique())
print("Unique Cast Members :", df_cast["person_id"].nunique())
print("Unique Crew Members :", df_crew["person_id"].nunique())
print("Unique Keywords     :", df_keywords[kw_col].nunique())

# =============================================================
# Question 2: Document Missing or Zero Budget and Revenue Counts
# =============================================================
print("\n" + "=" * 60)
print("--- Question 2: Missing / Zero Budget and Revenue ---")
print("=" * 60)
zero_budget = (df_movies["budget"] == 0).sum()
zero_revenue = (df_movies["revenue"] == 0).sum()
zero_both = ((df_movies["budget"] == 0) & (df_movies["revenue"] == 0)).sum()
valid_financials = ((df_movies["budget"] > 0) & (df_movies["revenue"] > 0)).sum()

print("Movies with $0 Budget      :", zero_budget)
print("Movies with $0 Revenue     :", zero_revenue)
print("Movies with Both $0        :", zero_both)
print("Movies with Valid Finances :", valid_financials)

# =============================================================
# Question 3: Compute Profit and ROI (Return on Investment)
# =============================================================
df_valid = df_movies[(df_movies["budget"] > 0) & (df_movies["revenue"] > 0)].copy()

# Simple math:
df_valid["profit"] = df_valid["revenue"] - df_valid["budget"]
df_valid["roi"] = df_valid["profit"] / df_valid["budget"]

print("\n" + "=" * 60)
print("--- Question 3: Top 5 Most Profitable Movies ---")
print("=" * 60)
top_profit = df_valid.sort_values(by="profit", ascending=False)
print(top_profit[["title", "budget", "revenue", "profit"]].head(5))

# =============================================================
# Question 4: Top 15 Highest-ROI Movies (Budget >= $1M)
# =============================================================
print("\n" + "=" * 60)
print("--- Question 4: Top 15 Highest-ROI Movies (Min $1M Budget) ---")
print("=" * 60)
df_big_budget = df_valid[df_valid["budget"] >= 1000000]
top_roi = df_big_budget.sort_values(by="roi", ascending=False)
print(top_roi[["title", "budget", "revenue", "roi"]].head(15))

# =============================================================
# Question 5: Yearly Release Frequency and Peak Release Year
# =============================================================
print("\n" + "=" * 60)
print("--- Question 5: Yearly Movie Releases & Peak Year ---")
print("=" * 60)
df_movies["release_year"] = pd.to_datetime(df_movies["release_date"], errors="coerce").dt.year
yearly_counts = df_movies["release_year"].value_counts()
print(yearly_counts.head(5))
print(f"Peak Year: {int(yearly_counts.index[0])} with {yearly_counts.iloc[0]} movies released")

# =============================================================
# Question 6: Runtime Statistical Outliers (Short and Long Films)
# =============================================================
print("\n" + "=" * 60)
print("--- Question 6: Runtime Outliers ---")
print("=" * 60)
valid_runtime = df_movies[df_movies["runtime"] > 0]
short_movies = valid_runtime[valid_runtime["runtime"] < 60]
long_movies = valid_runtime[valid_runtime["runtime"] > 200]

print(f"Short movies (< 60 mins)  : {len(short_movies)}")
print(f"Long movies (> 200 mins)   : {len(long_movies)}")
print("\nSample Long Movies:")
print(long_movies[["title", "runtime"]].head(5))

# =============================================================
# Question 7: Primary Genre and Popularity Across Genres
# =============================================================
print("\n" + "=" * 60)
print("--- Question 7: Average Popularity by Genre ---")
print("=" * 60)
mg_merged = df_movie_genres.merge(df_genres, on="genre_id").merge(df_movies, on="movie_id")
genre_pop = mg_merged.groupby("genre_name")["popularity"].mean().round(2).sort_values(ascending=False)
print(genre_pop)

# =============================================================
# Question 8: Top 10 Actors by Volume and Their Average Rating
# =============================================================
print("\n" + "=" * 60)
print("--- Question 8: Top Actors by Volume & Avg Rating ---")
print("=" * 60)
actor_col = "actor_name" if "actor_name" in df_cast.columns else "name"
cast_movies = df_cast.merge(df_movies, on="movie_id")
actor_stats = cast_movies.groupby(actor_col).agg(
    movie_count=("movie_id", "count"),
    avg_rating=("vote_average", "mean")
).round(2)
top_actors = actor_stats.sort_values(by="movie_count", ascending=False).head(10)
print(top_actors)

# =============================================================
# Question 9: Flag Duplicate Titles (Remakes or Re-releases)
# =============================================================
print("\n" + "=" * 60)
print("--- Question 9: Duplicate Titles (Remakes / Re-releases) ---")
print("=" * 60)
dup_titles = df_movies[df_movies.duplicated(subset=["title"], keep=False)].sort_values(by="title")
print(f"Total duplicate title records: {len(dup_titles)}")
print(dup_titles[["title", "release_date", "vote_average"]].head(10))

# =============================================================
# Question 10: Anomalies Between Popularity and Vote Count
# =============================================================
print("\n" + "=" * 60)
print("--- Question 10: Popularity vs Vote Count Anomalies ---")
print("=" * 60)
hype_anomaly = df_movies[(df_movies["popularity"] > df_movies["popularity"].median()) & (df_movies["vote_count"] < 50)]
print(f"Hyped movies (High popularity, < 50 votes): {len(hype_anomaly)}")
print(hype_anomaly[["title", "popularity", "vote_count", "release_date"]].head(5))