-- Phase 0 tables (spec §18). Later tables and columns come with their phase.
-- Times: integer milliseconds; timestamps: UTC ISO-8601 text; paths: relative to the media root.

CREATE TABLE project (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    folder TEXT NOT NULL,
    created_at TEXT NOT NULL
);

CREATE TABLE project_media_folder (
    project_id TEXT NOT NULL REFERENCES project (id),
    rel_path TEXT NOT NULL,
    PRIMARY KEY (project_id, rel_path)
);

CREATE TABLE shoot (
    id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL REFERENCES project (id),
    recorded_on TEXT NOT NULL,
    created_at TEXT NOT NULL,
    UNIQUE (project_id, recorded_on)
);

CREATE TABLE take (
    id TEXT PRIMARY KEY,
    shoot_id TEXT NOT NULL REFERENCES shoot (id),
    label TEXT,
    created_at TEXT NOT NULL
);

CREATE TABLE device (
    id TEXT PRIMARY KEY,
    shoot_id TEXT REFERENCES shoot (id),
    camera TEXT NOT NULL,
    clock_offset_ms INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE clip (
    id TEXT PRIMARY KEY,
    rel_path TEXT NOT NULL UNIQUE,
    size_bytes INTEGER NOT NULL,
    hash TEXT,
    origin TEXT NOT NULL DEFAULT 'own'
        CHECK (origin IN ('own', 'licensed', 'open_data', 'third_party_unlicensed')),
    availability TEXT NOT NULL DEFAULT 'online' CHECK (availability IN ('online', 'offline')),
    volume_id TEXT,
    shoot_id TEXT REFERENCES shoot (id),
    take_id TEXT REFERENCES take (id),
    device_id TEXT REFERENCES device (id),
    camera TEXT,
    duration_ms INTEGER,
    fps REAL,
    width INTEGER,
    height INTEGER,
    audio_channels INTEGER,
    color_transfer TEXT,
    start_tc TEXT,
    flags TEXT NOT NULL DEFAULT '{}',
    alt_audio_rel_path TEXT,
    proxy_rel_path TEXT,
    contact_sheet_rel_path TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE INDEX clip_shoot ON clip (shoot_id);
CREATE INDEX clip_hash ON clip (hash);

CREATE TABLE job (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    kind TEXT NOT NULL,
    params TEXT NOT NULL DEFAULT '{}',
    status TEXT NOT NULL DEFAULT 'queued'
        CHECK (status IN ('queued', 'running', 'done', 'failed')),
    progress INTEGER NOT NULL DEFAULT 0 CHECK (progress BETWEEN 0 AND 100),
    error TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE INDEX job_status ON job (status, id);

CREATE TABLE agent_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    at TEXT NOT NULL,
    agent TEXT,
    tool TEXT NOT NULL,
    args TEXT,
    result_summary TEXT,
    diff TEXT
);
