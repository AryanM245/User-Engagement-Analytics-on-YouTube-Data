"""
run_analysis.py
Executes all 15 SQL queries against the SQLite database and
saves results to queries/results/ as CSV files.
"""

import sqlite3
import csv
import os
import re

DB_PATH = "data/youtube.db"
SQL_PATH = "queries/analysis.sql"
OUT_DIR  = "queries/results"

os.makedirs(OUT_DIR, exist_ok=True)


def split_queries(sql_text):
    """Split SQL file into individual named queries."""
    # Remove all comment lines (lines starting with --)
    clean_lines = []
    for line in sql_text.splitlines():
        stripped = line.strip()
        if not stripped.startswith('--'):
            clean_lines.append(line)
    clean_sql = '\n'.join(clean_lines)

    # Split on semicolons to get individual statements
    # But we also need query numbers from the original text
    # Extract Q numbers and names from original
    header_re = re.compile(r'Q(\d+)\s*·\s*([^\n│┐]+)')
    headers = header_re.findall(sql_text)

    # Split clean SQL into statements
    statements = [s.strip() for s in clean_sql.split(';') if s.strip()]

    queries = []
    for i, stmt in enumerate(statements):
        if i < len(headers):
            qnum, qname = headers[i]
            qname = re.sub(r'[^a-zA-Z0-9 _]', '', qname).strip().replace(' ', '_').lower()
        else:
            qnum, qname = str(i+1), f"query_{i+1}"
        queries.append((qnum.strip(), qname, stmt))
    return queries


def run_all():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    with open(SQL_PATH, "r") as f:
        sql_text = f.read()

    queries = split_queries(sql_text)
    print(f"Found {len(queries)} queries. Running...\n")

    summary = []
    for qnum, qname, sql in queries:
        try:
            cur = conn.execute(sql)
            rows = cur.fetchall()
            cols = [d[0] for d in cur.description] if cur.description else []
            filename = f"Q{qnum.zfill(2)}_{qname[:50]}.csv"
            filepath = os.path.join(OUT_DIR, filename)
            with open(filepath, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(cols)
                writer.writerows(rows)
            print(f"  ✅ Q{qnum} [{qname}] → {len(rows)} rows")
            summary.append((qnum, qname, len(rows), filename, "OK"))
        except Exception as e:
            print(f"  ❌ Q{qnum} [{qname}] ERROR: {e}")
            summary.append((qnum, qname, 0, "", str(e)))

    conn.close()

    # Write summary
    with open(os.path.join(OUT_DIR, "_summary.csv"), "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["query_num", "name", "rows_returned", "output_file", "status"])
        writer.writerows(summary)

    print("\n✅ All queries done. Results in:", OUT_DIR)


if __name__ == "__main__":
    run_all()
