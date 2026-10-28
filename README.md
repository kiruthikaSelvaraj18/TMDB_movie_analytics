# 🎬 TMDB Movie Analytics Dashboard

An end-to-end exploratory data analysis and business intelligence platform evaluating the global movie industry using TMDB data. The application connects an interactive multi-page Streamlit web app directly to a normalized relational SQLite database.

---

## 🛠️ Tech Stack & Architecture

- **Language:** Python
- **Database:** SQLite3 (Normalized 6-table schema)
- **Data Analysis & Processing:** Pandas, NumPy
- **Visualizations:** Matplotlib, Seaborn
- **Web Application:** Streamlit

---

## 🌟 Key Features

- **Normalized Relational Architecture:** A 6-table relational SQLite database (`movies`, `genres`, `movie_genres`, `cast`, `crew`, `movie_keywords`) with maintained referential integrity.
- **SQL Analytical Queries:** 10 business queries implementing multi-table joins, string aggregations (`GROUP_CONCAT`), dynamic subqueries, and `HAVING` filters.
- **Pandas Advanced Data Tasks:** 10 analytical operations covering ROI/profit feature engineering, IQR runtime outlier detection, entity tracking, and anomaly detection.
- **Interactive Multi-Page Streamlit App:**
  - **🏠 Home Page:** Executive overview, project scope, and fast-track navigation.
  - **📊 Dashboard Overview:** Dynamic sidebar filters (genre multiselect, year slider, minimum rating slider, language selection), live matching movie counter, 4 core KPIs, Top 10 Revenue bar chart, Genre Distribution, and Budget vs. Revenue scatter plot.
  - **🔍 Query Explorer:** Dual-engine interface toggling between SQL and Pandas analytical tasks with dedicated charts, data tables, and structured business takeaways.
  - **🚪 Exit Page:** Clean feedback rating interface and session reset capability.

---

## 💡 Top 5 Overall Insights & Strategic Recommendations

1. **Budget vs. Box Office Revenue Elasticity**
   A strong positive correlation (> 0.70) exists between production budgets and global box office gross. However, tentpole budgets above $150M carry severe downside financial risk if not backed by established, pre-sold franchise intellectual property.

2. **Genre ROI Disparity**
   While Action and Adventure generate the highest raw gross box-office revenues, **Horror and Animation deliver the highest return-on-investment (ROI) multipliers** relative to their initial production budgets, offering studios the lowest risk profile.

3. **Runtime Distribution Sweet Spot**
   Over 65% of commercially viable feature films cluster tightly between **90 and 120 minutes**. Runtimes beyond 150 minutes represent statistical outliers and generally sustain theatrical viability only when tied to major cinematic event releases.

4. **Franchise IP & Thematic Keyword Density**
   The most frequent thematic keywords across commercial hits are `"based on novel or book"` and `"sequel"`. Established lore significantly lowers customer acquisition costs and strengthens foreign distribution compared to original standalone screenplays.

5. **Talent Collaborations & Ensemble Consistency**
   Directorial analysis shows strong recurring actor-director pairings (such as Christopher Nolan working across projects with core ensembles like Christian Bale and Cillian Murphy), stabilizing both box-office predictability and critical reception.

---

## 📁 Repository Structure

```text
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
├── sql_analysis.py            # 10 core SQL queries
├── pandas_analysis.py         # 10 Pandas analytical tasks
├── app.py                     # Multi-page Streamlit application
├── requirements.txt           # Project dependencies
└── README.md                  # Project documentation & insights
