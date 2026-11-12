import datetime as dt
import sys
import time
from collections.abc import Callable
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from reels_hub.app import create_app
from reels_hub.backup import daily_name, prune_daily
from reels_hub.config import Settings
from reels_hub.db import connect, migrate
from reels_hub.jobs import (
    BACKUP_KIND,
    JobContext,
    Worker,
    claim_next,
    enqueue,
    enqueue_due_backup,
    get_job,
    job_counts,
    requeue_running,
)

T0 = dt.datetime(2026, 11, 12, 18, 0, tzinfo=dt.UTC)


class FixedClock:
    def __init__(self, now: dt.datetime) -> None:
        self.now = now

    def __call__(self) -> dt.datetime:
        return self.now


def wait_for(predicate: Callable[[], bool], timeout: float = 10.0) -> None:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if predicate():
            return
        time.sleep(0.02)
    raise AssertionError("timed out waiting for the worker")


@pytest.fixture
def db_path(tmp_path: Path) -> Path:
    path = tmp_path / "hub.sqlite"
    migrate(path, tmp_path / "backups", now=lambda: T0)
    return path


@pytest.fixture
def backups(tmp_path: Path) -> Path:
    return tmp_path / "backups"


def status_of(db_path: Path, job_id: int) -> str:
    conn = connect(db_path)
    try:
        job = get_job(conn, job_id)
    finally:
        conn.close()
    assert job is not None
    return job.status


def test_jobs_are_claimed_in_queue_order(db_path: Path, backups: Path) -> None:
    ran: list[str] = []
    handlers = {kind: (lambda ctx, k=kind: ran.append(k)) for kind in ("a", "b", "c")}
    worker = Worker(db_path, backups, handlers=handlers, clock=FixedClock(T0))
    conn = connect(db_path)
    try:
        for kind in ("a", "b", "c"):
            enqueue(conn, kind, T0)
        while worker.run_once(conn):
            pass
    finally:
        conn.close()
    assert ran == ["a", "b", "c"]


def test_a_failing_job_is_recorded_with_its_error(db_path: Path, backups: Path) -> None:
    def boom(ctx: JobContext) -> None:
        raise ValueError("disk full")

    worker = Worker(db_path, backups, handlers={"boom": boom}, clock=FixedClock(T0))
    conn = connect(db_path)
    try:
        job_id = enqueue(conn, "boom", T0)
        worker.run_once(conn)
        job = get_job(conn, job_id)
    finally:
        conn.close()
    assert job is not None
    assert (job.status, job.error) == ("failed", "disk full")


def test_a_job_without_a_handler_fails(db_path: Path, backups: Path) -> None:
    worker = Worker(db_path, backups, clock=FixedClock(T0))
    conn = connect(db_path)
    try:
        job_id = enqueue(conn, "unknown", T0)
        worker.run_once(conn)
        job = get_job(conn, job_id)
    finally:
        conn.close()
    assert job is not None
    assert job.status == "failed"
    assert "no handler" in str(job.error)


def test_progress_is_kept_and_a_finished_job_reads_100(db_path: Path, backups: Path) -> None:
    def halfway(ctx: JobContext) -> None:
        ctx.progress(40)

    worker = Worker(db_path, backups, handlers={"half": halfway}, clock=FixedClock(T0))
    conn = connect(db_path)
    try:
        job_id = enqueue(conn, "half", T0)
        worker.run_once(conn)
        job = get_job(conn, job_id)
    finally:
        conn.close()
    assert job is not None
    assert (job.status, job.progress) == ("done", 100)


def test_running_jobs_are_requeued_on_start(db_path: Path) -> None:
    conn = connect(db_path)
    try:
        enqueue(conn, "crashed", T0)
        assert claim_next(conn, T0) is not None
        assert requeue_running(conn, T0) == 1
        assert job_counts(conn)["queued"] == 1
        assert job_counts(conn)["running"] == 0
    finally:
        conn.close()


def test_daily_backup_is_queued_only_when_the_last_one_is_a_day_old(
    db_path: Path, backups: Path
) -> None:
    conn = connect(db_path)
    try:
        assert enqueue_due_backup(conn, backups, T0) is not None
        assert enqueue_due_backup(conn, backups, T0) is None  # already queued
        worker = Worker(db_path, backups, clock=FixedClock(T0))
        worker.run_once(conn)
        assert (backups / daily_name(T0)).exists()
        assert enqueue_due_backup(conn, backups, T0 + dt.timedelta(hours=1)) is None
        assert enqueue_due_backup(conn, backups, T0 + dt.timedelta(hours=25)) is not None
    finally:
        conn.close()


def test_daily_backup_keeps_fourteen_daily_copies_and_all_pre_migration_copies(
    db_path: Path, backups: Path
) -> None:
    backups.mkdir(parents=True)
    for day in range(1, 17):
        stamp = dt.datetime(2026, 10, day, 18, 0, tzinfo=dt.UTC)
        (backups / daily_name(stamp)).write_bytes(b"old")
    (backups / "pre-migrate-1-2-20261001-1800.sqlite").write_bytes(b"pre")
    (backups / "pre-update-20261002-1800.sqlite").write_bytes(b"pre")
    conn = connect(db_path)
    try:
        enqueue(conn, BACKUP_KIND, T0)
    finally:
        conn.close()
    Worker(db_path, backups, clock=FixedClock(T0)).run_once(connect(db_path))

    names = sorted(path.name for path in backups.iterdir())
    daily = [name for name in names if name.startswith("hub-")]
    assert len(daily) == 14
    assert daily[-1] == daily_name(T0)
    assert "pre-migrate-1-2-20261001-1800.sqlite" in names
    assert "pre-update-20261002-1800.sqlite" in names


def test_prune_leaves_fewer_than_keep_untouched(backups: Path) -> None:
    backups.mkdir()
    (backups / daily_name(T0)).write_bytes(b"x")
    assert prune_daily(backups, keep=14) == []


def test_worker_thread_runs_queued_jobs(db_path: Path, backups: Path) -> None:
    done: list[str] = []
    worker = Worker(
        db_path,
        backups,
        handlers={"note": lambda ctx: done.append("note")},
        clock=FixedClock(T0),
        poll_seconds=0.02,
    )
    conn = connect(db_path)
    try:
        enqueue(conn, "note", T0)
        enqueue(conn, "note", T0)
        worker.start()
        wait_for(lambda: len(done) == 2)
    finally:
        worker.stop()
        conn.close()
    assert not worker.running


def test_stopping_kills_the_running_subprocess_and_requeues_the_job(
    db_path: Path, backups: Path
) -> None:
    backups.mkdir()
    (backups / daily_name(T0)).write_bytes(b"recent")

    def slow(ctx: JobContext) -> None:
        ctx.run([sys.executable, "-c", "import time; time.sleep(60)"])

    worker = Worker(
        db_path, backups, handlers={"slow": slow}, clock=FixedClock(T0), poll_seconds=0.02
    )
    conn = connect(db_path)
    try:
        job_id = enqueue(conn, "slow", T0)
        worker.start()
        wait_for(lambda: status_of(db_path, job_id) == "running")
        started = time.monotonic()
        worker.stop(timeout=20)
        assert time.monotonic() - started < 15
    finally:
        conn.close()
    assert status_of(db_path, job_id) == "queued"


def test_app_lifespan_starts_and_stops_the_worker(
    db_path: Path, backups: Path, settings: Settings
) -> None:
    migrate(settings.db_path, settings.backup_dir)
    worker = Worker(db_path, backups, clock=FixedClock(T0), poll_seconds=0.02)
    with TestClient(create_app(settings=settings, worker=worker)) as client:
        assert worker.running
        assert client.get("/health").status_code == 200
    assert not worker.running


def test_the_worker_waits_for_the_media_folder_then_prepares_and_schedules_scans(
    db_path: Path, backups: Path
) -> None:
    ready = {"mounted": False}
    prepared: list[str] = []
    scans: list[str] = []
    worker = Worker(
        db_path,
        backups,
        handlers={"scan": lambda ctx: scans.append("scan")},
        clock=FixedClock(T0),
        poll_seconds=0.02,
        ready=lambda: ready["mounted"],
        prepare=lambda: prepared.append("migrated"),
        schedules={"scan": 0.05},
    )
    worker.start()
    time.sleep(0.2)
    assert prepared == []
    assert scans == []
    ready["mounted"] = True
    wait_for(lambda: len(scans) >= 2)
    worker.stop()
    assert prepared == ["migrated"]
