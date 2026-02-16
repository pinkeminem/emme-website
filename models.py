import sqlite3
import json
import os
from config import Config

# Whitelist of valid table names to prevent SQL injection in get_rows()
VALID_TABLES = {
    'gallery_images', 'live_videos', 'shows', 'releases',
    'soundcloud_tracks', 'archive_articles', 'lighting_shows',
    'lighting_photos', 'contact_messages', 'blog_posts',
}
VALID_ORDER_COLUMNS = {
    'sort_order', 'id', 'year DESC, id', 'created_at DESC',
}


def get_db():
    db = sqlite3.connect(Config.DB_PATH)
    db.row_factory = sqlite3.Row
    db.execute('PRAGMA journal_mode=WAL')
    db.execute('PRAGMA foreign_keys=ON')
    return db


def init_db():
    db = get_db()
    db.executescript('''
        CREATE TABLE IF NOT EXISTS admin_user (
            id INTEGER PRIMARY KEY,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS page_content (
            id INTEGER PRIMARY KEY,
            page TEXT NOT NULL,
            section TEXT NOT NULL,
            content_json TEXT NOT NULL,
            UNIQUE(page, section)
        );

        CREATE TABLE IF NOT EXISTS gallery_images (
            id INTEGER PRIMARY KEY,
            filename TEXT NOT NULL,
            alt_text TEXT DEFAULT '',
            sort_order INTEGER DEFAULT 0
        );

        CREATE TABLE IF NOT EXISTS live_videos (
            id INTEGER PRIMARY KEY,
            filename TEXT NOT NULL,
            title TEXT DEFAULT '',
            location TEXT DEFAULT '',
            sort_order INTEGER DEFAULT 0
        );

        CREATE TABLE IF NOT EXISTS shows (
            id INTEGER PRIMARY KEY,
            show_date TEXT DEFAULT '',
            venue TEXT DEFAULT '',
            city TEXT DEFAULT '',
            info_url TEXT DEFAULT '',
            sort_order INTEGER DEFAULT 0
        );

        CREATE TABLE IF NOT EXISTS releases (
            id INTEGER PRIMARY KEY,
            title TEXT NOT NULL,
            cover_image TEXT DEFAULT '',
            bandcamp_url TEXT DEFAULT '',
            sort_order INTEGER DEFAULT 0
        );

        CREATE TABLE IF NOT EXISTS soundcloud_tracks (
            id INTEGER PRIMARY KEY,
            title TEXT NOT NULL,
            url TEXT DEFAULT '',
            sort_order INTEGER DEFAULT 0
        );

        CREATE TABLE IF NOT EXISTS archive_articles (
            id INTEGER PRIMARY KEY,
            year INTEGER NOT NULL,
            month_day TEXT DEFAULT '',
            title TEXT NOT NULL,
            url TEXT DEFAULT '',
            category TEXT DEFAULT ''
        );

        CREATE TABLE IF NOT EXISTS lighting_shows (
            id INTEGER PRIMARY KEY,
            role TEXT DEFAULT '',
            title TEXT NOT NULL,
            venue TEXT DEFAULT '',
            location TEXT DEFAULT '',
            links_json TEXT DEFAULT '[]',
            sort_order INTEGER DEFAULT 0
        );

        CREATE TABLE IF NOT EXISTS lighting_photos (
            id INTEGER PRIMARY KEY,
            filename TEXT NOT NULL,
            alt_text TEXT DEFAULT '',
            sort_order INTEGER DEFAULT 0
        );

        CREATE TABLE IF NOT EXISTS contact_messages (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            subject TEXT DEFAULT '',
            message TEXT NOT NULL,
            is_read INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS blog_posts (
            id INTEGER PRIMARY KEY,
            title TEXT NOT NULL,
            url TEXT DEFAULT '',
            excerpt TEXT DEFAULT '',
            category TEXT DEFAULT '',
            date_display TEXT DEFAULT '',
            sort_order INTEGER DEFAULT 0
        );

        CREATE TABLE IF NOT EXISTS login_attempts (
            id INTEGER PRIMARY KEY,
            ip TEXT NOT NULL,
            attempted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    ''')
    db.commit()
    db.close()


def get_content(page, section, default=None):
    db = get_db()
    row = db.execute(
        'SELECT content_json FROM page_content WHERE page=? AND section=?',
        (page, section)
    ).fetchone()
    db.close()
    if row:
        return json.loads(row['content_json'])
    return default


def set_content(page, section, data):
    db = get_db()
    db.execute('''
        INSERT INTO page_content (page, section, content_json)
        VALUES (?, ?, ?)
        ON CONFLICT(page, section) DO UPDATE SET content_json=excluded.content_json
    ''', (page, section, json.dumps(data)))
    db.commit()
    db.close()


def get_rows(table, order_by='sort_order'):
    if table not in VALID_TABLES:
        raise ValueError(f'Invalid table: {table}')
    if order_by not in VALID_ORDER_COLUMNS:
        raise ValueError(f'Invalid order: {order_by}')
    db = get_db()
    rows = db.execute(f'SELECT * FROM {table} ORDER BY {order_by}').fetchall()
    db.close()
    return [dict(r) for r in rows]


def get_unread_count():
    db = get_db()
    row = db.execute('SELECT COUNT(*) as c FROM contact_messages WHERE is_read=0').fetchone()
    db.close()
    return row['c'] if row else 0


def check_rate_limit(ip, window_seconds=300, max_attempts=5):
    """Returns True if rate limited (too many attempts)."""
    db = get_db()
    # Clean old attempts
    db.execute("DELETE FROM login_attempts WHERE attempted_at < datetime('now', ?)",
               (f'-{window_seconds} seconds',))
    count = db.execute(
        "SELECT COUNT(*) as c FROM login_attempts WHERE ip=? AND attempted_at > datetime('now', ?)",
        (ip, f'-{window_seconds} seconds')
    ).fetchone()['c']
    db.commit()
    db.close()
    return count >= max_attempts


def record_login_attempt(ip):
    db = get_db()
    db.execute('INSERT INTO login_attempts (ip) VALUES (?)', (ip,))
    db.commit()
    db.close()
