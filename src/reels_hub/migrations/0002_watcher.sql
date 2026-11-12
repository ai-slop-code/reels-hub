-- Watcher (spec §5.1): the camera's recording time and the DJI low-res proxy, next to the clip.
ALTER TABLE clip ADD COLUMN recorded_at TEXT;
ALTER TABLE clip ADD COLUMN lrf_rel_path TEXT;
