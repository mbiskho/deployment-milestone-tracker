from __future__ import annotations

import sqlite3
from datetime import date, timedelta
from pathlib import Path

from .templates import TEMPLATES

SCHEMA = """
CREATE TABLE IF NOT EXISTS deployments (
  id INTEGER PRIMARY KEY, customer TEXT NOT NULL, start DATE NOT NULL, template TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS milestones (
  id INTEGER PRIMARY KEY,
  deployment_id INTEGER NOT NULL REFERENCES deployments(id) ON DELETE CASCADE,
  position INTEGER NOT NULL,
  name TEXT NOT NULL,
  owner TEXT NOT NULL,                       -- 'us' or 'customer'
  due DATE NOT NULL,
  status TEXT NOT NULL DEFAULT 'not_started' CHECK (status IN ('not_started','in_progress','blocked','done')),
  blocker TEXT, blocker_owner TEXT, blocked_since DATE, done_on DATE
);
"""


def connect(path: str | Path = "tracker.db") -> sqlite3.Connection:
    conn = sqlite3.connect(path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.executescript(SCHEMA)
    return conn


def create_deployment(conn: sqlite3.Connection, customer: str, start: date, template: str) -> int:
    if template not in TEMPLATES:
        raise ValueError(f"unknown template {template!r}; have {sorted(TEMPLATES)}")
    with conn:
        cur = conn.execute("INSERT INTO deployments (customer, start, template) VALUES (?, ?, ?)",
                           (customer, start.isoformat(), template))
        dep_id = cur.lastrowid
        conn.executemany(
            "INSERT INTO milestones (deployment_id, position, name, owner, due) VALUES (?, ?, ?, ?, ?)",
            [(dep_id, i, name, owner, (start + timedelta(days=d)).isoformat())
             for i, (name, owner, d) in enumerate(TEMPLATES[template])],
        )
    return dep_id


def update_milestone(conn: sqlite3.Connection, mid: int, today: date, **changes) -> sqlite3.Row:
    row = conn.execute("SELECT * FROM milestones WHERE id = ?", (mid,)).fetchone()
    if row is None:
        raise KeyError(mid)
    status = changes.get("status", row["status"])
    fields = {k: v for k, v in changes.items() if k in {"status", "due", "blocker", "blocker_owner"} and v is not None}
    # Keep blocked_since honest: set when it becomes blocked, cleared when it isn't.
    if status == "blocked" and row["status"] != "blocked":
        fields["blocked_since"] = today.isoformat()
    if status != "blocked":
        fields.update(blocker=None, blocker_owner=None, blocked_since=None)
    if status == "done" and row["status"] != "done":
        fields["done_on"] = today.isoformat()
    if not fields:
        return row
    sets = ", ".join(f"{k} = ?" for k in fields)
    with conn:
        conn.execute(f"UPDATE milestones SET {sets} WHERE id = ?", (*fields.values(), mid))
    return conn.execute("SELECT * FROM milestones WHERE id = ?", (mid,)).fetchone()


def deployment(conn: sqlite3.Connection, dep_id: int) -> tuple[sqlite3.Row, list[sqlite3.Row]]:
    dep = conn.execute("SELECT * FROM deployments WHERE id = ?", (dep_id,)).fetchone()
    if dep is None:
        raise KeyError(dep_id)
    ms = conn.execute("SELECT * FROM milestones WHERE deployment_id = ? ORDER BY position", (dep_id,)).fetchall()
    return dep, ms
