import json
import sqlite3
from pathlib import Path
from uuid import uuid4
from datetime import datetime, timezone
from typing import Any


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def sqlite_path_from_url(database_url: str) -> Path:
    if database_url.startswith("sqlite:///"):
        return Path(database_url.replace("sqlite:///", "", 1)).resolve()

    raise ValueError("Only sqlite:/// database_url is supported in this starter.")


class SQLiteStore:
    def __init__(self, database_url: str):
        self.db_path = sqlite_path_from_url(database_url)

    def connect(self) -> sqlite3.Connection:
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def init_db(self) -> None:
        with self.connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS conversations (
                    id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
                """
            )

            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS messages (
                    id TEXT PRIMARY KEY,
                    conversation_id TEXT NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    sources_json TEXT NOT NULL DEFAULT '[]',
                    timings_json TEXT,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY(conversation_id) REFERENCES conversations(id) ON DELETE CASCADE
                )
                """
            )

            conn.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_messages_conversation_id
                ON messages(conversation_id)
                """
            )

    def create_conversation(self, title: str | None = None) -> dict[str, Any]:
        now = utc_now()
        conversation_id = str(uuid4())
        safe_title = title or "New conversation"

        with self.connect() as conn:
            conn.execute(
                """
                INSERT INTO conversations (id, title, created_at, updated_at)
                VALUES (?, ?, ?, ?)
                """,
                (conversation_id, safe_title, now, now),
            )

        return {
            "id": conversation_id,
            "title": safe_title,
            "created_at": now,
            "updated_at": now,
        }

    def conversation_exists(self, conversation_id: str) -> bool:
        with self.connect() as conn:
            row = conn.execute(
                "SELECT id FROM conversations WHERE id = ?",
                (conversation_id,),
            ).fetchone()

        return row is not None

    def list_conversations(self, limit: int = 50) -> list[dict[str, Any]]:
        with self.connect() as conn:
            rows = conn.execute(
                """
                SELECT id, title, created_at, updated_at
                FROM conversations
                ORDER BY updated_at DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()

        return [dict(row) for row in rows]

    def get_recent_messages(self, conversation_id: str, limit: int = 8) -> list[dict]:
        with self.connect() as conn:
            rows = conn.execute(
                """
                SELECT role, content, created_at
                FROM messages
                WHERE conversation_id = ?
                AND role IN ('user', 'assistant')
                ORDER BY created_at DESC
                LIMIT ?
                """,
                (conversation_id, limit),
            ).fetchall()

        messages = [
            {
                "role": row["role"],
                "content": row["content"],
            }
            for row in rows
        ]

        messages.reverse()
        return messages

    def get_conversation(self, conversation_id: str) -> dict[str, Any] | None:
        with self.connect() as conn:
            conversation = conn.execute(
                """
                SELECT id, title, created_at, updated_at
                FROM conversations
                WHERE id = ?
                """,
                (conversation_id,),
            ).fetchone()

            if conversation is None:
                return None

            messages = conn.execute(
                """
                SELECT id, conversation_id, role, content, sources_json, timings_json, created_at
                FROM messages
                WHERE conversation_id = ?
                ORDER BY created_at ASC
                """,
                (conversation_id,),
            ).fetchall()

        return {
            **dict(conversation),
            "messages": [
                {
                    "id": row["id"],
                    "conversation_id": row["conversation_id"],
                    "role": row["role"],
                    "content": row["content"],
                    "sources": json.loads(row["sources_json"] or "[]"),
                    "timings_ms": json.loads(row["timings_json"]) if row["timings_json"] else None,
                    "created_at": row["created_at"],
                }
                for row in messages
            ],
        }

    def delete_conversation(self, conversation_id: str) -> bool:
        with self.connect() as conn:
            conn.execute(
                "DELETE FROM messages WHERE conversation_id = ?",
                (conversation_id,),
            )
            cursor = conn.execute(
                "DELETE FROM conversations WHERE id = ?",
                (conversation_id,),
            )

        return cursor.rowcount > 0

    def add_message(
        self,
        conversation_id: str,
        role: str,
        content: str,
        sources: list[dict[str, Any]] | None = None,
        timings_ms: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        now = utc_now()
        message_id = str(uuid4())

        sources_json = json.dumps(sources or [], ensure_ascii=False)
        timings_json = json.dumps(timings_ms, ensure_ascii=False) if timings_ms else None

        with self.connect() as conn:
            conn.execute(
                """
                INSERT INTO messages (
                    id,
                    conversation_id,
                    role,
                    content,
                    sources_json,
                    timings_json,
                    created_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    message_id,
                    conversation_id,
                    role,
                    content,
                    sources_json,
                    timings_json,
                    now,
                ),
            )

            conn.execute(
                """
                UPDATE conversations
                SET updated_at = ?
                WHERE id = ?
                """,
                (now, conversation_id),
            )

        return {
            "id": message_id,
            "conversation_id": conversation_id,
            "role": role,
            "content": content,
            "sources": sources or [],
            "timings_ms": timings_ms,
            "created_at": now,
        }

    def rename_conversation_if_default(self, conversation_id: str, query: str) -> None:
        title = query.strip()
        if len(title) > 80:
            title = title[:77] + "..."

        with self.connect() as conn:
            row = conn.execute(
                "SELECT title FROM conversations WHERE id = ?",
                (conversation_id,),
            ).fetchone()

            if row and row["title"] == "New conversation":
                conn.execute(
                    """
                    UPDATE conversations
                    SET title = ?, updated_at = ?
                    WHERE id = ?
                    """,
                    (title, utc_now(), conversation_id),
                )
