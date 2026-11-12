# Reels Hub handoff

**Packaged:** 2026-11-12, from the session that built the Giro_00 intro reel and wrote the Reels Hub spec.
**Updated:** 2026-11-12: git set up, 11 of 18 reviews done, spec v0.6 merged, build machine ready (see "Status" below).
**Owner:** Ľuboš · **Host:** Katarina (Instagram @katttyi)

This folder holds everything needed to continue on another computer or with another AI model: the spec, the design language, the reference reel's notes and graphics, the expert review packets, and prompts for AI reviewers.

---

## Folder map
```
reels-hub-handoff/
├── HANDOFF.md                 ← you are here
├── CLAUDE.md                  ← standing rules, loaded automatically by Claude Code
├── REELS_HUB_SPEC.md          ← product + technical spec, v0.6
├── DESIGN_LANGUAGE.md         ← house style for all reels, v1.2
├── reviews/
│   ├── README.md              ← review process, decisions D1–D10, decision log R1–R123, sign-offs
│   ├── 01-…18-*.md            ← one review packet per expert role (reviewers write their input here)
│   └── prompts/
│       ├── 00-consolidator.prompt.md   ← merges reviews → decision log → next spec version
│       └── 01-…18-*.prompt.md          ← one prompt per AI reviewer
├── reels/
│   └── giro00-intro/          ← the first reel (Day 1 teaser for the Giro 2027 December series, published)
│       ├── review_notes.md    ← cut list, captions, sources, feedback rounds, open items
│       ├── instagram_caption.txt
│       └── graphics/          ← map PNGs + editable SVGs
├── tools/
│   └── mkmap.py               ← map generator (pure Python → SVG)
├── dev-kit/                   ← starter kit for the developer agent: AGENTS.md, build plan, bootstrap checklist, session prompts
└── context/
    └── claude-memory/         ← notes the previous Claude session kept (project, music, git rules)
```

## Status (2026-11-12)
- **Git:** this folder is a git repository; `main` holds the handoff plus all changes below. Every change goes on its own branch (CLAUDE.md).
- **Reviews:** 11 of 18 done, all "approve with changes": 01–05 (round 1) and 06, 07, 09, 11, 14, 15 (round 2). Not run: 08, 10, 12, 13, 16, 17, 18 (judged lower value for a simple tool).
- **Decisions:** the consolidator built the decision log in two rounds (R1–R57 → spec v0.5, R58–R118 → spec v0.6, all in `reviews/README.md`), plus the owner's bootstrap answers R119–R123 (GitHub Free merge gate, no pictures in the repo, native arm64 CI, approved dependencies); the owner decided every entry, and the accepted ones are applied in **spec v0.6** and **design language v1.2**. D5 is superseded by R49 (Instagram comments are not imported). The spec's §28 lists all changes per version.
- **Direction set by the owner:**
  - **Simple over robust:** one user (Ľuboš), one machine; build the simplest thing that supports the flow.
  - **Per-reel flow (spec §19.0):** create reel → shoot (no planning in the Hub) → add footage → the Hub analyzes automatically → reel prompt → the owner's Claude session edits with Reels Hub MCP + Edits MCP → `editors_notes.md` → approval → manual post → metrics.
  - **Overview** of what was built and when, including all graphics used (spec §6.5, Graphics screen).
  - **`editors_notes.md`** per reel documents everything used and every practice followed (spec §11.4); it is the input for critique.
  - **Critique** runs only when the owner triggers it, after a video exists (spec §16.5).
  - **December target:** everything except critique (phase 10) works by 1 Dec; dress rehearsal 27 Nov, go/no-go 28 Nov (spec §25).
  - **Release path (spec §23.6):** code in the GitHub repo `ai-slop-code/reels-hub` (org ai-slop-code, owner identity LubosBa); GitHub Actions runs the full test suite on every pull request (the merge gate) and on every merge to `main` builds the `linux/arm64` image and pushes it to `ghcr.io/ai-slop-code/reels-hub`; the run machine pulls it with `deploy.sh <tag>` (backup, restart, health check, rollback).
  - **Shooting:** both cameras at 25p (Sony 25p/50p, DJI 25 fps); 50p only for slow motion (DESIGN_LANGUAGE §6).
  - **December experiment:** the closing card alternates a teaser for the next stage (odd stages) with a plain statement (even stages) (spec §13.2, R103).
  - **Posts:** at most 5 hashtags (DESIGN_LANGUAGE §13).
- **Machines:**
  - **Build machine** (this Mac, checked 2026-11-12): used only to develop Reels Hub, never to run it. macOS 26.7 on Apple M5, git, Node 26, uv 0.13.7 with Python 3.12.16 for the project (system Python stays 3.15), ffmpeg/ffprobe 9.0.2, Podman 6.1 (machine with 5 CPUs, 8 GiB RAM, 100 GiB disk). No Edits app or Edits MCP, and none needed: the Hub never drives Edits itself (spec §4, §23.1), and tests use a fake transcriber and fake LLM (spec §24.2). Ready for phase 0.
  - **Run machine:** the owner's MacBook (D4), called "the old Mac" below: Apple M5, 24 GB RAM, 1 TB storage. It already holds the Giro_00 footage, Edits and the Edits project. Reels Hub will run there with the media library `~/Movies/ReelsHub`, the Podman machine sized per spec §23.3 and the Edits MCP. Not set up yet.

## What to do next
1. **Bootstrap `reels-hub`** per `dev-kit/README.md` (owner steps, then session prompt `dev-kit/prompts/01-bootstrap.prompt.md`), then build per the plan (`dev-kit/repo/docs/BUILD_PLAN.md`, roadmap §25): one branch per item; CI (GitHub Actions) must pass before a merge to `main`.
2. **Set up the run machine (old Mac)** at the end of phase 0, when CI has published a first image: Podman machine per spec §23.3, `~/Movies/ReelsHub`, a read-only `ghcr.io` token, `deploy.sh`, Edits MCP connected to the owner's Claude session. Check there once how Edits handles 25p footage and record it in the playbook (spec §14).
3. **Optional reviews:** packets 08, 10, 12, 13, 16, 17, 18 (prompts in `reviews/prompts/`; each reviewer writes **only** into its own packet), then the consolidator for v0.7.

## Status of the Giro_00 intro reel
- **Edits project:** `Giro_00_Intro`, 50.9 s, 9:16. It exists only in the Edits library on the **old Mac** (`~/Movies/Edits/Libraries/…`). It isn't portable through this folder.
- **Published** on Instagram (owner, 2026-11-12). Last applied feedback before posting: round 2 (closing card 3.5 s, "Štart v Terste, cieľ v Ríme." on the Terst–Rím map). No further action on this reel.
- **Lessons kept for later reels:** at most 5 hashtags (its caption had 8); the closing-card teaser is intended and becomes the December experiment.
- **Music:** "Dolce Vita" by Italian Atmosphere (Edits licensed library), approved.
- **Open items carried to later reels** (`reels/giro00-intro/review_notes.md` keeps the original list):
  - **Stage 1 reel:** "enters Slovenia" is verified; where and how long isn't. Slovenian press reports Lipica (~km 94) and Hrvatini (~km 134); confirm against the official Stage 1 profile (R117, `reviews/15-cycling-domain-expert.md`).
  - **Stage 2 reel:** Slovenia's final hosting agreement is due 3 Dec 2026, the day it posts; call the stage "plánovaná" until it's announced (R118).

## Not included (too large or machine-bound)
| Item | Where it lives on the old Mac | Size |
|---|---|---|
| Raw footage: Sony C0030/C0031, DJI 0038/0039/0040 (+ .WAV, .LRF) | `~/Personal/Videos/Giro_00_Intro/raw/{sony,dji}` | ≈ 37 GB |
| Hard links Edits uses (no extra space) | `~/Movies/Giro_00_Intro_raw/` | – |
| Edits library and project | `~/Movies/Edits/Libraries/` | – |
| Natural Earth country data used by `mkmap.py` | download `ne_10m_admin_0_countries.geojson` (v5.1.2) again | ≈ 25 MB |

Copy the raw footage separately if the new machine needs it. In the planned Reels Hub setup it belongs in `~/Movies/ReelsHub/<project>/raw/` (spec §23.2).

## Key facts a new model should know
- **Edits sandbox:** the Edits app can't read `~/Personal`; media must live under `~/Movies`.
- **Edits API quirks** are collected in spec §14 (playbook).
- **Music:** commercial / artist-grade first via Edits' licensed library; the owner dislikes generic royalty-free music; no yt-dlp, not even for auditioning. The agent can't listen to licensed tracks; the owner decides by ear.
- **Captions:** all speech captioned in Slovak; only use what Katarina actually said; never splice her words into sentences she didn't say; proposed lines go under "Suggested pickups (not recorded)" in the reel's `editors_notes.md`.
- **Approval:** never render or export a reel before the owner approves that exact version.
