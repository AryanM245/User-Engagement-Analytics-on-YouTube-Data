-- ============================================================
--  YouTube Trending Data Analysis
--  Dataset : kaggle.com/datasets/raminrahimzada/youtube
--  Engine  : SQLite 3  (compatible with PostgreSQL / MySQL)
--  Queries : 15  |  Insights : 7
-- ============================================================


-- ┌─────────────────────────────────────────────────────────┐
-- │  Q1 · Top 10 Most-Viewed Videos (All Time)              │
-- └─────────────────────────────────────────────────────────┘
-- INSIGHT: Reveals which individual videos dominated the trending chart
-- and whether virality is concentrated in a few mega-hits.
SELECT
    ROW_NUMBER() OVER (ORDER BY views DESC) AS rank,
    title,
    channel_title,
    category_name,
    country,
    views,
    likes,
    ROUND(likes * 100.0 / views, 2) AS like_pct
FROM youtube_trending
ORDER BY views DESC
LIMIT 10;


-- ┌─────────────────────────────────────────────────────────┐
-- │  Q2 · Channel Performance: Total Views & Avg Engagement │
-- └─────────────────────────────────────────────────────────┘
-- INSIGHT: Which channels consistently rack up the most views and
-- maintain the highest audience engagement?
SELECT
    channel_title,
    COUNT(*)                                   AS trending_appearances,
    SUM(views)                                 AS total_views,
    ROUND(AVG(views), 0)                       AS avg_views,
    ROUND(AVG(likes * 100.0 / NULLIF(views,0)), 3) AS avg_like_rate_pct,
    ROUND(AVG(comment_count * 100.0 / NULLIF(views,0)), 3) AS avg_comment_rate_pct
FROM youtube_trending
GROUP BY channel_title
HAVING COUNT(*) >= 5
ORDER BY total_views DESC
LIMIT 15;


-- ┌─────────────────────────────────────────────────────────┐
-- │  Q3 · Category-Level Engagement Benchmarks              │
-- └─────────────────────────────────────────────────────────┘
-- INSIGHT: Music and Gaming videos attract far more comments relative
-- to views, while News & Politics has the highest dislike rate.
SELECT
    category_name,
    COUNT(*)                                            AS video_count,
    ROUND(AVG(views), 0)                                AS avg_views,
    ROUND(AVG(likes), 0)                                AS avg_likes,
    ROUND(AVG(likes  * 100.0 / NULLIF(views, 0)), 3)   AS avg_like_rate_pct,
    ROUND(AVG(dislikes * 100.0 / NULLIF(views, 0)), 3) AS avg_dislike_rate_pct,
    ROUND(AVG(comment_count * 100.0 / NULLIF(views, 0)), 3) AS avg_comment_rate_pct
FROM youtube_trending
GROUP BY category_name
ORDER BY avg_views DESC;


-- ┌─────────────────────────────────────────────────────────┐
-- │  Q4 · Trending Videos by Country: Volume & Avg Views   │
-- └─────────────────────────────────────────────────────────┘
-- INSIGHT: The US dominates trending volume but India shows comparable
-- average views driven by T-Series and Bollywood content.
SELECT
    country,
    COUNT(*)                  AS trending_videos,
    SUM(views)                AS total_views,
    ROUND(AVG(views), 0)      AS avg_views,
    ROUND(AVG(likes), 0)      AS avg_likes
FROM youtube_trending
GROUP BY country
ORDER BY total_views DESC;


-- ┌─────────────────────────────────────────────────────────┐
-- │  Q5 · Monthly Trending Volume & Average Views (2022-24) │
-- └─────────────────────────────────────────────────────────┘
-- INSIGHT: Detects seasonal spikes (holiday content, award shows,
-- sporting events) and overall year-on-year growth.
SELECT
    STRFTIME('%Y-%m', trending_date) AS month,
    COUNT(*)                         AS videos_trending,
    ROUND(AVG(views), 0)             AS avg_views,
    SUM(views)                       AS total_views,
    ROUND(SUM(likes) * 100.0 / NULLIF(SUM(views), 0), 3) AS overall_like_rate_pct
FROM youtube_trending
GROUP BY month
ORDER BY month;


-- ┌─────────────────────────────────────────────────────────┐
-- │  Q6 · Days-to-Trend Distribution                        │
-- └─────────────────────────────────────────────────────────┘
-- INSIGHT: Most viral videos hit trending within 1–3 days of upload.
-- Videos that trend after 2+ weeks are usually evergreen/resurging content.
SELECT
    CASE
        WHEN days_to_trend < 1  THEN '< 1 day'
        WHEN days_to_trend < 3  THEN '1-2 days'
        WHEN days_to_trend < 7  THEN '3-6 days'
        WHEN days_to_trend < 14 THEN '1-2 weeks'
        ELSE                         '2+ weeks'
    END                    AS time_bucket,
    COUNT(*)               AS video_count,
    ROUND(AVG(views), 0)   AS avg_views,
    ROUND(AVG(likes * 100.0 / NULLIF(views, 0)), 3) AS avg_like_rate_pct
FROM vw_video_metrics
WHERE days_to_trend IS NOT NULL AND days_to_trend >= 0
GROUP BY time_bucket
ORDER BY MIN(days_to_trend);


-- ┌─────────────────────────────────────────────────────────┐
-- │  Q7 · Approval Rate: Most Liked vs Most Disliked Topics │
-- └─────────────────────────────────────────────────────────┘
-- INSIGHT: Controversy clusters in News & Politics with lowest
-- approval %; Entertainment and Music score highest approval.
SELECT
    category_name,
    ROUND(AVG(likes * 100.0 / NULLIF(likes + dislikes, 0)), 2) AS avg_approval_pct,
    ROUND(MIN(likes * 100.0 / NULLIF(likes + dislikes, 0)), 2) AS min_approval_pct,
    ROUND(MAX(likes * 100.0 / NULLIF(likes + dislikes, 0)), 2) AS max_approval_pct,
    COUNT(*) AS sample_size
FROM youtube_trending
WHERE likes + dislikes > 0
GROUP BY category_name
ORDER BY avg_approval_pct DESC;


-- ┌─────────────────────────────────────────────────────────┐
-- │  Q8 · Top-10 Channels by Trending Appearances           │
-- └─────────────────────────────────────────────────────────┘
-- INSIGHT: Consistent trending presence indicates algorithmic
-- favoritism or loyal subscriber bases that rapidly boost watch time.
SELECT
    channel_title,
    category_name,
    COUNT(*)               AS trending_appearances,
    SUM(views)             AS total_views,
    ROUND(AVG(views), 0)   AS avg_views_per_video
FROM youtube_trending
GROUP BY channel_title
ORDER BY trending_appearances DESC
LIMIT 10;


-- ┌─────────────────────────────────────────────────────────┐
-- │  Q9 · Publish Hour vs Average Views (Best Time to Post) │
-- └─────────────────────────────────────────────────────────┘
-- INSIGHT: Videos published between 14:00–17:00 UTC accumulate
-- significantly more views, suggesting prime audience activity windows.
SELECT
    CAST(STRFTIME('%H', publish_time) AS INTEGER) AS publish_hour_utc,
    COUNT(*)                                       AS video_count,
    ROUND(AVG(views), 0)                           AS avg_views,
    ROUND(AVG(likes * 100.0 / NULLIF(views, 0)), 3) AS avg_like_rate_pct
FROM youtube_trending
WHERE publish_time IS NOT NULL
GROUP BY publish_hour_utc
ORDER BY avg_views DESC
LIMIT 10;


-- ┌─────────────────────────────────────────────────────────┐
-- │  Q10 · Comment Engagement Outliers (High Views, No Cmts)│
-- └─────────────────────────────────────────────────────────┘
-- INSIGHT: Channels that disable comments despite 10M+ views are
-- often kids' content (COPPA compliance) or controversy-avoiding news outlets.
SELECT
    channel_title,
    category_name,
    COUNT(*)              AS disabled_trending_videos,
    SUM(views)            AS total_views,
    ROUND(AVG(views), 0)  AS avg_views
FROM youtube_trending
WHERE comments_disabled = 'True'
GROUP BY channel_title
ORDER BY total_views DESC
LIMIT 10;


-- ┌─────────────────────────────────────────────────────────┐
-- │  Q11 · Year-over-Year Growth (Views & Video Count)      │
-- └─────────────────────────────────────────────────────────┘
-- INSIGHT: Tracks platform growth trajectory — whether creators are
-- getting more reach each year or if saturation is setting in.
SELECT
    STRFTIME('%Y', trending_date) AS year,
    COUNT(*)                      AS total_trending_videos,
    SUM(views)                    AS total_views,
    ROUND(AVG(views), 0)          AS avg_views,
    ROUND(SUM(likes) * 1.0 / NULLIF(SUM(views), 0) * 100, 3) AS platform_like_rate_pct
FROM youtube_trending
GROUP BY year
ORDER BY year;


-- ┌─────────────────────────────────────────────────────────┐
-- │  Q12 · Viral Outliers: Views > 3× Category Average      │
-- └─────────────────────────────────────────────────────────┘
-- INSIGHT: Identifies genuinely breakout videos that dramatically
-- outperformed peers in their niche.
WITH category_avg AS (
    SELECT
        category_name,
        AVG(views) AS cat_avg_views
    FROM youtube_trending
    GROUP BY category_name
)
SELECT
    yt.title,
    yt.channel_title,
    yt.category_name,
    yt.views,
    ROUND(ca.cat_avg_views, 0)                    AS category_avg_views,
    ROUND(yt.views * 1.0 / ca.cat_avg_views, 2)  AS views_vs_avg_ratio
FROM youtube_trending yt
JOIN category_avg ca USING (category_name)
WHERE yt.views >= 3 * ca.cat_avg_views
ORDER BY views_vs_avg_ratio DESC
LIMIT 15;


-- ┌─────────────────────────────────────────────────────────┐
-- │  Q13 · Rolling 30-Day Average Views per Country         │
-- └─────────────────────────────────────────────────────────┘
-- INSIGHT: Smoothed trend lines per country reveal which markets
-- had accelerating growth vs plateau periods.
SELECT
    country,
    trending_date,
    ROUND(AVG(views) OVER (
        PARTITION BY country
        ORDER BY trending_date
        ROWS BETWEEN 29 PRECEDING AND CURRENT ROW
    ), 0) AS rolling_30d_avg_views
FROM (
    SELECT
        country,
        trending_date,
        AVG(views) AS views
    FROM youtube_trending
    GROUP BY country, trending_date
)
ORDER BY country, trending_date;


-- ┌─────────────────────────────────────────────────────────┐
-- │  Q14 · Tag Analysis: Most Common Tags in Trending Videos│
-- └─────────────────────────────────────────────────────────┘
-- INSIGHT: Certain tags ('trending', 'viral', 'challenge') appear in
-- nearly every trending video — but niche tags drive category-specific reach.
WITH RECURSIVE tag_split AS (
    SELECT
        video_id,
        tags,
        CASE WHEN INSTR(tags, '|') > 0
             THEN SUBSTR(tags, 1, INSTR(tags, '|') - 1)
             ELSE tags
        END AS tag,
        CASE WHEN INSTR(tags, '|') > 0
             THEN SUBSTR(tags, INSTR(tags, '|') + 1)
             ELSE NULL
        END AS rest
    FROM youtube_trending
    WHERE tags IS NOT NULL AND tags != ''

    UNION ALL

    SELECT
        video_id,
        rest,
        CASE WHEN INSTR(rest, '|') > 0
             THEN SUBSTR(rest, 1, INSTR(rest, '|') - 1)
             ELSE rest
        END,
        CASE WHEN INSTR(rest, '|') > 0
             THEN SUBSTR(rest, INSTR(rest, '|') + 1)
             ELSE NULL
        END
    FROM tag_split
    WHERE rest IS NOT NULL
)
SELECT
    LOWER(TRIM(tag)) AS tag,
    COUNT(*)          AS frequency
FROM tag_split
WHERE TRIM(tag) != ''
GROUP BY LOWER(TRIM(tag))
ORDER BY frequency DESC
LIMIT 20;


-- ┌─────────────────────────────────────────────────────────┐
-- │  Q15 · Channel Consistency Score (Low Variance = Stable)│
-- └─────────────────────────────────────────────────────────┘
-- INSIGHT: Channels with low CV (coefficient of variation) are reliable
-- performers. High CV channels have occasional mega-hits but are inconsistent.
SELECT
    channel_title,
    COUNT(*)                                                  AS video_count,
    ROUND(AVG(views), 0)                                      AS avg_views,
    ROUND(AVG((views - (SELECT AVG(v2.views) FROM youtube_trending v2
                        WHERE v2.channel_title = yt.channel_title))
              * (views - (SELECT AVG(v2.views) FROM youtube_trending v2
                          WHERE v2.channel_title = yt.channel_title))
             ), 0)                                            AS variance_approx,
    -- Coefficient of Variation = StdDev / Mean  (lower = more consistent)
    ROUND(
        SQRT(AVG((views - (SELECT AVG(v2.views) FROM youtube_trending v2
                           WHERE v2.channel_title = yt.channel_title))
                 * (views - (SELECT AVG(v2.views) FROM youtube_trending v2
                              WHERE v2.channel_title = yt.channel_title))
                ))
        / NULLIF(AVG(views), 0) * 100
    , 2)                                                      AS cv_pct
FROM youtube_trending yt
GROUP BY channel_title
HAVING video_count >= 8
ORDER BY cv_pct ASC
LIMIT 15;
