# Reels Hub

Local central intelligence for Katarina's Instagram Reels: one FastAPI app (web UI, MCP server, CLI) with SQLite, in one Podman container on the owner's Mac.

- What to build: [`docs/spec/REELS_HUB_SPEC.md`](docs/spec/REELS_HUB_SPEC.md) (v0.6) and [`docs/spec/DESIGN_LANGUAGE.md`](docs/spec/DESIGN_LANGUAGE.md)
- Why: [`docs/decisions.md`](docs/decisions.md)
- In what order: [`docs/BUILD_PLAN.md`](docs/BUILD_PLAN.md)
- Rules for the developer agent: [`AGENTS.md`](AGENTS.md)
- How the repo was set up: [`docs/BOOTSTRAP.md`](docs/BOOTSTRAP.md)

## Develop

Needs [uv](https://docs.astral.sh/uv/) (Python 3.12 is picked up from `.python-version`).

```bash
git config core.hooksPath .githooks   # once per clone: refuses pushes to main (R119)
uv sync
make test                             # ruff, mypy and pytest; CI runs the same target
uv run reels-hub serve --db "$HOME/.cache/reels-hub-dev/hub.sqlite" \
  --backup-dir "$HOME/.cache/reels-hub-dev/backups"   # migrates, runs the worker; http://127.0.0.1:8787/health
```

Container tests need Podman (or Docker on CI). On the build machine set `REELS_HUB_INSECURE_TLS=1` (R125); the npm step is then skipped when the registry is blocked, and CI runs the full check:

```bash
make test-container                   # image build, in-image tests and a smoke test
```

## Push guard

`main` is protected on GitHub (R124): a pull request with a green `test` check on an up-to-date branch is required, also for admins. Every change goes through a branch and a pull request, and is merged with:

```bash
gh pr checks --watch --fail-fast && gh pr merge --squash --delete-branch
```

The committed `.githooks/pre-push` hook refuses any push to `main` (tags and other branches pass). Enable it once per clone with `git config core.hooksPath .githooks`; check with `git config core.hooksPath` (prints `.githooks`).
