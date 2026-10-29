# TMDB Movie Analytics Dashboard

This project is an end-to-end data analysis of the TMDB movies dataset. I cleaned and structured the data into a relational SQLite database, answered 20 business questions using SQL and Pandas, and built an interactive dashboard using Streamlit to explore the results visually.


## What I Used
* **Python** (Pandas, Matplotlib, Seaborn)
* **SQLite** (Relational database management)
* **Streamlit** (Interactive web application)


## Project Workflow & Structure

1. **Data Cleaning & Database Setup:**
   * Cleaned raw CSV files by handling missing values, standardizing dates, fixing data types, and removing duplicate rows.
   * Preserved `0` values in budget and revenue during cleaning (since TMDB uses 0 for unrecorded financials) and filtered them conditionally during calculations.
   * Verified referential integrity to remove orphan records across child tables.
   * Loaded the cleaned data into an SQLite database (`tmdb_movies.db`) with 6 related tables: `movies`, `genres`, `movie_genres`, `cast`, `crew`, and `movie_keywords`.

2. **SQL Analysis (10 Queries):**
   * Wrote SQL queries covering multi-table joins, aggregations, `GROUP_CONCAT` for genres, subqueries for underperforming films, and `HAVING` clauses for active directors.

3. **Pandas EDA (10 Tasks):**
   * Calculated financial metrics like Profit (`revenue - budget`) and ROI (`profit / budget`).
   * Checked runtime distributions and outliers, identified peak movie release years, tracked duplicate titles/remakes, and counted entities across tables.

4. **Streamlit Multi-Page App (`app.py`):**
   * **Home:** Project introduction and direct launch buttons.
   * **Dashboard Overview:** Shared filters (genres, release years, minimum rating, language) with a live matching movie count, 4 KPI cards (Total Movies, Genres, Actors, Average Rating), revenue bar charts, genre breakdown, and a budget vs. revenue scatter plot.
   * **Query Explorer:** Toggle between SQL and Pandas questions to see output tables, charts, and explanations.
   * **Exit:** Clean thank-you screen with a reset button.


## Top 5 Key Findings & Takeaways

1. **Big Budgets Usually Make More Money, But Risk Is High:**  
   There is a strong positive correlation between how much a movie costs to make and its box office earnings. However, spending over $150M does not guarantee success—big-budget movies that flop (like *John Carter* or *The Lone Ranger*) create massive losses unless they belong to an established franchise.

2. **Horror and Animation Give the Best ROI:**  
   Action and Adventure movies bring in the largest total box office numbers, but genres like Horror and Animation produce much higher returns relative to their budgets. Lower production costs give them a safer profit margin.

3. **Most Successful Movies Stick to 90–120 Minutes:**  
   Around two-thirds of the movies in the dataset have runtimes between an hour and a half and two hours. Films running past 140 minutes only tend to do well if they are major cinematic event movies.

4. **Sequels and Book Adaptations Dominate:**  
   The most repeated keyword tags across top-earning movies are `"based on novel or book"` and `"sequel"`. Movies with an existing fanbase have lower marketing hurdles than completely original scripts.

5. **Directors Rely on Core Groups of Actors:**  
   Looking at director filmographies (such as Christopher Nolan), successful filmmakers consistently cast the same ensemble of actors across multiple projects. This creative consistency often helps stabilize both box office draw and review scores.


## Project Files

TMDB_movie_analytics/
│
├── data/
│   ├── movies.csv
│   ├── genres.csv
│   ├── movie_genres.csv
│   ├── cast.csv
│   ├── crew.csv
│   ├── movie_keywords.csv
│   └── tmdb_movies.db
│
├── sql_analysis.py            # 10 SQL query scripts
├── pandas_analysis.py         # 10 Pandas analysis tasks
├── visualizations.py          # Standalone visualization charts
├── app.py                     # Streamlit application
├── requirements.txt           # Required libraries
└── README.md                  # Project overview and insights
