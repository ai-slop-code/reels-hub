# Changelog

## Unreleased

- Proxies: every new clip gets a 540 px H.264 proxy (keyframe every 0.5 s, timecode, all audio tracks) and a contact sheet (one frame every 2 s) under the data folder; the master is never touched. No change to the daily flow yet.
- Footage watcher: every 10 s the Hub registers new camera files once they're fully copied and readable (hash, probe, shoot day from the camera's timestamp), attaches DJI `.LRF` and `.WAV`, re-attaches moved files, flags copies as duplicates and marks missing clips offline. Only `reels-hub project add <id> --folder <rel>` is needed to start watching. Nothing runs while the media folder is missing. No change to the daily flow yet.
- Probe: ffprobe facts per clip (duration, resolution, fps, audio channels, camera, timecode, colour transfer) with the `vfr` and `hdr_log` flags; test clips are generated at test time from `make_fixtures.sh` (none committed). No change to the daily flow.
- Settings from environment variables; the Hub refuses to start unless `REELS_HUB_HOST_MEDIA_ROOT` is an absolute Mac path. The media folder marker gates migrations and the worker; `/health` reports schema, media, disk, job counts and git SHA (503 only if the DB or the marker is missing). No change to the daily flow yet.
- Background jobs: a job queue in the database and a worker that runs one job at a time inside the Hub; the daily database backup (14 copies kept, plus every pre-migration copy) runs by itself. No change to the daily flow yet.
- Database: numbered forward-only migrations with a backup before each pending migration (`reels-hub migrate`); first schema covers projects, shoots, takes, devices, clips, the job queue and the agent log. No change to the daily flow yet.
- Release workflow: every merge to `main` builds the linux/arm64 image and pushes `ghcr.io/ai-slop-code/reels-hub` (commit SHA and `latest`); a `v*` tag pushes that version too. No change to the daily flow yet.
- Container image: multi-stage `Containerfile` (HyperFrames 0.9.39 in a node stage, arm64 runtime with ffmpeg and Debian Chromium, test stage); `make test-container` builds it, runs the in-image tests and a smoke test of `/health` in an isolated container; CI runs it. No change to the daily flow.
- Local image builds on the build machine can turn off TLS verification (`REELS_HUB_INSECURE_TLS=1`, never in CI or the image); HyperFrames is pinned to 0.9.39 (R125, R126). No change to the daily flow.
- Repo made public; `main` is protected on GitHub (PR + green `test` check); the container image will be public, so the run machine pulls without a token (R124). No change to the daily flow.
- Repo set up: spec, design language, decision log and build plan copied in from the handoff repo; Python skeleton with `reels-hub serve` / `version` and `GET /health`; `make test`; CI on `ubuntu-24.04-arm`; pre-push hook that refuses pushes to `main`; stub `Containerfile`. No change to the daily flow yet.
