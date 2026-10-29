import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "processed_news.db")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS processed_articles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source_url TEXT UNIQUE,
            original_title TEXT,
            rewritten_title TEXT,
            wp_post_id INTEGER,
            published_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

def is_article_processed(url: str) -> bool:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM processed_articles WHERE source_url = ?", (url,))
    result = cursor.fetchone()
    conn.close()
    return result is not None

def record_processed_article(source_url: str, original_title: str, rewritten_title: str, wp_post_id: int):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT OR REPLACE INTO processed_articles (source_url, original_title, rewritten_title, wp_post_id)
            VALUES (?, ?, ?, ?)
        """, (source_url, original_title, rewritten_title, wp_post_id))
        conn.commit()
    finally:
        conn.close()
