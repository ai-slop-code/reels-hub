"""Job queue and worker loop (spec §4, §21, §23.4; R13).

The `job` table is the queue. One worker thread runs one job at a time, in the same process as
the web app, so heavy work never runs inside a request. Jobs left `running` by a crash or restart
go back to `queued` when the worker starts. A timer enqueues periodic work and catches up
after sleep.
"""

import datetime as dt
import json
import logging
import sqlite3
import subprocess
import threading
import time
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from reels_hub.backup import DAILY_KEEP, daily_name, latest_daily_backup, prune_daily, write_backup
from reels_hub.db import connect

BACKUP_KIND = "backup"
BACKUP_INTERVAL = dt.timedelta(hours=24)

Clock = Callable[[], dt.datetime]
logger = logging.getLogger(__name__)


class JobInterrupted(Exception):
    """The worker is stopping. The job goes back to the queue instead of failing."""


@dataclass(frozen=True)
class Job:
    id: int
    kind: str
    params: dict[str, Any]
    status: str
    progress: int
    error: str | None


def _stamp(now: dt.datetime) -> str:
    return now.astimezone(dt.UTC).isoformat()


def _job(row: tuple[Any, ...]) -> Job:
    return Job(
        id=int(row[0]),
        kind=str(row[1]),
        params=json.loads(row[2]),
        status=str(row[3]),
        progress=int(row[4]),
        error=None if row[5] is None else str(row[5]),
    )


_COLUMNS = "id, kind, params, status, progress, error"


def enqueue(
    conn: sqlite3.Connection, kind: str, now: dt.datetime, params: Mapping[str, Any] | None = None
) -> int:
    stamp = _stamp(now)
    cursor = conn.execute(
        "INSERT INTO job (kind, params, status, progress, created_at, updated_at) "
        "VALUES (?, ?, 'queued', 0, ?, ?)",
        (kind, json.dumps(dict(params or {}), sort_keys=True), stamp, stamp),
    )
    return int(cursor.lastrowid or 0)


def get_job(conn: sqlite3.Connection, job_id: int) -> Job | None:
    row = conn.execute(f"SELECT {_COLUMNS} FROM job WHERE id = ?", (job_id,)).fetchone()
    return _job(row) if row else None


def claim_next(conn: sqlite3.Connection, now: dt.datetime) -> Job | None:
    row = conn.execute(
        f"UPDATE job SET status = 'running', progress = 0, updated_at = ? "
        f"WHERE id = (SELECT id FROM job WHERE status = 'queued' ORDER BY id LIMIT 1) "
        f"RETURNING {_COLUMNS}",
        (_stamp(now),),
    ).fetchone()
    return _job(row) if row else None


def _set(conn: sqlite3.Connection, job_id: int, now: dt.datetime, **columns: Any) -> None:
    assignments = ", ".join(f"{name} = ?" for name in columns)
    conn.execute(
        f"UPDATE job SET {assignments}, updated_at = ? WHERE id = ?",
        (*columns.values(), _stamp(now), job_id),
    )


def set_progress(conn: sqlite3.Connection, job_id: int, percent: int, now: dt.datetime) -> None:
    _set(conn, job_id, now, progress=max(0, min(100, percent)))


def finish(conn: sqlite3.Connection, job_id: int, now: dt.datetime) -> None:
    _set(conn, job_id, now, status="done", progress=100)


def fail(conn: sqlite3.Connection, job_id: int, error: str, now: dt.datetime) -> None:
    _set(conn, job_id, now, status="failed", error=error)


def requeue(conn: sqlite3.Connection, job_id: int, now: dt.datetime) -> None:
    _set(conn, job_id, now, status="queued", progress=0)


def requeue_running(conn: sqlite3.Connection, now: dt.datetime) -> int:
    cursor = conn.execute(
        "UPDATE job SET status = 'queued', progress = 0, updated_at = ? WHERE status = 'running'",
        (_stamp(now),),
    )
    return cursor.rowcount


def job_counts(conn: sqlite3.Connection) -> dict[str, int]:
    rows = conn.execute("SELECT status, COUNT(*) FROM job GROUP BY status").fetchall()
    counts = {"queued": 0, "running": 0, "done": 0, "failed": 0}
    counts.update({str(status): int(count) for status, count in rows})
    return counts


def enqueue_if_idle(conn: sqlite3.Connection, kind: str, now: dt.datetime) -> int | None:
    active = conn.execute(
        "SELECT 1 FROM job WHERE kind = ? AND status IN ('queued', 'running')", (kind,)
    ).fetchone()
    return None if active is not None else enqueue(conn, kind, now)


def enqueue_due_backup(conn: sqlite3.Connection, backup_dir: Path, now: dt.datetime) -> int | None:
    """Queue a daily backup when the newest one is older than 24 h (or missing)."""
    active = conn.execute(
        "SELECT 1 FROM job WHERE kind = ? AND status IN ('queued', 'running')", (BACKUP_KIND,)
    ).fetchone()
    if active is not None:
        return None
    latest = latest_daily_backup(backup_dir)
    if latest is not None and now - latest < BACKUP_INTERVAL:
        return None
    return enqueue(conn, BACKUP_KIND, now)


class JobContext:
    """What a handler gets: its job, the worker's connection and a way to run subprocesses."""

    def __init__(
        self,
        conn: sqlite3.Connection,
        job: Job,
        backup_dir: Path,
        clock: Clock,
        runner: "_Runner",
    ) -> None:
        self.conn = conn
        self.job = job
        self.backup_dir = backup_dir
        self._clock = clock
        self._runner = runner

    def now(self) -> dt.datetime:
        return self._clock()

    def progress(self, percent: int) -> None:
        set_progress(self.conn, self.job.id, percent, self._clock())

    def run(self, args: list[str]) -> subprocess.CompletedProcess[str]:
        """Run a subprocess (ffmpeg, HyperFrames). Raises JobInterrupted when the worker stops."""
        return self._runner.run(args)


class _Runner:
    def __init__(self) -> None:
        self.stopping = threading.Event()
        self._lock = threading.Lock()
        self._process: subprocess.Popen[str] | None = None

    def run(self, args: list[str]) -> subprocess.CompletedProcess[str]:
        process = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        with self._lock:
            self._process = process
            stopping = self.stopping.is_set()
        if stopping:
            process.kill()
        stdout, stderr = process.communicate()
        with self._lock:
            self._process = None
        if self.stopping.is_set():
            raise JobInterrupted()
        return subprocess.CompletedProcess(args, process.returncode, stdout, stderr)

    def kill(self) -> None:
        with self._lock:
            process = self._process
        if process is not None and process.poll() is None:
            process.kill()


Handler = Callable[[JobContext], None]


def run_daily_backup(ctx: JobContext) -> None:
    write_backup(ctx.conn, ctx.backup_dir, daily_name(ctx.now()))
    prune_daily(ctx.backup_dir, keep=DAILY_KEEP)


class Worker:
    """Runs jobs one at a time. Nothing runs until `ready()` is true (the media folder is mounted);
    `prepare()` runs once before the first job (migrations). `schedules` maps a job kind to the
    seconds between enqueues, and an enqueue is skipped while one of that kind is still queued."""

    def __init__(
        self,
        db_path: Path,
        backup_dir: Path,
        *,
        handlers: Mapping[str, Handler] | None = None,
        clock: Clock = lambda: dt.datetime.now(dt.UTC),
        poll_seconds: float = 10.0,
        timer_seconds: float = 300.0,
        ready: Callable[[], bool] = lambda: True,
        prepare: Callable[[], None] = lambda: None,
        schedules: Mapping[str, float] | None = None,
    ) -> None:
        self.db_path = db_path
        self.backup_dir = backup_dir
        self.handlers: dict[str, Handler] = {BACKUP_KIND: run_daily_backup, **(handlers or {})}
        self._clock = clock
        self._poll_seconds = poll_seconds
        self._timer_seconds = timer_seconds
        self._ready = ready
        self._prepare = prepare
        self._schedules = dict(schedules or {})
        self._runner = _Runner()
        self._thread: threading.Thread | None = None

    @property
    def running(self) -> bool:
        return self._thread is not None and self._thread.is_alive()

    def is_ready(self) -> bool:
        return self._ready()

    def run_once(self, conn: sqlite3.Connection) -> bool:
        """Run the next queued job, if any. Returns False when the queue is empty."""
        job = claim_next(conn, self._clock())
        if job is None:
            return False
        ctx = JobContext(conn, job, self.backup_dir, self._clock, self._runner)
        try:
            handler = self.handlers.get(job.kind)
            if handler is None:
                raise RuntimeError(f"no handler for job kind '{job.kind}'")
            handler(ctx)
        except JobInterrupted:
            requeue(conn, job.id, self._clock())
        except Exception as exc:
            logger.exception("job %s (%s) failed", job.id, job.kind)
            fail(conn, job.id, str(exc) or type(exc).__name__, self._clock())
        else:
            finish(conn, job.id, self._clock())
        return True

    def start(self) -> None:
        self._thread = threading.Thread(target=self._loop, name="reels-hub-worker", daemon=True)
        self._thread.start()

    def stop(self, timeout: float = 30.0) -> None:
        self._runner.stopping.set()
        self._runner.kill()
        if self._thread is not None:
            self._thread.join(timeout)

    def _loop(self) -> None:
        conn: sqlite3.Connection | None = None
        prepared = False
        next_timer = 0.0
        next_due = {kind: 0.0 for kind in self._schedules}
        try:
            while not self._runner.stopping.is_set():
                if not self._ready():
                    self._runner.stopping.wait(self._poll_seconds)
                    continue
                if not prepared:
                    try:
                        self._prepare()
                    except Exception:
                        logger.exception("preparing the database failed; retrying")
                        self._runner.stopping.wait(self._poll_seconds)
                        continue
                    prepared = True
                if conn is None:
                    conn = connect(self.db_path)
                    requeue_running(conn, self._clock())
                if time.monotonic() >= next_timer:
                    enqueue_due_backup(conn, self.backup_dir, self._clock())
                    next_timer = time.monotonic() + self._timer_seconds
                for kind, every in self._schedules.items():
                    if time.monotonic() >= next_due[kind]:
                        enqueue_if_idle(conn, kind, self._clock())
                        next_due[kind] = time.monotonic() + every
                if not self.run_once(conn):
                    self._runner.stopping.wait(self._poll_seconds)
        finally:
            if conn is not None:
                conn.close()
