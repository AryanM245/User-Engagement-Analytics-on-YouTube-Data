"""
setup_db.py
Creates the SQLite database and loads CSV data.
To use with real Kaggle data:
    1. pip install kagglehub
    2. Run: python scripts/fetch_kaggle.py   (downloads dataset)
    3. Run: python scripts/setup_db.py       (loads into SQLite)
"""

import sqlite3
import csv
import os

DB_PATH   = "data/youtube.db"
CSV_PATH  = "data/youtube_trending.csv"

CREATE_SCHEMA = """
CREATE TABLE IF NOT EXISTS youtube_trending (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    video_id         TEXT    NOT NULL,
    trending_date    DATE    NOT NULL,
    title            TEXT    NOT NULL,
    channel_title    TEXT    NOT NULL,
    category_id      INTEGER NOT NULL,
    category_name    TEXT    NOT NULL,
    publish_time     DATETIME,
    tags             TEXT,
    views            INTEGER DEFAULT 0,
    likes            INTEGER DEFAULT 0,
    dislikes         INTEGER DEFAULT 0,
    comment_count    INTEGER DEFAULT 0,
    comments_disabled TEXT   DEFAULT 'False',
    ratings_disabled  TEXT   DEFAULT 'False',
    description      TEXT,
    country          TEXT
);

-- Helper view: enriched metrics
CREATE VIEW IF NOT EXISTS vw_video_metrics AS
SELECT
    video_id,
    title,
    channel_title,
    category_name,
    country,
    trending_date,
    publish_time,
    views,
    likes,
    dislikes,
    comment_count,
    ROUND(likes  * 100.0 / NULLIF(views, 0), 4)              AS like_rate,
    ROUND(dislikes * 100.0 / NULLIF(views, 0), 4)            AS dislike_rate,
    ROUND(comment_count * 100.0 / NULLIF(views, 0), 4)       AS comment_rate,
    ROUND(likes * 1.0 / NULLIF(likes + dislikes, 0) * 100, 2) AS approval_pct,
    JULIANDAY(trending_date) - JULIANDAY(publish_time)         AS days_to_trend
FROM youtube_trending;
"""

def load_data(conn, csv_path):
    cur = conn.cursor()
    cur.execute("DELETE FROM youtube_trending")
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = []
        for row in reader:
            rows.append((
                row["video_id"],
                row["trending_date"],
                row["title"],
                row["channel_title"],
                int(row["category_id"]),
                row["category_name"],
                row["publish_time"],
                row["tags"],
                int(row["views"]),
                int(row["likes"]),
                int(row["dislikes"]),
                int(row["comment_count"]),
                row["comments_disabled"],
                row["ratings_disabled"],
                row["description"],
                row["country"],
            ))
    cur.executemany("""
        INSERT INTO youtube_trending
            (video_id, trending_date, title, channel_title, category_id,
             category_name, publish_time, tags, views, likes, dislikes,
             comment_count, comments_disabled, ratings_disabled, description, country)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
    """, rows)
    conn.commit()
    print(f"✅ Loaded {len(rows)} rows into {DB_PATH}")


if __name__ == "__main__":
    os.makedirs("data", exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.executescript(CREATE_SCHEMA)
    load_data(conn, CSV_PATH)
    conn.close()
    print("Database ready at:", DB_PATH)
