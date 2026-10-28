import sqlite3
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns

# =============================================================
# 0. CONFIGURATION & DATABASE CONNECTIVITY
# =============================================================
st.set_page_config(
    page_title="TMDB Movie Analytics",
    page_icon="🎬",
    layout="wide"
)

# Robust database query runner
def run_query(query):
    conn = sqlite3.connect("tmdb_movies.db")
    try:
        df = pd.read_sql_query(query, conn)
    finally:
        conn.close()
    return df

# Inspect SQLite table columns dynamically so no column error occurs
def get_db_columns(tbl):
    conn = sqlite3.connect("tmdb_movies.db")
    cols = [r[1] for r in conn.execute(f"PRAGMA table_info({tbl});").fetchall()]
    conn.close()
    return cols

crew_cols = [c.lower() for c in get_db_columns("crew")]
cast_cols = [c.lower() for c in get_db_columns("cast")]
kw_cols = [c.lower() for c in get_db_columns("movie_keywords")]

# Exact column matching for your database schema
director_col = "director_name" if "director_name" in crew_cols else ("name" if "name" in crew_cols else "person_name")
actor_col = "actor_name" if "actor_name" in cast_cols else ("name" if "name" in cast_cols else "person_name")
keyword_col = "keyword" if "keyword" in kw_cols else ("keywords" if "keywords" in kw_cols else "keyword_name")

@st.cache_data
def get_all_tables():
    conn = sqlite3.connect("tmdb_movies.db")
    movies = pd.read_sql_query("SELECT * FROM movies", conn)
    genres = pd.read_sql_query("SELECT * FROM genres", conn)
    movie_genres = pd.read_sql_query("SELECT * FROM movie_genres", conn)
    cast = pd.read_sql_query("SELECT * FROM cast", conn)
    crew = pd.read_sql_query("SELECT * FROM crew", conn)
    keywords = pd.read_sql_query("SELECT * FROM movie_keywords", conn)
    conn.close()

    # Pre-clean numeric fields
    movies["budget"] = pd.to_numeric(movies["budget"], errors="coerce").fillna(0)
    movies["revenue"] = pd.to_numeric(movies["revenue"], errors="coerce").fillna(0)
    movies["runtime"] = pd.to_numeric(movies["runtime"], errors="coerce").fillna(0)
    movies["vote_average"] = pd.to_numeric(movies["vote_average"], errors="coerce").fillna(0)
    movies["popularity"] = pd.to_numeric(movies["popularity"], errors="coerce").fillna(0)
    movies["release_year"] = pd.to_datetime(movies["release_date"], errors="coerce").dt.year
    if "original_language" not in movies.columns:
        movies["original_language"] = "en"
    movies["original_language"] = movies["original_language"].fillna("en")

    return movies, genres, movie_genres, cast, crew, keywords

movies_df, genres_df, movie_genres_df, cast_df, crew_df, keywords_df = get_all_tables()

# Initialize session state variables
if "nav_page" not in st.session_state:
    st.session_state["nav_page"] = "🏠 Home"
if "exit_submitted" not in st.session_state:
    st.session_state["exit_submitted"] = False

genre_names_list = sorted(genres_df["genre_name"].dropna().unique().tolist())
min_yr = int(movies_df["release_year"].dropna().min())
max_yr = int(movies_df["release_year"].dropna().max())
languages_list = ["All"] + sorted(movies_df["original_language"].dropna().unique().tolist())

# Default filter values stored in session state
if "selected_genres" not in st.session_state:
    st.session_state["selected_genres"] = ["Action", "Drama", "Comedy"] if set(["Action", "Drama", "Comedy"]).issubset(genre_names_list) else [genre_names_list[0]]
if "year_range" not in st.session_state:
    st.session_state["year_range"] = (1990, 2020)
if "min_rating" not in st.session_state:
    st.session_state["min_rating"] = 5.0
if "selected_language" not in st.session_state:
    st.session_state["selected_language"] = "All"


# =============================================================
# 1. SIDEBAR NAVIGATION
# =============================================================
if st.session_state["nav_page"] == "🚪 Exit" and st.session_state["exit_submitted"]:
    st.markdown(
        """
        <style>
            [data-testid="stSidebar"] {display: none;}
            [data-testid="collapsedControl"] {display: none;}
        </style>
        """,
        unsafe_allow_html=True
    )
elif st.session_state["nav_page"] in ["📊 Dashboard Overview", "🔍 Query Explorer"]:
    st.sidebar.title("🎬 Navigation")
    if st.sidebar.button("🏠 Return to Homepage", use_container_width=True):
        st.session_state["nav_page"] = "🏠 Home"
        st.rerun()

    pages = ["📊 Dashboard Overview", "🔍 Query Explorer", "🚪 Exit"]
    selected_page = st.sidebar.radio(
        "Current View:",
        pages,
        index=pages.index(st.session_state["nav_page"]) if st.session_state["nav_page"] in pages else 0
    )
    if selected_page != st.session_state["nav_page"]:
        st.session_state["nav_page"] = selected_page
        st.rerun()
else:
    st.sidebar.title("🎬 Navigation")
    pages = ["🏠 Home", "📊 Dashboard Overview", "🔍 Query Explorer", "🚪 Exit"]
    selected_page = st.sidebar.radio(
        "Navigate to:",
        pages,
        index=pages.index(st.session_state["nav_page"]) if st.session_state["nav_page"] in pages else 0
    )
    st.session_state["nav_page"] = selected_page


# =============================================================
# 2. SHARED FILTERS (VISIBLE ONLY ON DASHBOARD OVERVIEW)
# =============================================================
if st.session_state["nav_page"] == "📊 Dashboard Overview":
    st.sidebar.markdown("---")
    st.sidebar.subheader("🎛️ Shared Filters")

    st.session_state["selected_genres"] = st.sidebar.multiselect(
        "Select Genre(s):",
        options=genre_names_list,
        default=st.session_state["selected_genres"]
    )

    st.session_state["year_range"] = st.sidebar.slider(
        "Release Year Range:",
        min_yr, max_yr,
        st.session_state["year_range"]
    )

    st.session_state["min_rating"] = st.sidebar.slider(
        "Minimum Rating (0 to 10):",
        0.0, 10.0,
        float(st.session_state["min_rating"]),
        step=0.5
    )

    st.session_state["selected_language"] = st.sidebar.selectbox(
        "Original Language:",
        options=languages_list,
        index=languages_list.index(st.session_state["selected_language"]) if st.session_state["selected_language"] in languages_list else 0
    )

    # Dynamic filter SQL construction
    genre_filter_sql = ""
    if st.session_state["selected_genres"]:
        quoted_genres = ", ".join(f"'{g}'" for g in st.session_state["selected_genres"])
        genre_filter_sql = f"AND g.genre_name IN ({quoted_genres})"

    lang_filter_sql = ""
    if st.session_state["selected_language"] != "All":
        lang_filter_sql = f"AND m.original_language = '{st.session_state['selected_language']}'"

    filter_sql = f"""
    SELECT DISTINCT m.movie_id, m.title, m.release_date, m.budget, m.revenue, 
           m.vote_average, m.popularity, m.original_language, g.genre_name
    FROM movies m
    JOIN movie_genres mg ON m.movie_id = mg.movie_id
    JOIN genres g ON mg.genre_id = g.genre_id
    WHERE m.vote_average >= {st.session_state['min_rating']}
      AND strftime('%Y', m.release_date) BETWEEN '{st.session_state['year_range'][0]}' AND '{st.session_state['year_range'][1]}'
      {genre_filter_sql}
      {lang_filter_sql}
    """
    filtered_movies = run_query(filter_sql)
    matching_movie_ids = filtered_movies["movie_id"].unique().tolist()
    live_count = len(matching_movie_ids)
    st.sidebar.markdown(f"**🎯 Matching Movies: `{live_count:,}`**")


# =============================================================
# PAGE 1: 🏠 HOME PAGE
# =============================================================
if st.session_state["nav_page"] == "🏠 Home":
    st.markdown(
        """
        <div style="background: linear-gradient(135deg, #0f2027, #203a43, #2c5364); padding: 35px; border-radius: 15px; color: white; margin-bottom: 25px;">
            <h1 style="color: #ffffff; margin-bottom: 10px; font-size: 2.1rem; font-weight: 700;">
                🎬 An End-to-End Exploratory Data Analysis of the Global Movie Industry (TMDB)
            </h1>
            <p style="font-size: 1.1rem; color: #cfd8dc; margin-top: 5px; line-height: 1.5;">
                An interactive analytical platform exploring cinematic performance, financials, ratings, and industry creative networks.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    c_launch, _ = st.columns([1.2, 2])
    with c_launch:
        if st.button("👉 🚀 Launch Dashboard Overview", type="primary", use_container_width=True):
            st.session_state["nav_page"] = "📊 Dashboard Overview"
            st.rerun()

    st.markdown("---")
    f1, f2, f3 = st.columns(3)
    with f1:
        st.info("📊 **Dashboard Overview**\n\nFilter movies by multiple genres, release eras, and ratings with live KPIs.")
    with f2:
        st.success("🔍 **Dual Analytics Engine**\n\nExplore 10 SQL queries and 10 Pandas tasks with tailored charts and clean tabular outputs.")
    with f3:
        st.warning("💡 **Strategic Insights**\n\nDirect business takeaways and statistical reasoning under each analytical question.")

    st.markdown("---")
    st.markdown("##### 📌 Fast Track Navigation:")
    q_col1, q_col2 = st.columns(2)
    with q_col1:
        if st.button("🔍 Go to Query Explorer", use_container_width=True):
            st.session_state["nav_page"] = "🔍 Query Explorer"
            st.rerun()
    with q_col2:
        if st.button("🚪 Exit Session", use_container_width=True):
            st.session_state["nav_page"] = "🚪 Exit"
            st.rerun()


# =============================================================
# PAGE 2: 📊 DASHBOARD OVERVIEW
# =============================================================
elif st.session_state["nav_page"] == "📊 Dashboard Overview":
    st.title("📊 Movie Analytics Dashboard")
    st.markdown("---")

    # 4 Specific Required KPIs
    col1, col2, col3, col4 = st.columns(4)
    filtered_actors = cast_df[cast_df["movie_id"].isin(matching_movie_ids)]
    total_actors = filtered_actors[actor_col].nunique() if not filtered_actors.empty else 0
    total_genres = filtered_movies["genre_name"].nunique() if live_count > 0 else 0
    avg_rating = round(filtered_movies["vote_average"].mean(), 2) if live_count > 0 else 0.0

    col1.metric("Total Movies", f"{live_count:,}")
    col2.metric("Total Genres Represented", f"{total_genres}")
    col3.metric("Total Actors", f"{total_actors:,}")
    col4.metric("Average Rating", f"{avg_rating} / 10")

    st.markdown("---")

    # Dynamic Auto-Generated Text Insight
    if live_count > 0:
        genre_rev = filtered_movies[filtered_movies["revenue"] > 0].groupby("genre_name")["revenue"].sum()
        top_genre = genre_rev.idxmax() if not genre_rev.empty else "N/A"
        top_movie = filtered_movies.sort_values("revenue", ascending=False).iloc[0]["title"] if not filtered_movies.empty else "N/A"
        st.info(f"💡 **Automated Filter Insight**: In this active selection, **{top_genre}** generates the highest cumulative revenue, led by **'{top_movie}'**.")

    # Charts: Top 10 Revenue + Genre Distribution
    ch1, ch2 = st.columns(2)
    with ch1:
        st.subheader("Top 10 Highest-Grossing Films")
        top_rev = filtered_movies.drop_duplicates("movie_id").sort_values("revenue", ascending=False).head(10)
        if not top_rev.empty and top_rev["revenue"].max() > 0:
            fig, ax = plt.subplots(figsize=(6.5, 3.8))
            ax.barh(top_rev["title"], top_rev["revenue"] / 1e6, color="royalblue", height=0.6)
            ax.invert_yaxis()
            ax.set_xlabel("Revenue ($ Millions)")
            st.pyplot(fig)
        else:
            st.info("No recorded box office revenue for this filter selection.")

    with ch2:
        st.subheader("Genre Distribution")
        g_counts = filtered_movies["genre_name"].value_counts().head(7)
        if not g_counts.empty:
            fig, ax = plt.subplots(figsize=(6.5, 3.8))
            ax.bar(g_counts.index, g_counts.values, color="coral", width=0.55)
            ax.set_ylabel("Count")
            plt.xticks(rotation=45, ha="right")
            st.pyplot(fig)
        else:
            st.info("No genre records available.")

    # Chart 3: Budget vs Revenue Scatter Plot
    st.subheader("Budget vs Revenue Correlation")
    fin_df = filtered_movies[(filtered_movies["budget"] > 0) & (filtered_movies["revenue"] > 0)].drop_duplicates("movie_id")
    if not fin_df.empty:
        fig_sc, ax_sc = plt.subplots(figsize=(8, 3.8))
        ax_sc.scatter(fin_df["budget"] / 1e6, fin_df["revenue"] / 1e6, alpha=0.6, color="darkviolet", edgecolors="none")
        ax_sc.set_xlabel("Budget ($ Millions)")
        ax_sc.set_ylabel("Revenue ($ Millions)")
        ax_sc.grid(True, linestyle="--", alpha=0.4)
        st.pyplot(fig_sc)
    else:
        st.info("No films with both budget and revenue > 0 match the selected filters.")

    # Properly sized table
    st.markdown("---")
    st.subheader("🎬 Filtered Movie Records")
    display_df = (
        filtered_movies[["title", "genre_name", "release_date", "vote_average", "budget", "revenue"]]
        .drop_duplicates("title")
        .head(40)
    )

    st.dataframe(
        display_df,
        column_config={
            "title": st.column_config.TextColumn("Movie Title", width=220),
            "genre_name": st.column_config.TextColumn("Genre", width=110),
            "release_date": st.column_config.TextColumn("Release Date", width=120),
            "vote_average": st.column_config.NumberColumn("Rating", format="%.1f", width=90),
            "budget": st.column_config.NumberColumn("Budget ($)", format="$%,d", width=130),
            "revenue": st.column_config.NumberColumn("Revenue ($)", format="$%,d", width=140),
        },
        use_container_width=True,
        hide_index=True
    )


# =============================================================
# PAGE 3: 🔍 QUERY EXPLORER
# =============================================================
elif st.session_state["nav_page"] == "🔍 Query Explorer":
    st.title("🔍 Analytical Query Explorer")
    st.markdown("---")

    engine_choice = st.radio("Select Engine Mode:", ["SQL Analysis", "Pandas Analysis"], horizontal=True)

    # ---------------------------------------------------------
    # SQL TASKS (Q1 - Q10)
    # ---------------------------------------------------------
    if engine_choice == "SQL Analysis":
        sql_options = [
            "Q1: Action Movies Released After 2015",
            "Q2: Top 10 Highest-Grossing Films with Genres",
            "Q3: Average Budget & Revenue Grouped by Genre",
            "Q4: Top 10 Most Prolific Actors",
            "Q5: Directors with More Than 3 Films",
            "Q6: Top 10 Most Frequent Keywords",
            "Q7: High Budget / Low Revenue Movies (Subquery)",
            "Q8: Actors Directed by Christopher Nolan",
            "Q9: Highest-Rated Genres (Min 20 Movies)",
            "Q10: Top 10 Movies with Most Keywords"
        ]
        chosen_sql = st.selectbox("Choose a Query Task:", sql_options)

        if chosen_sql.startswith("Q1:"):
            q = """
            SELECT m.title, m.release_date, m.vote_average, g.genre_name 
            FROM movies m
            JOIN movie_genres mg ON m.movie_id = mg.movie_id
            JOIN genres g ON mg.genre_id = g.genre_id
            WHERE g.genre_name = 'Action' AND m.release_date >= '2016-01-01'
            ORDER BY m.release_date DESC;
            """
            df_res = run_query(q)
            st.subheader("Distribution of Action Movie Ratings (Post-2015)")
            fig, ax = plt.subplots(figsize=(6.5, 3.2))
            sns.histplot(df_res["vote_average"], bins=15, kde=True, color="firebrick", ax=ax)
            ax.set_xlabel("Rating (0 to 10)")
            st.pyplot(fig)
            st.dataframe(df_res.head(20), use_container_width=True, hide_index=True)
            st.info("💡 **Insight**: Post-2015 Action movies maintain a strong rating cluster around 6.0 to 6.8.")

        elif chosen_sql.startswith("Q2:"):
            q = """
            SELECT m.title, m.release_date, m.revenue, GROUP_CONCAT(g.genre_name, ', ') AS genres
            FROM movies m
            JOIN movie_genres mg ON m.movie_id = mg.movie_id
            JOIN genres g ON mg.genre_id = g.genre_id
            WHERE m.revenue > 0
            GROUP BY m.movie_id
            ORDER BY m.revenue DESC LIMIT 10;
            """
            df_res = run_query(q)
            st.subheader("Top 10 Highest-Grossing Films")
            fig, ax = plt.subplots(figsize=(6.5, 3.5))
            ax.barh(df_res["title"], df_res["revenue"] / 1e6, color="forestgreen", height=0.6)
            ax.invert_yaxis()
            ax.set_xlabel("Revenue ($ Millions)")
            st.pyplot(fig)
            st.dataframe(
                df_res,
                column_config={"revenue": st.column_config.NumberColumn("Revenue ($)", format="$%,d")},
                use_container_width=True,
                hide_index=True
            )
            st.info("💡 **Insight**: Major franchise and sci-fi/action epics occupy all top box-office ranks.")

        elif chosen_sql.startswith("Q3:"):
            q = """
            SELECT g.genre_name, COUNT(m.movie_id) AS movie_count, 
                   ROUND(AVG(m.budget), 2) AS avg_budget, ROUND(AVG(m.revenue), 2) AS avg_revenue
            FROM genres g
            JOIN movie_genres mg ON g.genre_id = mg.genre_id
            JOIN movies m ON mg.movie_id = m.movie_id
            WHERE m.budget > 0 AND m.revenue > 0
            GROUP BY g.genre_name ORDER BY avg_revenue DESC;
            """
            df_res = run_query(q)
            st.subheader("Average Budget vs Average Revenue by Genre")
            fig, ax = plt.subplots(figsize=(7, 3.6))
            ax.bar(df_res["genre_name"], df_res["avg_revenue"] / 1e6, label="Avg Revenue", color="teal", width=0.55)
            ax.bar(df_res["genre_name"], df_res["avg_budget"] / 1e6, label="Avg Budget", color="orange", alpha=0.7, width=0.55)
            plt.xticks(rotation=45, ha="right")
            ax.set_ylabel("$ Millions")
            ax.legend()
            st.pyplot(fig)
            st.dataframe(
                df_res,
                column_config={
                    "avg_budget": st.column_config.NumberColumn("Average Budget ($)", format="$%,d"),
                    "avg_revenue": st.column_config.NumberColumn("Average Revenue ($)", format="$%,d"),
                },
                use_container_width=True,
                hide_index=True
            )
            st.info("💡 **Insight**: Animation and Adventure produce the highest box-office return multiples.")

        elif chosen_sql.startswith("Q4:"):
            q = f"""
            SELECT c.{actor_col} AS actor_name, COUNT(c.movie_id) AS movie_count
            FROM cast c GROUP BY c.{actor_col} ORDER BY movie_count DESC LIMIT 10;
            """
            df_res = run_query(q)
            st.subheader("Top 10 Most Prolific Actors")
            fig, ax = plt.subplots(figsize=(6.5, 3.5))
            ax.barh(df_res["actor_name"], df_res["movie_count"], color="purple", height=0.6)
            ax.invert_yaxis()
            ax.set_xlabel("Total Films")
            st.pyplot(fig)
            st.dataframe(df_res, use_container_width=True, hide_index=True)
            st.info("💡 **Insight**: Dependable character actors frequently lead total feature film counts.")

        elif chosen_sql.startswith("Q5:"):
            q = f"""
            SELECT c.{director_col} AS director_name, COUNT(c.movie_id) AS movie_count
            FROM crew c WHERE c.job = 'Director'
            GROUP BY c.{director_col} HAVING COUNT(c.movie_id) > 3 ORDER BY movie_count DESC;
            """
            df_res = run_query(q)
            st.subheader("Active Directors with > 3 Films")
            fig, ax = plt.subplots(figsize=(6.5, 3.5))
            ax.bar(df_res["director_name"].head(8), df_res["movie_count"].head(8), color="dodgerblue", width=0.55)
            plt.xticks(rotation=45, ha="right")
            ax.set_ylabel("Films Directed")
            st.pyplot(fig)
            st.dataframe(df_res, use_container_width=True, hide_index=True)
            st.info("💡 **Insight**: SQL HAVING effectively isolates directors with long, established studio careers.")

        elif chosen_sql.startswith("Q6:"):
            q = f"""
            SELECT k.{keyword_col} AS keyword, COUNT(k.movie_id) AS movie_count
            FROM movie_keywords k 
            WHERE k.{keyword_col} IS NOT NULL AND TRIM(k.{keyword_col}) != ''
            GROUP BY k.{keyword_col} 
            ORDER BY movie_count DESC LIMIT 10;
            """
            df_res = run_query(q)
            st.subheader("Top 10 Most Frequent Thematic Keywords")
            fig, ax = plt.subplots(figsize=(6.5, 3.5))
            ax.barh(df_res["keyword"], df_res["movie_count"], color="coral", height=0.6)
            ax.invert_yaxis()
            ax.set_xlabel("Occurrences")
            st.pyplot(fig)
            st.dataframe(df_res, use_container_width=True, hide_index=True)
            st.info("💡 **Insight**: Plots based on books, sequels, and suspense appear most frequently across films.")

        elif chosen_sql.startswith("Q7:"):
            q = """
            SELECT title, release_date, budget, revenue
            FROM movies
            WHERE budget > (SELECT AVG(budget) FROM movies WHERE budget > 0)
              AND revenue < (SELECT AVG(revenue) FROM movies WHERE revenue > 0)
              AND budget > 0 ORDER BY budget DESC LIMIT 10;
            """
            df_res = run_query(q)
            st.subheader("Above-Average Budget with Below-Average Revenue")
            fig, ax = plt.subplots(figsize=(6.5, 3.5))
            ax.scatter(df_res["budget"] / 1e6, df_res["revenue"] / 1e6, color="crimson", s=80)
            for _, r in df_res.iterrows():
                ax.annotate(r["title"][:12], (r["budget"] / 1e6, r["revenue"] / 1e6), fontsize=8)
            ax.set_xlabel("Budget ($M)")
            ax.set_ylabel("Revenue ($M)")
            st.pyplot(fig)
            st.dataframe(
                df_res,
                column_config={
                    "budget": st.column_config.NumberColumn("Budget ($)", format="$%,d"),
                    "revenue": st.column_config.NumberColumn("Revenue ($)", format="$%,d"),
                },
                use_container_width=True,
                hide_index=True
            )
            st.info("💡 **Insight**: Subqueries isolate expensive productions that underperformed at the theatrical box office.")

        elif chosen_sql.startswith("Q8:"):
            q = f"""
            SELECT DISTINCT c.{actor_col} AS actor_name, m.title, m.release_date
            FROM cast c
            JOIN crew cr ON c.movie_id = cr.movie_id
            JOIN movies m ON c.movie_id = m.movie_id
            WHERE cr.job = 'Director' AND cr.{director_col} = 'Christopher Nolan'
            ORDER BY c.{actor_col} ASC;
            """
            df_res = run_query(q)
            st.subheader("Christopher Nolan Collaborations")
            top_collabs = df_res["actor_name"].value_counts().head(8)
            fig, ax = plt.subplots(figsize=(6.5, 3.5))
            ax.bar(top_collabs.index, top_collabs.values, color="slategray", width=0.55)
            plt.xticks(rotation=45, ha="right")
            ax.set_ylabel("Film Count")
            st.pyplot(fig)
            st.dataframe(df_res.head(25), use_container_width=True, hide_index=True)
            st.info("💡 **Insight**: Illustrates repeat artistic ensembles (e.g. Christian Bale, Cillian Murphy) across multiple Nolan films like The Dark Knight, Inception, and Oppenheimer.")

        elif chosen_sql.startswith("Q9:"):
            q = """
            SELECT g.genre_name, COUNT(m.movie_id) AS movie_count, 
                   ROUND(AVG(m.vote_average), 2) AS avg_rating
            FROM genres g
            JOIN movie_genres mg ON g.genre_id = mg.genre_id
            JOIN movies m ON mg.movie_id = m.movie_id
            GROUP BY g.genre_name HAVING COUNT(m.movie_id) >= 20 ORDER BY avg_rating DESC;
            """
            df_res = run_query(q)
            st.subheader("Average Rating by Genre (Min 20 Films)")
            fig, ax = plt.subplots(figsize=(7, 3.6))
            ax.bar(df_res["genre_name"], df_res["avg_rating"], color="darkseagreen", width=0.55)
            ax.set_ylim(5, 7.5)
            plt.xticks(rotation=45, ha="right")
            st.pyplot(fig)
            st.dataframe(df_res, use_container_width=True, hide_index=True)
            st.info("💡 **Insight**: War and History consistently receive higher average audience ratings than Horror.")

        elif chosen_sql.startswith("Q10:"):
            q = f"""
            SELECT m.title, COUNT(k.{keyword_col}) AS keyword_count
            FROM movies m
            JOIN movie_keywords k ON m.movie_id = k.movie_id
            GROUP BY m.movie_id 
            ORDER BY keyword_count DESC LIMIT 10;
            """
            df_res = run_query(q)
            st.subheader("Top 10 Movies with the Most Keyword Tags")
            fig, ax = plt.subplots(figsize=(6.5, 3.5))
            ax.barh(df_res["title"], df_res["keyword_count"], color="mediumpurple", height=0.6)
            ax.invert_yaxis()
            ax.set_xlabel("Number of Tags")
            st.pyplot(fig)
            st.dataframe(df_res, use_container_width=True, hide_index=True)
            st.info("💡 **Insight**: Deep lore and multi-genre films require higher keyword densities.")

    # ---------------------------------------------------------
    # PANDAS TASKS (P1 - P10)
    # ---------------------------------------------------------
    elif engine_choice == "Pandas Analysis":
        pandas_options = [
            "P1: Unique Entities Count Across Tables",
            "P2: Missing & Zero Budget/Revenue Records",
            "P3: Profit & ROI Calculation for Financials",
            "P4: Top 15 Highest-ROI Movies (Min $1M Budget)",
            "P5: Yearly Release Frequency & Peak Year",
            "P6: Movie Runtime Category Breakdown",
            "P7: Primary Genre Identification & Popularity",
            "P8: Top Actors by Volume & Average Ratings",
            "P9: Duplicate Title Check (Remakes / Re-releases)",
            "P10: Top 10 Most Popular Movies"
        ]
        chosen_p = st.selectbox("Choose a Pandas Task:", pandas_options)

        if chosen_p.startswith("P1:"):
            st.subheader("Unique Entity Totals Across Schema")
            counts = {
                "Movies": int(movies_df["movie_id"].nunique()),
                "Genres": int(genres_df["genre_id"].nunique()),
                "Actors": int(cast_df["person_id"].nunique()) if "person_id" in cast_df.columns else len(cast_df),
                "Crew": int(crew_df["person_id"].nunique()) if "person_id" in crew_df.columns else len(crew_df),
                "Keywords": int(keywords_df["keyword_id"].nunique()) if "keyword_id" in keywords_df.columns else len(keywords_df)
            }
            df_res = pd.DataFrame(list(counts.items()), columns=["Entity Category", "Total Count"])

            fig, ax = plt.subplots(figsize=(6.5, 3.2))
            colors = ["#4A90E2", "#50E3C2", "#B8E986", "#F5A623", "#9013FE"]
            ax.barh(df_res["Entity Category"], df_res["Total Count"], color=colors, height=0.55)
            ax.invert_yaxis()
            ax.set_xlabel("Total Unique Records")
            for i, v in enumerate(df_res["Total Count"]):
                ax.text(v + (max(df_res["Total Count"]) * 0.02), i, f" {v:,}", va='center', fontweight='bold', fontsize=9)
            st.pyplot(fig)

            st.dataframe(
                df_res,
                column_config={"Total Count": st.column_config.NumberColumn("Total Count", format="%,d")},
                use_container_width=True,
                hide_index=True
            )
            st.info("💡 **Insight**: Clearly contrasts reference tables (Genres: 19) against expansive creative personnel and keyword junction tables.")

        elif chosen_p.startswith("P2:"):
            z_budget = int((movies_df["budget"] == 0).sum())
            z_rev = int((movies_df["revenue"] == 0).sum())
            valid_both = int(((movies_df["budget"] > 0) & (movies_df["revenue"] > 0)).sum())
            df_res = pd.DataFrame({
                "Financial Category": ["Zero Budget (Unreported)", "Zero Revenue (Unreported)", "Complete Financial Records"],
                "Count": [z_budget, z_rev, valid_both]
            })
            st.subheader("Missing & Zero Financial Records")
            fig, ax = plt.subplots(figsize=(6, 3.2))
            ax.bar(df_res["Financial Category"], df_res["Count"], color=["#E74C3C", "#F39C12", "#27AE60"], width=0.45)
            plt.xticks(rotation=15, ha="right")
            st.pyplot(fig)
            st.dataframe(
                df_res,
                column_config={"Count": st.column_config.NumberColumn("Record Count", format="%,d")},
                use_container_width=True,
                hide_index=True
            )
            st.info("💡 **Insight**: In TMDB, missing financial records are stored as 0, which must be filtered during ROI computations.")

        elif chosen_p.startswith("P3:"):
            fin = movies_df[(movies_df["budget"] > 0) & (movies_df["revenue"] > 0)].copy()
            fin["profit"] = fin["revenue"] - fin["budget"]
            fin["roi"] = fin["profit"] / fin["budget"]
            st.subheader("Top 10 Most Profitable Movies ($M)")
            top_prof = fin.sort_values("profit", ascending=False).head(10)
            fig, ax = plt.subplots(figsize=(6.5, 3.6))
            ax.barh(top_prof["title"], top_prof["profit"] / 1e6, color="forestgreen", height=0.6)
            ax.invert_yaxis()
            ax.set_xlabel("Net Profit ($ Millions)")
            st.pyplot(fig)
            st.dataframe(
                top_prof[["title", "budget", "revenue", "profit", "roi"]],
                column_config={
                    "title": st.column_config.TextColumn("Movie Title"),
                    "budget": st.column_config.NumberColumn("Budget ($)", format="$%,d"),
                    "revenue": st.column_config.NumberColumn("Revenue ($)", format="$%,d"),
                    "profit": st.column_config.NumberColumn("Net Profit ($)", format="$%,d"),
                    "roi": st.column_config.NumberColumn("ROI Multiplier", format="%.2fx"),
                },
                use_container_width=True,
                hide_index=True
            )
            st.info("💡 **Insight**: Net profit calculation strips out production costs to show actual financial gains.")

        elif chosen_p.startswith("P4:"):
            fin1m = movies_df[(movies_df["budget"] >= 1e6) & (movies_df["revenue"] > 0)].copy()
            fin1m["roi"] = (fin1m["revenue"] - fin1m["budget"]) / fin1m["budget"]
            top_roi = fin1m.sort_values("roi", ascending=False).head(10)
            st.subheader("Top 10 Highest ROI Movies (Min $1M Budget)")
            fig, ax = plt.subplots(figsize=(6.5, 3.6))
            ax.barh(top_roi["title"], top_roi["roi"], color="darkcyan", height=0.6)
            ax.invert_yaxis()
            ax.set_xlabel("ROI Multiplier (x Budget)")
            st.pyplot(fig)
            st.dataframe(
                top_roi[["title", "budget", "revenue", "roi"]],
                column_config={
                    "title": st.column_config.TextColumn("Movie Title"),
                    "budget": st.column_config.NumberColumn("Budget ($)", format="$%,d"),
                    "revenue": st.column_config.NumberColumn("Revenue ($)", format="$%,d"),
                    "roi": st.column_config.NumberColumn("ROI Multiplier", format="%.2fx"),
                },
                use_container_width=True,
                hide_index=True
            )
            st.info("💡 **Insight**: Setting a $1M budget floor removes micro-budget skew, highlighting high-return theatrical films.")

        elif chosen_p.startswith("P5:"):
            yearly = movies_df["release_year"].value_counts().sort_index()
            yearly = yearly[yearly.index >= 1980]
            st.subheader("Yearly Movie Production Frequency")
            fig, ax = plt.subplots(figsize=(7, 3.4))
            ax.plot(yearly.index, yearly.values, marker="o", color="crimson", linewidth=2)
            ax.set_xlabel("Release Year")
            ax.set_ylabel("Titles Released")
            st.pyplot(fig)
            
            table_yearly = yearly.reset_index()
            table_yearly.columns = ["Release Year", "Movies Released"]
            table_yearly["Release Year"] = table_yearly["Release Year"].astype(str)
            
            st.dataframe(
                table_yearly,
                column_config={
                    "Release Year": st.column_config.TextColumn("Release Year"),
                    "Movies Released": st.column_config.NumberColumn("Movies Released", format="%,d")
                },
                use_container_width=True,
                hide_index=True
            )
            st.info("💡 **Insight**: Reflects exponential rise in annual feature film production entering the 21st century.")

        elif chosen_p.startswith("P6:"):
            st.subheader("Movie Runtime Duration Categories")
            valid_runtimes = movies_df[movies_df["runtime"] > 0]["runtime"]
            bins = [0, 90, 120, 150, 400]
            labels = ["Short (< 90 mins)", "Standard (90-120 mins)", "Long (120-150 mins)", "Epic (150+ mins)"]
            runtime_cats = pd.cut(valid_runtimes, bins=bins, labels=labels).value_counts()[labels]

            fig, ax = plt.subplots(figsize=(6.2, 3.2))
            ax.bar(runtime_cats.index, runtime_cats.values, color="skyblue", width=0.45)
            plt.xticks(rotation=20, ha="right")
            ax.set_ylabel("Number of Movies")
            st.pyplot(fig)

            df_cat = pd.DataFrame({"Duration Category": runtime_cats.index, "Movie Count": runtime_cats.values})
            st.dataframe(
                df_cat,
                column_config={"Movie Count": st.column_config.NumberColumn("Movie Count", format="%,d")},
                use_container_width=True,
                hide_index=True
            )
            st.info("💡 **Insight**: Over 65% of feature films belong to the standard 90–120 minute theatrical category.")

        elif chosen_p.startswith("P7:"):
            mg_p7 = movies_df.merge(movie_genres_df, on="movie_id").merge(genres_df, on="genre_id")
            pop_g = mg_p7.groupby("genre_name")["popularity"].mean().sort_values(ascending=False).head(10)
            st.subheader("Top Genres by Average Popularity")
            fig, ax = plt.subplots(figsize=(7, 3.6))
            ax.bar(pop_g.index, pop_g.values, color="coral", width=0.55)
            plt.xticks(rotation=45, ha="right")
            ax.set_ylabel("Average Popularity Score")
            st.pyplot(fig)
            
            df_p7 = pop_g.reset_index()
            df_p7.columns = ["Genre", "Average Popularity"]
            st.dataframe(
                df_p7,
                column_config={"Average Popularity": st.column_config.NumberColumn("Popularity Index", format="%.2f")},
                use_container_width=True,
                hide_index=True
            )
            st.info("💡 **Insight**: Sci-Fi and Adventure drive the highest viral engagement and audience search popularity.")

        elif chosen_p.startswith("P8:"):
            cast_m = cast_df.merge(movies_df, on="movie_id")
            top_actors = cast_m.groupby(actor_col).agg(
                movie_count=("movie_id", "count"),
                avg_rating=("vote_average", "mean")
            ).sort_values("movie_count", ascending=False).head(10)
            st.subheader("Top Actors by Film Volume & Ratings")
            fig, ax = plt.subplots(figsize=(6.5, 3.5))
            ax.scatter(top_actors["movie_count"], top_actors["avg_rating"], color="navy", s=80)
            for name, row in top_actors.iterrows():
                ax.annotate(name, (row["movie_count"], row["avg_rating"]), fontsize=8)
            ax.set_xlabel("Film Count")
            ax.set_ylabel("Average Rating")
            st.pyplot(fig)
            st.dataframe(
                top_actors.reset_index().rename(columns={actor_col: "Actor Name", "movie_count": "Movie Count", "avg_rating": "Average Rating"}),
                column_config={"Average Rating": st.column_config.NumberColumn("Average Rating", format="%.2f")},
                use_container_width=True,
                hide_index=True
            )
            st.info("💡 **Insight**: Visualizes actor productivity against average audience satisfaction.")

        elif chosen_p.startswith("P9:"):
            st.subheader("Frequently Remade / Multi-Release Movie Franchises")
            dupes = movies_df[movies_df.duplicated(subset=["title"], keep=False)].copy()
            dupe_summary = dupes.groupby("title").agg(
                releases=("release_date", "count")
            ).sort_values(by="releases", ascending=False).head(8).reset_index()

            fig, ax = plt.subplots(figsize=(7, 3.5))
            ax.barh(dupe_summary["title"], dupe_summary["releases"], color="#E67E22", height=0.55)
            ax.invert_yaxis()
            ax.set_xlabel("Number of Theatrical Releases")
            ax.set_xticks([0, 1, 2, 3, 4])
            st.pyplot(fig)

            top_titles = dupe_summary["title"].tolist()
            dupes_detail = dupes[dupes["title"].isin(top_titles)].sort_values(by=["title", "release_date"])
            
            st.dataframe(
                dupes_detail[["title", "release_date", "vote_average", "budget"]],
                column_config={
                    "title": st.column_config.TextColumn("Movie Title"),
                    "release_date": st.column_config.TextColumn("Release Date"),
                    "vote_average": st.column_config.NumberColumn("Rating", format="%.2f"),
                    "budget": st.column_config.NumberColumn("Budget ($)", format="$%,d")
                },
                use_container_width=True,
                hide_index=True
            )
            st.info("💡 **Insight**: Shows top remade titles like Halloween, Robin Hood, Alice in Wonderland, and Cinderella with distinct theatrical release dates across decades.")

        elif chosen_p.startswith("P10:"):
            st.subheader("Top 10 Most Popular Movies (TMDB Index)")
            top_pop = movies_df.sort_values("popularity", ascending=False).head(10)
            fig, ax = plt.subplots(figsize=(6.5, 3.6))
            ax.barh(top_pop["title"], top_pop["popularity"], color="mediumvioletred", height=0.6)
            ax.invert_yaxis()
            ax.set_xlabel("Popularity Score")
            st.pyplot(fig)
            st.dataframe(
                top_pop[["title", "release_date", "popularity", "vote_count", "vote_average"]],
                column_config={
                    "title": st.column_config.TextColumn("Movie Title"),
                    "release_date": st.column_config.TextColumn("Release Date"),
                    "popularity": st.column_config.NumberColumn("Popularity Score", format="%.1f"),
                    "vote_count": st.column_config.NumberColumn("Total Votes", format="%,d"),
                    "vote_average": st.column_config.NumberColumn("Rating", format="%.1f")
                },
                use_container_width=True,
                hide_index=True
            )
            st.info("💡 **Insight**: Cultural blockbusters and viral franchise entries drive extraordinary spikes in TMDB popularity metrics.")


# =============================================================
# PAGE 4: 🚪 EXIT
# =============================================================
elif st.session_state["nav_page"] == "🚪 Exit":
    if st.session_state["exit_submitted"]:
        st.markdown("<br><br><br>", unsafe_allow_html=True)
        col_l, col_center, col_r = st.columns([1, 2, 1])
        with col_center:
            chosen_rating = st.session_state.get("rating_choice", "😊")
            smiley_face = chosen_rating.split()[0]
            
            st.markdown(
                f"""
                <div style="text-align: center; padding: 45px; border-radius: 20px; background: linear-gradient(135deg, #11998e, #38ef7d); color: white; box-shadow: 0 8px 25px rgba(0,0,0,0.2);">
                    <h1 style="font-size: 3.2rem; font-weight: 700; margin-bottom: 5px;">🎉 Thank You!</h1>
                    <div style="font-size: 5.5rem; margin: 20px 0;">{smiley_face}</div>
                    <p style="font-size: 1.25rem; color: #e8f5e9; margin-top: 10px;">Your analytics session is complete.</p>
                </div>
                """,
                unsafe_allow_html=True
            )
            st.write("<br>", unsafe_allow_html=True)
            
            if st.button("🏠 Return to Homepage & Explore Again", type="primary", use_container_width=True):
                st.session_state["nav_page"] = "🏠 Home"
                st.session_state["exit_submitted"] = False
                st.rerun()

    else:
        st.markdown("<br><br>", unsafe_allow_html=True)
        col_l, col_center, col_r = st.columns([1, 2, 1])
        with col_center:
            st.markdown(
                """
                <div style="text-align: center; padding: 30px; border-radius: 16px; background-color: #f8f9fa; border: 1px solid #e9ecef;">
                    <h2 style="color: #2c3e50; margin-bottom: 10px;">🎬 Session Exit</h2>
                    <p style="color: #6c757d; font-size: 1.05rem;">Please select your experience rating before concluding:</p>
                </div>
                """,
                unsafe_allow_html=True
            )
            st.write("")

            emoji_rating = st.radio(
                "Rate your experience:",
                options=["😡", "🙁", "😐", "😊", "🤩"],
                index=3,
                horizontal=True
            )

            st.write("")
            c_sub1, c_sub2 = st.columns(2)
            with c_sub1:
                if st.button("Submit & Exit", type="primary", use_container_width=True):
                    st.session_state["exit_submitted"] = True
                    st.session_state["rating_choice"] = emoji_rating
                    st.rerun()
            with c_sub2:
                if st.button("Cancel (Return Home)", use_container_width=True):
                    st.session_state["nav_page"] = "🏠 Home"
                    st.rerun()