# 📺 YouTube Trending Data Analysis — SQL Project

> **End-to-end SQL analysis** of YouTube trending videos using data from  
> [Kaggle: raminrahimzada/youtube](https://www.kaggle.com/datasets/raminrahimzada/youtube)

---

## 🗂️ Project Structure

```
youtube-sql-analysis/
│
├── data/
│   ├── youtube_trending.csv   ← dataset (generated or from Kaggle)
│   └── youtube.db             ← SQLite database (auto-created)
│
├── queries/
│   ├── analysis.sql           ← all 15 SQL queries (documented)
│   └── results/               ← CSV output from each query
│       ├── Q01_top_10_...csv
│       ├── Q02_channel_...csv
│       └── ...
│
├── insights/
│   └── INSIGHTS.md            ← 7 data-backed findings with tables
│
└── scripts/
    ├── fetch_kaggle.py        ← downloads real dataset from Kaggle
    ├── generate_data.py       ← synthetic data generator (dev/demo)
    ├── setup_db.py            ← loads CSV → SQLite + creates views
    └── run_analysis.py        ← runs all 15 queries → saves results
```

---

## ⚡ Quick Start

### Option A — Use Real Kaggle Data (Recommended)

```bash
# 1. Install dependencies
pip install kagglehub

# 2. Set up Kaggle credentials
#    → kaggle.com → Account → API → Create New Token
#    → saves ~/.kaggle/kaggle.json automatically

# 3. Fetch dataset
python scripts/fetch_kaggle.py

# 4. Load into SQLite
python scripts/setup_db.py

# 5. Run all 15 queries
python scripts/run_analysis.py
```

### Option B — Use Synthetic Demo Data

```bash
# 1. Generate 5,000 realistic rows
python scripts/generate_data.py

# 2. Load into SQLite
python scripts/setup_db.py

# 3. Run all 15 queries
python scripts/run_analysis.py
```

---

## 🗃️ Database Schema

```sql
CREATE TABLE youtube_trending (
    id                INTEGER  PRIMARY KEY AUTOINCREMENT,
    video_id          TEXT     NOT NULL,
    trending_date     DATE     NOT NULL,
    title             TEXT     NOT NULL,
    channel_title     TEXT     NOT NULL,
    category_id       INTEGER  NOT NULL,
    category_name     TEXT     NOT NULL,
    publish_time      DATETIME,
    tags              TEXT,
    views             INTEGER  DEFAULT 0,
    likes             INTEGER  DEFAULT 0,
    dislikes          INTEGER  DEFAULT 0,
    comment_count     INTEGER  DEFAULT 0,
    comments_disabled TEXT     DEFAULT 'False',
    ratings_disabled  TEXT     DEFAULT 'False',
    description       TEXT,
    country           TEXT
);

-- Pre-built view with derived engagement metrics
CREATE VIEW vw_video_metrics AS
SELECT
    ...,
    ROUND(likes * 100.0 / NULLIF(views, 0), 4)               AS like_rate,
    ROUND(likes * 1.0 / NULLIF(likes + dislikes, 0) * 100, 2) AS approval_pct,
    JULIANDAY(trending_date) - JULIANDAY(publish_time)         AS days_to_trend
FROM youtube_trending;
```

---

## 🔍 The 15 SQL Queries

| # | Query | Technique Used |
|---|-------|---------------|
| Q1  | Top 10 Most-Viewed Videos | `ROW_NUMBER() OVER`, ORDER BY |
| Q2  | Channel Performance (Views + Engagement) | `GROUP BY`, `HAVING`, aggregates |
| Q3  | Category-Level Engagement Benchmarks | Multi-metric `AVG` grouping |
| Q4  | Trending by Country (Volume & Avg Views) | `GROUP BY country`, `SUM` |
| Q5  | Monthly Trending Volume 2022–2024 | `STRFTIME`, time-series grouping |
| Q6  | Days-to-Trend Distribution | `CASE WHEN` bucketing, `VIEW` join |
| Q7  | Approval Rate by Category | Ratio calc, `NULLIF` safe division |
| Q8  | Top-10 Channels by Trending Appearances | `COUNT`, `ORDER BY` |
| Q9  | Best Hour to Publish (UTC) | `STRFTIME('%H')`, time aggregation |
| Q10 | Channels Disabling Comments | Filter on boolean flag |
| Q11 | Year-over-Year View Growth | `STRFTIME('%Y')`, time comparison |
| Q12 | Viral Outliers (3× Category Avg) | `WITH` CTE, self-join, ratio filter |
| Q13 | Rolling 30-Day Avg Views per Country | `WINDOW` function, `ROWS BETWEEN` |
| Q14 | Most Common Tags in Trending Videos | Recursive CTE string split |
| Q15 | Channel Consistency Score (CV%) | Correlated subquery, variance calc |

---

## 💡 Key Insights (Summary)

> Full tables and explanations → [`insights/INSIGHTS.md`](insights/INSIGHTS.md)

1. **Music dominates reach** (13.6M avg views) but **Education leads engagement** (7.33% like rate)
2. **Same-day trending videos** average 7.9M views — 34% more than videos trending after 2+ days
3. **Pets & Animals** tops audience approval at 85.36% likes-to-votes ratio
4. **Sony Music** leads all channels: most trending appearances (143) + highest avg views (12.2M)
5. **2024 shows a 3.9% view dip** vs 2023's 11% growth — potential short-form content impact
6. **<8% of videos** in any category account for the majority of total views (viral concentration)
7. **Comment-disabled kids' content** matches or beats comment-enabled peers in views — comments are optional, not mandatory for algorithmic reach

---

## 🛠️ Tech Stack

| Tool | Purpose |
|------|---------|
| Python 3 | Data generation, ETL, query execution |
| SQLite 3 | Analytical database (zero setup) |
| SQL | All analysis — CTEs, window functions, recursive queries |
| kagglehub | Kaggle API wrapper for dataset download |
| CSV | Intermediate data format |

> Compatible with **PostgreSQL** and **MySQL** with minor dialect adjustments  
> (replace `STRFTIME` with `DATE_FORMAT`/`TO_CHAR`, `JULIANDAY` with `DATEDIFF`).

---

## 📁 Results Preview

After running `run_analysis.py`, each query's output lands in `queries/results/`:

```
Q01_top_10_mostviewed_videos_all_time.csv
Q02_channel_performance_total_views__avg_engagement.csv
Q03_categorylevel_engagement_benchmarks.csv
...
Q15_channel_consistency_score_low_variance__stable.csv
_summary.csv   ← run status for all 15 queries
```

---

## 📄 License

MIT — use freely for learning, portfolios, and data projects.

---

*Built with Python + SQL · Data from Kaggle (raminrahimzada/youtube)*
