import sqlite3
import json
import os

DB_NAME = "news.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS news (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            original_text TEXT NOT NULL,
            source_url TEXT NOT NULL,
            source_name TEXT NOT NULL,
            moods TEXT DEFAULT '{}',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def save_news(news_list):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    for item in news_list:
        cursor.execute('''
            INSERT OR IGNORE INTO news (title, original_text, source_url, source_name)
            VALUES (?, ?, ?, ?)
        ''', (item['title'], item['original_text'], item['source_url'], item['source_name']))
    conn.commit()
    conn.close()

def get_all_news():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM news ORDER BY id DESC LIMIT 20')
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def get_news_by_id(news_id):
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM news WHERE id = ?', (news_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def update_mood(news_id, mood, text):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT moods FROM news WHERE id = ?', (news_id,))
    row = cursor.fetchone()
    moods = json.loads(row[0]) if row and row[0] else {}
    moods[mood] = text
    cursor.execute('UPDATE news SET moods = ? WHERE id = ?', (json.dumps(moods, ensure_ascii=False), news_id))
    conn.commit()
    conn.close()