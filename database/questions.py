"""使用 SQLite 在本机保存错题。"""
import sqlite3
from datetime import datetime, timezone
from config import DATABASE_PATH


def _connect():
    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("""
        CREATE TABLE IF NOT EXISTS wrong_questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question TEXT NOT NULL,
            answer TEXT NOT NULL DEFAULT '',
            note TEXT NOT NULL DEFAULT '',
            created_at TEXT NOT NULL
        )
    """)
    conn.commit()
    return conn


def add_wrong(question, answer="", note=""):
    if not question or not question.strip():
        raise ValueError("题目内容不能为空")
    with _connect() as conn:
        cur = conn.execute(
            "INSERT INTO wrong_questions(question, answer, note, created_at) VALUES (?, ?, ?, ?)",
            (question.strip(), answer.strip(), note.strip(), datetime.now(timezone.utc).isoformat())
        )
        return cur.lastrowid


def list_wrong():
    with _connect() as conn:
        return [dict(row) for row in conn.execute(
            "SELECT * FROM wrong_questions ORDER BY id DESC"
        ).fetchall()]
