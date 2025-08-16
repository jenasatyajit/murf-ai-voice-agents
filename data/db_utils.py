import sqlite3
import os
from typing import List, Tuple

DB_PATH = os.path.join(os.path.dirname(__file__), "chat_history.db")

def init_db():
    """Initialize the chat history database."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS chat_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            role TEXT NOT NULL,
            message TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

def add_message(session_id: str, role: str, message: str):
    """Add a message to the chat history."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        INSERT INTO chat_history (session_id, role, message)
        VALUES (?, ?, ?)
    """, (session_id, role, message))
    conn.commit()
    conn.close()

def get_last_messages(session_id: str, limit: int = 10) -> List[Tuple[str, str]]:
    """Get the last `limit` messages for a session."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        SELECT role, message FROM chat_history
        WHERE session_id = ?
        ORDER BY timestamp DESC
        LIMIT ?
    """, (session_id, limit))
    rows = c.fetchall()
    conn.close()
    return list(reversed(rows))  # reverse to get chronological order
