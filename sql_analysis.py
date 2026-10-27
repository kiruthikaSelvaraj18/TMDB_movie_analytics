import sqlite3
import pandas as pd

# Connect to the SQLite database
conn = sqlite3.connect("tmdb_movies.db")

# =============================================================
# Query 1: Action Movies Released After 2015
# =============================================================
q1 = """
SELECT m.title, m.release_date, m.vote_average, g.genre_name
FROM movies m
JOIN movie_genres mg ON m.movie_id = mg.movie_id
JOIN genres g ON mg.genre_id = g.genre_id
WHERE g.genre_name = 'Action'
  AND m.release_date >= '2016-01-01'
ORDER BY m.release_date DESC;
"""
df_q1 = pd.read_sql_query(q1, conn)
print("--- Query 1: Action Movies Released After 2015 ---")
print(df_q1.head(10))

# =============================================================
# Query 2: Top 10 Highest-Grossing Films with Genres
# =============================================================
q2 = """
SELECT m.title, m.release_date, m.revenue, GROUP_CONCAT(g.genre_name, ', ') AS genres
FROM movies m
JOIN movie_genres mg ON m.movie_id = mg.movie_id
JOIN genres g ON mg.genre_id = g.genre_id
WHERE m.revenue > 0
GROUP BY m.movie_id
ORDER BY m.revenue DESC
LIMIT 10;
"""
df_q2 = pd.read_sql_query(q2, conn)
print("\n--- Query 2: Top 10 Highest-Grossing Films ---")
print(df_q2)

# =============================================================
# Query 3: Average Budget & Revenue Grouped by Genre
# =============================================================
q3 = """
SELECT g.genre_name, 
       COUNT(m.movie_id) AS movie_count,
       ROUND(AVG(m.budget), 2) AS avg_budget, 
       ROUND(AVG(m.revenue), 2) AS avg_revenue
FROM genres g
JOIN movie_genres mg ON g.genre_id = mg.genre_id
JOIN movies m ON mg.movie_id = m.movie_id
WHERE m.budget > 0 AND m.revenue > 0
GROUP BY g.genre_name
ORDER BY avg_revenue DESC;
"""
df_q3 = pd.read_sql_query(q3, conn)
print("\n--- Query 3: Average Budget & Revenue by Genre ---")
print(df_q3)

# =============================================================
# Query 4: Top 10 Most Prolific Actors
# =============================================================
q4 = """
SELECT c.actor_name, COUNT(c.movie_id) AS movie_count
FROM cast c
GROUP BY c.actor_name
ORDER BY movie_count DESC
LIMIT 10;
"""
df_q4 = pd.read_sql_query(q4, conn)
print("\n--- Query 4: Top 10 Most Prolific Actors ---")
print(df_q4)

# =============================================================
# Query 5: Directors with More Than 3 Films
# =============================================================
q5 = """
SELECT c.director_name, COUNT(c.movie_id) AS movie_count
FROM crew c
WHERE c.job = 'Director'
GROUP BY c.director_name
HAVING COUNT(c.movie_id) > 3
ORDER BY movie_count DESC;
"""
df_q5 = pd.read_sql_query(q5, conn)
print("\n--- Query 5: Directors with More Than 3 Films ---")
print(df_q5.head(10))

# =============================================================
# Query 6: Top 10 Most Frequent Keywords
# =============================================================
q6 = """
SELECT k.keyword, COUNT(k.movie_id) AS movie_count
FROM movie_keywords k
GROUP BY k.keyword
ORDER BY movie_count DESC
LIMIT 10;
"""
df_q6 = pd.read_sql_query(q6, conn)
print("\n--- Query 6: Top 10 Most Frequent Keywords ---")
print(df_q6)

# =============================================================
# Query 7: Above-Average Budget but Below-Average Revenue
# =============================================================
q7 = """
SELECT title, release_date, budget, revenue
FROM movies
WHERE budget > (SELECT AVG(budget) FROM movies WHERE budget > 0)
  AND revenue < (SELECT AVG(revenue) FROM movies WHERE revenue > 0)
  AND budget > 0
ORDER BY budget DESC
LIMIT 10;
"""
df_q7 = pd.read_sql_query(q7, conn)
print("\n--- Query 7: High Budget / Low Revenue Movies ---")
print(df_q7)

# =============================================================
# Query 8: Actors Directed by Christopher Nolan
# =============================================================
q8 = """
SELECT DISTINCT c.actor_name, m.title, m.release_date
FROM cast c
JOIN crew cr ON c.movie_id = cr.movie_id
JOIN movies m ON c.movie_id = m.movie_id
WHERE cr.job = 'Director' 
  AND cr.director_name = 'Christopher Nolan'
ORDER BY m.release_date DESC;
"""
df_q8 = pd.read_sql_query(q8, conn)
print("\n--- Query 8: Actors Directed by Christopher Nolan ---")
print(df_q8.head(10))

# =============================================================
# Query 9: Highest-Rated Genres (Min 20 Movies)
# =============================================================
q9 = """
SELECT g.genre_name, 
       COUNT(m.movie_id) AS movie_count, 
       ROUND(AVG(m.vote_average), 2) AS avg_rating
FROM genres g
JOIN movie_genres mg ON g.genre_id = mg.genre_id
JOIN movies m ON mg.movie_id = m.movie_id
GROUP BY g.genre_name
HAVING COUNT(m.movie_id) >= 20
ORDER BY avg_rating DESC;
"""
df_q9 = pd.read_sql_query(q9, conn)
print("\n--- Query 9: Highest-Rated Genres (Min 20 Movies) ---")
print(df_q9)

# =============================================================
# Query 10: Top 10 Movies with the Most Keywords
# =============================================================
q10 = """
SELECT m.title, COUNT(k.keyword) AS keyword_count
FROM movies m
JOIN movie_keywords k ON m.movie_id = k.movie_id
GROUP BY m.movie_id
ORDER BY keyword_count DESC
LIMIT 10;
"""
df_q10 = pd.read_sql_query(q10, conn)
print("\n--- Query 10: Top 10 Movies with Most Keywords ---")
print(df_q10)

conn.close()