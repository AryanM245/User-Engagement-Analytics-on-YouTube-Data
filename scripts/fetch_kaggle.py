"""
fetch_kaggle.py
Downloads the real dataset from Kaggle and places it at data/youtube_trending.csv

Prerequisites:
    pip install kagglehub
    Set up ~/.kaggle/kaggle.json with your API credentials
    (Kaggle → Account → API → Create New Token)

Usage:
    python scripts/fetch_kaggle.py

The script downloads the dataset, auto-detects the CSV file,
and copies it to data/youtube_trending.csv for setup_db.py to consume.
"""

import os
import glob
import shutil

def fetch():
    try:
        import kagglehub
    except ImportError:
        print("❌ kagglehub not installed. Run: pip install kagglehub")
        return

    print("📥 Downloading dataset: raminrahimzada/youtube ...")
    path = kagglehub.dataset_download("raminrahimzada/youtube")
    print(f"📁 Raw download path: {path}")

    # Find CSV files in the download
    csv_files = glob.glob(os.path.join(path, "**/*.csv"), recursive=True)
    if not csv_files:
        print("❌ No CSV found in download. Check path manually:", path)
        return

    print(f"Found CSVs: {csv_files}")
    # Pick the largest CSV (likely the main dataset)
    main_csv = max(csv_files, key=os.path.getsize)
    print(f"✅ Using: {main_csv}")

    os.makedirs("data", exist_ok=True)
    dest = "data/youtube_trending.csv"
    shutil.copy(main_csv, dest)
    print(f"✅ Copied to {dest}")
    print("\nNext step: python scripts/setup_db.py")


if __name__ == "__main__":
    fetch()
