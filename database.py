import sqlite3
from contextlib import contextmanager

DB_PATH = "bot_data.db"

@contextmanager
def get_db():
    conn = sqlite3.connect(DB_PATH, isolation_level=None)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

def init_db():
    with get_db() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                lang TEXT NOT NULL DEFAULT 'en'
            );
            CREATE TABLE IF NOT EXISTS repos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                github_url TEXT UNIQUE,
                owner TEXT,
                repo TEXT,
                last_sha TEXT,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            );
        """)

def set_language(user_id: int, lang: str):
    with get_db() as conn:
        conn.execute("INSERT OR REPLACE INTO users (user_id, lang) VALUES (?, ?)", (user_id, lang))

def get_language(user_id: int) -> str:
    with get_db() as conn:
        row = conn.execute("SELECT lang FROM users WHERE user_id = ?", (user_id,)).fetchone()
        return row["lang"] if row else None

def add_repo(user_id: int, url: str, owner: str, repo: str, sha: str):
    with get_db() as conn:
        conn.execute(
            "INSERT OR REPLACE INTO repos (user_id, github_url, owner, repo, last_sha) VALUES (?, ?, ?, ?, ?)",
            (user_id, url, owner, repo, sha)
        )

def get_user_repos(user_id: int) -> list:
    with get_db() as conn:
        return conn.execute("SELECT * FROM repos WHERE user_id = ? ORDER BY id DESC", (user_id,)).fetchall()

def get_all_repos_for_polling() -> list:
    with get_db() as conn:
        return conn.execute("SELECT user_id, github_url, owner, repo, last_sha FROM repos").fetchall()

def update_repo_sha(github_url: str, new_sha: str):
    with get_db() as conn:
        conn.execute("UPDATE repos SET last_sha = ? WHERE github_url = ?", (new_sha, github_url))

def remove_repo(user_id: int, repo_id: int):
    """Removes a repository for the user."""
    with get_db() as conn:
        conn.execute("DELETE FROM repos WHERE id = ? AND user_id = ?", (repo_id, user_id))
