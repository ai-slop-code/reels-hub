# Changelog

## Unreleased

- Repo made public; `main` is protected on GitHub (PR + green `test` check); the container image will be public, so the run machine pulls without a token (R124). No change to the daily flow.
- Repo set up: spec, design language, decision log and build plan copied in from the handoff repo; Python skeleton with `reels-hub serve` / `version` and `GET /health`; `make test`; CI on `ubuntu-24.04-arm`; pre-push hook that refuses pushes to `main`; stub `Containerfile`. No change to the daily flow yet.
