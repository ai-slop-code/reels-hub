# Review packet 11: DevOps (Mac + Podman)

**Priority:** before phase 0 (foundations)
**Time needed:** ~1.5 h
**Decisions already made:** D9 one Podman container, media at `~/Movies/ReelsHub`; D10 branch-per-feature with full tests before merge (see [README](README.md#decisions-already-made-please-dont-reopen)).

## Why you
Podman on macOS runs a Linux VM with real limits: no Metal GPU, slower file access through the VM, unreliable file-change events. The setup has to stay fast and painless for daily production.

## Read
- [§23 Deployment (Podman)](../spec/REELS_HUB_SPEC.md#23-deployment-podman)
- [§24 Development workflow](../spec/REELS_HUB_SPEC.md#24-development-workflow)
- [§21 Tech stack](../spec/REELS_HUB_SPEC.md#21-tech-stack)
- [§5.1 Ingest](../spec/REELS_HUB_SPEC.md#5-module-a-footage-index-and-moments)

## Questions
1. **Podman machine:** provider (applehv vs. libkrun), sizing (CPU, RAM, disk) for 4K ingest, transcription and HyperFrames rendering.
2. **File access:** bind-mounting `~/Movies/ReelsHub` (14 GB clips). Expected throughput through virtiofs; anything to tune? Is partial hashing enough?
3. **Watching:** polling interval vs. a small Mac-side notifier that pings the container.
4. **GPU helper:** the optional Mac service with mlx-whisper (§23.5). Run it via launchd? Packaging (pipx, Homebrew)?
5. **Image:** multi-stage build with Python, ffmpeg, OpenCV, Node 22 and Chromium. Size, build time, caching. Arm64 only?
6. **Lifecycle:** restarts, updates without losing jobs, migrations on start, health checks, logs.
7. **Tests in the container:** the smoke test in §24.2. Run it locally for every branch before merge; how to keep it fast?
8. **Backups:** SQLite `.backup` to `/media/_backups` (Time Machine). Good enough? Restore drill?

## Your input

*Reviewed against spec v0.5. All 8 questions still apply to v0.5. Q6 is answered within R13: a simple `job` table, with no leases or heartbeats.*

**What I checked (2026-11-12):**
- On the build machine, read-only: `podman --version` gives 6.1.4. `podman machine inspect` shows applehv, 5 CPUs, 8 GiB, 100 GiB, `UserModeNetworking: true`, `Rosetta: false`. The host is an Apple M5 with 10 cores and 24 GiB RAM on macOS 26.7.3.
- [Podman v6.0.0 release notes](https://github.com/containers/podman/releases/tag/v6.0.0): Intel Macs are no longer supported. The default macOS provider is now `libkrun`, and `podman machine init --provider` is new. `podman image scp --format` was added. `podman volume prune` now removes only anonymous volumes.
- [Discussion #27679](https://github.com/podman-container-tools/podman/discussions/27679): reports of bind-mount permission problems on `libkrun` that don't happen on `applehv`.
- [Podman Desktop 1.29 notes](https://podman-desktop.io/blog/podman-desktop-release-1.29): Intel Macs stay on Podman 5.x.
- [HyperFrames rendering guide](https://hyperframes.heygen.com/guides/rendering) and [hyperframes.app rendering docs](https://hyperframes.app/docs/3-guides/4-rendering): rendering uses Puppeteer with a bundled Chromium plus the system FFmpeg.
- Anything I give from memory is marked **unverified**.

### Summary
The deployment design fits a one-person tool: one image, one container, footage bind-mounted from `~/Movies/ReelsHub`, and the DB in a named volume. The spec still assumes **one Mac**, but the work now happens on two:
- The **M5 build machine** only builds and tests.
- The **old Mac** runs the Hub with the real footage, and its hardware is unknown.

That leaves four gaps:
- **Image architecture and Podman version depend on the old Mac's CPU.** Podman 6 dropped Intel Macs. On an Intel run machine the image must be `amd64` and the run machine stays on Podman 5.x.
- **No release path from the build machine to the run machine.** Proposed: `podman save` to a file, copy it over, then `podman load` and a small `hubctl` script.
- **The spec's machine sizing (8 CPUs / 16 GB / 200 GB) is likely too big for an older MacBook.**
- **Data loss.** The DB lives inside the Podman VM disk. A `podman machine rm`/`reset` wipes it. The backup in `/media/_backups` is the only copy and needs a restore drill.

The other changes are small and concrete: the watcher only registers a file once it's fully copied, start-on-login, the health check in the run command, Chromium from Debian, and phase 0's "done when" measured on the run machine.

### Answers

#### Q1. Podman machine: provider and sizing
**Provider:** use **`applehv`** explicitly on both machines: `podman machine init --provider applehv …` (the flag is new in Podman 6).
- `libkrun` became the default in 6.0. Its advantage is a GPU passed into the VM via Vulkan (Venus), not Metal. mlx-whisper, CTranslate2 (faster-whisper) and OpenCV wouldn't use it.
- There are reports of bind-mount permission problems with `libkrun` (#27679). 6.0.1 fixed a bug where a host port scan could shut down `libkrun` VMs.
- The build machine already runs `applehv`, so tests and production use the same provider.
- If the old Mac is Intel, Podman 5.x uses `applehv` anyway.

**Sizing for the run machine** (it does all the heavy work: proxies, transcription, renders):

| Old Mac RAM | `--cpus` | `--memory` | `--disk-size` | Notes |
|---|---|---|---|---|
| 8 GB | cores − 2 | 5120 | 100 | Tight. Transcription with large-v3 int8 needs ≈ 3–4 GB (unverified); use the Mac helper (if Apple Silicon) or a smaller or turbo model |
| 16 GB | cores − 2 | 8192 | 100 | Recommended minimum |
| ≥ 24 GB | cores − 2 | 12288 | 100 | Comfortable |

Leave 2 cores and at least 6 GB for macOS, Edits and Claude, because Edits is open during the edit while the worker may be rendering.

`--disk-size 100` is enough: the image (current + previous) ≈ 5 GB, Whisper models 3–6 GB, `/data` proxies and contact sheets ≈ 2 % of masters (≈ 18 GB for 900 GB of footage), DB < 1 GB. The VM disk is a sparse file that grows but never shrinks, so a 200 GB cap only means a larger possible footprint on what is probably a small SSD.

Podman 6 refuses `--cpus` above the host's core count, so the spec's 8 CPUs fails on a 4- or 6-core Mac. **Build machine:** the current 5 CPUs / 8 GiB / 100 GiB is fine for builds and the smoke test. Leave it as is.

#### Q2. File access through the VM (virtiofs)
- **Throughput:** I can't measure it here because there's no footage on this machine. From memory (**unverified**), virtiofs on `applehv` reads large files sequentially at several hundred MB/s up to above 1 GB/s on Apple Silicon. That isn't the bottleneck. **Video decode on the CPU is**: 4K H.264/HEVC is decoded in software inside the VM, with no VideoToolbox. Measure once on the run machine:
  ```bash
  time podman run --rm -v "$HOME/Movies/ReelsHub":/media:ro localhost/reels-hub:<version> dd if=/media/giro00/raw/sony/C0031.MP4 of=/dev/null bs=8M
  ```
  ```bash
  time podman run --rm -v "$HOME/Movies/ReelsHub":/media:ro localhost/reels-hub:<version> ffmpeg -v error -i /media/giro00/raw/sony/C0031.MP4 -vf scale=-2:540:flags=fast_bilinear -c:v libx264 -preset veryfast -crf 28 -an -f null -
  ```
  The first command measures read speed and the second measures proxy speed.
- **Tuning:**
  - Drop `:z` from the bind mount. It asks for SELinux relabelling of every file in the VM. On a macOS virtiofs share that's at best a no-op and at worst a slow walk over 14 GB files (**unverified** which one).
  - Keep many-small-file writes (contact-sheet JPEGs, frame dumps) in `/data`, not on `/media`.
  - Make proxies from the camera's own low-res files where they exist. DJI `.LRF` is already a low-res H.264 proxy. Sony bodies can record proxies (camera setting), so check the model. That removes most of the 4K decode work, which decides whether phase 0's "Giro_00 drop in ≤ 30 min" is reachable on an older Mac (see P8).
- **Partial hashing:** enough. Use xxh3-128 over the first 1 MiB, the last 1 MiB and the size, and on re-attach (R27) also compare the ffprobe duration. Camera MP4 headers carry creation time and timecode, so collisions between real clips are practically impossible. **The real risk is hashing a file that is still being copied** (Finder copy, `cp` from the card): the tail hash is wrong and ffprobe fails or reads a truncated file. Rule: register a file only after its **size and mtime have stayed the same for 2 polls ≥ 10 s apart and ffprobe succeeds**.

#### Q3. Watching: polling or a Mac-side notifier
**Polling. No notifier.** In v0.5 the poll is only a fallback, because the producer clicks **Add footage** (or calls `add_footage`) after copying the cards. That click should trigger an immediate scan of the project's `raw/` folders.
- Background poll every **10 s** using `os.scandir` over `/media/*/raw/**`. That's a few hundred `stat` calls over virtiofs, negligible.
- Ignore `._*`, `.DS_Store`, `.Spotlight-V100`, `.Trashes`, `*.download`, `*.part`, and names starting with `~` or `.`.
- Treat `.LRF` and `.WAV` as sidecars (§5.1).
- A Mac notifier (fswatch or FSEvents → HTTP ping) would be a second process on the Mac to install, start at login and monitor, which goes against R56 for a saving of at most 10 s.

**Missing-mount guard:** if the bind mount is empty (VM started without the share, or the folder renamed), the watcher must **not** mark the whole library `offline` (R27). The Hub writes a marker file `/media/.reels-hub-root` on first setup. While it's missing, the watcher pauses and `/health` reports `media_mounted: false`.

#### Q4. The GPU helper (§23.5)
Only build it if the §5.1a benchmark run **on the run machine** shows CPU transcription is too slow. **It only works if the old Mac is Apple Silicon**, because MLX requires Apple Silicon.
- **Packaging:** use `uv tool install` from a wheel built on the build machine (`uv build`, then copy `reels_hub_transcribe-<v>-py3-none-any.whl`). Not pipx, not a Homebrew tap. That's one tool (uv) on the run machine and no tap to maintain.
- **Service:** a launchd user agent at `~/Library/LaunchAgents/sk.reelshub.transcribe.plist`:
  - `RunAtLoad` true, `KeepAlive` true
  - `ProgramArguments` = `[~/.local/bin/reels-hub-transcribe, --host, 127.0.0.1, --port, 8788]`
  - `StandardOutPath` and `StandardErrorPath` = `~/Library/Logs/ReelsHub/transcribe.log`
  - `EnvironmentVariables.HF_HOME=~/Library/Caches/ReelsHub/hf`
  - Load with `launchctl bootstrap gui/$(id -u) <plist>`.
- **Security:** the helper accepts only paths under `REELS_HUB_HOST_MEDIA_ROOT`.
- **Reachability:** with gvproxy user-mode networking, `host.containers.internal` should forward to the Mac's `127.0.0.1` (from memory, **unverified**). Check from the container with `curl -fsS http://host.containers.internal:8788/health` before relying on it.
- **File access:** if launchd agents can't read `~/Movies`, grant Full Disk Access to the helper binary (**unverified**; `~/Movies` is not one of the folders macOS protects by default, as far as I know).

#### Q5. Image
Build with `podman build --platform linux/<arch>`, one target per run machine:
- **arm64 only** if the old Mac is Apple Silicon.
- **amd64 only** if it's Intel. Build it on the M5 with `--platform linux/amd64`, which runs under emulation and is slow. Enabling Rosetta for the machine is **unverified** for Podman 6 + applehv; the build machine currently has `Rosetta: false`.

Never build multi-arch for one user.

Stages:
1. `node` stage: `node:22-bookworm-slim`, `npm ci` with a committed `package-lock.json` that pins `hyperframes` to an exact version (the docs show 0.7.x). Never `npx` at runtime, because that downloads on first render.
2. `runtime` stage: `python:3.12-slim-bookworm` pinned by digest, plus:
   - `apt-get install --no-install-recommends ffmpeg chromium fonts-noto-core` (OFL fonts only, R46)
   - Node binary and `node_modules` copied from stage 1
   - `PUPPETEER_SKIP_DOWNLOAD=1` and `PUPPETEER_EXECUTABLE_PATH=/usr/bin/chromium`. Chrome for Testing has published no linux-arm64 builds (from memory, **unverified** for 2026), so Puppeteer's bundled download fails or is x86-only on arm64. Debian's `chromium` works on both architectures. Whether HyperFrames respects `PUPPETEER_EXECUTABLE_PATH` or has its own flag is **unverified**; check `hyperframes doctor`.
   - Python dependencies through `uv sync --frozen --no-dev --no-install-project` in a layer **before** `COPY src/`, with `RUN --mount=type=cache,target=/root/.cache/uv`.
   - `opencv-python-headless` (wheel, not apt).
   - If torch is needed (WhisperX/pyannote, Demucs), install it from the CPU index `https://download.pytorch.org/whl/cpu`. On amd64, the default PyPI torch includes CUDA (+2–3 GB).
3. `test` stage: `FROM runtime` + dev dependencies + `tests/`. Never shipped.

**Size budget:** ≈ 1.8–2.5 GB uncompressed (arm64, no torch). With torch CPU ≈ +0.5–1 GB. All estimates, **unverified**. The build should fail above 3.5 GB.

**Build time:** cold ≈ 8–15 min on the M5. A code-only change ≈ 20–60 s, because only the `COPY src/` layer changes (estimate).

**Gotcha:** Podman builds in OCI format by default and **drops `HEALTHCHECK`** from the Containerfile with only a warning. Put the health check in the run command (P3) or build with `--format docker`. I prefer the run command.

**Models:** download into `/data/models` on first use (as specified), with the Hugging Face revision pinned in config next to the model ID. Add `reels-hub models pull` so the download happens once on setup and not during the first real ingest.

**Labels:** `org.opencontainers.image.version` and `org.opencontainers.image.revision` (git SHA). `/health` echoes both.

#### Q6. Lifecycle
- **Start after login or reboot:**
  - The Podman VM does **not** start by itself on macOS. Add a launchd agent `sk.reelshub.podman.plist` (`RunAtLoad` true, no `KeepAlive`) that runs `podman machine start` and then `podman start reels-hub`. Both are idempotent.
  - Add `--restart=always` on the container. I don't rely on `podman-restart.service` inside the machine because its behaviour there is **unverified**.
  - This replaces "Quadlet / `podman generate systemd` inside the machine" in §23.3. Files inside the VM vanish on `podman machine rm` and are invisible from macOS.
- **Laptop sleep:** sleep pauses the VM, so jobs pause and nothing is lost. Set the run machine's power setting to *prevent automatic sleeping on power adapter when the display is off* during a series, so the analysis that starts after copying cards actually finishes. **Periodic work uses catch-up, not wall-clock cron:** every 10 min, the worker enqueues the nightly backup if the last one is older than 24 h, and a metric pull if its window is due. A MacBook asleep at 03:00 still gets its backup on wake.
- **Stop:** `podman stop -t 60`. On SIGTERM the worker:
  - stops claiming jobs;
  - kills its ffmpeg, Chromium or Whisper subprocess;
  - sets the job back to `queued`.

  All outputs are written to a temp name and renamed when complete, so a half-written proxy or render is never registered. At most one job's work is lost, and it re-runs on start.
- **Update without losing jobs:** `hubctl update` (P2):
  1. waits until no job is `running` (or `--force`);
  2. runs a backup;
  3. stops and removes the container;
  4. runs the new tag;
  5. waits ≤ 120 s for `/health` to show the new version;
  6. otherwise prints the rollback command.

  Queued jobs survive in the DB.
- **Migrations on start:**
  - If (and only if) a migration is pending, write a backup with `VACUUM INTO /data/backups/pre-migrate-<from>-<to>.sqlite`, copy it to `/media/_backups/db/`, then apply each file in its own transaction.
  - Skip the backup if that exact file already exists, so a crash loop doesn't fill the disk.
  - On a migration error, exit with code 3 and print the file name and the rollback command.
- **Health:** `/health` returns JSON:
  ```json
  {"status": "ok", "version": "0.3.0", "git_sha": "…", "schema_version": 7, "media_mounted": true, "data_free_gb": 61, "media_free_gb": 140, "worker_last_tick_s": 4, "jobs": {"queued": 0, "running": 1, "failed": 0}}
  ```
  It returns HTTP 503 **only** if the DB can't be opened or the media marker is missing. A slow worker is a warning, not a failure, so a 20-minute transcription doesn't trigger `--health-on-failure=restart`.
- **Logs:**
  - stdout (`podman logs`) for live viewing;
  - also `/data/logs/hub.log` with rotation (5 × 10 MB), because `podman rm` on every update throws away container logs;
  - job errors stay in the `job` table and show on **Today**.

  `hubctl logs` = `podman logs --tail 200 -f reels-hub`.

#### Q7. Tests in the container (§24.2)
These run on the **build machine only**, in two tiers:

| Tier | What | Where | Budget |
|---|---|---|---|
| `make test` | Unit, DB, MCP contract, golden prompts, editors' notes, all with fakes | Host via `uv run pytest -n auto` (native, fast) | ≤ 60 s |
| `make test-container` (part of the pre-merge check) | 1) `podman build --target test` (cached), then `pytest -m "ingest or graphics"` **inside** the image, so the image's ffmpeg, OpenCV and Chromium are tested, not the host's ffmpeg 9.0.2. 2) Smoke test of the `runtime` image with `TRANSCRIBE_BACKEND=fake`: `/health`, MCP `initialize` + `tools/list`, copy a fixture clip into a temp media folder, wait until it's registered, check the derived host path, check the container can write `/media/_backups/.write-test` and the Mac sees it, backup → restore → same row counts. 3) Playwright on the host against the smoke container | Podman | ≤ 3 min with a warm cache, ≤ 15 min cold |
| `make test-real` | One real engine per tier (Whisper on a 5 s clip, one HyperFrames render) | Podman, manual or weekly | — |

To keep it fast:
- Layer order as in Q5, with the uv cache mount and a `.containerignore` (`.git`, `.venv`, `node_modules`, `dist/`, large LFS fixtures).
- Never use `--no-cache` in the pre-merge check.
- Fixtures: 2–5 s clips at 540p (< 5 MB each), plus **one** 2 s 4K HEVC clip so the decode path is covered.
- The smoke container gets a unique name (`reels-hub-test-<branch>`), a random host port (`-p 127.0.0.1::8787`), its own throwaway volume, and a temp media folder **under `$HOME`** (`~/.cache/reels-hub-test/<branch>`), because only `$HOME`, `/private` and `/var/folders` are shared into the VM by default.
- A `trap` removes the container and volume, so tests never touch the real `reels-hub` container or `reels-hub-data`.
- The script first checks that the machine is running (`podman machine inspect --format '{{.State}}'`).

#### Q8. Backups
Not enough as written. Four gaps:
1. **The DB lives inside the VM disk.** The named volume is inside `~/.local/share/containers/podman/machine/…`. `podman machine rm`, `podman machine reset`, re-creating the machine to resize it or change provider, or moving the old Mac from Podman 5 to 6 all delete it. Podman secrets live there too.
2. **Time Machine will copy the whole VM disk image on every change** (tens of GB per hourly backup). Exclude it with `tmutil addexclusion ~/.local/share/containers` and rely on the DB backup in `/media/_backups`.
3. **"Nightly" doesn't happen on a sleeping laptop.** Use the catch-up rule from Q6.
4. **There's no restore step and no drill.**

What I'd do:
- **DB:** use `VACUUM INTO /data/backups/tmp.sqlite` (or the SQLite online backup API), run `PRAGMA integrity_check` on the copy, then move it to `/media/_backups/db/hub-YYYYMMDD-HHMM.sqlite` (write to a temp name, then rename, so Time Machine never catches a half-written file). Keep 14 daily copies plus every `pre-migrate-*` and `pre-update-*`.
- **Derived files:** `rsync -a` (incremental) of `/data/files` (proxies, contact sheets, voice prints) to `/media/_backups/data/`. Exclude `/data/models` and `/data/tmp`, which can be downloaded or rebuilt again.
- **Restore:** `hubctl restore <file>` stops the container, copies the file into the volume with a throwaway container, and starts the container again.
- **Drill:** once before the 27 Nov dress rehearsal and once a month, run `hubctl restore --check <latest>`. It restores into a scratch volume, starts `reels-hub-restorecheck` on `127.0.0.1:8789` with `/media` mounted read-only, compares row counts for `reel`, `clip`, `moment` and `feedback_item`, then removes everything. That takes about 5 min. The automated backup → restore test is part of the smoke test in Q7.
- **Masters:** they're in `~/Movies/ReelsHub` but only backed up if Time Machine covers it. 300–900 GB needs a Time Machine disk of that size. Otherwise, keep the SD cards until the reel is posted (owner's call; see P9).

### Proposals

#### P1. Build machine vs. run machine: confirm hardware and choose the architecture
- **Type:** addition
- **Section:** §23 (new §23.0), intro "Scope", §27
- **Proposal:**
  - Write the two-machine setup down.
  - Confirm the old Mac's hardware **before phase 0 ends**: `uname -m`, `sw_vers`, `sysctl -n machdep.cpu.brand_string hw.ncpu hw.memsize`, `df -h ~`.
  - Choose the image architecture and Podman major version from the answers.
  - Deploy to the run machine at the end of phase 0, not first at the dress rehearsal.
- **Suggested spec text:** new §23.0 (before §23.1):
  > ### 23.0 Build machine and run machine
  > - **Build machine** (Apple M5, Podman 6, applehv): develops, tests (§24.2) and builds release images. It never runs the Hub with real footage.
  > - **Run machine** (the owner's MacBook, "old Mac"): holds Edits, the footage in `~/Movies/ReelsHub` and runs the Hub container. Needs: Podman (official installer), a Podman machine sized per §23.3, ≥ 100 GB free for the VM plus room for the series' masters (§27), Claude Code or Desktop, Edits + Edits MCP. No Python, Node or repo checkout needed.
  > - **Architecture** follows the run machine:
  >
  >   | Run machine | Image | Podman on run machine | Mac transcription helper (§23.5) |
  >   |---|---|---|---|
  >   | Apple Silicon | `linux/arm64` | 6.x, `--provider applehv` | possible (mlx-whisper) |
  >   | Intel | `linux/amd64` (cross-built on the M5) | 5.x (Podman 6 dropped Intel Macs) | not possible; CPU or smaller model |
  > - Confirm with `uname -m`, `sw_vers`, `sysctl -n hw.ncpu hw.memsize` and `df -h ~` on the run machine before phase 0 ends.
  > - First deploy to the run machine at the end of phase 0; phase "done when" checks that involve footage or speed (phase 0, §5.1a benchmark) are measured **on the run machine**.

  Scope line: "one user (Ľuboš), one Mac" → "one user (Ľuboš), one Mac running the Hub (the build machine only develops it, §23.0)".
- **Why:** the image architecture, the Podman version (6.0 dropped Intel Macs, per the release notes checked 2026-11-12), the machine sizing and whether §23.5 is possible all depend on hardware nobody has confirmed. Benchmarks on the M5 would be optimistic for an older Mac.
- **Priority:** must-have before build

#### P2. Release and deploy via `podman save` / `podman load` and one `hubctl` script
- **Type:** addition
- **Section:** §23.6 (Tags, Updates), §23.3, §24.5
- **Proposal:**
  - Ship each release from the build machine as one OCI archive plus its sha256.
  - Copy it to the run machine (AirDrop, USB or `scp` with Remote Login on).
  - Deploy with a bash script `deploy/hubctl` that is the **only** place the `podman run` command lives.
  - Drop the optional `compose.yaml`, because podman-compose or docker-compose is one more tool to install.
  - No registry for now.
- **Suggested spec text:** replace the "Tags" and "Updates" bullets in §23.6 with:
  > - **Release (build machine):** from a green `main`, tag `vX.Y.Z`, then
  >   ```bash
  >   podman build --platform linux/arm64 --target runtime -t localhost/reels-hub:X.Y.Z --label org.opencontainers.image.version=X.Y.Z --label org.opencontainers.image.revision=$(git rev-parse HEAD) .
  >   ```
  >   ```bash
  >   podman save --format oci-archive -o dist/reels-hub-X.Y.Z-arm64.tar localhost/reels-hub:X.Y.Z && shasum -a 256 dist/reels-hub-X.Y.Z-arm64.tar > dist/reels-hub-X.Y.Z-arm64.tar.sha256
  >   ```
  >   Copy `dist/reels-hub-X.Y.Z-arm64.tar`, its `.sha256` and `deploy/hubctl` to `~/ReelsHub/releases/` on the run machine (AirDrop, USB or `scp`). Use `linux/amd64` instead if the run machine is Intel (§23.0).
  > - **Deploy (run machine):** `hubctl update ~/ReelsHub/releases/reels-hub-X.Y.Z-arm64.tar` checks the sha256, `podman load`s the image, waits until no job is running, backs up the DB, stops (`-t 60`) and removes the container, runs the new tag with the settings in §23.3 and waits up to 120 s for `/health` to report the new version. It keeps the previous two images and removes older ones.
  > - **Rollback:** `hubctl rollback X.Y.(Z-1)` restores the `pre-update` backup and runs the previous tag.
  > - `hubctl` also provides `install` (one-time setup, §23.3), `status`, `logs`, `backup` and `restore`. Tags are explicit versions; `latest` is not used on the run machine.
- **Why:** there's currently no defined way to get the image from the build machine to the run machine. Save/load needs nothing beyond Podman on both sides and works across Podman 6 → 5 because it's plain OCI. `podman image scp` would need SSH into the run machine's VM, and a registry (GHCR) needs accounts and tokens, which is more than one person needs. One script means the run settings can't drift between a README, compose and memory.
- **Priority:** must-have before build (phase 0 deliverable)

#### P3. Corrected run and machine commands
- **Type:** change
- **Section:** §23.3, §23.4 ("VM resource limits" row)
- **Proposal:**
  - Explicit `applehv` provider; sizing from the run machine's RAM.
  - Drop `:z`; add a restart policy, stop timeout, health check and TZ.
  - Add a launchd agent so the VM and container come back after login.
  - Remove the Quadlet / compose lines.
- **Suggested spec text:** replace the first code block in §23.3 with:
  > ```bash
  > podman machine init --provider applehv --cpus <cores−2> --memory <8192 for 16 GB Macs, 5120 for 8 GB, 12288 for ≥ 24 GB> --disk-size 100
  > ```

  Replace the `podman run` block with:
  > ```bash
  > podman run -d --name reels-hub --restart=always --stop-timeout=60 -p 127.0.0.1:8787:8787 -v "$HOME/Movies/ReelsHub":/media -v reels-hub-data:/data --secret meta_token --secret anthropic_key -e REELS_HUB_HOST_MEDIA_ROOT="$HOME/Movies/ReelsHub" -e TRANSCRIBE_BACKEND=cpu -e TZ=Europe/Bratislava --health-cmd /app/bin/healthcheck --health-interval=30s --health-retries=3 --health-start-period=120s --health-on-failure=restart localhost/reels-hub:X.Y.Z
  > ```

  Replace the "Optional `compose.yaml`" and "`--restart unless-stopped`, or a Quadlet…" bullets with:
  > - The health check is set in the run command, not in the Containerfile (Podman's default OCI image format ignores `HEALTHCHECK`).
  > - `hubctl install` adds `~/Library/LaunchAgents/sk.reelshub.podman.plist` (RunAtLoad) that runs `podman machine start` and then `podman start reels-hub` at login, because the Podman VM doesn't start on its own on macOS.
  > - Run machine power setting during a series: prevent automatic sleeping on power adapter when the display is off, so analysis started after copying cards finishes.
  > - Podman secrets live inside the VM: keep the tokens in the macOS Keychain or a password manager, and re-create the secrets after any `podman machine rm`/re-init.

  §23.4 row "VM resource limits", Handling: "Size the Podman machine (e.g. 8 CPUs, 16 GB)" → "Size the Podman machine from the run machine's hardware (§23.3: cores − 2, RAM table)".
- **Why:** the spec's 8 CPUs / 16 GB doesn't fit an 8 GB or 4–6-core MacBook (Podman 6 rejects too many CPUs). `:z` asks for relabelling a 14 GB-file share for no benefit on macOS (**unverified** whether it's a no-op or slow). `libkrun` (the 6.0 default) has reported bind-mount permission problems and no Metal benefit. A Containerfile `HEALTHCHECK` silently does nothing with Podman's default format. Without a login agent, the Hub is down after every reboot until someone notices.
- **Priority:** must-have before build

#### P4. The DB is inside the VM disk: backups that survive it, and a restore drill
- **Type:** change
- **Section:** §23.6 ("Backups" bullet), §21 ("Backup" row)
- **Proposal:** the backup format, retention, catch-up timing, Time Machine exclusion, a restore command, a monthly drill, and a runbook rule.
- **Suggested spec text:** replace the §23.6 "Backups" bullet with:
  > - **Backups:** the named volume `reels-hub-data` lives inside the Podman VM disk, so `podman machine rm`, `reset` or re-creating the machine deletes it. The copy in `/media/_backups/` is the real backup.
  >   - **DB:** `VACUUM INTO` a temp file, `PRAGMA integrity_check`, then rename to `/media/_backups/db/hub-YYYYMMDD-HHMM.sqlite`. Keep 14 daily copies plus every `pre-migrate-*` and `pre-update-*` copy.
  >   - **Derived files:** incremental `rsync -a` of `/data/files` (proxies, contact sheets, voice prints) to `/media/_backups/data/`; `/data/models` and `/data/tmp` are excluded.
  >   - **Timing:** the worker checks every 10 min and runs the backup if the last one is older than 24 h (a sleeping MacBook catches up on wake), and always before an update or migration.
  >   - **Time Machine:** backs up `~/Movies/ReelsHub` including `_backups`; exclude the VM disk with `tmutil addexclusion ~/.local/share/containers`.
  >   - **Restore:** `hubctl restore <file>`. **Drill:** `hubctl restore --check <file>` restores into a scratch volume, starts a second container on `127.0.0.1:8789` with `/media` read-only, compares row counts and cleans up; run it before the 27 Nov dress rehearsal and monthly.
  >   - **Rule:** run `hubctl backup` before any `podman machine` change.

  §21 Backup row: "Nightly SQLite backup + derived files to `/media/_backups` (visible to Time Machine)" → "Daily (catch-up) SQLite backup + incremental derived files to `/media/_backups`, restore drill monthly (§23.6)".
- **Why:** losing the VM disk is the most likely way to lose all moments, ratings, exclusions, approvals and feedback, and Podman upgrades and resizes sometimes require re-creating the machine. An untested backup isn't a backup. Without the exclusion, Time Machine would copy a multi-GB VM disk image on every hourly run.
- **Priority:** must-have before build (phase 0)

#### P5. Watcher: register only fully copied files; never mark the library offline because of a missing mount
- **Type:** change
- **Section:** §5.1 ("Watch folders", step 1), §23.4 ("File-change events" row)
- **Proposal:** a stability rule, an immediate scan on Add footage, ignore patterns, and a media marker file.
- **Suggested spec text:**
  - §5.1 "Polled every few seconds." → "Polled every 10 s (configurable); **Add footage** and `add_footage` trigger an immediate scan. A file is registered only when its size and mtime are unchanged across 2 polls ≥ 10 s apart and ffprobe succeeds (cards are often still copying). Ignored: `._*`, `.DS_Store`, `.Spotlight-V100`, `.Trashes`, `*.download`, `*.part`, hidden files."
  - §5.1 step 1 → "Hash it (xxh3-128 over the first 1 MiB + last 1 MiB + size) to detect duplicates and moves; re-attach (R27) also compares the ffprobe duration."
  - New bullet in §23.2: "On first setup the Hub writes `/media/.reels-hub-root`. If the marker is missing, the watcher pauses, no clip is marked `offline`, and `/health` returns 503 with `media_mounted: false`."
- **Why:** hashing a half-copied 14 GB file gives a wrong tail hash and a broken probe, which leads to duplicate or corrupt clip records. An empty mount (VM started without the share, folder renamed) would otherwise flip every clip to `offline` under R27's availability logic.
- **Priority:** must-have before build (phase 0)

#### P6. Image recipe: Debian Chromium, pinned HyperFrames, CPU torch, cache-friendly layers
- **Type:** change
- **Section:** §23.6 ("Image" bullet)
- **Proposal:** make the build recipe specific enough that an agent gets it right the first time on arm64.
- **Suggested spec text:** replace the §23.6 "Image" bullet with:
  > - **Image:** multi-stage `Containerfile`, one architecture per release (§23.0). Stages: `node` (`node:22-bookworm-slim`, `npm ci` with `hyperframes` pinned to an exact version in `package-lock.json`; never `npx` at runtime), `runtime` (`python:3.12-slim-bookworm` pinned by digest; apt: `ffmpeg chromium fonts-noto-core` with `--no-install-recommends`; `PUPPETEER_SKIP_DOWNLOAD=1`, Chromium path `/usr/bin/chromium` passed to HyperFrames; `uv sync --frozen --no-dev` in a layer before `COPY src/`, with a uv cache mount; `opencv-python-headless`; torch, if needed, from the CPU index `https://download.pytorch.org/whl/cpu`) and `test` (`FROM runtime` + dev dependencies + `tests/`, never shipped). Size budget: the `runtime` image stays under 3.5 GB (the build test fails above it). Whisper models are downloaded into `/data/models` by `reels-hub models pull` (Hugging Face revision pinned in config), not baked in. A `.containerignore` excludes `.git`, `.venv`, `node_modules`, `dist/` and large fixtures.
- **Why:** HyperFrames renders through Puppeteer with a bundled Chromium (HyperFrames docs, checked 2026-11-12). Puppeteer's bundled browser has no linux-arm64 build as far as I know (**unverified**, check with `hyperframes doctor` in the first image). `npx` at runtime means network downloads and unpinned versions on the run machine. Layer order decides whether a code change rebuilds in seconds or minutes. Default PyPI torch on amd64 pulls CUDA.
- **Priority:** before phase 0 (image) / before phase 7 (HyperFrames parts)

#### P7. Container tests: two tiers, isolated from the real Hub
- **Type:** change
- **Section:** §24.2 ("Container" row and bullets)
- **Proposal:** split host and container tests and add time budgets, so the pre-merge check stays fast enough to actually run on every branch.
- **Suggested spec text:** §24.2 "Container" row → `| Container | `podman build --target test` then ingest and graphics tests inside the image; smoke test of the runtime image (fake transcriber): `/health`, MCP initialize + tools/list, fixture clip registered with the right host path, container can write to the media share, backup → restore round trip; Playwright against it | podman, `make test-container` |`. Add bullets:
  > - `make test` (host, fakes, `pytest -n auto`) ≤ 60 s; `make test-container` ≤ 3 min with a warm cache. The pre-merge check runs both; it never uses `--no-cache`.
  > - The container tests run on the build machine and never touch the `reels-hub` container or the `reels-hub-data` volume: unique container name per branch, random host port, throwaway volume, temp media folder under `$HOME/.cache/reels-hub-test/`, all removed by a `trap`.
  > - Fixtures: 2–5 s clips at 540p plus one 2 s 4K HEVC clip.
- **Why:** ffmpeg on the host (9.0.2) differs from the image's Debian ffmpeg. Ingest tests must run in the image or they test the wrong binary. Without isolation, a test run on a machine that also runs a dev Hub could clobber its data. Without budgets, a slow suite gets skipped.
- **Priority:** before phase 0 ends

#### P8. Proxy speed on the old Mac: use camera proxies first; measure "done when" on the run machine
- **Type:** risk
- **Section:** §5.1 step 3, §25 (phase 0 "done when")
- **Proposal:**
  - Use DJI `.LRF` (and Sony proxy files if the camera records them) as the 540p source and skip the transcode.
  - Contact sheets decode keyframes only.
  - Make the phase 0 timing check explicit about the machine.
- **Suggested spec text:**
  - §5.1 step 3 → "Make a proxy: 540p H.264 for the UI and agents (use the camera's own proxy when present: DJI `.LRF`, Sony proxy recording; otherwise `ffmpeg -vf scale=-2:540:flags=fast_bilinear -c:v libx264 -preset veryfast -crf 28`), plus a contact sheet every 2 s decoded from keyframes (`-skip_frame nokey`)."
  - §25 phase 0 "Done when": append "(measured on the run machine, §23.0)".
- **Why:** all decoding in the VM is software (no VideoToolbox). A Giro_00-sized drop is ≈ 40 min of 4K across 3 cameras (≈ 37 GB). Decoding that at ≥ 1.3× real time on an older MacBook's CPU inside a VM is doubtful (**unverified** until measured with the Q2 commands). If it misses the target, the only alternative is VideoToolbox on the Mac side, which is the extra service R56 wants to avoid.
- **Priority:** before phase 0 ends

#### P9. Disk space for masters on the run machine
- **Type:** risk
- **Section:** §27 ("Where masters live long-term?" row)
- **Proposal:** I'm not reopening R27. I'm recording the concrete consequence and a check.
- **Suggested spec text:** append to the §27 row:
  > Giro_00 alone was ≈ 37 GB of masters for a 50 s reel; 24 similar reels ≈ 900 GB, more than the internal SSD of most older MacBooks. Before the series and weekly during it, `/health` shows `media_free_gb`; below 100 GB the **Today** page warns. If space runs out, masters of reels already `posted` move to the external SSD first (their clips go `offline`, proxies and transcripts stay). Time Machine must be large enough for `~/Movies/ReelsHub`, or SD cards are kept until the reel is posted.
- **Why:** R27 keeps masters on the Mac until the 28 d window closes. On a 512 GB machine that's mathematically impossible for a 24-reel series at Giro_00's footage rate. A full disk also stops the VM and Edits, which breaks principle 10.
- **Priority:** before phase 0 ends (check free space on the run machine now)

#### P10. One-time move of the Giro_00 footage into the media library without a second copy
- **Type:** addition
- **Section:** §23.2
- **Proposal:** document how existing footage enters `~/Movies/ReelsHub` on the run machine.
- **Suggested spec text:** new bullet in §23.2:
  > - Existing footage (Giro_00: `~/Personal/Videos/Giro_00_Intro/raw/…`, ≈ 37 GB) is brought in with hard links on the same APFS volume (`ln <file> ~/Movies/ReelsHub/giro00/raw/sony/`), not copies, so it takes no extra space and the Edits project's existing links keep working.
- **Why:** a plain copy would cost another 37 GB on a machine that's already short of space (P9). The Hub only reads `raw/`, so hard links are safe.
- **Priority:** before phase 0 ends

#### P11. Mac transcription helper: packaging and service
- **Type:** change
- **Section:** §23.5
- **Proposal:** replace "pipx or Homebrew" with uv + a launchd agent, and state that it's Apple Silicon only.
- **Suggested spec text:** §23.5 first bullet →
  > - A tiny service (`reels-hub-transcribe`, **Apple Silicon run machine only**) built as a wheel on the build machine and installed with `uv tool install <wheel>`; it runs mlx-whisper on the GPU, listens on `127.0.0.1:8788`, and is kept running by `~/Library/LaunchAgents/sk.reelshub.transcribe.plist` (RunAtLoad, KeepAlive, logs in `~/Library/Logs/ReelsHub/`). It accepts only paths under `REELS_HUB_HOST_MEDIA_ROOT`. Before enabling `TRANSCRIBE_BACKEND=host`, verify reachability from the container: `curl -fsS http://host.containers.internal:8788/health`.
- **Why:** uv is already the project's tool. A Homebrew tap is a second distribution channel to maintain. launchd is the native way to keep a user service alive on macOS. `host.containers.internal` → host loopback via gvproxy is from memory (**unverified**).
- **Priority:** later (only if the §5.1a benchmark on the run machine needs it)

**Sign-off:** approve with changes
