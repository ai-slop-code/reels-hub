# Reels Hub build plan

The ordered plan for building Reels Hub from spec v0.6 (`docs/spec/REELS_HUB_SPEC.md`). Work top to bottom: one item = one branch = one pull request (see `AGENTS.md` → "Work loop"). Tick an item (`- [x]`) in the same PR that completes it.

**Legend**
- `- [ ] feature/…`: a branch to build, in order. **Scope · Spec · Depends on · Tests · Verify** describe it.
- 🔑 **OWNER:** needs something only the owner can give or do (account, token, footage, run machine, decision).
- ⛔ **STOP:** stop, report (template in `AGENTS.md`) and wait for the owner's go-ahead.
- **Q#:** an open question for the owner (table below). Don't answer it yourself; use the suggested default only after the owner has confirmed it in `docs/decisions.md`.
- *(if time allows)*: the spec marks it optional for December; first to cut.

---

## Calendar (tight)

Today is 2026-11-12. All phases except 10 should work in a light version by **1 Dec** (spec §25.1). That is about 16 working days for 54 branches, with an owner review at every phase end. **The plan is tight.** Phases needed for the **go/no-go on 28 Nov** are **0–4 and 9**; everything else may slip into December without blocking a post (spec §2, principle 10).

| Phase | Target dates | Owner work at the end of the phase |
|---|---|---|
| 0 · Foundations | 13–15 Nov | Set up the run machine, first deploy, timing and Edits checks (16 Nov) |
| 1 · Transcripts and moments | 16–18 Nov | ASR reference transcript and benchmark run (Q3, R81) |
| 2 · MCP v1 | 19 Nov | Connect Claude Code on the run machine; fresh-agent check |
| 3 · Facts and glossary | 20–21 Nov | Stage table data (Q12), Katarina's dialect words |
| 9 · Projects, reel prompt and notes | 22–24 Nov | `giro2027-advent` project values; Stage 1 footage shot |
| 4 · Reviews and approvals | 25 Nov | Anthropic key; deploy for the rehearsal |
| Restore rehearsal | **by 26 Nov** | Restore the DB once on the run machine (spec §23.6) |
| Dress rehearsal | **27 Nov** | Stage 1 reel end to end (spec §25.1) |
| Go/no-go | **28 Nov** | Phases 0–4 and 9 "done when" pass? |
| 5 · Analytics v1 | 28–29 Nov | Meta app and token; the manual 24 h form must be **live before 2 Dec 19:00** (24 h after the first post) |
| 7 · Graphics and motion | 29–30 Nov | Edits alpha-video import test |
| 8 · Music | 30 Nov | GetSongBPM key if used |
| 6 · Learning loop | 30 Nov–1 Dec (then ongoing) | – |
| 10 · AI critique | after December | Not planned here |

From 1 Dec, deploy to the run machine only when 2 approved reels are in the buffer (spec §24.5).

**If behind, cut in this order** (propose it in the phase report; the owner decides):
1. *(if time allows)* items: speaker labels (1.8) and audio auto-sync (1.9). A manual clock offset is enough for December (spec §5.2).
2. Phase 6 moves after 1 Dec (it's "ongoing" in spec §25).
3. Phase 8: keep only license records and the Dolce Vita seed (8.1); music is picked in Edits by hand as for Giro_00.
4. Phase 7: keep the asset registry and graphics overview (7.1, 7.2); container map templates and HyperFrames later (`tools/mkmap.py` on the Mac still works).
5. Phase 5: keep publication + the manual 24 h form (5.1); the API importer later.
6. Polish inside phases: version diff (4.4), calendar grid (9.7), `lint_draft` (4.5).

**Never cut:** any "done when" check of phases 0–4 and 9, DB backup and restore, approval and `export_allowed`, exclusion rules.

---

## Owner inputs (owner fills in "Status")

| # | Input | Needed by | Status |
|---|---|---|---|
| I1 | GitHub: `gh` logged in as LubosBa (scopes `repo`, `workflow`); GitHub Free; repo public with `main` protected (R124) | Bootstrap | |
| I2 | Repo `ai-slop-code/reels-hub` created (public since R124), merge settings and Actions permissions done (`docs/BOOTSTRAP.md`) | Bootstrap | |
| I3 | Answers to Q1, Q4, Q15 and the GitHub plan | Bootstrap | Done 2026-11-12 (R119–R123) |
| I4 | Run machine: Podman 6 version and free disk confirmed; setup per `docs/RUNBOOK.md` (spec §23.3) | End of phase 0 | |
| I5 | ~~Read-only GHCR token on the run machine~~ not needed: the image is public (R124) | End of phase 0 | Not needed (R124) |
| I6 | Podman secrets `meta_token`, `anthropic_key`, `hf_token` on the run machine; placeholders are fine until the real values exist (the run command needs all three) | End of phase 0 | |
| I7 | Giro_00 masters hard-linked into `~/Movies/ReelsHub/giro00/raw/{sony,dji}` (spec §23.2, R67); Giro_00 graphics copied from the handoff archive (`reels/giro00-intro/graphics/`) into `~/Movies/ReelsHub/giro00/graphics/` (R120) | End of phase 0 | |
| I8 | Phase 0 timing (≤ 30 min for a Giro_00-sized drop), Edits host-path import, **Edits 25p check** (which project rates, how 25p conforms; spec §14, R70) | End of phase 0 | |
| I9 | ASR reference transcript: ~5 min of C0031 + one DJI excerpt, corrected by ear (~1 h), saved in `/data/bench/` on the run machine, never in Git (spec §5.1a, R81); then run the benchmark | Phase 1 | |
| I10 | Hugging Face token (pyannote is gated) and voice-print ranges for Katarina and Ľuboš | Phase 1, item 1.8 | |
| I11 | Claude Code on the run machine connected to the Hub MCP; Edits MCP connected | Phase 2 end | |
| I12 | Stage table data for the 21 stages (Q12) | Phase 3 | |
| I13 | Katarina's dialect words for `keep_as_said` (spec §8, R100) | Phase 3 | |
| I14 | `giro2027-advent` values: `posting_time` from in-app "Most active times", brief, slots (spec §6.1) | Phase 9 | |
| I15 | Stage 1 footage shot and copied to the run machine | Before 27 Nov | |
| I16 | Real Anthropic API key (Podman secret) and the pinned model ID (Q14) | Phase 4 | |
| I17 | Restore rehearsal done on the run machine | Before 27 Nov | |
| I18 | Meta developer app (Instagram Login, Development mode, Katarina's account given a role), Professional/Creator account confirmed, long-lived token | Phase 5 | |
| I19 | Edits import test of the HyperFrames MP4 and alpha MOV in a copy of `Giro_00_Intro` | Phase 7 | |
| I20 | GetSongBPM API key (only if used) | Phase 8 | |

## Open questions (answers go into `docs/decisions.md`)

| # | Question | Needed by | Suggested default |
|---|---|---|---|
| Q1 | Real footage snippets (Katarina's face and voice) in the private GitHub repo? | Bootstrap | **Answered (R120):** no pictures, just the code. Clips and images generated by scripts at test time, not committed; real snippets only in git-ignored `tests/fixtures/local/`; no Git LFS; Giro_00 graphics not copied |
| Q2 | Giro_00 transcript text in golden tests: only the lines already quoted in the docs, the full C0031 transcript, or none? | Phase 1 | Only lines already quoted in `docs/`, plus synthetic filler |
| Q3 | For the optional real-engine test: synthetic Slovak speech made with macOS `say` (a stock voice, not Katarina's or Ľuboš's)? | Phase 1 | Yes, generated at test time with `say` (not committed, R120) |
| Q4 | Which runner for CI and the arm64 release build? | Bootstrap | **Answered (R121):** `ubuntu-24.04-arm` works for the repo; QEMU only as a fallback if it ever fails |
| Q5 | Spec §23.6 names `reels-hub restore <file>`, but the run machine has no Python or repo (§23.0). Make it `deploy.sh restore <file>`? | Phase 0 | Yes, `deploy.sh restore <file>` |
| Q6 | How is the MCP token (spec §22, §23.3 "token header") created and stored? The run command has no secret for it | Phase 2 | Hub generates it on first start into `/data/mcp_token` (mode 600); `podman exec reels-hub reels-hub mcp-token` prints it |
| Q7 | What sets the statuses `exported` and `analyzed` (spec §6.2)? No tool or step names them | Phase 4/5 | `exported`: a "Mark exported" button, or implicitly on `link_publication`; `analyzed`: when the 7 d snapshot exists |
| Q8 | `lint_draft(edits_project_id \| frame_sheet)` and `check_mix(edits_project_id)`: the Hub can't read Edits. What do they take? The prompt (§6.4) calls `lint_draft` | Phase 4/8 | `lint_draft` runs the R76 light checks on the version's cut list; `check_mix` stores the levels the agent reports |
| Q9 | Reel-card baseline: spec §12.3/§12.4 say the account's trailing 30-day median; R107 (light step) says the project's previous 5 reels | Phase 5 | Previous 5 reels of the project |
| Q10 | The refreshed Instagram long-lived token must be stored somewhere; Podman secrets are read-only inside the container and §22 forbids secrets in the DB | Phase 5 | A file in `/data/secrets/` (mode 600), seeded from the `meta_token` secret |
| Q11 | Container-rendered maps can't use Avenir Next (DESIGN_LANGUAGE §3). Which OFL font for map labels? And may the Hub download Natural Earth v5.1.2 (~25 MB) into `/data/geo` (pinned URL + checksum)? | Phase 7 | Noto Sans (from `fonts-noto-core`); yes to the download |
| Q12 | Who provides the 21-stage table? giroditalia.it blocks automated fetches (spec §7.2) | Phase 3 | Owner pastes or approves a CSV the agent drafts from the docs; agent never scrapes |
| Q13 | Fact conflict detection (spec §7.2): automatic or manual? | Phase 3 | Manual: the producer or an agent sets `conflicting`; the "Needs attention" queue lists them |
| Q14 | Which dated Claude model ID is pinned for Hub-side LLM calls (spec §21)? | Phase 4 | Owner picks |
| Q15 | Is the pre-approved dependency list in `AGENTS.md` OK? | Bootstrap | **Answered (R122):** yes, approved |

---

## Phase 0 · Foundations
**Goal:** `podman run` gives a working Hub on the run machine; footage registered and Edits-ready.
**Spec:** §4, §5.1, §18, §21, §23, §24, §25 (R12–R14, R18, R58–R65).
**Done when (spec §25):** A Giro_00-sized drop is registered with proxies in ≤ 30 min (measured on the run machine, §23.0), and a host path imports in Edits without copying.

- [x] **0.1 `chore/bootstrap`**
  - Scope: copy the docs per `docs/BOOTSTRAP.md` and fix relative links; `AGENTS.md`, `CLAUDE.md`, `README.md`, `CHANGELOG.md`; `pyproject.toml` (uv, Python 3.12, package `reels_hub` in `src/`, ruff, mypy, pytest config); `Makefile` (`test`, `lint`, `test-container` stub); CLI `reels-hub` (`serve`, `version`); FastAPI app with a minimal `GET /health`; `.gitignore` (`.venv`, `.env`, `tests/fixtures/local/`, generated fixtures, `node_modules/`, `dist/`); `.githooks/pre-push` that refuses any push to `refs/heads/main` (tags allowed), enabled with `git config core.hooksPath .githooks` and documented in `README.md` (R119); `.github/workflows/ci.yml` with one job named **`test`** on `pull_request`, `runs-on: ubuntu-24.04-arm` (R121); `.github/pull_request_template.md`; a stub `Containerfile` that runs the app. No images or other binaries (R120).
  - Spec: §21, §24, §24.4. Depends on: owner bootstrap steps (I1–I3).
  - Tests: `/health` returns 200; `tests/test_docs_links.py` checks that every relative Markdown link in the repo resolves (code spans and fenced blocks ignored); CLI `version`; the pre-push hook rejects a `main` ref and allows others.
  - Verify: CI job `test` runs on `ubuntu-24.04-arm` and is green; merge with `gh pr checks --watch --fail-fast && gh pr merge --squash --delete-branch`.
- [ ] **0.2 `chore/container-image`**
  - Scope: the full multi-stage `Containerfile` per spec §23.6 (`node` with `hyperframes@0.9.39` pinned in `package-lock.json` (R126); `runtime` on `python:3.12-slim-bookworm` pinned by digest with `ffmpeg chromium fonts-noto-core`, `PUPPETEER_SKIP_DOWNLOAD=1`, `uv sync --frozen --no-dev` before `COPY src/` with a cache mount, OCI version and revision labels; `test` stage); `.containerignore`; `bin/healthcheck`; `scripts/container-test.sh` (build the `test` target and run `pytest -m container` inside it; build `runtime` and run the isolated smoke test); `make test-container`; CI runs it inside job `test`.
  - Spec: §23.6, §24.2, R63, R64, R121. Depends on: 0.1. QEMU fallback only if the arm64 runner fails (R121).
  - Tests: smoke test (container starts, `/health`); `hyperframes doctor` passes with Debian Chromium.
  - Local network (R125): support `REELS_HUB_INSECURE_TLS=1` for local builds (TLS verification off for podman pulls, apt, uv and npm; build args only, never in the final image, never in CI). npm is blocked on the build machine's network, so locally the `node` stage can't build: `make test-container` reports that and skips; CI must pass in full.
  - Verify: CI's container tests pass; locally `REELS_HUB_INSECURE_TLS=1 make test-container` builds what the network allows and reports the npm block clearly; afterwards `podman ps -a` and `podman volume ls` show nothing left from the test.
- [ ] **0.3 `chore/release-image`**
  - Scope: `.github/workflows/release.yml` on `ubuntu-24.04-arm` (R121): on push to `main`, build `linux/arm64` `runtime` and push `ghcr.io/ai-slop-code/reels-hub:<sha>` and `:latest`; on tag `v*`, push `:vX.Y.Z`. `permissions: contents: read, packages: write`; log in with `GITHUB_TOKEN`; label `org.opencontainers.image.source=https://github.com/ai-slop-code/reels-hub`.
  - Spec: §21, §23.6, R59. Depends on: 0.2.
  - Tests: none beyond CI; workflow lint by running it.
  - Verify: after merge, `gh run list --workflow release.yml` is green; the package exists and is **public**, linked to the repo (🔑 OWNER: a new GHCR package may start private; if so, set it to public once on its package settings page, R124).
- [ ] **0.4 `feature/db-migrations`**
  - Scope: DB helper; migration runner over `src/reels_hub/migrations/NNNN_<name>.sql` with a `schema_version`; if a migration is pending, back up first (`VACUUM INTO` temp → `PRAGMA integrity_check` → rename to `/media/_backups/db/pre-migrate-<from>-<to>-YYYYMMDD-HHMM.sqlite`); `0001` creates the phase-0 tables (`project` minimal, `project_media_folder`, `shoot`, `take`, `device`, `clip`, `job`, `agent_log`). Later tables come with their phase.
  - Spec: §18, §21, §23.6, R18, R61. Depends on: 0.1.
  - Tests: applies to an empty DB; second start is a no-op; backup only when pending; failed integrity check → no rename; FTS5 is available.
  - Verify: `uv run reels-hub migrate` against a temp dir.
- [ ] **0.5 `feature/job-worker`**
  - Scope: `job` API (enqueue, claim, progress, done/failed with error); worker loop started with the app, one heavy job at a time; `running` jobs re-queued on start; on SIGTERM kill the subprocess and set the job back to `queued`; a timer that enqueues catch-up work. First periodic job: daily DB backup when the last is older than 24 h (keep 14 daily plus all `pre-*`).
  - Spec: §4, §21, §23.4, §23.6, R13, R61. Depends on: 0.4.
  - Tests: claim order; re-queue on restart; failure recorded; backup catch-up and retention (fake clock).
  - Verify: unit tests; job counts appear in `/health` after 0.6.
- [ ] **0.6 `feature/media-root-health`**
  - Scope: config (`REELS_HUB_HOST_MEDIA_ROOT` must be absolute, else exit with a clear error; `/media` and `/data` overridable for tests); write the media marker on first setup; path helpers (relative ↔ container ↔ host); `/health` JSON with `version`, `git_sha`, `schema_version`, `media_mounted`, `media_free_gb`, `data_free_gb`, job counts; 503 only if the DB can't open or the marker is missing.
  - Spec: §23.2, §23.3, R14, R62, R66. Depends on: 0.4, 0.5.
  - Tests: path derivation; `~` and relative roots refused; both 503 cases.
  - Verify: smoke test checks the `/health` fields.
- [ ] **0.7 `feature/probe-and-fixtures`**
  - Scope: `tests/fixtures/make_fixtures.sh` (ffmpeg lavfi test patterns and tones, all < 5 MB), run by `make test` and the container tests to generate the clips at test time into a git-ignored folder; only the script is committed (R120): Sony-like `C0001.MP4` 540p 25p with timecode, 2 audio channels and a Sony-style XML sidecar; DJI-like `DJI_…_0001_D.MP4` 25p with `.LRF` and `.WAV`; a 50p clip; a VFR clip; an HLG-tagged clip; a clip with clipped audio; a camera pair with a known audio offset; one 2 s 4K HEVC clip. ffprobe wrapper: duration (ms), codec, resolution, fps, audio channels, camera model, start timecode, color transfer; flags `vfr` and `hdr_log` (the fps-mismatch flag needs a reel: 9.3).
  - Spec: §5.1 step 2, §24.2, R69, R70, R120. Depends on: 0.2.
  - Tests: parser on stored ffprobe JSON (host); probing every fixture inside the image (`-m container`).
  - Verify: `make fixtures` is reproducible; `git status` shows no generated media; `make test-container` green.
- [ ] **0.8 `feature/watcher`**
  - Scope: polling watcher (10 s, configurable) over `/media/<project>/raw/{sony,dji,phone,audio}` for folders in `project_media_folder` (a minimal `reels-hub project add <id> --folder <rel>` until 9.1); register only after size and mtime are stable across 2 polls ≥ 10 s apart and ffprobe succeeds; ignore list; pause if the marker is missing (mark nothing offline); xxh3 over first 1 MiB + last 1 MiB + size; duplicates and moves re-attached by hash + duration; `availability`, `volume_id`; DJI `.LRF` and `.WAV` attached (WAV as alternate audio); a `scan_now()` for Add footage; enqueue probe and proxy jobs; shoot = recording day per project (takes come in 1.7).
  - Spec: §5.1, §23.2, §23.4, R27, R62. Depends on: 0.5–0.7.
  - Tests: a growing file isn't registered until stable (fake clock); ignore patterns; missing marker pauses; move re-attach; duplicate detection.
  - Verify: smoke test copies a fixture into the temp media folder and sees it registered with the right host path.
- [ ] **0.9 `feature/proxies`**
  - Scope: proxy job with the exact settings of spec §5.1 step 3 (540 px high, H.264 High CRF 23, keyframe every 0.5 s, source fps, timecode, AAC 128 kbps 48 kHz with all channels, faststart) into `/data`; contact sheet every 2 s; helper that reads single frames from the master; temp name then rename.
  - Spec: §5.1, §21, R65. Depends on: 0.8.
  - Tests (inside the image): proxy height, keyframe interval, audio channel count, timecode, faststart.
  - Verify: timing on real footage is measured by the owner at the phase end.
- [ ] **0.10 `chore/deploy-backup-restore`**
  - Scope: `deploy/deploy.sh <tag>` per spec §23.6 (pull the public image, no login (R124), `pre-update` backup, remember the running tag, stop `-t 60`, remove, run, wait ≤ 120 s for `/health` to show the new version, roll back to the backup and previous tag on failure) holding the **only** `podman run` (spec §23.3); `deploy.sh restore <file>` (Q5); `deploy/sk.reelshub.podman.plist`; name, volume, port and media overridable by env **for tests only**; `docs/RUNBOOK.md` for the owner (run-machine setup, first deploy, Giro_00 hard links, copying the Giro_00 graphics from the handoff archive into `~/Movies/ReelsHub/giro00/graphics/`, restore rehearsal, logs, MCP connection placeholder).
  - Spec: §23.3, §23.6, §24.5, R59–R61. Depends on: 0.3, 0.6.
  - Tests: `scripts/deploy-test.sh` (isolated): deploy tag A, upgrade to tag B, forced health failure rolls back to A, backup → restore round trip.
  - Verify: the test passes locally; nothing named `reels-hub` or `reels-hub-data` was touched.
- [ ] **0.11 `feature/ui-shell`**
  - Scope: base Jinja2 layout with vendored `htmx.min.js` (no build step); navigation for the §20 screens (later ones as placeholders); **Today** (jobs running or failed, clip flags, footage not yet on a reel, warning below 100 GB free); **Library** (clips by shoot, proxy player, contact sheet). Playwright wired into `make test` against a test server with a temp DB and fixture media.
  - Spec: §20, R66, R69. Depends on: 0.9.
  - Tests: Playwright: Today shows a failed job and a VFR flag; Library plays a proxy.
  - Verify: screenshot in the PR.
- [ ] ⛔ **STOP: phase 0 report.** 🔑 OWNER (I4–I8, ideally I17): set up the run machine per `docs/RUNBOOK.md`, `deploy.sh <sha>`, hard-link Giro_00 and copy its graphics, measure the "done when", import a host path in Edits, do the Edits 25p check. The agent adds the 25p result to the playbook seed in 2.1.

## Phase 1 · Transcripts and moments
**Goal:** finding the hook takes minutes.
**Spec:** §5.1 steps 4–7, §5.1a, §5.2, §5.3, §5.4, §18 (R71–R73, R81–R89).
**Done when (spec §25):** Searching "lizatko" returns C0031 at 490.1 s in under 1 s.

- [ ] **1.1 `feature/transcripts-fake`**
  - Scope: migration for `transcript`, `transcript_word`, `transcript_edit`; transcriber interface with `TRANSCRIBE_BACKEND=fake|cpu` (the `host` helper of §23.5 is not built); fake backend returns words from fixture JSON; `transcribe` job after probe; engine, model, revision and config stored per run; one `active` run per clip; `check_language` flag for segments with mean word probability < 0.4; manual fixes stored in `transcript_edit` and applied on read, raw words never overwritten.
  - Spec: §5.1 step 4, §5.1a, §18, R84, R87. Depends on: 0.8.
  - Tests: run stored with config; edits applied on read; raw words unchanged; flag threshold.
  - Verify: Library shows a fake transcript for a fixture clip.
- [ ] **1.2 `feature/whisperx-cpu`**
  - Scope: real backend: WhisperX on faster-whisper, CPU int8, decoding config from spec §5.1a (forced `sk`, beam 5, no conditioning, VAD, word timestamps, hallucination blocklist); per-reel `hotwords` capped at 150 tokens; forced alignment with `comodoro/wav2vec2-xls-r-300m-sk-cv8`, `timing: interpolated` for unplaceable words; audio decoded with ffmpeg to 16 kHz mono in memory; torch from the CPU index; `reels-hub models pull` downloads pinned revisions into `/data/models` (kinit model converted once with `ct2-transformers-converter`); runtime with `HF_HUB_OFFLINE=1`.
  - Spec: §5.1a, §21, §23.4, §23.6, R82, R83, R89, R90. Depends on: 1.1.
  - Tests: config and hotword-cap unit tests; one `real` test (skipped in CI) on a 5 s speech fixture (Q3).
  - Verify: image still builds on arm64; note the image size and CI time in the PR.
- [ ] **1.3 `feature/asr-benchmark`**
  - Scope: `reels-hub bench asr --ref <file in /data/bench> --clip <rel_path> [--range] --configs <a,b>`: WER (NFC, lowercase, no punctuation, diacritics kept), glossary-name accuracy, speed (minutes per hour of audio); Markdown report in `/data/bench/`. References never in Git.
  - Spec: §5.1a, R81, R82. Depends on: 1.2.
  - Tests: WER and name accuracy on toy strings.
  - Verify: 🔑 OWNER (I9) runs it on the run machine with `podman exec`. The agent then sets `asr.model` from the result in a small follow-up PR. Pass bar: WER ≤ 12 %, names ≥ 90 %. If neither config passes, stop and ask.
- [ ] **1.4 `feature/search`**
  - Scope: `transcript_fts` (`unicode61 remove_diacritics 2`), kept in sync with the active run; prefix fallback for terms ≥ 5 characters (drop the last 2), exact matches first; filters (speaker, camera, rating, tag, project, used/unused, date); hits grouped by take; **Search** screen.
  - Spec: §5.4, §20, R85 (light step), R88. Depends on: 1.1.
  - Tests: "lizatko" finds "lízatko" and "lízatka"; "zoncolan" finds "Zoncolan"; the done-when fixture (clip `giro00-sony-c0031`, word at 490 100 ms, text per Q2) returns in < 1 s.
  - Verify: Playwright search flow.
- [ ] **1.5 `feature/shots-silences-clipping`**
  - Scope: shot detection (PySceneDetect), silences (ffmpeg), audio QC: clipped ranges (≥ 3 consecutive samples at or above −0.1 dBFS) stored as numbers on the clip; overlapping moments get `tech:clipped`.
  - Spec: §5.1 steps 6–7, §5.1b, R72. Depends on: 0.9.
  - Tests (inside the image): the clipped fixture yields its known range; shots on a cut fixture.
  - Verify: flags visible in Library.
- [ ] **1.6 `feature/moments-exclusions`**
  - Scope: `moment` table; prefixed tag vocabulary validated (§5.3); rating, `usable`, `excluded_by` (person exclusions absolute, only the same person lifts them; agents only `agent_proposed`); exclude a whole take; cut points snap to the nearest silence within ±150 ms else pad 80 ms; reuse warning in the same project; unused gems (not `time:dated`); Library transcript panel with `M` to mark a moment, exclude action, J/K/L scrubbing.
  - Spec: §5.3, §17.3, §20, R3, R73. Depends on: 1.4, 1.5.
  - Tests: exclusion rules; snapping; vocabulary validation; Playwright mark and exclude.
  - Verify: screenshot.
- [ ] **1.7 `feature/takes-clock-offsets`**
  - Scope: group clips recorded at the same time across cameras into takes; clock offset per device per shoot (manual entry in UI and CLI, always overrides); alternate angles; synced angles side by side with jump.
  - Spec: §5.2, §18. Depends on: 0.8, 1.1.
  - Tests: grouping with a known offset; manual override wins.
  - Verify: Playwright take view.
- [ ] **1.8 `feature/speakers`** *(if time allows)* 🔑 OWNER (I10)
  - Scope: pyannote `speaker-diarization-community-1` through WhisperX; one voice print per person from producer-chosen ranges; thresholds in config; `unknown` for turns < 1.5 s in an unsure cluster; relabel in the UI; CC-BY attribution on an About page. Voice prints never leave the Hub.
  - Spec: §5.1a, §22, R86, R90. Depends on: 1.2.
  - Tests: naming logic on synthetic embeddings; `real` test skipped in CI.
  - Verify: owner checks labels on C0031.
- [ ] **1.9 `feature/audio-sync`** *(if time allows)*
  - Scope: coarse 100 Hz log-energy envelope cross-correlation, fine GCC-PHAT at 16 kHz within ±100 ms, confidence ≥ 3 else ask for a manual offset; drift check on first and last 2 min, flag above one frame (40 ms at 25p).
  - Spec: §5.2, R71. Depends on: 1.7.
  - Tests: the known-offset fixture pair within one frame; low-confidence case.
  - Verify: unit and container tests.
- [ ] ⛔ **STOP: phase 1 report.** 🔑 OWNER: deploy, ingest Giro_00 on the run machine, search "lizatko"; benchmark result (I9).

## Phase 2 · MCP v1
**Goal:** agents build drafts with full context.
**Spec:** §17, §22, §9, §14 (R12, R17).
**Done when (spec §25):** A fresh agent finds the Giro_00 hook and an importable Mac path without browsing the file system.

- [ ] **2.1 `feature/design-tokens-playbook`**
  - Scope: import the front matter and YAML blocks of `docs/spec/DESIGN_LANGUAGE.md` (bundled into the package or image) as versioned tokens; `playbook_item` seeded from spec §14 plus the owner's 25p result; **Design** and **Playbook** screens; services for `get_style_tokens`, `get_playbook`, `add_playbook_item`.
  - Spec: §9, §14, §20. Depends on: 0.11.
  - Tests: every YAML block parses; version recorded; add item with date and tool version.
  - Verify: screens render.
- [ ] **2.2 `feature/mcp-server`**
  - Scope: MCP Python SDK, streamable HTTP, mounted at `/mcp` in the same FastAPI app; token required (Q6); every write logged in `agent_log` (agent, session, tool, args, diff); **Agent log** screen; `docs/RUNBOOK.md` gets the Claude Code connection command.
  - Spec: §17, §22, R12. Depends on: 2.1. Q6.
  - Tests: no token → rejected; handshake; write logged with diff.
  - Verify: smoke test does the MCP `initialize` + `tools/list`.
- [ ] **2.3 `feature/mcp-read-tools`**
  - Scope: tools `search_moments`, `get_transcript`, `get_take`, `frame_sheet`, `host_paths`, `get_job`, `get_style_tokens`, `get_playbook`, `add_playbook_item`; resources `hub://design-language/current`, `hub://playbook/edits`, `hub://glossary/sk` (empty until 3.3). `limit` 20 / `offset`; long tools return `job_id`; errors name the next action. Excluded ranges and `third_party_unlicensed` media are filtered out, including in `get_transcript`.
  - Spec: §17.1–§17.3, R17. Depends on: 2.2, 1.6.
  - Tests: each tool against fixtures; exclusions filtered.
  - Verify: call the tools from a test MCP client.
- [ ] **2.4 `feature/mcp-moment-writes`**
  - Scope: `tag_moment`, `exclude_range` (stored as `agent_proposed`); diffs in `agent_log`.
  - Spec: §17.2, §17.3, R3. Depends on: 2.3.
  - Tests: agents can't lift a person's exclusion or change `usable` on it.
  - Verify: contract tests.
- [ ] **2.5 `test/mcp-contract`**
  - Scope: contract suite run in CI: schema snapshot of every tool; no tool can approve (by name and by effect); excluded ranges and third-party media never returned by any tool or resource; MCP handshake inside the container smoke test.
  - Spec: §17.3, §24.2. Depends on: 2.4.
  - Tests: the suite itself.
  - Verify: CI green.
- [ ] ⛔ **STOP: phase 2 report.** 🔑 OWNER (I11): connect Claude Code on the run machine; ask a fresh session to find the Giro_00 hook and its Mac path.

## Phase 3 · Facts and glossary
**Goal:** fewer factual and caption errors.
**Spec:** §7, §8 (R92–R95, R100, R110–R113, R115, R117, R118).
**Done when (spec §25):** Stage 1 "enters Slovenia" shows as `verified` and "where / how long" as `conflicting`; `fix_captions` turns "lyžičko" into "lízatko" (glossary) and "po 30" into "po tridsiatke" (style rule).

- [ ] **3.1 `feature/fact-store`**
  - Scope: `fact`, `fact_source` (statuses verified / attributed / unverified / conflicting / outdated; tiers primary > archive > secondary > lead; leads never cited); "Needs attention" queue (Q13); `review_by`; **Re-checked** button setting `checked` to today with an optional pasted quote; spectator-advice type with an "access unconfirmed" flag; the four seed facts of spec §7.1; **Facts** screen. Automated page checks optional and best-effort: a failure says "check manually" and never changes `status`.
  - Spec: §7.1, §7.2, §20, R110, R111, R113, R117, R118. Depends on: 0.11. Q13.
  - Tests: silence is not a conflict; attributed vs verified rules; Re-checked; the Stage 1 seed statuses (done-when part 1).
  - Verify: Playwright Facts screen.
- [ ] **3.2 `feature/stage-table`** 🔑 OWNER (I12)
  - Scope: `stage` table for a fact domain, versioned import from YAML/CSV; optional `climbs` and `places` with country, each pointing to a fact; resource `hub://stages/giro2027`.
  - Spec: §7.2, §17.1, R115. Depends on: 3.1. Q12.
  - Tests: import, versioning, only verified/attributed places exposed for maps.
  - Verify: resource returns the table.
- [ ] **3.3 `feature/glossary`** 🔑 OWNER (I13)
  - Scope: `glossary_term` with `forms`, `captions: as_said | canonical`, `heard_as`, `keep_as_said`, `pronunciation`, `source`, `checked_by`; sets `sk-italy` and `sk-cycling` seeded from the 52 terms in `docs/reviews/14-slovak-language-editor.md` (Q6 there); Katarina's dialect words when supplied; resource `hub://glossary/sk`; glossary terms feed the per-reel `hotwords` (1.2).
  - Spec: §8, §17.1, R93–R95, R100. Depends on: 3.1.
  - Tests: seed imports all terms with correct diacritics; matching on any form.
  - Verify: glossary resource.
- [ ] **3.4 `feature/fix-captions`**
  - Scope: `correction` (`heard_phrase`, `correct_phrase`, `always`); `fix_captions` applies glossary `heard_as` and forms (replacement keeps the case), full-phrase corrections and `always` single-word rules; other matches returned as suggestions; number style rules from DESIGN_LANGUAGE §4 (e.g. "po 30" → "po tridsiatke"); never touches `transcript_word`.
  - Spec: §8, DESIGN_LANGUAGE §4, R92, R96. Depends on: 3.3.
  - Tests: done-when part 2; "takúto lyžičko" only changes as a full phrase; a non-`always` single word is only suggested; raw transcript unchanged.
  - Verify: unit tests.
- [ ] **3.5 `feature/fact-mcp-lint`**
  - Scope: MCP `check_fact`, `add_fact`, `mark_fact_checked`, `lint_script` (claims without a matching fact, glossary violations; `kind: caption` counts hashtags, max 5), `fix_captions`.
  - Spec: §7.2, §8.1, §17.2. Depends on: 3.2–3.4.
  - Tests: contract tests; 6 hashtags → flagged.
  - Verify: CI green.
- [ ] ⛔ **STOP: phase 3 report.**

## Phase 9 · Projects, reel prompt and notes
**Goal:** from added footage to a ready prompt without manual steps; every reel documented and visible in the overview.
**Spec:** §6, §11.4, §13.2, §19.0–§19.2, §20 (R5, R34, R53, R57, R101, R103–R106).
**Done when (spec §25):** Prompt ready < 2 min after the footage's analysis finishes, with no producer clicks; the Giro_00 golden test passes; a fresh agent's draft comes with a complete `editors_notes.md`.

- [ ] **9.1 `feature/projects`** 🔑 OWNER (I14)
  - Scope: project from YAML (spec §6.1 fields) with links to media folders, assets, fact domain, glossary sets, design-language version, music signature, `posting_time`, experiment; `create_project`, `get_project`, `link_assets`; **Projects** screen (list; create by pasting or uploading YAML as the light wizard); seed YAML for `giro2027-advent`. Replaces the minimal CLI from 0.8.
  - Spec: §6.1, §17.2, §18, §20. Depends on: 3.5.
  - Tests: YAML validation; links created; ingest of the project's folders starts.
  - Verify: Playwright create project.
- [ ] **9.2 `feature/reels`**
  - Scope: `reel` fields per spec §18; status pipeline with `status_change` and the "going back" rules; slot type and target runtime defaults (DESIGN_LANGUAGE §10); commercial flags and `collab`; experiment variant (odd stages `tease`, even `statement`; Day 1 and Days 23–24 out) via `log_experiment`; **New reel** screen; `create_reel`, `get_reel`, `update_reel`, `list_reels`.
  - Spec: §6.2, §13.2, §17.2, §20, R103–R106. Depends on: 9.1. Q7.
  - Tests: allowed transitions; going back; experiment assignment.
  - Verify: Playwright new reel.
- [ ] **9.3 `feature/add-footage-analysis`**
  - Scope: **Add footage** (pre-selects clips ingested since the reel was created and not linked to another reel; producer confirms), `reel_clip`, immediate scan; statuses `footage_added → analyzing → prompt_ready` run by a job chain that waits for the linked clips' ingest, applies glossary and correction memory to caption-facing text, suggests moments and builds the prompt; adding footage before `approved` goes back to `analyzing`; fps-mismatch flag against the reel's other clips; progress and failures on the reel and in Today; `add_footage` returns a `job_id`.
  - Spec: §5.1 step 2, §6.3, §19.1, R69. Depends on: 9.2, 3.4.
  - Tests: full chain with fakes; fps mismatch flagged; going back.
  - Verify: Playwright add footage → prompt ready.
- [ ] **9.4 `feature/moment-ranking-gathering`**
  - Scope: auto-suggested moments (light: questions and claims as hook candidates, list beats, sign-offs); ranking per spec §6.3 (filters → FTS5 BM25 on topic and stage keywords → rating → recency); the gathering table of spec §6.3 as one context object (brief, facts with statuses, candidate moments and unused gems, tokens, graphics templates and graphics used, music, glossary, playbook, learnings, continuity, open items).
  - Spec: §5.3, §6.3, R35. Depends on: 9.3.
  - Tests: ranking order; excluded and third-party never included.
  - Verify: unit tests.
- [ ] **9.5 `feature/reel-prompt`**
  - Scope: the versioned template of spec §6.4; generator (lean, `hub://` links for bulk data, Slovak quoted verbatim); `reel_prompt` history; Reel screen preview, edit, regenerate, copy; save `<project>/reels/<slot>/PROMPT.md`; resource `hub://reel/{id}/prompt`; `generate_reel_prompt`; status `editing` when copied or read.
  - Spec: §6.4, §17.1, §17.2, R34, R101, R104, R114. Depends on: 9.4.
  - Tests: golden prompts for a Giro_00 fixture project (Q2) and a Stage 1 fixture (verified / attributed / unconfirmed lines); fixed clock and IDs; prompt build < 2 min with fakes.
  - Verify: done-when parts 1 and 2.
- [ ] **9.6 `feature/editors-notes`**
  - Scope: the spec §11.4 template, created with the first version or on demand at `<project>/reels/<slot>/editors_notes.md`; `editors_notes` row with FTS; "Clips used" and "Graphics used" parsed into `asset_usage` (minimal `asset` table created here; 7.1 completes it); `get_editors_notes`, `update_editors_notes`, `hub://reel/{id}/editors-notes`; view and edit on the Reel screen; `open_item` with carry-over, seeded for the Stage 1 and Stage 2 reels (spec §7.1).
  - Spec: §11.4, §17.1, §17.2, §18, R53, R54. Depends on: 9.2.
  - Tests: template created; tables parsed into `asset_usage`; open items carried to the prompt.
  - Verify: Playwright view and edit.
- [ ] **9.7 `feature/project-overview`**
  - Scope: **Project overview** per spec §6.5 (reel list with created, footage added, approved, posted dates and links; calendar grid with status colors and continuity warnings); `check_continuity`; resources `hub://project/{id}`, `hub://reel/{id}`.
  - Spec: §6.2 continuity, §6.5, §17.1, §20. Depends on: 9.6.
  - Tests: dates from `status_change`; a broken promise is flagged.
  - Verify: Playwright overview.
- [ ] ⛔ **STOP: phase 9 report.** 🔑 OWNER: a fresh Claude session drafts from a Hub prompt and writes `editors_notes.md` (done-when part 3).

## Phase 4 · Reviews and approvals
**Goal:** clean feedback rounds; exports only after approval.
**Spec:** §11.1–§11.3, §17.2, §17.3, §26 (R1, R2, R75).
**Done when (spec §25):** `export_allowed` is false before approval and again after a newer version is created.

- [ ] **4.1 `feature/versions`**
  - Scope: `version` with the cut list (minimum fields of spec §11.1, validated); `create_version`; `request_approval` (reel → `in_review`); a new version after approval sends the reel back to `in_review` and invalidates the old approval.
  - Spec: §11.1, §11.3, §6.2, R75. Depends on: 9.6.
  - Tests: validation; invalidation.
  - Verify: contract tests.
- [ ] **4.2 `feature/feedback`**
  - Scope: `feedback` items; paste a list → items split by the Hub-side LLM (Anthropic client wrapper; fake in tests; plain line split when no key is set); `log_feedback`, `resolve_feedback`; `in_review → editing`; author Katarina when Ľuboš logs her remark; `after_post`.
  - Spec: §11.2, §21, §26. Depends on: 4.1. Q14.
  - Tests: split with the fake LLM; status changes; resolution links a version.
  - Verify: Playwright paste feedback.
- [ ] **4.3 `feature/approval`**
  - Scope: approval screen (version, open feedback, open items, `editors_notes.md` with its checklist; waive open items explicitly); **Approve** button in the UI only, recording by, at and hands-on minutes; `get_approval`, `export_allowed`. No MCP tool approves.
  - Spec: §11.3, §17.3, §26, R1, R2. Depends on: 4.1, 4.2.
  - Tests: done-when; contract test that no tool approves; approval only through the UI route.
  - Verify: Playwright approve flow.
- [ ] **4.4 `feature/version-diff`**
  - Scope: simple diff of two cut lists item by item (text, timing, assets).
  - Spec: §11.2. Depends on: 4.1.
  - Tests: diff on fixture cut lists.
  - Verify: screenshot.
- [ ] **4.5 `feature/lint-draft`** *(if time allows; Q8)*
  - Scope: `lint_draft` on the version's cut list with the R76 light checks (flash frames, main-track gaps, excluded range used).
  - Spec: §9, §17.2, R76. Depends on: 4.1.
  - Tests: each check on a fixture.
  - Verify: contract test.
- [ ] ⛔ **STOP: phase 4 report.** 🔑 OWNER: deploy, restore rehearsal (I17) if not done, dress rehearsal 27 Nov (spec §25.1), go/no-go 28 Nov.

## Phase 5 · Analytics v1
**Goal:** we see what works.
**Spec:** §12, §19.4 (R29, R49, R102, R108).
**Done when (spec §25):** Every posted reel has a 24 h snapshot.

- [ ] **5.1 `feature/publication-manual-metrics`** (must be deployed before 2 Dec 19:00)
  - Scope: `publication`, `metric_snapshot`, `retention_point`; `link_publication` and a UI form (reel → `posted`); the 2-minute manual 24 h form; manual 7 d follows and retention entry; Today shows "24 h snapshot due"; Analytics screen (light).
  - Spec: §12.1, §19.4, §20, R29. Depends on: 4.3. Q7.
  - Tests: snapshot due logic (fake clock); manual entry stored with `source: manual`.
  - Verify: Playwright 24 h form.
- [ ] **5.2 `feature/features-reel-card`**
  - Scope: reel features (spec §12.2) computed from Hub data; derived metrics (spec §12.3); reel card against the baseline (Q9); `get_metrics`, `get_retention`.
  - Spec: §12.2–§12.4, R102, R108. Depends on: 5.1. Q9.
  - Tests: derived metric math; hashtag count in features.
  - Verify: screenshot.
- [ ] **5.3 `feature/instagram-importer`** 🔑 OWNER (I18)
  - Scope: Instagram API with Instagram Login (v27.0 names incl. `reels_skip_rate`, `reposts`, `facebook_views`), token from secret `meta_token`, refresh with an alert 7 days before expiry (Q10), pulls at 24 h (if ready), 72 h, 7 d, 28 d by timer catch-up, `api_version` recorded, external calls logged. No comments, no scraping.
  - Spec: §12.1, §22, R49, R102. Depends on: 5.1. Q10.
  - Tests: all HTTP mocked; metric mapping; expiry alert.
  - Verify: owner runs one pull on the run machine.
- [ ] ⛔ **STOP: phase 5 report.**

## Phase 7 · Graphics and motion
**Goal:** on-brand graphics, and we see what we've used.
**Spec:** §10, §10.1, §17.2, §20, DESIGN_LANGUAGE §3, §7, §11 (R46–R48, R51, R54).
**Done when (spec §25):** The graphics overview lists every Giro_00 graphic with the reel and timeline position that used it (measured on the run machine with the real graphics in the media library; R120).

- [ ] **7.1 `feature/asset-registry`**
  - Scope: the full asset record (spec §10, §10.1: template, params, data source, license, `origin`, `ai_generated`, fonts as `font` assets); `register_asset`; seed the Giro_00 assets of DESIGN_LANGUAGE §11 as records only (paths `giro00/graphics/…` in the media library; the files aren't in the repo, R120; RUNBOOK tells the owner to copy them from the handoff archive).
  - Spec: §10, §18, R46, R48, R51. Depends on: 9.6.
  - Tests: registration (with generated test images); `third_party_unlicensed` hidden from agents.
  - Verify: contract tests.
- [ ] **7.2 `feature/graphics-overview`**
  - Scope: **Graphics** screen; `list_graphics_usage`; `hub://graphics/{project}`; Giro_00's notes in the §11.4 format (from `docs/reference/giro00/review_notes.md`) as seed data.
  - Spec: §10, §11.4, §17.1, §20, R54. Depends on: 7.1.
  - Tests: done-when on the seed records (generated stand-in images); Playwright screen.
  - Verify: screenshot; the real done-when is checked by the owner on the run machine with the Giro_00 graphics in the media library.
- [ ] **7.3 `feature/map-templates`**
  - Scope: `tools/mkmap.py` wrapped as parameterized templates `map_overview` and `map_closeup` in the package; Natural Earth data (Q11); SVG → PNG with resvg in the container with an OFL font (Q11); `generate_map` writes to `/media/<project>/graphics/` and registers the asset (`origin: open_data`). No organizer maps.
  - Spec: §10, §21, DESIGN_LANGUAGE §7, R47. Depends on: 7.1. Q11.
  - Tests (inside the image): render and compare with reference frames generated at test time (not committed, R120).
  - Verify: PNG attached to the PR, not committed.
- [ ] **7.4 `feature/hyperframes-card`** 🔑 OWNER (I19)
  - Scope: `card_map_cities` composition (tokens as CSS variables); `render_motion` job for MP4 and MOV ProRes 4444 alpha; asset record with HTML hash, HyperFrames version, format, alpha, fonts.
  - Spec: §10.1, R46. Depends on: 7.3.
  - Tests (inside the image): one render per format; frame diff.
  - Verify: owner imports both into a copy of `Giro_00_Intro` and records the result in the playbook.
- [ ] ⛔ **STOP: phase 7 report.** 🔑 OWNER: check the done-when on the run machine (Giro_00 graphics in `~/Movies/ReelsHub/giro00/graphics/`).

## Phase 8 · Music
**Goal:** better music in minutes, no stock "garbage".
**Spec:** §15, §17.2, §22 (R41, R42, R44, R77).
**Done when (spec §25):** A shortlist of 3 with license records in ≤ 5 min; no audio file written.

- [ ] **8.1 `feature/music-assets`**
  - Scope: `music_track`, `music_license`, `music_audition`, blocklist; Dolce Vita seed (spec §15.7); signature track; `get_music_license`.
  - Spec: §15.4, §15.6, §15.7, §18. Depends on: 7.1.
  - Tests: seed; license fields.
  - Verify: contract tests.
- [ ] **8.2 `feature/music-shortlist`** 🔑 OWNER (I20, optional)
  - Scope: music brief; `search_music` takes candidates the agent got from the Edits catalog and adds metadata (MusicBrainz; GetSongBPM with its backlink; iTunes Search / Deezer JSON metadata only); stock excluded unless `include_stock: true`; `shortlist_music` (max 3, with reasons); `rate_track`; taste notes.
  - Spec: §15.2, §15.4, §17.2. Depends on: 8.1.
  - Tests: all HTTP mocked; max 3; **no audio file written anywhere** (filesystem check).
  - Verify: done-when with mocks.
- [ ] **8.3 `feature/analyze-track-mix`**
  - Scope: `analyze_track` refuses tier 1 (metadata only) and analyzes tier 2/3 or own audio (librosa; Demucs only if needed, ask first); `check_mix` stores levels only (Q8).
  - Spec: §15.2, §15.3, §22, R41, R44. Depends on: 8.1. Q8.
  - Tests: tier-1 refusal; levels stored, no audio.
  - Verify: contract tests.
- [ ] ⛔ **STOP: phase 8 report.**

## Phase 6 · Learning loop (ongoing)
**Goal:** each reel improves the next.
**Spec:** §13, §12.6, §6.3.
**Done when (spec §25):** The next reel's prompt shows the latest findings and the previous reel's metrics.

- [ ] **6.1 `feature/findings`**
  - Scope: `finding` with evidence; statuses; findings list and a weekly review page; promotion path stays manual; `get_insights` (light, LLM with the fake in tests).
  - Spec: §13.1, §12.6, §19.4. Depends on: 5.2.
  - Tests: status changes; evidence links.
  - Verify: screenshot.
- [ ] **6.2 `feature/prompt-learnings`**
  - Scope: the prompt's "Learned from previous reels" section filled with the latest findings, the previous reel's metrics and its `editors_notes.md` practices; `recommend` and `explain_drop` in a light version.
  - Spec: §6.3, §6.4, §13.3, §12.6. Depends on: 6.1, 9.5.
  - Tests: golden prompt with findings and metrics (done-when).
  - Verify: golden diff in the PR.
- [ ] ⛔ **STOP: December report.**

## Phase 10 · AI critique (after December)
Not planned yet. Scope: spec §16 and §25 row 10. Start only when the owner asks; deferred R9, R36–R38, R80 may come back then.
