# Reels Hub developer kit

This kit lets a fresh AI developer agent (Claude Code or OpenCode) build **Reels Hub** in a new private GitHub repo, `ai-slop-code/reels-hub`, phase by phase from spec v0.6, with few questions. At bootstrap it is copied into that repo, together with the spec, the design language and the decision log. From then on `reels-hub/docs/` is the only source of truth, and this handoff repo is a frozen archive.

> After bootstrap this file lives at `docs/BOOTSTRAP.md` in reels-hub. Links in the kit are written for that layout, so they resolve only after the copy.

## What's in the kit

| Kit file | Goes to (reels-hub) | Purpose |
|---|---|---|
| `dev-kit/README.md` | `docs/BOOTSTRAP.md` | This checklist (kept as a record) |
| `dev-kit/repo/AGENTS.md` | `AGENTS.md` | Standing instructions for the developer agent (both tools read it) |
| `dev-kit/repo/CLAUDE.md` | `CLAUDE.md` | Only `@AGENTS.md`, so Claude Code loads the same rules |
| `dev-kit/repo/docs/BUILD_PLAN.md` | `docs/BUILD_PLAN.md` | Ordered phases and branches, owner inputs, open questions, calendar |
| `dev-kit/prompts/01-bootstrap.prompt.md` | `docs/prompts/` | First session: the agent's part of the bootstrap |
| `dev-kit/prompts/02-next-item.prompt.md` | `docs/prompts/` | Every later session: continue to the end of the phase, then report |
| `dev-kit/prompts/03-phase-review.prompt.md` | `docs/prompts/` | Optional: owner-started review of a finished phase |

How the agent works: one branch per plan item → PR → waits for GitHub Actions → squash-merges itself when green → next item. It **stops and reports at the end of every phase** and whenever it needs a decision or something only the owner can give (details in [AGENTS.md](../AGENTS.md)).

---

## Bootstrap checklist

### Owner does (in this order)

1. **Read the kit.** The bootstrap questions Q1, Q4 and Q15 and the GitHub plan are answered (R119–R123, 2026-11-12) and pre-filled in `dev-kit/prompts/01-bootstrap.prompt.md`; add Q2 there if you want to answer it now (it's needed by phase 1).
2. **GitHub CLI on the build machine.** Check `gh --version`; if missing, `brew install gh`. Then log in as LubosBa with the scopes the agent needs (pushing workflow files needs `workflow`):
   ```bash
   gh auth login --hostname github.com --git-protocol https
   ```
   ```bash
   gh auth refresh --hostname github.com --scopes repo,workflow
   ```
3. **GitHub plan: Free is fine (R119).** Branch protection and rulesets aren't available for a private repo on GitHub Free, so `main` isn't protected by GitHub. Instead the agent merges only with `gh pr checks --watch --fail-fast && gh pr merge --squash --delete-branch` (the merge runs only if CI is green; never `--admin`), and a committed `.githooks/pre-push` hook refuses pushes to `main`. The repo stays private.
4. **Create the private repo** (with a README so `main` exists):
   ```bash
   gh repo create ai-slop-code/reels-hub --private --add-readme --description "Reels Hub: local central intelligence for Katarina's Reels"
   ```
5. **Merge settings**: squash only, delete branches after merge:
   ```bash
   gh repo edit ai-slop-code/reels-hub --enable-squash-merge --enable-merge-commit=false --enable-rebase-merge=false --delete-branch-on-merge
   ```
6. **Actions permissions**: read-only `GITHUB_TOKEN` by default; the release workflow asks for `packages: write` itself (job-level `permissions`), which is what GHCR needs:
   ```bash
   gh api -X PUT repos/ai-slop-code/reels-hub/actions/permissions/workflow -f default_workflow_permissions=read -F can_approve_pull_request_reviews=false
   ```
7. **Start the first agent session** in `/Users/S38RA/Personal/repos/` (Claude Code or OpenCode) with `dev-kit/prompts/01-bootstrap.prompt.md` from this handoff repo (it isn't in reels-hub yet).
8. **Watch the first PR's CI.** The CI job runs on `ubuntu-24.04-arm` (R121: arm64 runners work for this repo). If it ever fails to get a runner, the agent stops and reports; the fallback is QEMU emulation for the arm64 image.
9. **On your own clones of reels-hub** (if any), enable the push guard once: `git config core.hooksPath .githooks`.
10. **After the first merge to `main` with the release workflow (plan item 0.3)**: open the package page for `reels-hub` under the ai-slop-code org → Packages. Check it is **private** and linked to the repo (it should be, via the `org.opencontainers.image.source` label).
11. **Approve the archive note** in the handoff repo (agent step 7 below).

### Agent does (prompt `01-bootstrap`)

1. `gh auth status`; clone `ai-slop-code/reels-hub` to `/Users/S38RA/Personal/repos/reels-hub`; `git switch -c chore/bootstrap`.
2. **Copy files** per the mapping table below (source: `/Users/S38RA/Personal/repos/reels-hub-handoff`). Plain copies; no content edits except link fixes. Text only: no images, footage or other binaries (R120).
3. **Fix relative links** per the table below, then add `tests/test_docs_links.py`, which fails on any broken relative Markdown link in the repo (it ignores code spans and fenced code blocks, so the examples in this file don't count).
4. **Write `docs/decisions.md`**: the "Decisions already made" table (D1–D10), the full decision log (R1–R123, including the owner's bootstrap answers R119–R123) and the sign-offs from `reviews/README.md`, plus an empty section "Decisions during the build" where new entries start at R124. Add a note at the top of `docs/reviews/README.md`: "Frozen copy. The live decision log is `../decisions.md`."
5. **Skeleton, CI, push guard and stub Containerfile** per plan item 0.1 in `docs/BUILD_PLAN.md`; run `git config core.hooksPath .githooks`; `make test` passes locally.
6. **First PR**: tick 0.1, open the PR, then merge only with `gh pr checks --watch --fail-fast && gh pr merge --squash --delete-branch` (never `gh pr merge` alone, never `--admin`). If CI never starts, stop and report (owner step 8).
7. **Freeze the handoff repo**: in `/Users/S38RA/Personal/repos/reels-hub-handoff`, on a `chore/archive-note` branch (its own `CLAUDE.md` rules), add an archive note at the top of `HANDOFF.md`: "**Archived 2026-11-xx.** This repo is frozen. The spec, design language and decision log now live in https://github.com/ai-slop-code/reels-hub (`docs/`)." Merge it into the handoff repo's `main` only after the owner OKs it.
8. Report (short) and stop. Later sessions use `docs/prompts/02-next-item.prompt.md`.

### File mapping (handoff repo → reels-hub)

| Source (reels-hub-handoff) | Destination (reels-hub) | Note |
|---|---|---|
| `REELS_HUB_SPEC.md` | `docs/spec/REELS_HUB_SPEC.md` | Source of truth (v0.6) |
| `DESIGN_LANGUAGE.md` | `docs/spec/DESIGN_LANGUAGE.md` | v1.2 |
| `reviews/README.md` | `docs/reviews/README.md` (frozen copy) **and** extract into `docs/decisions.md` (live) | See agent step 4 |
| `reviews/01-…18-*.md` | `docs/reviews/` | Background only |
| `reviews/prompts/` | `docs/reviews/prompts/` | For optional later reviews; their paths refer to the old layout |
| `reels/giro00-intro/review_notes.md`, `instagram_caption.txt` | `docs/reference/giro00/` | Reference reel, text only. Its `graphics/` (PNG + SVG) are **not copied** (R120): they stay in this archive and on the run machine |
| `tools/mkmap.py` | `tools/mkmap.py` | Map generator, wrapped in phase 7 |
| `HANDOFF.md`, `CLAUDE.md` | `docs/reference/handoff/HANDOFF.md`, `docs/reference/handoff/CLAUDE.handoff.md` | Snapshot of the handoff state and old rules; superseded by `AGENTS.md`. Rename `CLAUDE.md` so Claude Code doesn't load it as a nested instruction file |
| `context/claude-memory/` | `docs/reference/handoff/claude-memory/` | Background (project, music, git rules) |
| `dev-kit/README.md` | `docs/BOOTSTRAP.md` | |
| `dev-kit/repo/AGENTS.md`, `dev-kit/repo/CLAUDE.md` | `AGENTS.md`, `CLAUDE.md` | |
| `dev-kit/repo/docs/BUILD_PLAN.md` | `docs/BUILD_PLAN.md` | |
| `dev-kit/prompts/*.prompt.md` | `docs/prompts/` | |
| `.git/`, `dev-kit/` itself, `reels/giro00-intro/graphics/` | not copied | |

### Link fixes (after copying)

| Files | Replace | With |
|---|---|---|
| `docs/reviews/*.md` | `](../REELS_HUB_SPEC.md` | `](../spec/REELS_HUB_SPEC.md` |
| `docs/reviews/*.md` | `](../DESIGN_LANGUAGE.md` | `](../spec/DESIGN_LANGUAGE.md` |
| `docs/reviews/*.md` | `](../reels/giro00-intro/` | `](../reference/giro00/` |
| `docs/spec/REELS_HUB_SPEC.md` | `` [`reviews/README.md`](reviews/README.md) `` | `` [`docs/decisions.md`](../decisions.md) `` |
| `docs/spec/REELS_HUB_SPEC.md` | `](reels/giro00-intro/review_notes.md)` (and its link text) | `](../reference/giro00/review_notes.md)` |
| `docs/spec/REELS_HUB_SPEC.md` front matter `related:` | `reels/giro00-intro/review_notes.md`, `reviews/README.md` | `../reference/giro00/review_notes.md`, `../decisions.md` |

`DESIGN_LANGUAGE.md` links to `REELS_HUB_SPEC.md` in the same folder, so it stays valid. Plain-text paths such as `tools/mkmap.py` are repo-root paths and stay. Files under `docs/reference/handoff/` are a snapshot and aren't edited. Find leftovers with:
```bash
grep -rnE '\]\((\.\./)?(REELS_HUB_SPEC|DESIGN_LANGUAGE|reviews/|reels/)' docs
```
The link fixes count as "typos and clarifications" (no behavior change), so they go into the same bootstrap PR without a decision entry.

---

## Owner inputs needed later

The full table, with a status column for you to fill in, is in [BUILD_PLAN.md](BUILD_PLAN.md) under "Owner inputs".

| When | Input |
|---|---|
| End of phase 0 (~16 Nov) | **Run machine** set up per `docs/RUNBOOK.md` (written in plan item 0.10; spec §23.3): confirm the Podman 6 version and free disk; Podman machine `applehv`, 8 CPUs, 12 GB, 100 GB; `~/Movies/ReelsHub`; launchd agent; `tmutil` exclusion |
| End of phase 0 | **GHCR read token**: a classic personal access token with only `read:packages` (GitHub Packages doesn't take fine-grained tokens), stored in the run machine's Keychain (`security add-generic-password -s reels-hub-ghcr -a lubosba -w`) |
| End of phase 0 | Podman secrets `meta_token`, `anthropic_key`, `hf_token` exist (placeholders until the real values; the run command needs all three) |
| End of phase 0 | Giro_00 masters hard-linked into `~/Movies/ReelsHub/giro00/raw/` (R67), and the Giro_00 graphics copied from the handoff archive into `~/Movies/ReelsHub/giro00/graphics/` (R120); the "done when" timing; a host path imported in Edits; the **Edits 25p check** (spec §14, R70) |
| Phase 1 (~16–18 Nov) | **ASR reference transcript**: ~5 min of C0031 + one DJI excerpt, corrected by ear (~1 h), in `/data/bench/` on the run machine, never in Git (R81); then run the benchmark command the agent gives you |
| Phase 1, if speaker labels are built | **Hugging Face token** (pyannote is gated) as the real `hf_token` secret; time ranges for Katarina's and Ľuboš's voice prints |
| Phase 2 | Claude Code on the run machine connected to the Hub MCP; Edits MCP connected |
| Phase 3 | The 21-stage table data (Q12); Katarina's dialect words for `keep_as_said` (R100) |
| Phase 9 | `giro2027-advent` values: posting time from "Most active times", brief, slots |
| Before 27 Nov | **Stage 1 footage** shot and on the run machine; **restore rehearsal** done (spec §23.6) |
| Phase 4 | Real **Anthropic API key** as Podman secret `anthropic_key`; the pinned model ID (Q14) |
| Phase 5 (~28 Nov) | **Meta developer app** with Instagram Login in Development mode, Katarina's account given a role, Professional/Creator account confirmed, long-lived token as `meta_token` |
| Phase 7 | Import test of the HyperFrames MP4 and alpha MOV in a copy of `Giro_00_Intro` |
| Phase 8 | GetSongBPM API key, only if used |

## Open questions for the owner

Answer each before the phase named. Details and suggested defaults are in [BUILD_PLAN.md](BUILD_PLAN.md) under "Open questions". The bootstrap ones are answered (2026-11-12).

1. **Q1 · Real footage snippets in the repo:** *answered (R120): no pictures, just the code.* Test clips and images are generated by scripts at test time and not committed; real snippets stay in the git-ignored `tests/fixtures/local/` (tests skip when absent); no Git LFS; the Giro_00 graphics aren't copied.
2. **Q2 · Giro_00 transcript text in golden tests:** only the lines already quoted in the docs (default), the full C0031 transcript, or none? Text is less sensitive than video, but it's still her words on GitHub. *(Phase 1)*
3. **Q3 · Synthetic Slovak speech** from macOS `say` (a stock voice, not Katarina's or Ľuboš's) as the fixture for the optional real-engine ASR test? *(Phase 1)*
4. **Q4 · arm64 CI:** *answered (R121): `ubuntu-24.04-arm` works for the repo;* QEMU only as a fallback if it ever fails.
5. **Q5 · Restore command:** `deploy.sh restore <file>` instead of `reels-hub restore`, because the run machine has no Python? *(Phase 0)*
6. **Q6 · MCP token:** how it's created and stored. *(Phase 2)*
7. **Q7 · Statuses `exported` and `analyzed`:** what sets them? *(Phase 4/5)*
8. **Q8 · `lint_draft` and `check_mix`:** what they take, since the Hub can't read Edits. *(Phase 4/8)*
9. **Q9 · Reel-card baseline:** 30-day account median (spec §12.3) or the project's previous 5 reels (R107 light step)? *(Phase 5)*
10. **Q10 · Instagram token refresh:** where the refreshed token is kept. *(Phase 5)*
11. **Q11 · Map font and Natural Earth download** for container-rendered maps. *(Phase 7)*
12. **Q12 · Stage table source** (giroditalia.it blocks automated fetches). *(Phase 3)*
13. **Q13 · Fact conflicts:** manual status (default) or automatic detection? *(Phase 3)*
14. **Q14 · Pinned Claude model ID** for Hub-side LLM calls. *(Phase 4)*
15. **Q15 · Pre-approved dependency list** in `AGENTS.md` → "Dependencies": *answered (R122): approved as is.*
16. **GitHub plan:** *answered (R119): GitHub Free, no enforced branch protection;* the chained merge command and the pre-push hook are the guard (owner step 3).
