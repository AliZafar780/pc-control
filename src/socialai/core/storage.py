"""
Data Storage

Handles persistence of posts, sessions, and user data.
"""

import json
import sqlite3
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone

from socialai.config import Config


class Storage:
    """Manages data persistence using SQLite."""
    
    def __init__(self, config: Config):
        self.config = config
        self.db_path = config.storage.db_path
        self._ensure_database()
    
    def _ensure_database(self) -> None:
        """Ensure database and tables exist."""
        db_dir = Path(self.db_path).parent
        db_dir.mkdir(parents=True, exist_ok=True)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create tables
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS posts (
                id TEXT PRIMARY KEY,
                platform TEXT NOT NULL,
                content TEXT NOT NULL,
                title TEXT,
                author TEXT,
                author_id TEXT,
                url TEXT,
                created_at TEXT,
                metrics TEXT,
                engagement_score REAL,
                tags TEXT,
                summary TEXT,
                saved_at TEXT NOT NULL
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS searches (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                query TEXT NOT NULL,
                platform TEXT,
                results_count INTEGER,
                searched_at TEXT NOT NULL
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                id TEXT PRIMARY KEY,
                platforms TEXT,
                duration INTEGER,
                start_time TEXT,
                end_time TEXT,
                posts_read TEXT,
                notes TEXT,
                is_focus_mode INTEGER,
                created_at TEXT NOT NULL
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS bookmarks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                post_id TEXT NOT NULL,
                note TEXT,
                created_at TEXT NOT NULL,
                FOREIGN KEY (post_id) REFERENCES posts(id)
            )
        """)
        
        conn.commit()
        conn.close()
    
    def save_post(self, post: 'Post') -> None:
        """Save a post to the database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO posts 
            (id, platform, content, title, author, author_id, url, created_at, 
             metrics, engagement_score, tags, summary, saved_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            post.id,
            post.platform,
            post.content,
            post.title,
            post.author,
            post.author_id,
            post.url,
            post.created_at.isoformat() if post.created_at else None,
            json.dumps(post.metrics.__dict__) if post.metrics else None,
            post.engagement_score,
            json.dumps(post.tags),
            post.summary,
            datetime.now(timezone.utc).isoformat()
        ))
        
        conn.commit()
        conn.close()
    
    def save_feed(self, platform: str, posts: List['Post']) -> None:
        """Save multiple posts to the database."""
        for post in posts:
            self.save_post(post)
    
    def get_post(self, post_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a post by ID."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM posts WHERE id = ?", (post_id,))
        row = cursor.fetchone()
        
        conn.close()
        
        return dict(row) if row else None
    
    def get_saved_posts(self, platform: Optional[str] = None, limit: int = 100) -> List[Dict[str, Any]]:
        """Retrieve saved posts."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        if platform:
            cursor.execute(
                "SELECT * FROM posts WHERE platform = ? ORDER BY saved_at DESC LIMIT ?",
                (platform, limit)
            )
        else:
            cursor.execute(
                "SELECT * FROM posts ORDER BY saved_at DESC LIMIT ?",
                (limit,)
            )
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def delete_post(self, post_id: str) -> bool:
        """Delete a post from the database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM posts WHERE id = ?", (post_id,))
        deleted = cursor.rowcount > 0
        
        conn.commit()
        conn.close()
        
        return deleted
    
    def save_search(self, query: str, posts: List['Post'], platform: Optional[str] = None) -> None:
        """Save search query and results."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO searches (query, platform, results_count, searched_at)
            VALUES (?, ?, ?, ?)
        """, (
            query,
            platform,
            len(posts),
            datetime.now(timezone.utc).isoformat()
        ))
        
        # Save posts
        for post in posts:
            self.save_post(post)
        
        conn.commit()
        conn.close()
    
    def get_search_history(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Retrieve search history."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT * FROM searches ORDER BY searched_at DESC LIMIT ?",
            (limit,)
        )
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def save_session(self, session: 'Session') -> None:
        """Save a session to the database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO sessions
            (id, platforms, duration, start_time, end_time, posts_read, notes, 
             is_focus_mode, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            session.id,
            json.dumps(session.platforms),
            session.duration,
            session.start_time.isoformat() if session.start_time else None,
            session.end_time.isoformat() if session.end_time else None,
            json.dumps(session.posts_read),
            json.dumps(session.notes),
            1 if session.is_focus_mode else 0,
            datetime.now(timezone.utc).isoformat()
        ))
        
        conn.commit()
        conn.close()
    
    def get_sessions(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Retrieve session history."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT * FROM sessions ORDER BY created_at DESC LIMIT ?",
            (limit,)
        )
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def bookmark_post(self, post_id: str, note: Optional[str] = None) -> None:
        """Bookmark a post."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO bookmarks (post_id, note, created_at)
            VALUES (?, ?, ?)
        """, (post_id, note, datetime.now(timezone.utc).isoformat()))
        
        conn.commit()
        conn.close()
    
    def get_bookmarks(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Retrieve bookmarked posts."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT b.*, p.* 
            FROM bookmarks b
            JOIN posts p ON b.post_id = p.id
            ORDER BY b.created_at DESC
            LIMIT ?
        """, (limit,))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def remove_bookmark(self, post_id: str) -> bool:
        """Remove a bookmark."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM bookmarks WHERE post_id = ?", (post_id,))
        deleted = cursor.rowcount > 0
        
        conn.commit()
        conn.close()
        
        return deleted
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get storage statistics."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        stats = {}
        
        # Post count
        cursor.execute("SELECT COUNT(*) FROM posts")
        stats['total_posts'] = cursor.fetchone()[0]
        
        # Platform breakdown
        cursor.execute("""
            SELECT platform, COUNT(*) as count 
            FROM posts 
            GROUP BY platform
        """)
        stats['posts_by_platform'] = {row[0]: row[1] for row in cursor.fetchall()}
        
        # Search count
        cursor.execute("SELECT COUNT(*) FROM searches")
        stats['total_searches'] = cursor.fetchone()[0]
        
        # Session count
        cursor.execute("SELECT COUNT(*) FROM sessions")
        stats['total_sessions'] = cursor.fetchone()[0]
        
        # Bookmark count
        cursor.execute("SELECT COUNT(*) FROM bookmarks")
        stats['total_bookmarks'] = cursor.fetchone()[0]
        
        conn.close()
        
        return stats
    
    def clear_old_data(self, days: int = 30) -> int:
        """Clear data older than specified days."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        from datetime import timedelta
        cutoff = datetime.now(timezone.utc) - timedelta(days=days)
        cutoff_iso = cutoff.isoformat()
        
        # Delete old posts
        cursor.execute("DELETE FROM posts WHERE saved_at < ?", (cutoff_iso,))
        deleted_posts = cursor.rowcount
        
        # Delete old searches
        cursor.execute("DELETE FROM searches WHERE searched_at < ?", (cutoff_iso,))
        deleted_searches = cursor.rowcount
        
        conn.commit()
        conn.close()
        
        return deleted_posts + deleted_searches


# Forward references
from socialai.adapters.base import Post
from socialai.core.session import Session
