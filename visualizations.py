import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# =============================================================
# 0. DATABASE CONNECTION & DATA PREPARATION
# =============================================================
conn = sqlite3.connect("tmdb_movies.db")

# Load necessary tables into DataFrames
df_movies = pd.read_sql_query("SELECT * FROM movies", conn)
df_genres = pd.read_sql_query("SELECT * FROM genres", conn)
df_movie_genres = pd.read_sql_query("SELECT * FROM movie_genres", conn)

conn.close()

# Ensure numeric types and extract 4-digit release year
df_movies["budget"] = pd.to_numeric(df_movies["budget"], errors="coerce").fillna(0)
df_movies["revenue"] = pd.to_numeric(df_movies["revenue"], errors="coerce").fillna(0)
df_movies["runtime"] = pd.to_numeric(df_movies["runtime"], errors="coerce").fillna(0)
df_movies["vote_average"] = pd.to_numeric(df_movies["vote_average"], errors="coerce").fillna(0)
df_movies["popularity"] = pd.to_numeric(df_movies["popularity"], errors="coerce").fillna(0)
df_movies["release_year"] = pd.to_datetime(df_movies["release_date"], errors="coerce").dt.year

# Common clean subsets for reusable plotting
df_fin = df_movies[(df_movies["budget"] > 0) & (df_movies["revenue"] > 0)].copy()
df_genre_names = df_movie_genres.merge(df_genres, on="genre_id")


# =============================================================
# PART 1: UNIVARIATE ANALYSIS (4 Charts)
# =============================================================

# --- Univariate 1: Distribution of Movie Budgets (Histogram / KDE) ---
df_budget = df_movies[df_movies["budget"] > 0]
plt.figure(figsize=(8, 4))
sns.histplot(df_budget["budget"] / 1e6, bins=30, kde=True, color="purple")
plt.title("Univariate 1: Distribution of Movie Budgets", fontsize=14)
plt.xlabel("Budget (in Millions USD)", fontsize=11)
plt.ylabel("Number of Movies", fontsize=11)
plt.tight_layout()
plt.show()

# --- Univariate 2: Distribution of Runtimes (Box Plot) ---
clean_runtime = df_movies[(df_movies["runtime"] >= 40) & (df_movies["runtime"] <= 300)]
plt.figure(figsize=(8, 3))
sns.boxplot(x=clean_runtime["runtime"], color="skyblue")
plt.title("Univariate 2: Distribution of Movie Runtimes (Box Plot)", fontsize=14)
plt.xlabel("Runtime (Minutes)", fontsize=11)
plt.tight_layout()
plt.show()

# --- Univariate 3: Distribution of vote_average Scores (Histogram) ---
clean_votes = df_movies[df_movies["vote_average"] > 0]
plt.figure(figsize=(8, 4))
sns.histplot(clean_votes["vote_average"], bins=20, kde=True, color="forestgreen")
plt.title("Univariate 3: Distribution of Vote Average Ratings", fontsize=14)
plt.xlabel("Audience Rating (0 to 10)", fontsize=11)
plt.ylabel("Number of Movies", fontsize=11)
plt.tight_layout()
plt.show()

# --- Univariate 4: Count of Movies per Genre (Bar Plot) ---
top_genres = df_genre_names["genre_name"].value_counts().head(10)
plt.figure(figsize=(8, 4))
plt.barh(top_genres.index, top_genres.values, color="teal")
plt.title("Univariate 4: Top 10 Most Common Movie Genres", fontsize=14)
plt.xlabel("Number of Movies", fontsize=11)
plt.ylabel("Genre", fontsize=11)
plt.gca().invert_yaxis()
plt.tight_layout()
plt.show()


# =============================================================
# PART 2: BIVARIATE ANALYSIS (4 Charts)
# =============================================================

# --- Bivariate 1: Budget vs. Box Office Revenue (Scatter Plot) ---
plt.figure(figsize=(8, 5))
plt.scatter(df_fin["budget"] / 1e6, df_fin["revenue"] / 1e6, alpha=0.5, color="purple")
plt.title("Bivariate 1: Movie Budget vs. Box Office Revenue", fontsize=14)
plt.xlabel("Budget (in Millions USD)", fontsize=11)
plt.ylabel("Revenue (in Millions USD)", fontsize=11)
plt.grid(True, linestyle="--", alpha=0.5)
plt.tight_layout()
plt.show()

# --- Bivariate 2: Average Audience Rating by Genre (Bar Plot) ---
mg_merged = df_movies.merge(df_movie_genres, on="movie_id").merge(df_genres, on="genre_id")
selected_genres = ["Drama", "Comedy", "Action", "Horror", "Animation", "Romance", "Thriller"]
sub_genres = mg_merged[mg_merged["genre_name"].isin(selected_genres)]
avg_ratings = sub_genres.groupby("genre_name")["vote_average"].mean().sort_values()

plt.figure(figsize=(8, 4))
plt.bar(avg_ratings.index, avg_ratings.values, color="coral")
plt.title("Bivariate 2: Average Audience Rating by Genre", fontsize=14)
plt.xlabel("Genre", fontsize=11)
plt.ylabel("Average Rating (0 to 10)", fontsize=11)
plt.ylim(5.0, 7.5)
plt.tight_layout()
plt.show()

# --- Bivariate 3: Movie Releases Over Time (Line Chart) ---
yearly_counts = df_movies["release_year"].value_counts().sort_index()
yearly_counts = yearly_counts[yearly_counts.index >= 1980]

plt.figure(figsize=(9, 4))
plt.plot(yearly_counts.index, yearly_counts.values, marker="o", color="crimson", linewidth=2)
plt.title("Bivariate 3: Movie Releases Over Time (1980 - Present)", fontsize=14)
plt.xlabel("Release Year", fontsize=11)
plt.ylabel("Number of Movies", fontsize=11)
plt.grid(True, linestyle="--", alpha=0.5)
plt.tight_layout()
plt.show()

# --- Bivariate 4: Runtime vs. Audience Rating (Scatter Plot) ---
valid_runtime_votes = df_movies[
    (df_movies["runtime"] >= 40) & 
    (df_movies["runtime"] <= 240) & 
    (df_movies["vote_average"] > 0)
]

plt.figure(figsize=(8, 5))
plt.scatter(
    valid_runtime_votes["runtime"], 
    valid_runtime_votes["vote_average"], 
    alpha=0.4, 
    color="darkorange"
)
plt.title("Bivariate 4: Movie Runtime vs. Audience Rating", fontsize=14)
plt.xlabel("Runtime (Minutes)", fontsize=11)
plt.ylabel("Audience Rating (0 to 10)", fontsize=11)
plt.grid(True, linestyle="--", alpha=0.5)
plt.tight_layout()
plt.show()


# =============================================================
# PART 3: MULTIVARIATE ANALYSIS (5 Charts)
# =============================================================

# --- Multivariate 1: Correlation Matrix Heatmap ---
plt.figure(figsize=(8, 6))
numeric_fields = ["budget", "revenue", "runtime", "vote_average", "popularity"]
corr = df_movies[numeric_fields].corr()
sns.heatmap(corr, annot=True, cmap="coolwarm", fmt=".2f", linewidths=0.5)
plt.title("Multivariate 1: Correlation Heatmap Across Numerical Features", fontsize=14)
plt.tight_layout()
plt.show()

# --- Multivariate 2: Budget vs Revenue Segmented by Era (Color Scatter) ---
df_fin["era"] = df_fin["release_year"].apply(lambda y: "Pre-2000" if y < 2000 else "2000 & Later")
plt.figure(figsize=(8, 5))
sns.scatterplot(
    data=df_fin,
    x=df_fin["budget"] / 1e6,
    y=df_fin["revenue"] / 1e6,
    hue="era",
    palette={"Pre-2000": "gray", "2000 & Later": "royalblue"},
    alpha=0.6
)
plt.title("Multivariate 2: Budget vs Revenue Segmented by Era", fontsize=14)
plt.xlabel("Budget (in Millions USD)", fontsize=11)
plt.ylabel("Revenue (in Millions USD)", fontsize=11)
plt.tight_layout()
plt.show()

# --- Multivariate 3: Average Revenue by Genre Across Decades (Grouped Bar) ---
mg_fin = df_movies[df_movies["revenue"] > 0].merge(df_movie_genres, on="movie_id").merge(df_genres, on="genre_id")
mg_fin["decade"] = (mg_fin["release_year"] // 10) * 10
mg_fin_decades = mg_fin[mg_fin["decade"].isin([1990, 2000, 2010])]

top_commercial = ["Action", "Adventure", "Animation", "Comedy", "Drama"]
sub_decade = mg_fin_decades[mg_fin_decades["genre_name"].isin(top_commercial)]
decade_rev = sub_decade.groupby(["genre_name", "decade"])["revenue"].mean().unstack() / 1e6

decade_rev.plot(kind="bar", figsize=(9, 5), colormap="viridis")
plt.title("Multivariate 3: Average Box Office Revenue by Genre Across Decades", fontsize=14)
plt.xlabel("Genre", fontsize=11)
plt.ylabel("Average Revenue (in Millions USD)", fontsize=11)
plt.legend(title="Decade")
plt.tight_layout()
plt.show()

# --- Multivariate 4: Budget vs Revenue Sized by Popularity (Bubble Plot) ---
plt.figure(figsize=(9, 5))
sns.scatterplot(
    data=df_fin,
    x=df_fin["budget"] / 1e6,
    y=df_fin["revenue"] / 1e6,
    size="popularity",
    sizes=(20, 300),
    alpha=0.6,
    color="dodgerblue",
    legend=False
)
plt.title("Multivariate 4: Budget vs Revenue Sized by Popularity", fontsize=14)
plt.xlabel("Budget (in Millions USD)", fontsize=11)
plt.ylabel("Revenue (in Millions USD)", fontsize=11)
plt.grid(True, linestyle="--", alpha=0.5)
plt.tight_layout()
plt.show()

# --- Multivariate 5: Median ROI by Genre and Decade Heatmap ---
df_roi = df_movies[(df_movies["budget"] >= 1e6) & (df_movies["revenue"] > 0)].copy()
df_roi["roi"] = (df_roi["revenue"] - df_roi["budget"]) / df_roi["budget"]
df_roi["decade"] = (df_roi["release_year"] // 10) * 10

mg_roi = df_roi.merge(df_movie_genres, on="movie_id").merge(df_genres, on="genre_id")
core_genres = ["Action", "Adventure", "Animation", "Comedy", "Drama", "Horror", "Thriller"]
sub_roi = mg_roi[(mg_roi["decade"].isin([1990, 2000, 2010])) & (mg_roi["genre_name"].isin(core_genres))]

roi_pivot = sub_roi.pivot_table(index="genre_name", columns="decade", values="roi", aggfunc="median")

plt.figure(figsize=(8, 5))
sns.heatmap(roi_pivot, annot=True, cmap="YlGnBu", fmt=".2f", linewidths=0.5)
plt.title("Multivariate 5: Median ROI by Genre Across Decades", fontsize=14)
plt.xlabel("Decade", fontsize=11)
plt.ylabel("Genre", fontsize=11)
plt.tight_layout()
plt.show()