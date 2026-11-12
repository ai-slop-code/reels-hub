# Reels Hub: instructions for the developer agent

You build **Reels Hub**: a local-first app (one FastAPI process with a web UI, an MCP server and a CLI, plus SQLite, in one Podman container) that holds everything about Katarina's Instagram Reels: footage, moments, transcripts, facts, glossary, design rules, graphics, versions, approvals and metrics. Ľuboš (the owner, "the producer") is its only user. His own Claude session edits each reel through the Hub's MCP and the Edits MCP. The Hub never drives Edits itself (spec §4, §23.1).

**Per-reel flow (spec §19.0):** create reel → shoot (no planning in the Hub) → add footage → automatic analysis → reel prompt → the owner's Claude session edits (Hub MCP + Edits MCP) and writes `editors_notes.md` → approval in the Hub → manual post → metrics → next prompt.

**Principle: simple over robust (spec §2, principle 11).** One user, one machine. Build the light version each phase asks for. No extra queues, hooks, hashes, toolsets or services unless the spec names them.

## Dates (today is 2026-11-12)
- Build order (spec §25.1): **0 → 1 → 2 → 3 → 9 → 4 → 5 → 7 → 8 → 6**. Phase 10 (critique) only after December.
- Restore rehearsal on the run machine **before 27 Nov**. Dress rehearsal **27 Nov**. Go/no-go **28 Nov** (needs phases 0–4 and 9). Series starts **1 Dec**.
- Target dates per phase, and what to cut first if late: `docs/BUILD_PLAN.md` → "Calendar".

## Start of every session: read in this order
1. This file.
2. `docs/BUILD_PLAN.md`: find the first unchecked item (`- [ ]`) in the current phase. Check its "depends on" and any `Q:` or 🔑 marks.
3. Only the spec sections that item cites: `docs/spec/REELS_HUB_SPEC.md` (v0.6) and, for anything visual, captions or sound, `docs/spec/DESIGN_LANGUAGE.md` (v1.2).
4. `docs/decisions.md` only when you need the reason behind a rule (D1–D10, R1–R123, later entries).
5. Background only, when a detail is missing: `docs/reviews/` (expert packets), `docs/reference/giro00/` (the reference reel).

Run `git status` and `gh pr list` first: an earlier session may have left an open PR or a half-done branch. Finish that before starting anything new.

## Source of truth and spec changes
- `docs/spec/` and `docs/decisions.md` are the only source of truth. The old handoff repo is a frozen archive; don't use it.
- D1–D10 and the owner's decisions R1–R123 (R119–R123: bootstrap answers) are **settled. Don't reopen them.** Entries marked `deferred` stay out of scope unless the owner brings them back.
- **Don't silently change behavior described in the spec.**
  - Typos, broken links and clarifications that don't change behavior: fix them in the same PR.
  - Behavior changes: stop and ask the owner. If approved, in the same PR: update the spec, add a decision-log entry to `docs/decisions.md` (next number after the last one, starting at R124; "From: dev"; date; reason) and add a line to the spec's §28 changelog under a new "v0.6.x (dev)" heading.
- Where the spec is silent on an implementation detail (file layout, function names, internal APIs), choose the simplest option and note it in the PR body. That is not a behavior change.

## Work loop (one branch per item)
Every item in `docs/BUILD_PLAN.md` is one branch. Never commit or push to `main` (spec §24.1, D10). GitHub doesn't protect `main` (GitHub Free, R119); the committed `.githooks/pre-push` hook refuses pushes to it, so check once per clone that `git config core.hooksPath` prints `.githooks`.
```bash
git switch main && git pull --ff-only
git switch -c feature/<name>          # or fix/<name>, chore/<name>; use the name from BUILD_PLAN
```
```bash
uv sync                               # after changing pyproject.toml, commit uv.lock too
uv run ruff check . && uv run ruff format --check . && uv run mypy src
make test                             # the full suite (spec §24.2); CI runs the same target
make test-container                   # image build + tests inside the image + isolated smoke test;
                                      # run locally when you touch the image, ingest, graphics or deploy (CI always runs it)
```
1. Build the item. Add tests for the new behavior (see "Testing").
2. Tick the item in `docs/BUILD_PLAN.md` (`- [x]`) and add a line to `CHANGELOG.md` under "Unreleased", in the same branch.
3. Rebase on the latest `main`, re-run `make test`, push:
   ```bash
   git fetch origin && git rebase origin/main && make test
   git push -u origin HEAD              # after a rebase of an already pushed branch: --force-with-lease
   ```
4. Open the PR, wait for CI, merge only when green, always with the chained command (the merge runs only if the checks pass; never `gh pr merge` alone, never `--admin`, R119):
   ```bash
   gh pr create --base main --title "feat: <what>" --body-file "$TMPDIR/pr-body.md"
   gh pr checks --watch --fail-fast && gh pr merge --squash --delete-branch
   git switch main && git pull --ff-only
   ```
5. If CI is red: fix on the same branch and push again. Never merge red, and never merge while checks are pending or missing. Never disable, skip or loosen a test to get green; if a test is wrong, say so in the PR body.
6. **Migrations:** numbered SQL files, forward-only (spec §21, §23.6). After a rebase, if `main` already has your migration number, renumber yours to the next free number. Never edit a migration that is already on `main`; add a new one.
7. **If `main` goes red** (spec §24.1, rule 6): stop feature work, fix it on a `fix/` branch first. Nothing else merges until `main` is green.
8. One item per branch. If an item turns out too big, split it in `docs/BUILD_PLAN.md` (in the PR) and say so.

**PR titles:** `feat: …`, `fix: …`, `chore: …`, `docs: …`, `test: …`. **PR body:** What · Why (BUILD_PLAN item) · Spec refs (`spec §n`, `R##`) · Tests added · How verified · Screenshots for UI changes (Playwright screenshot attached to the PR, never committed; R120) · Deviations / choices made where the spec is silent.

**CHANGELOG.md (spec §24.3):** one line per PR under "Unreleased", in plain words, with the daily-flow impact if any. At an owner-approved release, move the lines under `## vX.Y.Z (date)` and tag `main` (`git tag vX.Y.Z && git push origin vX.Y.Z`); CI then pushes the version image (spec §23.6).

## When to stop and ask the owner
Stop, explain briefly, propose options with your recommendation, and wait, when:
- the spec doesn't cover a decision that changes behavior, or contradicts itself (open questions are listed as `Q1`, `Q2`, … in `docs/BUILD_PLAN.md`; don't answer them yourself);
- you need a **dependency not named in the spec or in the list below**;
- something needs the owner: accounts, tokens, real footage, the run machine, money, a GitHub setting;
- a "done when" check can't be met, or can only be checked on the run machine;
- you would have to touch anything listed under "Machine safety".

Before stopping, finish and merge the current branch if it is complete and green. If the owner already supplied an input (see the "Owner inputs" table in `docs/BUILD_PLAN.md`), don't ask again. If an item's code can be finished, tested with fakes and merged, and only its real-world check needs the owner (e.g. running the ASR benchmark on the run machine), merge it, keep the owner action for the phase report and continue.

**At the end of every phase**, stop and report, then wait for a go-ahead:
```markdown
## Phase <n> report: <name>
**Done when (spec §25):** <the line> → met / not met / needs the run machine
- How checked: <tests, commands, numbers>. For run-machine checks: exact commands for the owner.
**Built:** <merged PRs, one line each>
**Deviations from the spec or plan:** <none | list with reasons>
**Open questions / owner actions:** <numbered list>
**Next:** phase <m>, first item <branch>. Suggested release tag: vX.Y.Z
```

## Tech conventions (from the spec; don't add others)
| Topic | Rule | Spec |
|---|---|---|
| Runtime | Python **3.12** via **uv**; package `reels_hub` in `src/` layout; CLI `reels-hub`; MCP server name `reels-hub` | §21, §24 |
| Web | **FastAPI**; UI server-rendered **Jinja2 + HTMX**, no JS build step; UI labels in English | §20, §21 |
| Process | One FastAPI app serves UI, REST and MCP; a **worker loop in the same container** runs jobs one heavy job at a time; heavy work never inside a web request; no job-pool processes | §4, R12 |
| MCP | **MCP Python SDK**, streamable HTTP only, at `http://127.0.0.1:8787/mcp`; token required; `verb_noun` tool names exactly as in §17.2; one tool list; `limit` (default 20) + `offset`; long tools return `job_id`; errors say what to do next | §17, §22 |
| DB | **SQLite + FTS5** (`unicode61 remove_diacritics 2`); numbered, forward-only SQL migrations; DB backup (`VACUUM INTO` + `integrity_check`) before migrating | §18, §21, §23.6 |
| Jobs | Simple `job` table (status, progress, error); `running` jobs re-queued on start; periodic work enqueued by a timer with catch-up | §21, §23.4 |
| Data | Media times in **integer milliseconds**; timestamps UTC ISO-8601; paths **relative to the media root** (or `/data`); short readable IDs/slugs; no absolute paths in the DB | §18 |
| Paths | One absolute host media root `REELS_HUB_HOST_MEDIA_ROOT` (refuse to start if not absolute); container `/media`, data `/data`; media marker `/media/.reels-hub-root` | §23.2 |
| Media | ffmpeg/ffprobe; OpenCV (`opencv-python-headless`) + PySceneDetect; outputs written to a temp name, then renamed | §5.1, §5.1b |
| ASR | WhisperX on faster-whisper (CPU, int8), forced `sk`; model chosen by benchmark; weights in `/data/models` with pinned revisions; audio decoded with ffmpeg and passed in memory (no torchcodec) | §5.1a, §23.4 |
| LLM | Anthropic API from the container, key as Podman secret `anthropic_key`, dated model ID in config (never an alias) | §21 |
| Graphics | Python SVG templates → PNG with resvg (OFL fonts only in the container); HyperFrames (Node 22) as a **CLI subprocess**, pinned in `package-lock.json`, never `npx` at runtime | §10, §10.1, §21 |
| Image | One multi-stage `Containerfile`, **`linux/arm64`** only; stages `node`, `runtime`, `test`; health check in the run command, not the Containerfile | §23.6 |
| CI | GitHub Actions on **`ubuntu-24.04-arm`** (native, R121), QEMU only as a fallback; job `test` on PRs; release build on `main` and `v*` tags | §23.6, §24.1 |
| Deploy | `deploy/deploy.sh <tag>` holds the **only** `podman run` command | §23.3, §23.6 |
| Quality | ruff, mypy, pytest, Playwright; one command `make test` (or `reels-hub test`) | §24.2 |

**Dependencies.** Allowed: what the spec names (D7: HyperFrames, faster-whisper / WhisperX / pyannote, OpenCV, Edits MCP; plus §21: FastAPI, Jinja2, HTMX, MCP SDK, PySceneDetect, librosa, Demucs, resvg, torch CPU, anthropic) and this list, which the owner approved at bootstrap because the spec implies it: `uvicorn`, `python-multipart`, `pyyaml`, `xxhash`, `httpx`, `numpy`, `scipy`, `pydantic` (with FastAPI), `pytest-playwright`, `types-*` stubs; in CI the official `actions/*` actions, `astral-sh/setup-uv` and, only for the QEMU fallback, `docker/setup-qemu-action` (R122). CI and the release build run on `ubuntu-24.04-arm` (R121). The CLI uses `argparse` (stdlib). Anything else, including a pytest plugin: **ask first**.

## Testing (spec §24.2)
- Every PR runs the full suite in CI (job `test`, on `ubuntu-24.04-arm`); a PR merges only when it's green (chained merge command, R119).
- **Fakes by default:** `TRANSCRIBE_BACKEND=fake` and a fake LLM. A real engine runs only in a test marked `real` (skipped in CI) on a small fixture.
- **Never** real footage, real accounts or real tokens in tests. External APIs (Instagram, Anthropic, MusicBrainz, GetSongBPM, fact pages) are mocked.
- **Fixtures: no pictures, just the code (R120).** No footage, photos or images in the repo, and no Git LFS. Test clips are generated at test time by `tests/fixtures/make_fixtures.sh` (ffmpeg lavfi test patterns and tones, metadata mimicking Sony and DJI) into an ignored folder; test images and reference frames are generated too (synthetic SVG/PNG). Only the scripts and small text files (JSON, YAML) are committed. Real snippets live only in `tests/fixtures/local/` (git-ignored); tests that need them `skip` when absent.
- Golden tests (reel prompt) use a fixed clock and fixed IDs; update a golden file only on purpose and say so in the PR.
- **Container tests are isolated** (spec §24.2): unique container name (`reels-hub-test-<random>`), random host port (`-p 127.0.0.1::8787`), a throwaway volume, a temp media folder under `$HOME/.cache/reels-hub-test/`, all removed by a `trap … EXIT`. Never use the names `reels-hub` or `reels-hub-data`.

## Machine safety (build machine)
The build machine is a **shared developer Mac**. Its Podman machine also runs unrelated containers (e.g. `ferl-stage01-postgres`, `ferl-stage01-postgres18`, Atlassian MCP containers).
- Never stop, remove, prune or modify containers, volumes, images, networks or secrets you didn't create in the current test run. Clean up only by exact name or tag.
- Never run `podman system prune`, `podman image prune`, `podman volume prune`, `podman container prune`, or `podman machine stop|rm|reset|set|init`. If the Podman machine is down or too small, ask.
- Never read, write or list `~/Movies`, `~/Pictures` or any real media on the build machine. Temp files go under `$HOME/.cache/reels-hub-test/` or the repo's ignored folders.
- Don't install system software (Homebrew, global npm or pip). Project dependencies go through `uv` and `npm ci` inside the repo only.
- **The run machine is never touched by you.** The owner runs `deploy/deploy.sh` and the commands you give him.
- GitHub: push only your own branches. Never push to or force-push `main`, never bypass or disable the pre-push hook (`--no-verify`), never change repo settings, never delete tags or packages, never create other repos. Never commit secrets; `.env` and tokens stay out of Git.

## Product rules the code must respect
- **No MCP tool can approve a version.** Approval only in the Hub UI; a newer version invalidates older approvals. `export_allowed(version)` returns false until the exact version is approved (§11.3, §17.3, R1, R2).
- **Exclusions:** ranges excluded by a person (`excluded_by: katarina | luboš`) and `third_party_unlicensed` media are **never returned to agents**; agents can't lift them; agent exclusions are stored as `agent_proposed` (§5.3, §17.3, R3, R48).
- **Captions and speech:** Slovak, only from real words; no frankenbites; proposed lines only under "Suggested pickups (not recorded)" in `editors_notes.md`, never as transcript, caption or on-screen speech. Correction memory never rewrites raw transcript words (§6.4, §8, R4, R5, R92).
- **No synthetic host:** no TTS, cloning, lip-sync or likeness of Katarina or Ľuboš; voice prints only for speaker labels, never exported (§22, R10).
- **Music:** tier-1 (Edits) audio is never captured, stored or analyzed; `analyze_track` refuses tier 1; no yt-dlp; no iTunes/Deezer preview downloads; only levels are stored (§15.2, §22, R41, R44).
- **Instagram:** official API with Instagram Login only; comments are **not imported**; posting stays manual, no `publish_*` tools (§12.1, R28, R49).
- **Max 5 hashtags** per post; `lint_script(kind: caption)` counts them (§8.1).
- **Critique** (phase 10) runs only when the producer triggers it; nothing starts it automatically (§16.5, R55).
- **Never render or export a reel** without the producer's approval of that exact version. Graphics renders for an edit are fine; reel exports are not.
- Secrets only as Podman secrets; never in the image, the DB or logs (§22). Ports on `127.0.0.1` only.
- Everything on screen, in captions or in a suggested pickup is Slovak with correct diacritics and glossary forms (§20, R8).
