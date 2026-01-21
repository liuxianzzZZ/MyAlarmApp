import sqlite3
import threading
from datetime import datetime, timedelta

DB_PATH = "tasks.db"
DATE_FMT = "%Y-%m-%d %H:%M"

_lock = threading.Lock()

class Database:
    def __init__(self, path: str = DB_PATH):
        self.path = path
        self._init_db()

    def _connect(self):
        return sqlite3.connect(self.path, check_same_thread=False)

    def _init_db(self):
        with _lock:
            conn = self._connect()
            cur = conn.cursor()
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    note TEXT DEFAULT '',
                    due_datetime TEXT NOT NULL,
                    priority INTEGER DEFAULT 1,
                    repeat_mode TEXT DEFAULT 'once',
                    status TEXT DEFAULT 'pending',
                    is_deleted INTEGER DEFAULT 0
                )
                """
            )
            conn.commit()
            conn.close()

    def add_task(self, title: str, note: str, due_datetime: str, priority: int, repeat_mode: str):
        with _lock:
            conn = self._connect()
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO tasks (title, note, due_datetime, priority, repeat_mode) VALUES (?, ?, ?, ?, ?)",
                (title, note, due_datetime, priority, repeat_mode),
            )
            conn.commit()
            task_id = cur.lastrowid
            conn.close()
            return task_id

    def mark_done(self, task_id: int):
        with _lock:
            conn = self._connect()
            cur = conn.cursor()
            cur.execute("UPDATE tasks SET status='done' WHERE id=? AND is_deleted=0", (task_id,))
            conn.commit()
            conn.close()

    def soft_delete(self, task_id: int):
        with _lock:
            conn = self._connect()
            cur = conn.cursor()
            cur.execute("UPDATE tasks SET is_deleted=1 WHERE id=?", (task_id,))
            conn.commit()
            conn.close()

    def undo_delete(self, task_id: int):
        with _lock:
            conn = self._connect()
            cur = conn.cursor()
            cur.execute("UPDATE tasks SET is_deleted=0 WHERE id=?", (task_id,))
            conn.commit()
            conn.close()

    def get_all_pending_tasks(self):
        with _lock:
            conn = self._connect()
            cur = conn.cursor()
            cur.execute(
                "SELECT id, title, note, due_datetime, priority, repeat_mode, status, is_deleted FROM tasks WHERE status='pending' AND is_deleted=0"
            )
            rows = cur.fetchall()
            conn.close()
            return [
                {
                    "id": r[0],
                    "title": r[1],
                    "note": r[2],
                    "due_datetime": r[3],
                    "priority": r[4],
                    "repeat_mode": r[5],
                    "status": r[6],
                    "is_deleted": r[7],
                }
                for r in rows
            ]

    def get_task_by_id(self, task_id: int):
        with _lock:
            conn = self._connect()
            cur = conn.cursor()
            cur.execute(
                "SELECT id, title, note, due_datetime, priority, repeat_mode, status, is_deleted FROM tasks WHERE id=?",
                (task_id,),
            )
            r = cur.fetchone()
            conn.close()
            if not r:
                return None
            return {
                "id": r[0],
                "title": r[1],
                "note": r[2],
                "due_datetime": r[3],
                "priority": r[4],
                "repeat_mode": r[5],
                "status": r[6],
                "is_deleted": r[7],
            }

    def _advance_due(self, task):
        dt = datetime.strptime(task["due_datetime"], DATE_FMT)
        mode = (task["repeat_mode"] or "once").lower()
        if mode == "daily":
            dt = dt + timedelta(days=1)
            return dt.strftime(DATE_FMT)
        if mode == "weekly":
            dt = dt + timedelta(weeks=1)
            return dt.strftime(DATE_FMT)
        if mode == "custom":
            dt = dt + timedelta(days=1)
            return dt.strftime(DATE_FMT)
        return None

    def check_alarm(self, now_dt: datetime):
        with _lock:
            conn = self._connect()
            cur = conn.cursor()
            cur.execute(
                "SELECT id, title, note, due_datetime, priority, repeat_mode FROM tasks WHERE status='pending' AND is_deleted=0 ORDER BY priority DESC, due_datetime ASC LIMIT 1"
            )
            r = cur.fetchone()
            if not r:
                conn.close()
                return None
            task = {
                "id": r[0],
                "title": r[1],
                "note": r[2],
                "due_datetime": r[3],
                "priority": r[4],
                "repeat_mode": r[5],
            }
            due = datetime.strptime(task["due_datetime"], DATE_FMT)
            if due <= now_dt:
                next_due = self._advance_due(task)
                if next_due:
                    cur.execute("UPDATE tasks SET due_datetime=? WHERE id=?", (next_due, task["id"]))
                else:
                    cur.execute("UPDATE tasks SET status='done' WHERE id=?", (task["id"],))
                conn.commit()
                conn.close()
                return task
            conn.close()
            return None

