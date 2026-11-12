---
name: reels-hub-project
description: "Reels Hub — planned local \"central intelligence\" app for Katarina's Instagram Reels; spec location and core flow"
metadata:
  node_type: memory
  type: project
  originSessionId: 31e669fe-99b9-4a02-8a11-54dd37c24ecb
  modified: 2026-11-12T08:13:37.261Z
---

The user plans to build **Reels Hub**, a local-first app (SQLite + MCP server + web UI) holding footage, moments, facts, design language, music, reviews, AI critique and Instagram analytics for Katarina's Reels. Spec: `REELS_HUB_SPEC.md` in the `reels-hub-handoff/` folder (v0.6, 2026-11-12; originally written at `~/Personal/Videos/Giro_00_Intro/` on the old Mac); design rules in `DESIGN_LANGUAGE.md` next to it. Principle: simple over robust, one user, one machine.

Deployment: developed and tested on a build Mac; GitHub Actions builds the `linux/arm64` image and pushes it to `ghcr.io/ai-slop-code/reels-hub`; the run Mac (the old Mac, M5 / 24 GB / 1 TB, holds Edits and footage) pulls it with `deploy.sh`. One **Podman** container (UI, MCP on 127.0.0.1:8787, ingest, HyperFrames). Media library at `~/Movies/ReelsHub` bind-mounted as `/media` (Edits can read ~/Movies, not ~/Personal); data in named volume. Edits, Claude and an optional mlx-whisper GPU helper stay on the Mac (no Metal GPU inside Podman's VM).

Core flow per reel (spec §19.0): create reel → shoot (no planning in the Hub) → add footage → Hub analyzes automatically → **prompt for Claude** → the owner's Claude session edits via Reels Hub MCP + Edits MCP and writes `editors_notes.md` → producer feedback/approval → manual post → analytics feed the next prompt. AI critique only when the owner triggers it. The Hub also shows an overview of what was built and when, including graphics used.

**Why:** reduce repeated work (transcribing, syncing, fact-checking, Edits quirks) seen on the Giro_00 intro and learn from performance.

**How to apply:** build against the spec; follow [[reels-hub-branch-workflow]]; music rules in [[music-preferences]].
