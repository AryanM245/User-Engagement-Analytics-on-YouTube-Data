"""
generate_data.py
Generates a realistic YouTube trending dataset mirroring the Kaggle
dataset: raminrahimzada/youtube
Columns: video_id, trending_date, title, channel_title, category_id,
         publish_time, tags, views, likes, dislikes, comment_count,
         comments_disabled, ratings_disabled, description, country
"""

import csv
import random
import hashlib
import datetime
import os

random.seed(42)

# ── Category mapping (matches YouTube API) ───────────────────────────────────
CATEGORIES = {
    1:  "Film & Animation",
    2:  "Autos & Vehicles",
    10: "Music",
    15: "Pets & Animals",
    17: "Sports",
    19: "Travel & Events",
    20: "Gaming",
    22: "People & Blogs",
    23: "Comedy",
    24: "Entertainment",
    25: "News & Politics",
    26: "Howto & Style",
    27: "Education",
    28: "Science & Technology",
    29: "Nonprofits & Activism",
}

COUNTRIES = ["US", "IN", "GB", "CA", "AU", "DE", "FR", "BR", "JP", "MX"]

CHANNELS = [
    ("PewDiePie",         20), ("T-Series",          10), ("MrBeast",           24),
    ("Dude Perfect",      17), ("Cocomelon",           1), ("SETIndia",          24),
    ("5-Minute Crafts",  26), ("WWE",                17), ("Zee Music",         10),
    ("Like Nastya",      22), ("Vlad and Niki",      22), ("Markiplier",        20),
    ("BLACKPINK",        10), ("BTS",                10), ("NBA",               17),
    ("ESPN",             17), ("CNN",                25), ("BBC News",          25),
    ("Vox",              27), ("TED",                27), ("Kurzgesagt",        27),
    ("Veritasium",       28), ("3Blue1Brown",        27), ("Linus Tech Tips",   28),
    ("MKBHD",            28), ("Tasty",              26), ("Gordon Ramsay",     26),
    ("Smosh",            23), ("Saturday Night Live",23), ("CollegeHumor",      23),
    ("Jimmy Fallon",     24), ("Ellen",              24), ("GoodMythicalMorning",22),
    ("Vice",             25), ("NowThis News",       25), ("Lofi Girl",         10),
    ("Sony Music",       10), ("Universal Music",   10), ("Warner Music",      10),
    ("A24",               1), ("Marvel",             1), ("DC",                 1),
]

TITLE_TEMPLATES = [
    "I Spent {n} Days {action}",
    "{action} for {n} Hours Straight",
    "The Truth About {topic}",
    "Why {topic} Changed Everything",
    "We Tried {topic} So You Don't Have To",
    "{n} Things You Didn't Know About {topic}",
    "How {topic} Actually Works",
    "World's {superlative} {topic}",
    "Building {topic} From Scratch",
    "{topic} Is Not What You Think",
    "I Challenged {topic}",
    "Rating {topic} With {celebrity}",
    "Reacting To {topic}",
    "{n} vs 1: {topic} Edition",
    "The REAL Reason Behind {topic}",
]

TOPICS = [
    "YouTube", "TikTok", "AI", "Space", "the Ocean", "the Government",
    "Minecraft", "100 Fans", "this Challenge", "Amazon", "the Internet",
    "Music", "Food", "Science", "History", "Money", "Climate Change",
    "the Algorithm", "Famous YouTubers", "this Experiment",
]

ACTIONS = [
    "Surviving on $1", "Living Underground", "Eating Only Pizza",
    "Building a House", "Learning a New Language", "Swimming with Sharks",
    "Coding an App", "Breaking a World Record",
]

SUPERLATIVES = ["Largest", "Smallest", "Fastest", "Cheapest", "Most Expensive",
                "Most Dangerous", "Rarest"]

CELEBRITIES = ["MrBeast", "PewDiePie", "a Billionaire", "100 Kids", "an Expert",
               "my Friends", "Strangers"]


def random_video_id():
    chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-"
    return "".join(random.choices(chars, k=11))


def random_title():
    tmpl = random.choice(TITLE_TEMPLATES)
    return tmpl.format(
        n=random.choice([1, 3, 7, 10, 24, 30, 100, 1000]),
        action=random.choice(ACTIONS),
        topic=random.choice(TOPICS),
        superlative=random.choice(SUPERLATIVES),
        celebrity=random.choice(CELEBRITIES),
    )


def random_tags(category_id):
    base = ["youtube", "viral", "trending"]
    cat_name = CATEGORIES.get(category_id, "").lower().replace(" & ", " ").split()
    extras = random.sample(TOPICS + ACTIONS, k=random.randint(3, 8))
    all_tags = list(set(base + cat_name + [t.lower() for t in extras]))
    return "|".join(random.sample(all_tags, k=min(len(all_tags), random.randint(4, 10))))


def generate_views_likes(category_id):
    """Simulate view/like distributions per category."""
    base_views = {
        10: 8_000_000, 24: 5_000_000, 17: 4_000_000,
        20: 6_000_000, 22: 3_000_000, 23: 3_500_000,
        25: 2_000_000, 27: 1_500_000, 28: 1_800_000,
        26: 2_500_000,  1: 4_500_000,
    }.get(category_id, 2_000_000)

    views = max(1000, int(random.lognormvariate(0, 1) * base_views))
    like_rate = random.uniform(0.02, 0.12)
    dislike_rate = random.uniform(0.001, 0.025)
    comment_rate = random.uniform(0.005, 0.04)
    likes = int(views * like_rate)
    dislikes = int(views * dislike_rate)
    comments = int(views * comment_rate)
    return views, likes, dislikes, comments


def generate_dataset(n_videos=5000, output_path="data/youtube_trending.csv"):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    start_date = datetime.date(2022, 1, 1)
    end_date   = datetime.date(2024, 12, 31)
    delta_days = (end_date - start_date).days

    fieldnames = [
        "video_id", "trending_date", "title", "channel_title", "category_id",
        "category_name", "publish_time", "tags", "views", "likes", "dislikes",
        "comment_count", "comments_disabled", "ratings_disabled",
        "description", "country",
    ]

    rows = []
    for _ in range(n_videos):
        channel, cat_id = random.choice(CHANNELS)
        # Occasionally use random category
        if random.random() < 0.3:
            cat_id = random.choice(list(CATEGORIES.keys()))

        trend_date = start_date + datetime.timedelta(days=random.randint(0, delta_days))
        publish_offset = random.randint(1, 30)
        publish_time = datetime.datetime.combine(
            trend_date - datetime.timedelta(days=publish_offset),
            datetime.time(random.randint(0, 23), random.randint(0, 59))
        )

        views, likes, dislikes, comments = generate_views_likes(cat_id)

        rows.append({
            "video_id":          random_video_id(),
            "trending_date":     trend_date.strftime("%Y-%m-%d"),
            "title":             random_title(),
            "channel_title":     channel,
            "category_id":       cat_id,
            "category_name":     CATEGORIES.get(cat_id, "Unknown"),
            "publish_time":      publish_time.strftime("%Y-%m-%dT%H:%M:%S.000Z"),
            "tags":              random_tags(cat_id),
            "views":             views,
            "likes":             likes,
            "dislikes":          dislikes,
            "comment_count":     comments,
            "comments_disabled": random.choices([True, False], weights=[5, 95])[0],
            "ratings_disabled":  random.choices([True, False], weights=[3, 97])[0],
            "description":       f"Watch this video about {random.choice(TOPICS).lower()}. Subscribe for more!",
            "country":           random.choice(COUNTRIES),
        })

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"✅ Generated {len(rows)} rows → {output_path}")


if __name__ == "__main__":
    generate_dataset(n_videos=5000)
