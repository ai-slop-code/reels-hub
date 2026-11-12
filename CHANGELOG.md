# Changelog

## Unreleased

- Container image: multi-stage `Containerfile` (HyperFrames 0.9.39 in a node stage, arm64 runtime with ffmpeg and Debian Chromium, test stage); `make test-container` builds it, runs the in-image tests and a smoke test of `/health` in an isolated container; CI runs it. No change to the daily flow.
- Local image builds on the build machine can turn off TLS verification (`REELS_HUB_INSECURE_TLS=1`, never in CI or the image); HyperFrames is pinned to 0.9.39 (R125, R126). No change to the daily flow.
- Repo made public; `main` is protected on GitHub (PR + green `test` check); the container image will be public, so the run machine pulls without a token (R124). No change to the daily flow.
- Repo set up: spec, design language, decision log and build plan copied in from the handoff repo; Python skeleton with `reels-hub serve` / `version` and `GET /health`; `make test`; CI on `ubuntu-24.04-arm`; pre-push hook that refuses pushes to `main`; stub `Containerfile`. No change to the daily flow yet.
