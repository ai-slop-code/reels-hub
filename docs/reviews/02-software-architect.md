# Review packet 02: software architect

**Priority:** must review before implementation
**Time needed:** 2–3 h
**Decisions already made:** D1 build, D2 AI builds it and the timeline stands, D3 cost no constraint, D7 dependencies accepted, D9 Podman, D10 branch-per-feature (see [README](../reviews/README.md#decisions-already-made-please-dont-reopen)).

## Why you
The spec has 12 modules, an MCP server, background jobs and a Podman deployment. It needs a coherent architecture that an AI coding agent can build incrementally, with every feature merged only when the full test suite passes.

## Read
- [§2 Principles](../spec/REELS_HUB_SPEC.md#2-principles), [§4 Architecture](../spec/REELS_HUB_SPEC.md#4-architecture)
- [§5 Footage index](../spec/REELS_HUB_SPEC.md#5-module-a-footage-index-and-moments), [§6 Projects and reel prompt](../spec/REELS_HUB_SPEC.md#6-module-b-projects-reels-and-the-reel-prompt)
- [§17 Agent interface](../spec/REELS_HUB_SPEC.md#17-agent-interface-mcp-server), [§18 Data model](../spec/REELS_HUB_SPEC.md#18-data-model), [§19 Key workflows](../spec/REELS_HUB_SPEC.md#19-key-workflows)
- [§21 Tech stack](../spec/REELS_HUB_SPEC.md#21-tech-stack), [§23 Deployment](../spec/REELS_HUB_SPEC.md#23-deployment-podman), [§24 Development workflow](../spec/REELS_HUB_SPEC.md#24-development-workflow), [§25 Roadmap](../spec/REELS_HUB_SPEC.md#25-roadmap)

## Questions
1. **Language:** Python (FastAPI) or TypeScript? HyperFrames is Node, while ingest and ML are Python. One runtime plus a sidecar, or two services in one image?
2. **Module boundaries:** are the 12 modules the right split? Propose package layout, ownership of tables and internal APIs so features can be built on separate branches without collisions.
3. **Data model:** review §18. Are `version.cut_list` as JSON, `features` as JSON blob and the moment/take/clip split right? What needs proper tables vs. JSON? Migration strategy?
4. **Jobs:** APScheduler vs. a small persistent queue (e.g. SQLite-backed) for long jobs (transcription, renders, critique) that must survive container restarts. Retries, idempotency, progress reporting?
5. **MCP design:** is one server with ~40 tools the right shape, or should tools be grouped / namespaced? Resources vs. tools split, pagination, large payloads (transcripts, frame sheets).
6. **Path mapping:** container ↔ host paths (§23.2). Where does this live so every tool returns the right path for Edits and Claude?
7. **Build order:** confirm or reorder the phases so each `feature/…` branch is independently testable and mergeable. What's the thinnest vertical slice that makes "New reel → prompt" work end to end?
8. **Extensibility:** other editors later (DaVinci, Final Cut), other platforms (YouTube Shorts, TikTok). What should be abstracted now vs. later?

## Expected output
- Architecture decision records (ADRs) for language, job queue, MCP shape and data model.
- Proposed repo layout for `reels-hub`.
- Ordered list of feature branches for phases 0–2 and 9.

## Your input

*Reviewer: AI software architect · reviewed spec v0.4 · 2026-11-12. External facts checked on 2026-11-12 with sources linked inline; anything not checked is marked **unverified**.*

### Summary
The product design is coherent and the 12 modules map well to real work, but v0.4 is still a **feature spec, not a buildable architecture**. Four things would make parallel AI-built branches collide or break in production: (1) no persistent job model (APScheduler alone can't make transcription, renders and metric pulls survive restarts; APScheduler 4 is still an alpha); (2) the path mapping is described per record (`container_path` + `host_path` with a `~`), not as one enforced abstraction; (3) §18 is internally inconsistent (`cut_item` tables vs. `cut_list` JSON, `staged_path` although staging was removed, `moment.clip` vs. `take`, stored `used_in` lists) and has no ID, time-unit, versioning or migration rules; (4) there are no module boundaries or registration points, so every feature branch would edit the same schema file, MCP tool list, router and CHANGELOG. I propose four ADRs (language, job queue, MCP shape, data model), a `src/reels_hub/` layout with enforced layering, and an ordered list of 28 branches whose first 19 already deliver "New reel → prompt" end to end. One real gap outside my questions: the **approval gate can't be enforced server-side for Edits exports**, because export happens in the Edits MCP, which the Hub never sees (P7).

### Answers

#### Q1. Language: Python or TypeScript; one runtime plus sidecar, or two services?
**Python 3.12 for the whole Hub. HyperFrames runs as a Node CLI subprocess in the same image, not as a service.** (ADR-001 is in P1.)

- Most of the work is in Python: faster-whisper/WhisperX/pyannote, OpenCV/PySceneDetect, librosa/Demucs, sqlite-vec, embeddings. In TypeScript, every one of these would be a subprocess or a Python sidecar anyway. HyperFrames is the only Node dependency, and it's batch work: params in, file out. A render job calls `node render/run.mjs --composition <dir> --params <json> --out <path>` with a timeout, reads a JSON result from stdout and registers the asset. No ports, no second health check, no IPC protocol. That respects D9 (one container) with one supervisor process.
- **Node is pinned to 22 LTS in the image.** `render/` has its own `package.json` + `package-lock.json`, installed during the image build with `npm ci`. Python never imports Node and Node never touches the DB. The renderer sits behind a `MotionRenderer` protocol, so tests use a fake that writes a 1-frame file.
- **MCP:** the official Python SDK `mcp` 2.x is stable (2.0.0 released 2026-07-28, implementing the stateless MCP spec 2026-07-28: [PyPI](https://pypi.org/project/mcp/), [spec blog](https://blog.modelcontextprotocol.io/posts/2026-07-28/)). Mount it inside the same FastAPI/ASGI app at `/mcp`, so the UI, the REST API and MCP share one process, one DB engine and one auth layer.
- **UI:** server-rendered **Jinja2 + HTMX + Alpine.js** with no JS build step. One language for agents to write, Playwright covers it, and nothing to keep in sync between a React app and an API. The only exception allowed later is one isolated TypeScript "review player" island (J/K/L scrubbing, timeline markers), built with Vite into `static/` if HTMX/Alpine isn't enough. Decide this in phase 4, not now.
- **Tooling:** `uv` (lockfile `uv.lock`), ruff, mypy `--strict` on `core/` and module `service.py` files, pytest, import-linter (enforces boundaries, see Q2).
- **Process model inside the container:** `reels-hub run` starts uvicorn (UI + API + MCP) and a small supervisor that spawns worker processes for each job pool (Q4). Heavy work (ffmpeg, whisper, Chrome) runs in those workers or their subprocesses, never in the web process.

#### Q2. Module boundaries, package layout, table ownership, internal APIs
The 12 modules are the right *domain* split. Four structural changes are needed so they can be built on separate branches:
1. **Add `core`** (DB, IDs, paths, jobs, events, audit, assets, auth) and **`integrations`** (adapters to external things: Instagram Graph API, music catalogs, transcription backends, HyperFrames runner, LLM client). Integrations are the only code allowed to call the network or external binaries, which keeps "tests never touch real accounts" (§24.2) easy to enforce.
2. **Split Module B into `projects` and `reelprompt`.** The prompt generator (§6.3–6.4) reads from almost every other module, so it has to sit in a higher layer than the modules it reads. The same applies to `critique`.
3. **Asset registry in `core.assets`.** Graphics, motion, music and fonts all register assets. Without this, three modules would each own a slice of one table.
4. **Layering, enforced by import-linter in the test suite:**
   `interfaces (api, ui, mcp, cli)` → `orchestration (reelprompt, critique, learning)` → `domain (footage, projects, facts, language, design, graphics, reviews, analytics, playbook, music)` → `integrations` → `core`.
   A domain module may import another domain module **only through its `service.py` facade and its `schemas.py` DTOs**. Never through its tables or internals.

**Repo layout**
```
reels-hub/
├── pyproject.toml · uv.lock · Makefile · Containerfile · Containerfile.base · compose.yaml
├── CLAUDE.md · CHANGELOG.md · changes/            # one changelog fragment per branch (changes/<branch>.md)
├── docs/adr/0001-language.md … 0004-data-model.md
├── migrations/                                    # Alembic, single linear history
├── render/                                        # Node 22: HyperFrames compositions + run.mjs + package-lock.json
├── src/reels_hub/
│   ├── app.py                                     # builds the ASGI app; ENABLED_MODULES list = only shared edit point
│   ├── core/  config.py db.py ids.py clock.py paths.py jobs/ events.py audit.py assets.py auth.py
│   ├── integrations/  instagram/ music_catalogs/ transcribe/ (cpu.py host.py fake.py) hyperframes.py llm.py
│   ├── modules/
│   │   ├── footage/      # A: ingest pipeline, transcripts, speakers, sync, shots, moments, search
│   │   ├── projects/     # B1: projects, reels, slots, publications, pickups, open items, calendar
│   │   ├── facts/        # C
│   │   ├── language/     # D: glossary, corrections, caption QA
│   │   ├── design/       # E: design-language versions, tokens, style lint
│   │   ├── graphics/     # F: map + motion templates (uses core.assets, integrations.hyperframes)
│   │   ├── reviews/      # G: versions, cut items, feedback, approvals
│   │   ├── analytics/    # H
│   │   ├── playbook/     # J
│   │   ├── music/        # K
│   │   ├── reelprompt/   # B2 (orchestration): intelligence gathering + prompt templates
│   │   ├── critique/     # L (orchestration)
│   │   └── learning/     # I (orchestration)
│   │       └── each module: __init__.py (register()) · models.py · schemas.py · service.py
│   │                        · jobs.py · events.py · mcp_tools.py · api.py · ui/ (templates) · tests/
│   ├── mcp/      server.py registry.py errors.py pagination.py
│   ├── api/  ui/ (layout, nav, shared components)  cli/
└── tests/  contract/ (MCP schemas, path rule, layering)  container/  fixtures/ (Git LFS)
```

**Registration instead of shared files.** Each module exposes `register(hub: HubRegistry)`, which adds its routes, MCP tools, job handlers, event handlers, nav items and scheduled jobs. The only shared line a feature branch touches is one entry in `ENABLED_MODULES` in `app.py`. CHANGELOG conflicts go away with per-branch fragments in `changes/`, concatenated at release. Migrations are the one remaining shared sequence (see Q3).

**Table ownership** (only the owner writes; others read through the owner's `service.py`):

| Owner | Tables |
|---|---|
| core | `file`, `asset`, `asset_usage`, `job`, `job_schedule`, `event`, `agent_log`, `change_log`, `api_token`, `setting` |
| footage | `shoot`, `device`, `take`, `clip`, `clip_step`, `transcript`, `transcript_segment`, `transcript_word`, `speaker`, `voiceprint`, `shot`, `silence`, `moment`, `moment_tag`, `segment_fts`, `vec_*` |
| projects | `project`, `project_media_folder`, `project_asset`, `reel`, `publication`, `pickup`, `open_item` |
| reelprompt | `prompt_template`, `reel_prompt` |
| facts | `fact_domain`, `fact`, `fact_source`, `stage` |
| language | `glossary_set`, `glossary_term`, `correction` |
| design | `design_language_version`, `design_token` |
| graphics | `motion_template`, `graphic_render` (render params; the file goes to `asset`) |
| reviews | `version`, `cut_item`, `caption_item`, `approval`, `feedback` |
| analytics | `metric_snapshot`, `retention_point`, `comment`, `reel_features` |
| learning | `finding`, `finding_evidence`, `experiment` |
| playbook | `playbook_item` |
| music | `music_track`, `music_license`, `music_analysis`, `music_audition`, `taste_profile`, `blocklist_item` |
| critique | `rubric_version`, `critique`, `critique_item` |

**Internal APIs:** the facades are plain typed Python functions taking a `UnitOfWork` (session + clock + actor), returning pydantic DTOs from `schemas.py`. MCP tools, REST routes and the UI are thin adapters over the same facade functions. That is how "every UI capability is also an MCP tool" (§2.6) stays true without duplicating logic. Cross-module **reactions** (new version → fast critique, publication linked → schedule metric pulls, clip transcribed → suggest moments) go through `core.events` (P10), not direct calls.

**Late-built modules:** `reelprompt` depends on facts, analytics, critique and music, which ship later. It declares `Protocol`s (`FactsProvider`, `InsightsProvider`, `MusicProvider`, …). Until the module exists, a `Null…Provider` returns "none yet", so phase 9 can merge before phases 3, 5, 8 and 10.

#### Q3. Data model: JSON vs. tables, moment/take/clip, migrations
**Rules for every table** (ADR-004, P4):
- **IDs:** `TEXT` primary key = type prefix + ULID (`clp_01JD…`, `mom_01JD…`), generated by `core.ids` (injectable for golden tests). Projects and reels also get a unique human **slug** (`giro2027-advent`, `giro00`). MCP accepts either. Never reuse a slug as a foreign key, because slugs get renamed.
- **Time:** all media times are **integer milliseconds** (`src_in_ms`, `t_in_ms`). Floats in seconds (`490.1`) cause drift and equality bugs in sync offsets and cut lists. The API can still show seconds. Wall-clock timestamps are UTC ISO-8601 text. `posted_at` also stores `tz` for weekday/hour analysis.
- **Optimistic concurrency:** `row_version INTEGER` on `reel`, `moment`, `fact`, `feedback`, `version`. Update tools take `expected_row_version` so a human edit in the UI and an agent edit can't silently overwrite each other.
- **Provenance:** derived rows (`transcript`, `shot`, `moment` with `origin='auto'`, `reel_features`, `music_analysis`, `critique`) store `producer` (e.g. `faster-whisper large-v3 int8`) and `producer_version`. Re-runs create a new row; they don't overwrite.

**JSON vs. tables**

| Data | v0.4 | Recommendation | Why |
|---|---|---|---|
| `version.cut_list` | JSON (table list) **and** `cut_item` (diagram) | **Both, with clear roles:** `cut_list` JSON is the immutable, schema-versioned snapshot (validated by a pydantic `CutList v1` model). `cut_item` / `caption_item` rows are a **derived index** written in the same transaction | Snapshot = what the agent built (diffs, critique, audit). Rows = queries: "where is moment X used", retention overlay, feature computation |
| `moment.tags` | JSON | **`moment_tag(moment_id, tag)` table** with an index, plus a `kind` split for `prop:` / `topic:` prefixes | Filtering and faceting are core to search (§5.4); JSON `LIKE` doesn't scale or index |
| `moment.used_in`, `fact.used_in`, `music.used_in` | stored lists | **Derived** from `cut_item` / `asset_usage` / a `fact_usage` link table; never stored | Stored copies go stale on every new version |
| `features` (§12.2) | JSON blob | **Keep JSON** in `reel_features(reel_id, schema_version, computed_at, producer_version, data)`, plus a SQL view `v_reel_features` that `json_extract`s the analysed fields | Under 1,000 reels JSON is fast. Features evolve quickly, and the view gives analytics typed columns without migrations |
| `metric_snapshot` | long format | **Keep long format.** Add `platform`, `metric_canonical`, `metric_raw`, `api_version` | Already right; canonical names make cross-platform work later trivial |
| `project.run`, `reel.brief`, `critique.scores` | JSON | Keep JSON (read whole, rarely queried) | |
| Transcript | `transcript_word` per clip | **`transcript`** (one per run: clip_id, producer, version, language, glossary_hash, is_current) → **`transcript_segment`** (phrase-level text, speaker, t_in_ms, t_out_ms) → **`transcript_word`**. FTS5 on **segments**, `tokenize = "unicode61 remove_diacritics 2"` | Re-running a better model (§5.1a) must not destroy corrected data. FTS over single words can't match phrases. `remove_diacritics 2` gives "zoncolan" → "Zoncolan" and "lizatko" → "lízatko" |
| Files | `clip.path`, `staged_path`, `hash` | **`file`** table (core): `root` (`media` / `data`), `rel_path`, `size`, `mtime`, `quick_hash` (xxh3-128 of head 4 MiB + tail 4 MiB + size), `full_hash` (filled lazily by a background job), `status` (present / missing / moved). `clip`, `asset`, sidecars and renders reference `file_id`. **Drop `staged_path`** | One path abstraction (Q6); move/duplicate detection in one place; staging was removed in §23.2 |
| `reel.ig_media_id`, `posted_at` | on reel | **`publication(reel_id, platform, account, media_id, url, posted_at, tz, trial: bool)`** | Trial Reels (§13.2), cross-posting (§15.6) and reposts each create a second publication; doing this now is cheap (Q8) |
| `reel.edits_project` | on reel and version | **`editor_ref`** JSON `{editor: "edits", project_id, project_name}` on `version` | Editor-neutral (Q8) |

**Moment / take / clip.** Keep the split, but define the time base: a **moment is anchored to one clip** (`clip_id`, `src_in_ms`, `src_out_ms`) and has an optional `take_id`. Alternative angles are **not stored** on the moment (`alt_angles` in §5.3). They are computed from the take's `device` offsets at read time, so re-syncing a take fixes every moment automatically. `rating`, `usable` and `reason_excluded` stay as columns. Add `origin` (`auto` / `human` / `agent`) and `confirmed_by`, because auto-suggested moments need a different trust level in search ranking.

**Migrations.** Alembic on SQLAlchemy 2.0 with `render_as_batch=True` (SQLite can't `ALTER` most constraints):
- **Forward-only.** §24.2 asks for "migrations up/down". Drop *down*: on SQLite, down-migrations are rarely correct and never used. Instead, `reels-hub db upgrade` first runs `VACUUM INTO '/data/backups/pre-<rev>-<ts>.db'`. Rollback = stop the container, restore that file, run the previous image.
- **Single linear history**, checked by a contract test (`alembic heads` must return exactly one head). Parallel branches will both create revision N+1. The rebase step in §24.1 adds: "re-point your migration's `down_revision` to the new head and re-run the suite". A `reels-hub db rebase-migration` helper does this automatically.
- **Upgrade test from real history:** every release tag saves a fixture DB (`tests/fixtures/db/v0.1.0.sqlite`, …). The suite upgrades each one to head and runs the smoke queries.
- **Pragmas** on every connection: `journal_mode=WAL`, `synchronous=NORMAL`, `foreign_keys=ON`, `busy_timeout=5000`. The DB must live on the `/data` named volume, **never on the `/media` bind mount**. SQLite WAL needs reliable shared-memory locking, and the macOS virtiofs share doesn't promise it (**unverified** for the current libkrun provider; don't test it in production).

#### Q4. Jobs: APScheduler vs. a persistent queue
**Use a small SQLite-backed job table owned by `core.jobs`. Remove APScheduler** (ADR-002, P2).

- **Facts (checked 2026-11-12):** APScheduler 4.x, the only line with persistent, multi-worker job stores, is still pre-release at **4.0.0a6 (April 2025)** and its README says "do NOT use this release in production" ([PyPI](https://pypi.org/project/APScheduler/4.0.0a6/)). The stable 3.11 line is a scheduler for in-process functions; it has no queue semantics, leases, progress or idempotency. Huey 3.5 ships `SqliteHuey` with retries and periodic tasks ([docs](https://huey.readthedocs.io/en/latest/guide.html)), but it keeps its own opaque DB and has no progress, DAG or idempotency key. We'd rebuild those on top anyway, and the job state is domain data the UI shows ("transcribing C0031 · 43 %").
- **Why a custom table is safe here:** one machine, one SQLite DB, a few hundred jobs a day. The whole thing is about 400 lines plus tests, and AI agents can write it reliably.

**Schema** (`job`):
```yaml
job:
  id: job_01JD…
  kind: footage.transcribe            # <module>.<verb>; handler registered by the module
  pool: heavy                         # heavy | media | light | net
  payload: { clip_id: clp_…, backend: cpu, model: large-v3 }
  idempotency_key: "footage.transcribe:clp_…:large-v3:glossary=3f2a"   # unique among non-failed jobs
  status: queued                      # queued | running | succeeded | failed | cancelled | dead
  priority: 50                        # lower runs first; interactive requests = 10
  attempts: 0
  max_attempts: 3
  run_after: 2026-11-12T10:00:00Z
  lease_until: null                   # set on claim; heartbeat extends it
  worker_id: null
  progress: 0.0                       # 0–1
  progress_note: null                 # "segment 41/96"
  parent_id: null                     # pipeline parent (ingest of one clip)
  result: null                        # JSON; asset/file ids, not blobs
  error: null                         # { code, message, retryable }
  created_by: { actor: agent|user|system, id: … }
  created_at / started_at / finished_at
```

**Mechanics**
- **Claim:** `UPDATE job SET status='running', lease_until=now+60s, worker_id=? WHERE id = (SELECT id FROM job WHERE status='queued' AND pool=? AND run_after<=now ORDER BY priority, created_at LIMIT 1) RETURNING *`, one transaction (`BEGIN IMMEDIATE`).
- **Heartbeat** every 15 s extends the lease. **On startup** and every 60 s, the reaper requeues `running` jobs whose lease has expired (attempts + 1). This is how a restart, a crash or `podman stop` mid-transcription recovers.
- **Pools and concurrency** (configurable; defaults for an 8-CPU/16 GB Podman machine): `heavy: 1` (transcribe, diarize, HyperFrames render, Demucs, full critique), `media: 2` (proxy, contact sheet, shot detection, frame extraction), `light: 4` (probe, hash, embeddings of text, lint), `net: 2` (Instagram, fact re-check, catalogs; rate-limited per host).
- **Retries:** exponential backoff of 30 s, 5 min, 30 min, then `dead` (shown in the UI's Today screen). Handlers raise `PermanentError` (corrupt file, unsupported codec) to skip retries.
- **Idempotency:** (1) the `idempotency_key` unique index means enqueueing the same work twice returns the existing job. (2) Outputs are content-addressed: `/data/derived/<file_quick_hash>/<step>/<params_hash>/…`, written to `*.tmp` then `rename()`d. (3) DB results are written in the **same transaction** that marks the job `succeeded`. Re-running a job after a crash just overwrites identical output.
- **Pipelines:** ingest for one clip is a parent job plus step jobs (`probe → proxy → transcribe → diarize → shots → embed → suggest_moments`). Per-clip step state lives in `clip_step(clip_id, step, status, producer_version)`. Bumping a step's `producer_version` in code makes a nightly job re-enqueue only stale steps. That covers "re-run when a better model ships" (§5.1a).
- **Scheduling without APScheduler:**
  - One-off future work is just a job with `run_after`. Linking a publication enqueues the 1 h / 24 h / 72 h / 7 d / 28 d metric pulls as 5 jobs with keys like `analytics.pull:pub_…:24h`.
  - Periodic work (watcher poll every 5 s, nightly backup at 03:00, daily account insights, daily fact re-check) is declared by each module as `job_schedule(name, cron, kind, payload)`. A 30 s scheduler loop enqueues the current period with key `<name>:<period_start>`. After downtime, the loop enqueues each missed schedule **once** (catch-up, not a backlog), and the unique key prevents duplicates.
  - The watcher poll runs in the scheduler loop itself, not as a job row, so 17,000 rows a day don't accumulate.
- **Progress reporting:** handlers call `ctx.progress(0.43, "segment 41/96")`, which is written at most every 2 s. The UI subscribes to `GET /api/jobs/events` (Server-Sent Events). MCP gets `get_job(id)` and `list_jobs(filter)`. Long MCP tools return `{job_id, status, poll_after_s}` immediately (Q5).
- **Cancellation:** `cancel_requested` flag. Handlers check it between steps, and the worker kills child processes (ffmpeg, node) after a 10 s grace period.
- **Retention:** succeeded jobs older than 30 days are deleted; failed and dead jobs are kept for 90 days.

#### Q5. MCP design: one server or groups, resources vs. tools, pagination, large payloads
**One server named `reels-hub`, Streamable HTTP only, about 55 tools.** Shape it for agents (ADR-003, P6):

- **One server, not several.** Tools share auth, audit and the approval gate, and the agent needs them together in one session. Context cost is solved on the client side: Claude Code defers MCP tool definitions behind tool search by default ([Claude Code docs: tool search](https://code.claude.com/docs/en/agent-sdk/tool-search), checked 2026-11-12). For clients without tool search, the server supports `?toolsets=footage,reels,design,…` on the `/mcp` URL (default: all) so a narrower profile can be configured per client.
- **Naming:** keep the spec's verb_noun names (they're already unique and readable; the client adds `mcp__reels-hub__`). Enforce `^[a-z][a-z0-9_]{2,47}$` in a contract test. This fits the Claude API tool-name limit of 64 characters including the client prefix (**unverified** for every client). Group tools in the registry by module and set `annotations.readOnlyHint` / `destructiveHint` / `idempotentHint` on every tool.
- **Transport:** drop the stdio mode from §21. The server lives in the container, so stdio would need `podman exec -i` and a second process writing to the same DB. Claude Code and Claude Desktop both connect over HTTP. The spec's MCP version is **2026-07-28 (stateless)**. Agent identity comes from the bearer token (one token per client, mapped to `agent_id`) plus an optional `X-Reels-Hub-Session` header used only for log grouping.
- **Resources vs. tools:** resources are for **stable, addressable context** (design language, playbook, glossary, stage table, project, reel, transcript by clip). Many agents never read resources on their own, so **every resource also has a `get_*` tool** returning the same content, and tool results reference big content with MCP `resource_link` items instead of inlining it.
- **MCP prompts primitive:** expose the reel prompt (§6.4) as an MCP **prompt** `reel_prompt(reel)`. Claude Code surfaces server prompts as slash commands, so "send to Claude" becomes `/mcp__reels-hub__reel_prompt giro05` with no clipboard step (**unverified** exact slash syntax in the current Claude Code release).
- **Response budget:** every tool response ≤ **8,000 tokens** by default (Claude Code warns on large MCP outputs and truncates at about 25,000 tokens by default; **unverified** current numbers). A contract test renders each tool against the fixture DB and fails above budget.
- **Pagination:** list and search tools take `limit` (default 20, max 100) and `cursor` (opaque, base64 of the sort key + id) and return `next_cursor`. Search results are **summaries** (id, 1-line transcript ≤ 120 chars, rating, tags, duration, thumbnail `resource_link`). Detail comes from `get_*`.
- **Transcripts:** `get_transcript(clip, range_ms?, granularity: segment|word = segment)`. Word granularity requires a range ≤ 120 s. A 13-min take at segment level is about 3–4k tokens; at word level it would be over 25k.
- **Frame sheets:** `frame_sheet` returns **one** JPEG grid (≤ 12 frames, long edge ≤ 1568 px, quality 80) as image content, plus `host_path`s of the full-resolution frames written to `/media/<project>/_hub/frames/` for when the agent needs detail.
- **Long-running tools** (`create_project` ingest, `render_motion`, `critique_reel mode=full`, `analyze_preview`): return `{job_id, status, poll_after_s}` and let the agent call `get_job`. Don't build on MCP Tasks yet: it was experimental in 2025-11-25 and moved to an extension with a changed lifecycle in 2026-07-28 ([RC notes](https://blog.modelcontextprotocol.io/posts/2026-07-28-release-candidate/)). Short operations (< 20 s, e.g. `fast` critique on cached frames, `generate_map`) stay synchronous with MCP progress notifications.
- **Errors:** tool execution errors (`isError: true`) with a machine code: `NOT_FOUND`, `CONFLICT_ROW_VERSION`, `APPROVAL_REQUIRED`, `EXCLUDED_RANGE_REASON_REQUIRED`, `JOB_PENDING`, `VALIDATION`. Input validation errors go back as tool errors, not protocol errors, so the model can self-correct (per MCP 2025-11-25 changelog, [source](https://modelcontextprotocol.io/specification/2025-11-25/changelog)).
- **Write tools** take `expected_row_version` where applicable and return the new version plus the `change_log` id, so §22's "agent writes are reversible" has a concrete `revert_change(change_id)` tool.
- **Missing tools** (gaps in §17.2): `get_job`, `list_jobs`, `cancel_job`, `list_reels(project, status?)`, `link_publication(reel, platform, media_id)`, `revert_change`, `add_pickup`, `list_open_items`.

#### Q6. Path mapping: where it lives
In **one module, `core/paths.py`**, and nowhere else (P3):
- **Storage:** the DB never stores absolute paths. `file.root ∈ {media, data}` + `file.rel_path` (POSIX, **NFC-normalised**). Container root and host root come from config. `REELS_HUB_HOST_MEDIA_ROOT` must be **absolute**: startup fails on `~`, relative paths or a trailing slash. §23.2 shows `host_path: ~/Movies/…`, which Edits and most tools won't expand.
- **One output type:** every tool, API response and prompt that mentions a file returns a `FileRef`:
  ```yaml
  file_ref:
    file_id: fil_01JD…
    host_path: /Users/lubos/Movies/ReelsHub/giro2027/raw/sony/C0031.MP4   # null if not on the Mac share
    url: http://127.0.0.1:8787/files/fil_01JD…                           # always works (UI, previews)
    container_path: /media/giro2027/raw/sony/C0031.MP4                    # debug only; agents must not use it
    edits_readable: true
  ```
- **`/data` files are not visible on the Mac.** Proxies, contact sheets and cached frames live on the named volume, so `host_path` is `null` and the `url` is used. Anything Edits or Claude must open as a file (graphics, motion renders, frame grids for agents, baked composites) is **materialised under `/media/<project>/_hub/<kind>/`**. §23.2 already says this for graphics; make it a rule for every module via `paths.publish_to_media(file_id, project, kind)`.
- **Contract test:** a JSON walker over every MCP tool's output in the fixture run fails if any string starting with `/media/` or `/data/` appears outside `container_path`. That makes "every tool returns the right path" a test, not a convention.
- **Verification on start:** the container writes `/media/.reels-hub-root.json` `{instance_id, container_root, written_at}`. `scripts/doctor.sh` (run on the Mac) checks that `$REELS_HUB_HOST_MEDIA_ROOT/.reels-hub-root.json` exists with the same `instance_id`, which proves the env var and the bind mount agree. The container smoke test (§23.6) runs the same check.
- **Unicode:** Slovak names in folders (`Terst`, `Rím`) can show up in NFD from macOS tools and NFC from Linux. Normalise to NFC for lookups. Keep the on-disk name byte-exact in `file.rel_path_raw` to open files. `create_project` enforces an ASCII slug for the project folder (`giro2027`).
- **Podman provider risk:** Podman 6 made `libkrun` the default macOS machine provider ([release notes](https://fossies.org/linux/podman/RELEASE_NOTES.md)), and users report stricter bind-mount permissions than `applehv` ([discussion #27679](https://github.com/podman-container-tools/podman/discussions/27679)). Writes from the container into `~/Movies/ReelsHub/<project>/_hub/` must be part of the container smoke test. Packet 11 (DevOps) should pick the provider.
- **Watcher:** inotify events don't cross the macOS share ([podman #22343](https://github.com/podman-container-tools/podman/issues/22343)), so the polling in §23.4 is correct. Poll `stat()` of the `raw/` trees every 5 s. A file is "stable" when its size and mtime haven't changed for two consecutive polls, and only then is it hashed and ingested. This prevents ingesting half-copied 14 GB cards.

#### Q7. Build order: phases and branches; thinnest vertical slice
**The phase order 0 → 1 → 2 → 9 → 3 is right, but phase 1 should be split.** Branches 11–13 (transcription, transcripts + FTS, moments) are enough for prompts. Speakers, sync, shots, embeddings and auto-moments are *quality* features that can merge after the slice works, which reduces risk before 1 December.

**Thinnest vertical slice ("New reel → prompt" end to end):** create project from YAML via CLI/MCP → register `raw/` → probe + proxy + CPU transcript → FTS search of segments → human or agent tags moments with `tag_moment` → design tokens + playbook + basic glossary imported → `create_reel(slot)` → `generate_reel_prompt` with facts, insights, music and critique providers returning "none yet" → prompt available as MCP prompt, `PROMPT.md` and clipboard. No speakers, sync, vision, embeddings or auto-suggest. This is branches 1–19 below.

**Ordered feature branches for phases 0–2 and 9** (each one merges on its own with the full suite green; "→" marks dependencies):

| # | Branch | Phase | Scope · merge test |
|---|---|---|---|
| 1 | `chore/repo-skeleton` | 0 | uv, ruff, mypy, pytest, import-linter contracts, `make test`, `CLAUDE.md`, `changes/` fragments, ADRs 0001–0004 · lint + empty suite pass |
| 2 | `chore/container-image` | 0 | `Containerfile.base` (Python 3.12, ffmpeg, Node 22, Chromium, OpenCV) tagged by lockfile hash; thin app image; `/health` · container smoke test |
| 3 | `feature/core-db` → 1 | 0 | engine + pragmas, Alembic, `ids`, `clock`, config validation · migration + single-head tests |
| 4 | `feature/core-audit` → 3 | 0 | `change_log`, `agent_log`, `UnitOfWork` with actor; `revert_change` · unit tests |
| 5 | `feature/core-jobs` → 3 | 0 | job table, pools, leases, reaper, schedules, SSE, `reels-hub run` supervisor · crash/restart test (kill worker mid-job, job completes once) |
| 6 | `feature/core-paths` → 3 | 0 | `file`, `FileRef`, host mapping, `publish_to_media`, `.reels-hub-root.json`, `doctor.sh` · path contract test |
| 7 | `feature/mcp-skeleton` → 4, 5, 6 | 0 | `/mcp` stateless HTTP, token auth, registry, errors, pagination, `get_job`/`list_jobs`/`host_paths` · MCP contract harness + budget test |
| 8 | `feature/ingest-register` → 5, 6 | 0 | poller with stability check, `quick_hash`, ffprobe, sidecar attach (`.LRF`, `.WAV`), shoot/clip/device rows · fixture Sony + DJI ingest |
| 9 | `feature/ingest-proxy` → 8 | 0 | 540p proxy, contact sheet every 2 s, thumbnails · fixture output dims/durations |
| 10 | `feature/ui-shell` → 7 | 0 | layout, nav, Library list, jobs panel (SSE) · Playwright smoke |
| 11 | `feature/transcribe-backend` → 5 | 1 | `Transcriber` protocol; `fake` (fixture JSON), `cpu` (faster-whisper), `host` client stub; glossary prompt · fake in suite, 5 s real-model test with a `tiny` cached model |
| 12 | `feature/transcripts-fts` → 9, 11 | 1 | transcript/segment/word tables, FTS5 `remove_diacritics 2`, `get_transcript` · diacritic search tests |
| 13 | `feature/moments-core` → 12 | 1 | moment + `moment_tag`, do-not-use ranges, `tag_moment`, `exclude_range`, `search_moments` (FTS + filters) · MCP contract |
| 14 | `feature/design-tokens` → 7 | 2 | import `DESIGN_LANGUAGE.md` front matter + YAML, versions, `get_style_tokens`, `hub://design-language/current` · golden import of the real file |
| 15 | `feature/playbook` → 7 | 2 | `playbook_item`, seed from §14, `get_playbook`/`add_playbook_item` |
| 16 | `feature/glossary-basic` → 7 | 2 | glossary sets + terms import, `hub://glossary/sk` (correction memory stays in phase 3) |
| 17 | `feature/projects` → 8, 14, 16 | 9 | `project`, media folders, `project_asset`, `create_project` (YAML/MCP/CLI), parent inheritance, auto-link of new footage |
| 18 | `feature/reels` → 17 | 9 | `reel`, slots, status machine, `publication`, `pickup`, `open_item`, `create_reel`/`update_reel`/`list_reels`, continuity check |
| 19 | `feature/reel-prompt` → 13, 15, 18 | 9 | gatherer with providers (`Null…` for facts/insights/music/critique), template v1, word budget, golden tests on a fixture project, MCP prompt + tool, `PROMPT.md` · **slice complete** |
| 20 | `feature/new-reel-ui` → 19 | 9 | Projects list, Create-project wizard, New reel screen with prompt preview/edit (saved as prompt version) · Playwright |
| 21 | `feature/mcp-resources` → 19 | 2 | all `hub://` resources + `get_*` mirrors, `resource_link`s in results |
| 22 | `feature/library-tagging-ui` → 13, 10 | 1 | transcript side panel, proxy player, `M` to mark moment |
| 23 | `feature/speakers` → 12 | 1 | diarization + voiceprints, speaker correction UI hook |
| 24 | `feature/multicam-sync` → 12 | 1 | take grouping, transcript-alignment sync, device offsets, `get_take` |
| 25 | `feature/shots-silences` → 9 | 1 | PySceneDetect shots, silence detection |
| 26 | `feature/moment-suggest` → 23, 25 | 1 | auto-suggested hooks/punchlines/sign-offs (`origin=auto`) |
| 27 | `feature/semantic-search` → 12 | 1 | text embeddings + sqlite-vec; visual embeddings later |
| 28 | `feature/frame-sheets` → 9, 6 | 2 | `frame_sheet` tool, publishing to `_hub/frames` |

Phase 3 (`feature/facts-store`, `feature/stage-table`, `feature/correction-memory`, `feature/script-lint`) follows. Each one replaces a `Null…Provider` in `reel-prompt`, with a golden-test update in the same branch.

**Sizing note:** sqlite-vec is still pre-1.0 (v0.1.9, March 2026; [GitHub](https://github.com/asg017/sqlite-vec)). Isolate it behind a `VectorIndex` interface in `footage/search.py` so an upgrade only touches that file.

#### Q8. Extensibility: other editors and platforms
**Abstract now (cheap now, expensive later):**
- **`publication` table** (Q3) instead of `reel.ig_media_id`/`posted_at`. One reel, many posts (IG, Trial Reel, YouTube Shorts, TikTok).
- **`editor_ref`** `{editor, project_id, project_name}` on `version`, and an **editor-neutral `CutList v1`**: tracks (`main`, `overlay`, `text`, `caption`, `music`, `sfx`), items referencing Hub `file_id` / `moment_id`, `src_in_ms` / `src_out_ms` / `rec_in_ms`, an `effects` list as free-form JSON, and `fps` + canvas. Keep field names close to OpenTimelineIO concepts (track / clip / source range) so an OTIO exporter is a mapping later, without adding the dependency now.
- **Playbook keyed by `tool`** (already done) and **metrics keyed by `platform` + `metric_canonical`** (Q3).
- **Platform profile as data** in the design system: `platform_profile: {id: instagram-reels, aspect: 9:16, fps_options: [24,30,60], max_runtime_s: 180, safe_zones: …, music_license_scope: meta}`. Lint, critique and the prompt read the profile, not constants. Max runtime and safe-zone numbers are **unverified** and belong to packet 07.
- **Analytics importer interface** `MetricsSource.pull(publication) -> list[MetricSnapshot]` in `integrations/`. Instagram is the only implementation.

**Later (don't build):** DaVinci Resolve / Final Cut exporters (OTIO/FCPXML), TikTok/YouTube importers, multi-user auth and roles, a plugin system. A "second editor" adapter isn't needed because the editor is driven by the agent through its own MCP. The Hub only needs to *record* the editor reference and an editor-neutral cut list.

### Proposals

#### P1. ADR-001: Python core, HyperFrames as subprocess, HTML UI, HTTP-only MCP
- **Type:** change
- **Section:** §21, §4
- **Proposal:** Settle the runtime question and remove the stdio MCP mode.
- **Suggested spec text:** In §21, replace the rows
  `| Runtime | Python 3.12 (FastAPI) **or** TypeScript (Node/Bun) | Both have mature MCP SDKs; Python is better for media and ML |` →
  `| Runtime | **Python 3.12** (FastAPI/ASGI, uv, SQLAlchemy 2 + Alembic). HyperFrames runs as a **Node 22 CLI subprocess** from \`render/\` inside the same image; no second service | Ingest, ML, music analysis and DB are Python; HyperFrames is the only Node part and is batch work (ADR-001) |`
  `| UI | Local web app (React or HTMX) on \`localhost\` | Simple, works in any browser |` →
  `| UI | Server-rendered **Jinja2 + HTMX + Alpine.js**, no JS build step; one isolated TypeScript player island allowed from phase 4 if needed | One language for AI agents, Playwright-testable |`
  `| Agent API | MCP server (stdio for Claude Code, streamable HTTP for others) | Standard for agents |` →
  `| Agent API | MCP server \`reels-hub\` on **Streamable HTTP only** at \`/mcp\`, spec 2026-07-28 (stateless), Python SDK \`mcp\` 2.x, mounted in the same ASGI app as the UI | The server lives in the container; stdio would need \`podman exec\` and a second DB writer |`
  In §4 add: "**Process model:** `reels-hub run` starts uvicorn (UI, REST, MCP) and a supervisor that spawns one worker process per job pool (§21 Jobs). Heavy work never runs in the web process."
- **Why:** 9 of 10 heavy dependencies are Python. One process tree fits D9. The MCP Python SDK 2.0.0 is stable (2026-07-28, [PyPI](https://pypi.org/project/mcp/)). Dropping stdio removes a second process writing to SQLite.
- **Priority:** must-have before build

#### P2. ADR-002: persistent SQLite job queue replaces APScheduler
- **Type:** change
- **Section:** §21 (Scheduling), §4, §23.4
- **Proposal:** Replace APScheduler with a `core.jobs` queue (lease, retries, idempotency key, pools, progress, schedules) as specified in Q4.
- **Suggested spec text:** In §21 replace `| Scheduling | Built-in job runner (APScheduler) | Ingest, metric pulls, fact re-checks |` →
  `| Jobs | **SQLite-backed job queue** in \`core.jobs\` (table \`job\`): leases with heartbeat (60 s / 15 s), reaper on start, retries 30 s → 5 min → 30 min then \`dead\`, unique \`idempotency_key\`, pools \`heavy:1 media:2 light:4 net:2\`, progress via SSE and MCP \`get_job\`. Periodic work declared as \`job_schedule\` rows (cron), enqueued once per period, catch-up once after downtime. No APScheduler | Long jobs survive restarts; job state is visible in UI and MCP (ADR-002) |`
  Add to §23.4 table: `| **Container restarts mid-job** | Transcription or render lost | Leased jobs are requeued on start; outputs written to \`*.tmp\` and renamed; DB result committed with job status |`
- **Why:** APScheduler 4 is still alpha 4.0.0a6 with a "do not use in production" warning ([PyPI](https://pypi.org/project/APScheduler/4.0.0a6/), checked 2026-11-12). 3.x has no queue, lease or progress. Job state is domain data the UI must show.
- **Priority:** must-have before build

#### P3. One path abstraction: `file` table + `FileRef`, enforced by a contract test
- **Type:** change
- **Section:** §23.2, §5.1 step 8, §18 (`clip`)
- **Proposal:** Store `root + rel_path` only, compute host/container paths in `core/paths.py`, return `FileRef` everywhere, publish Edits-needed files under `/media/<project>/_hub/`, verify the mount on start, and test that no container path leaks.
- **Suggested spec text:** Replace the §23.2 bullets from "Every file record stores both paths:" through "Mapping is configured once: …" with:
  "- The DB stores **no absolute paths**: each file is `file(root: media|data, rel_path, size, mtime, quick_hash, full_hash, status)`. `core/paths.py` is the only code that turns it into paths.
  - Every tool, API response and prompt returns a **FileRef**: `{file_id, host_path, url, container_path, edits_readable}`. `host_path` is `null` for files on `/data`; `url` (`http://127.0.0.1:8787/files/<id>`) always works.
  - `REELS_HUB_HOST_MEDIA_ROOT` must be an **absolute** path (e.g. `/Users/lubos/Movies/ReelsHub`); the container refuses to start on `~` or a relative path.
  - Anything Edits or an agent must open as a file (graphics, motion renders, frame grids, baked composites) is published to `/media/<project>/_hub/<kind>/`.
  - On start the container writes `/media/.reels-hub-root.json`; `scripts/doctor.sh` on the Mac checks it under the host root.
  - Contract test: no MCP output may contain a string starting with `/media/` or `/data/` outside `container_path`.
  - File names are NFC-normalised for lookups; project folders use ASCII slugs."
  In §5.1 step 8 replace "Record both paths: container path and Mac (host) path, …" → "**Register the file** (`root=media`, relative path, quick hash); host paths are derived (§23.2)." In §18 `clip` row replace `path, hash, staged_path` → `file_id`.
- **Why:** `~` in `host_path` isn't usable by Edits. `/data` files have no host path at all. Per-record dual paths go stale when the root changes. Podman 6 defaults to `libkrun` on macOS with stricter share permissions ([release notes](https://fossies.org/linux/podman/RELEASE_NOTES.md), [#27679](https://github.com/podman-container-tools/podman/discussions/27679)), so writes into `_hub/` must be smoke-tested.
- **Priority:** must-have before build

#### P4. ADR-004: data-model rules and §18 corrections
- **Type:** change
- **Section:** §18, §5.3
- **Proposal:** Add global rules (prefixed ULID ids + slugs, integer ms, UTC, `row_version`, provenance) and fix the specific tables as in Q3.
- **Suggested spec text:** Insert at the top of §18:
  "**Rules (ADR-004)**
  - IDs: type prefix + ULID (`clp_…`, `mom_…`, `rel_…`); projects and reels also have a unique slug (`giro2027-advent`, `giro00`); foreign keys always use ids.
  - Media times are **integer milliseconds** (`src_in_ms`); timestamps are UTC ISO-8601; `publication.tz` keeps the local zone.
  - Mutable rows edited by both humans and agents carry `row_version`; updates must pass `expected_row_version`.
  - Derived rows store `producer` and `producer_version`; re-runs add rows, never overwrite.
  - `*.used_in` lists are never stored; they are derived from `cut_item` and `asset_usage`."
  Replace/add these rows in the Key tables:
  `| \`file\` | id, root (media/data), rel_path, rel_path_raw, size, mtime, quick_hash, full_hash, status |`
  `| \`clip\` | id, file_id, camera, device_id, duration_ms, fps, res, start_tc, shoot_id, take_id |`
  `| \`transcript\` / \`transcript_segment\` / \`transcript_word\` | clip_id, producer, producer_version, language, glossary_hash, is_current / transcript_id, t_in_ms, t_out_ms, text, speaker / segment_id, t_in_ms, t_out_ms, text, speaker, confidence |`
  `| \`segment_fts\` | FTS5 over transcript_segment.text, \`tokenize = "unicode61 remove_diacritics 2"\` |`
  `| \`moment\` / \`moment_tag\` | id, clip_id, take_id, src_in_ms, src_out_ms, rating, usable, reason_excluded, origin (auto/human/agent), confirmed_by, notes, row_version / moment_id, tag |`
  `| \`publication\` | id, reel_id, platform, account, media_id, url, posted_at, tz, trial |`
  `| \`version\` | id, reel_id, n, editor_ref (json: editor, project_id, project_name), cut_list (json, CutList v1 snapshot, immutable), content_hash, preview_file_id, created_at |`
  `| \`cut_item\` / \`caption_item\` | derived index of version.cut_list, written in the same transaction |`
  `| \`reel_features\` | reel_id, schema_version, computed_at, producer_version, data (json); view \`v_reel_features\` exposes analysed fields |`
  `| \`metric_snapshot\` | publication_id, window, platform, metric_canonical, metric_raw, value, api_version, pulled_at |`
  Remove `ig_media_id, posted_at` from `reel` and `staged_path` from `clip`. In §5.3, remove `used_in` and `alt_angles` from the moment YAML and add: "Alternative angles are computed from the take's device offsets at read time; usage is derived from versions."
- **Why:** v0.4 contradicts itself (`cut_item` vs. `cut_list`, `staged_path` vs. §23.2). Float seconds break sync and cut equality. Stored `used_in` lists go stale. Transcript re-runs would overwrite human corrections. Tag filtering needs an index.
- **Priority:** must-have before build

#### P5. Module layout, layering and registration
- **Type:** addition
- **Section:** §4 (new §4.1), §24
- **Proposal:** Adopt the repo layout, table ownership and layering from Q2; enforce them with import-linter; one `register()` per module; changelog fragments.
- **Suggested spec text:** New §4.1:
  "### 4.1 Code structure
  - Package `reels_hub` with `core/` (db, ids, clock, paths, jobs, events, audit, assets, auth), `integrations/` (Instagram, music catalogs, transcription backends, HyperFrames, LLM), `modules/<name>/` (footage, projects, facts, language, design, graphics, reviews, analytics, playbook, music, reelprompt, critique, learning), and the interfaces `api/`, `ui/`, `mcp/`, `cli/`.
  - Layers (import-linter, part of the suite): interfaces → orchestration (reelprompt, critique, learning) → domain modules → integrations → core. A module uses another only through its `service.py` and `schemas.py`.
  - Each module owns its tables (table in ADR-004) and exposes `register(hub)` that adds routes, MCP tools, job handlers, event handlers, schedules and nav items. `app.py` lists enabled modules; that is the only shared edit per feature.
  - Orchestration modules depend on providers (`FactsProvider`, `InsightsProvider`, `MusicProvider`, `CritiqueProvider`) with `Null…` defaults, so they can ship before the modules they read."
  In §24.3 replace "`CHANGELOG.md`" → "a changelog fragment `changes/<branch-name>.md` (collected into `CHANGELOG.md` at release)".
- **Why:** Without registration points and ownership, every parallel branch edits the same schema, tool list, router and changelog, so D10 merges turn into conflict resolution done by AI agents.
- **Priority:** must-have before build

#### P6. ADR-003: MCP shape, budgets, pagination, async jobs
- **Type:** change
- **Section:** §17 (new §17.4), §17.2
- **Proposal:** One server; toolsets filter; every resource mirrored by a `get_*` tool; `resource_link` for bulk data; 8k-token response budget with a contract test; cursor pagination; segment-level transcripts by default; long tools return `job_id`; error codes; reel prompt also as an MCP prompt; add the missing tools.
- **Suggested spec text:** New §17.4:
  "### 17.4 Interface rules (ADR-003)
  - One server `reels-hub`, Streamable HTTP at `/mcp`. Optional `?toolsets=footage,reels,facts,design,graphics,music,reviews,analytics,playbook,jobs` to narrow the tool list per client; default all.
  - Tool names `^[a-z][a-z0-9_]{2,47}$`, with `readOnlyHint` / `destructiveHint` / `idempotentHint` annotations.
  - Every `hub://` resource has a matching `get_*` tool. Tool results reference large content with `resource_link` instead of inlining it.
  - Response budget: ≤ 8,000 tokens per tool response by default, checked by a contract test.
  - Lists and searches: `limit` (default 20, max 100), opaque `cursor`, `next_cursor`; search returns summaries, details via `get_*`.
  - `get_transcript` returns segments by default; `granularity=word` needs a range ≤ 120 s.
  - `frame_sheet` returns one JPEG grid (≤ 12 frames, long edge ≤ 1568 px) plus host paths of full-resolution frames under `/media/<project>/_hub/frames/`.
  - Operations that can take over 20 s return `{job_id, status, poll_after_s}`; the agent polls `get_job`. MCP Tasks will be adopted once the extension is supported by Claude Code.
  - Errors are tool errors with a code: `NOT_FOUND`, `VALIDATION`, `CONFLICT_ROW_VERSION`, `APPROVAL_REQUIRED`, `EXCLUDED_RANGE_REASON_REQUIRED`, `JOB_PENDING`.
  - Write tools accept `expected_row_version` and return a `change_id`; `revert_change(change_id)` undoes it.
  - The reel prompt is also exposed as an MCP prompt `reel_prompt(reel)`."
  Add to §17.2 a **Jobs and admin** group: `get_job(id)`, `list_jobs(filter)`, `cancel_job(id)`, `revert_change(change_id)`. Add to **Projects and reels**: `list_reels(project, status?)`, `link_publication(reel, platform, media_id, trial?)`, `add_pickup(reel, text, reason)`, `list_open_items(scope)`.
- **Why:** About 55 tools and 13-min transcripts would blow agent context. Claude Code defers MCP tools behind tool search ([docs](https://code.claude.com/docs/en/agent-sdk/tool-search)), but large *results* still land in context. MCP Tasks moved out of core in 2026-07-28 with a changed lifecycle ([source](https://blog.modelcontextprotocol.io/posts/2026-07-28-release-candidate/)), so polling `get_job` is the portable choice.
- **Priority:** before phase 2 (the skeleton rules apply from branch 7 in phase 0)

#### P7. The approval gate can't block Edits exports server-side
- **Type:** risk
- **Section:** §11.3, §17.3, §22
- **Proposal:** State what the Hub can and can't enforce. Bind approvals to a version **content hash**. Enforce on the client side with a Claude Code `PreToolUse` hook on the Edits MCP export tool that calls `reels-hub approval check`.
- **Suggested spec text:** Add to §11.3:
  "- **Enforcement boundary:** the Hub enforces the gate for its own tools (final render, publish, status `exported`). Export inside Edits happens through the Edits MCP, which the Hub doesn't see. There the gate is enforced by a **Claude Code `PreToolUse` hook** matching the Edits export tool (`mcp__<edits-server>__<export-tool>`) that runs `reels-hub approval check --edits-project <id>` and denies the call unless the latest version of that Edits project is approved.
  - An approval binds to `version.content_hash` (hash of the canonical cut list + preview file hash). `export_allowed` recomputes it; any change invalidates the approval.
  - The repo ships the hook in `.claude/settings.json` and `scripts/approval-check.sh`."
- **Why:** §11.3 says export tools "refuse", but the only export tool is in Edits. Claude Code `PreToolUse` hooks can deny MCP tool calls by name pattern `mcp__<server>__<tool>` ([hooks reference](https://code.claude.com/docs/en/hooks), checked 2026-11-12). The Edits MCP export tool name is **unverified**; confirm it in the playbook. Edits made by hand in the Edits app can't be gated at all, so the content hash is the backstop.
- **Priority:** before phase 4

#### P8. Forward-only migrations with automatic backup and history tests
- **Type:** change
- **Section:** §24.2 (Database row), §23.6
- **Proposal:** Replace up/down migrations with forward-only Alembic plus a pre-migration snapshot, a single-head check and upgrade tests from every released schema.
- **Suggested spec text:** In §24.2 replace `| Database | Migrations up/down, constraints, FTS and vector queries | pytest + temp SQLite |` →
  `| Database | Forward-only Alembic migrations (\`render_as_batch\`); exactly one head; upgrade from every released fixture DB (\`tests/fixtures/db/v*.sqlite\`) to head; constraints, FTS and vector queries | pytest + temp SQLite |`
  In §23.6 replace "DB migrations run on start." → "DB migrations run on start after `VACUUM INTO /data/backups/pre-<rev>-<timestamp>.db`. Rollback = restore that file and run the previous image tag. Connections use WAL, `synchronous=NORMAL`, `foreign_keys=ON`, `busy_timeout=5000`; the DB never lives on the `/media` share."
  Add to §24.1 step 4: "If the branch adds a migration, re-point its `down_revision` to the current head after rebasing (`reels-hub db rebase-migration`)."
- **Why:** SQLite down-migrations are rarely correct and never exercised. Parallel branches will always collide on the next revision number. A snapshot is a real rollback.
- **Priority:** must-have before build

#### P9. Branch plan for phases 0–2 and 9 with an early vertical slice
- **Type:** change
- **Section:** §25
- **Proposal:** Adopt the 28-branch order from Q7. Split phase 1 into "core" (transcripts, FTS, moments) and "quality" (speakers, sync, shots, auto-moments, embeddings), and run phase 9 right after phase 1 core.
- **Suggested spec text:** In §25 replace the phase 1 row with two rows:
  `| **1a · Transcripts and moments (core)** | Transcription backend (CPU + fake), transcript tables, FTS5 search, manual/agent moment tagging, do-not-use ranges | Agents can find lines and tag moments |`
  `| **1b · Footage intelligence** (after 9) | Speakers, multicam sync, shots/silences, auto-suggested moments, semantic search, tagging UI | Finding the hook takes minutes |`
  Replace the "Target before December 1" paragraph with: "**Target before December 1:** phase 0, 1a, the minimal parts of 2 (design tokens, playbook, basic glossary), and 9: the vertical slice *create project → ingest → transcript search → tag moments → New reel → prompt* (branches 1–19 in `docs/branch-plan.md`). Then 1b, the rest of 2, and 3. Critique (10) and analytics (5) can start mid-project; early posts are backfilled from the API."
- **Why:** As written, prompts wait for diarization, sync and vision, the riskiest ML work. The slice gets the main flow (§19.0) running with the least ML risk.
- **Priority:** must-have before build

#### P10. Internal domain events (outbox) for cross-module reactions
- **Type:** addition
- **Section:** §4 (in new §4.1), §16.5, §19.4
- **Proposal:** Add a `core.events` outbox. Modules publish facts (`version.created`, `publication.linked`, `clip.transcribed`, `fact.status_changed`); other modules subscribe and enqueue jobs. No direct cross-module calls for reactions.
- **Suggested spec text:** Add to §4.1: "- **Events:** state changes that other modules react to are written to an `event` table in the same transaction (`clip.ingested`, `clip.transcribed`, `version.created`, `approval.granted`, `approval.invalidated`, `publication.linked`, `fact.status_changed`). Subscribers are registered via `register(hub)` and typically enqueue a job keyed by the event id, so each reaction runs once even after restarts."
- **Why:** §16.5 ("on every new version run critique") and §19.4 ("scheduled pulls after posting") otherwise force `reviews` to import `critique` and `projects` to import `analytics`, breaking the layering in P5.
- **Priority:** before phase 4

#### P11. Test tiers and a cached base image so "full suite per merge" stays fast
- **Type:** change
- **Section:** §24.2, §23.6
- **Proposal:** Keep D10's "full suite before merge", but make it practical: base image cached by lockfile hash, ML stubbed by default with one tiny real-model test, deterministic clock and ids for golden tests, and a time budget.
- **Suggested spec text:** Add to §24.2 after the table:
  "- **Base image** `reels-hub-base:<hash of uv.lock + render/package-lock.json + Containerfile.base>` holds Python, ffmpeg, Node 22, Chromium, OpenCV and ML wheels; it's rebuilt only when that hash changes. The app image is a thin layer on top.
  - Tests use the `fake` transcriber, renderer and LLM by default. One marked test per backend runs the real engine on a 5 s fixture with the smallest model, cached in `/data/models`.
  - Golden tests inject a fixed clock and id generator (`core.clock`, `core.ids`).
  - Budget: `make test` (everything except container) ≤ 5 min; `make test-full` (adds image build + container smoke) ≤ 15 min with a warm base image. `make test-full` is the pre-merge gate."
- **Why:** The image holds Chromium, torch, pyannote and OpenCV; cold builds take tens of minutes (**unverified** estimate). Without caching, D10 makes agents wait or skip the suite. Non-deterministic ids and clocks make golden tests flaky.
- **Priority:** must-have before build (phase 0)

#### P12. Editor- and platform-neutral records
- **Type:** addition
- **Section:** §18, §9, §12.1
- **Proposal:** Do only the cheap parts now: `publication` (in P4), `editor_ref` + `CutList v1` with OTIO-like fields, a `platform_profile` in the design system, and an importer interface. Postpone other editors and platforms.
- **Suggested spec text:** Add to §9: "- **Platform profiles** as data: `platform_profile: {id: instagram-reels, aspect: \"9:16\", fps_options: [24, 30, 60], max_runtime_s: <confirm>, safe_zones: {…}, music_license_scope: meta}`. Lint, critique and the reel prompt read the profile of the reel's publication target, never hard-coded values."
  Add to §18 after the key tables: "**CutList v1** (editor-neutral, stored in `version.cut_list`): `{schema: 1, fps, canvas_px, tracks: [{kind: main|overlay|text|caption|music|sfx, items: [{ref: file_id|moment_id|asset_id, src_in_ms, src_out_ms, rec_in_ms, effects: {…}}]}]}`. Field names follow OpenTimelineIO concepts so an OTIO/FCPXML exporter is a mapping later."
  Add to §12.1: "Importers implement `MetricsSource.pull(publication) → [metric_snapshot]`; Instagram is the first implementation."
- **Why:** These shapes are cheap to get right now and need a data migration to change once there are 24 reels of history. Everything else (DaVinci, TikTok) is speculative and should wait.
- **Priority:** before phase 9

#### P13. Delivery risk: 19 days to 1 December
- **Type:** risk
- **Section:** §25
- **Proposal:** No change to D2. Record the consequence and the cut line: if branch 19 (`feature/reel-prompt`) isn't merged by **2026-11-26**, the December project starts with the Hub as a footage index + MCP only, and prompts are written by hand from `hub://` resources.
- **Suggested spec text:** Add to §27: `| Phases 0, 1a, 2 (min) and 9 are about 4–5 weeks of nominal work but have 19 days before 1 December (2026-11-12 → 2026-12-01) | Build the slice first (branches 1–19); checkpoint 2026-11-26: if \`feature/reel-prompt\` isn't on \`main\`, run December with ingest + search + MCP read tools and hand-written prompts, and finish phase 9 during the project |`
- **Why:** D2 accepts the timeline. This only names the fallback so nobody discovers it on 30 November.
- **Priority:** must-have before build

**Sign-off:** approve with changes
