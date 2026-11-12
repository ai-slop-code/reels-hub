"""Minimal project registration until the YAML projects of 9.1 (spec §6.1, §23.2)."""

import datetime as dt
import sqlite3

from reels_hub.paths import safe_rel


def add_project_folder(
    conn: sqlite3.Connection, project_id: str, folder: str, now: dt.datetime
) -> None:
    stamp = now.astimezone(dt.UTC).isoformat()
    conn.execute(
        "INSERT OR IGNORE INTO project (id, title, folder, created_at) VALUES (?, ?, ?, ?)",
        (project_id, project_id, folder, stamp),
    )
    conn.execute(
        "INSERT OR IGNORE INTO project_media_folder (project_id, rel_path) VALUES (?, ?)",
        (project_id, safe_rel(folder)),
    )
