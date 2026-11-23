"""使用 SQLite 在本机保存错题，并支持导出 CSV。"""
import csv
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from config import DATABASE_PATH, DATA_DIR


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


def _spreadsheet_safe(value):
    """防止导出文本被表格软件误当作公式执行。"""
    text = "" if value is None else str(value)
    if text.startswith(("=", "+", "-", "@", "\t", "\r")):
        return "'" + text
    return text


def export_wrong(output_path=None):
    """将本地错题导出为 Excel 兼容 UTF-8 CSV，默认保存在 data/ 内。"""
    rows = list_wrong()
    if output_path is None:
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = DATA_DIR / f"错题本_{stamp}.csv"
    path = Path(output_path).expanduser()
    path.parent.mkdir(parents=True, exist_ok=True)

    headers = ["编号", "题目", "答案/记录", "笔记", "记录时间（UTC）"]
    with path.open("w", encoding="utf-8-sig", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(headers)
        for row in rows:
            writer.writerow([
                row["id"],
                _spreadsheet_safe(row["question"]),
                _spreadsheet_safe(row["answer"]),
                _spreadsheet_safe(row["note"]),
                row["created_at"],
            ])
    return path
