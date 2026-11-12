---
title: "Reels Hub: local central intelligence for Katarina's Reels"
status: draft
version: 0.6
updated: 2026-11-12
owner: Ľuboš
related:
  - DESIGN_LANGUAGE.md
  - ../reference/giro00/review_notes.md
  - ../decisions.md
---

# Reels Hub: product and technical spec

A **local-first app** that holds everything about our Reels: footage, the best moments in it, facts, design rules, the graphics we've used, reviews and performance. Any AI agent can read it and contribute to it through a standard interface (MCP).

> **The goal:** the next Reel starts where the last one ended. No re-transcribing, no re-syncing cameras, no re-checking facts, no rediscovering tool quirks. Every posted Reel teaches us something measurable for the next one.

> **Scope:** one user (Ľuboš), one Mac running the Hub (the build machine and CI only develop, test and build it, §23.0). Build the simplest thing that supports the main flow (§19.0): create the reel in an existing project → shoot (the plan stays in our heads) → add the footage → the Hub analyzes it automatically and builds the reel prompt → the producer's Claude session edits through the Hub MCP and the Edits MCP → producer feedback and approval → post → analytics feed the next prompt. Every reel ends with an `editors_notes.md` (§11.4). AI critique comes later and only when the producer asks for it (§16).

---

## Contents
1. [Why: lessons from Giro_00_Intro](#1-why-lessons-from-giro_00_intro)
2. [Principles](#2-principles)
3. [Users and roles](#3-users-and-roles)
4. [Architecture](#4-architecture)
5. [Module A: footage index and moments](#5-module-a-footage-index-and-moments)
6. [Module B: projects, reels and the reel prompt](#6-module-b-projects-reels-and-the-reel-prompt)
7. [Module C: facts and sources](#7-module-c-facts-and-sources)
8. [Module D: glossary and caption intelligence](#8-module-d-glossary-and-caption-intelligence)
9. [Module E: design system as data](#9-module-e-design-system-as-data)
10. [Module F: graphics generator](#10-module-f-graphics-generator)
11. [Module G: reviews, feedback and approvals](#11-module-g-reviews-feedback-and-approvals)
12. [Module H: performance analytics](#12-module-h-performance-analytics)
13. [Module I: learning loop and experiments](#13-module-i-learning-loop-and-experiments)
14. [Module J: tool knowledge (Edits playbook)](#14-module-j-tool-knowledge-edits-playbook)
15. [Module K: music](#15-module-k-music)
16. [Module L: AI critique](#16-module-l-ai-critique)
17. [Agent interface (MCP server)](#17-agent-interface-mcp-server)
18. [Data model](#18-data-model)
19. [Key workflows](#19-key-workflows)
20. [User interface](#20-user-interface)
21. [Tech stack](#21-tech-stack)
22. [Security, privacy and safety](#22-security-privacy-and-safety)
23. [Deployment (Podman)](#23-deployment-podman)
24. [Development workflow](#24-development-workflow)
25. [Roadmap](#25-roadmap)
26. [Success metrics for the Hub itself](#26-success-metrics-for-the-hub-itself)
27. [Risks and open questions](#27-risks-and-open-questions)
28. [Changelog](#28-changelog)

---

## 1. Why: lessons from Giro_00_Intro

The Day 1 intro took one long session. Most of that time went to work a system could have done in advance:

| What happened | Time sink | What the Hub does instead |
|---|---|---|
| Edits couldn't read `~/Personal` (sandbox) | Diagnosing, hard-linking footage | Media library lives in `~/Movies/ReelsHub`, mounted into the container and readable by Edits (§23.2) |
| 13-min main take + 2 × 13-min DJI | Transcribing 40 min of audio before choosing a line | Transcripts exist the moment footage lands |
| Sony and DJI clocks 1 h apart | Manually computing a 24.85 s offset | Offset stored per device per shoot; auto-sync by audio cross-correlation (§5.2) |
| Best material in ~5 short ranges | Scanning transcripts and frame sheets | Tagged, rated **moments** searchable across all shoots |
| Auto-captions misheard "lízatko", wrote "po 30" | Manual correction per caption | Glossary + correction memory applied automatically |
| Captions went stale after trims | Delete and regenerate | Playbook warns: "trim first, then caption" |
| Organizer's announcement vs. route page disagreed on Stage 1 | Cross-checking sources | Fact store flags conflicts with source links |
| Royalty-free music download failed | Trial and error | Playbook records the working path (licensed library) |
| Three feedback rounds | Re-reading chat | Feedback items tied to timestamps and elements, tracked to done |
| Graphics, music and practices recorded only in `review_notes.md` | Re-reading notes to find what was used | Every reel ends with an indexed `editors_notes.md`; a graphics overview shows every graphic used and where (§11.4, §20) |
| No performance data yet | – | Analytics module links stats to structure, so the next Reel improves |

---

## 2. Principles

1. **Local-first.** Everything runs on the Mac. Footage never leaves the disk. Cloud services are optional add-ons.
2. **Reference, don't copy.** The Hub stores paths, hashes and derived data (transcripts, thumbnails, proxies), never duplicate masters.
3. **Moments over files.** The unit of reuse is a tagged time range, not a 14 GB clip.
4. **Every claim has a source.** Facts carry a URL, a date checked and a confidence.
5. **Humans approve, agents prepare.** Agents can draft, cut, caption and analyze. Only the producer approves, and he approves a specific version in the Hub. No MCP tool can approve. Nothing is exported before approval, and posting stays manual.
6. **Agent-native.** Every capability in the UI is also an MCP tool (except approving), and every agent action is logged.
7. **Learn from every post.** Performance is linked back to hooks, length, music, graphics and topics.
8. **Plain formats.** SQLite, Markdown, YAML, JSON, PNG/SVG. It must stay readable without the app.
9. **Real music, properly licensed.** Commercial and artist-grade tracks first, generic royalty-free stock last. Never ripped.
10. **Never block a post.** The Hub speeds up production but is never required to post. Keep at least 2 approved reels ahead of the posting date during a series. If the Hub is down, the manual workflow (Edits + Claude + Markdown notes in the project folder) still works, and the Hub catches up afterwards by importing the version and the publication.
11. **Simple over robust.** One user, one machine. Build the simplest thing that supports the main flow (§19.0). Add robustness (queues with leases, hooks, hashes, toolsets, extra services) only when a real problem shows up.

---

## 3. Users and roles

| Role | Who | Needs |
|---|---|---|
| **Producer / editor** | Ľuboš, the **only Hub user** | Find material fast, review drafts, approve versions, see what graphics we've used, see performance |
| **Host** | Katarina, on camera. She doesn't use the Hub and gets no generated documents | Her words are used only as she said them (§6.4); her exclusions are absolute (§5.3). If Ľuboš passes on a remark of hers, he logs it as feedback with `author: Katarina` |
| **AI agent** | Claude or other MCP clients | Structured access to footage, transcripts, facts, style rules, playbook. Write access for drafts, notes, tags and `editors_notes.md` |

- No login, no roles, no second UI. The Hub binds to localhost only (§22).
- The Hub does no shoot planning: Katarina and Ľuboš shoot with the plan in their heads, then add the footage to the reel (§19.0).
- Collaborators (guest editor, designer) and a host view are out of scope until a real need appears (§2 principle 11).

---

## 4. Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                         Reels Hub (local)                        │
│                                                                  │
│  ┌────────────┐   ┌──────────────┐   ┌────────────────────────┐  │
│  │  Watcher   │──▶│  job table   │──▶│ Worker loop            │  │
│  │ (raw/ dirs)│   │  (SQLite)    │   │  • probe (ffprobe)     │  │
│  └────────────┘   └──────────────┘   │  • proxy + thumbnails  │  │
│                                      │  • transcribe (Whisper)│  │
│                                      │  • diarize speakers    │  │
│                                      │  • sync cameras        │  │
│                                      │  • scene / shot detect │  │
│                                      │  • renders (HyperFrames│  │
│                                      │    CLI subprocess)     │  │
│                                      └──────────┬─────────────┘  │
│                                                 ▼                │
│  ┌───────────────────────────────────────────────────────────┐   │
│  │ Storage: SQLite (+FTS5) · files on disk                   │   │
│  └───────────────────────────────────────────────────────────┘   │
│        ▲                 ▲                    ▲                  │
│  ┌─────┴─────┐    ┌──────┴───────┐     ┌──────┴────────┐         │
│  │  Web UI   │    │  MCP server  │     │  Importers    │         │
│  │ (HTMX)    │    │ (streamable  │     │ IG insights,  │         │
│  │ localhost │    │  HTTP)       │     │ CSV, sources  │         │
│  └───────────┘    └──────────────┘     └───────────────┘         │
│                          ▲                                       │
└──────────────────────────┼───────────────────────────────────────┘
                           │
              Claude / other agents · Edits MCP
```

- **One process, three faces:** the web UI for humans, the MCP server for agents, the CLI for scripts. One FastAPI app serves the UI, REST and MCP; a worker loop in the same container runs jobs from the `job` table, one heavy job at a time. Heavy work never runs inside a web request.
- **Edits integration is indirect.** Agents use the Hub's MCP for knowledge and the Edits MCP for editing. The Hub records what was built (Edits project IDs, cut lists, `editors_notes.md`).

---

## 5. Module A: footage index and moments

### 5.1 Ingest
- **Watch folders:** `/media/<project>/raw/{sony,dji,phone,audio}` inside the container = `<media root>/<project>/raw/…` on the Mac, i.e. `~/Movies/ReelsHub/<project>/raw/…` (§23.2). Polled every 10 s (configurable); **Add footage** and `add_footage` trigger an immediate scan.
- **Only fully copied files:** a file is registered only when its size and mtime are unchanged across 2 polls ≥ 10 s apart and ffprobe succeeds (cards are often still copying). Ignored: `._*`, `.DS_Store`, `.Spotlight-V100`, `.Trashes`, `*.download`, `*.part` and other hidden files. If the media marker `/media/.reels-hub-root` is missing, the watcher pauses and marks nothing offline (§23.2).
- **On a new file:**
  1. Hash it (xxh3 over the first 1 MiB + last 1 MiB + size) to detect duplicates and moves; re-attach also compares the ffprobe duration.
  2. Probe it: duration, codec, resolution, fps, audio channels, camera model, start timecode and color transfer. **Flag** the clip on the reel and in **Today** (never block) if (a) its fps differs from the reel's other clips (house standard: 25p on both cameras, DESIGN_LANGUAGE §6; 50p only for intended slow motion), (b) it's variable frame rate (`r_frame_rate` ≠ `avg_frame_rate`, typical for phones), or (c) it's HDR or Log (`color_transfer` arib-std-b67 / smpte2084, DJI D-Log M).
  3. Make a proxy for the UI and agents: 540 px high, source aspect, H.264 High CRF 23, keyframe every 0.5 s (`-g 12` at 25p), source frame rate (no conform), source timecode, AAC 128 kbps 48 kHz with all source audio channels, faststart. Plus a contact sheet every 2 s. Frame-accurate checks (first frame, `focus_x`) read single frames from the master. Edits always imports the masters; the Hub makes no edit proxies.
  4. Transcribe in Slovak (`language: sk`, forced) with word-level timestamps, then forced alignment (§5.1a). No per-segment language detection: on short segments it confuses Slovak with Czech. Segments with mean word probability < 0.4 are flagged `check_language` in the UI.
  5. Label speakers (Katarina / Ľuboš / other / unknown) with voice prints (§5.1a, *if time allows in phase 1*).
  6. Detect shots and silences.
  7. **Audio QC:** find clipped ranges (3 or more consecutive samples at or above −0.1 dBFS); overlapping moments get the tag `tech:clipped`. Only numbers are stored.
  8. *(Later)* Embed text and frames for semantic and visual search (§5.4).
  9. **Register the file** with its path relative to the media root. Mac (host) and container paths are derived from it (§23.2), so Edits and Claude get a real Mac path. No staging copy is needed because the library already lives in `~/Movies`.
- **Sidecars:** read DJI `.LRF` (proxy) and `.WAV` (mic) and attach them to the parent clip. The WAV is an **alternate audio source** in the take, synced with its parent's offset, so the editor can take a clipped passage, or Ľuboš's off-camera lines, from the DJI mic. The Hub never mixes or processes audio itself.
- **Origin:** every clip and asset has `origin`: `own | licensed | open_data | third_party_unlicensed`. `third_party_unlicensed` items (race broadcast, organizer photos and maps, other creators' reels) are reference only: hidden from agent search and moment suggestions, and never used in a reel (checked in the `editors_notes.md` checklist, §11.4).
- **Masters location:** masters stay in `~/Movies/ReelsHub/<project>` until the 28 d metric window of the project's last reel closes, then move to an external SSD. If disk space runs short earlier, masters of reels already `posted` may move to the external SSD early (§27). Clips get `availability` (online / offline) and `volume_id`; files that come back are re-attached by hash. Proxies, transcripts and contact sheets stay on the Mac. No NAS support.

### 5.1a Transcription engine
| Engine | Strengths | On Apple Silicon | Role |
|---|---|---|---|
| [openai/whisper](https://github.com/openai/whisper) | Reference implementation | Slow (PyTorch) | Not used directly |
| [faster-whisper](https://github.com/SYSTRAN/faster-whisper) | Fast, accurate, word timestamps, VAD | CPU only (CTranslate2), int8 is still usable | Base for **WhisperX** |
| WhisperX (on faster-whisper) | Better word alignment + **speaker labels** (pyannote) | CPU | Candidate for speaker-labelled transcripts |
| mlx-whisper / whisper.cpp | Uses the Mac's GPU (Metal / Core ML) | Fastest | Candidate for raw speed (Mac helper only, §23.5) |
| [kinit/whisper-large-v3-turbo-sk](https://huggingface.co/kinit/whisper-large-v3-turbo-sk) (MIT) | Slovak fine-tune; published Slovak WER about a third of base large-v3; turbo decodes several times faster | CPU via CTranslate2 int8 (converted once with `ct2-transformers-converter`) | **Lead candidate** for CPU in Podman |

- **Decision by benchmark, not by preference** (run once before phase 1, and again before any model change):
  - **Runs:** base `large-v3` vs. `kinit/whisper-large-v3-turbo-sk`, both through WhisperX on CPU in the container. Other candidates (`kinit/whisper-large-v3-sk`, mlx-whisper on the Mac helper) only if both miss the bar.
  - **Test set:** ~5 min of Giro_00 C0031 plus one DJI excerpt with Ľuboš and cross-talk. The Edits transcript covers only the ~45 s used in Giro_00, so the producer corrects a verbatim reference for these minutes (~1 h: draft from one engine, corrected by ear; numbers as spoken words, names in glossary form). References live in `/data/bench/`, never in Git.
  - **Metrics:** WER (NFC, lowercase, no punctuation, diacritics kept), glossary-name accuracy, speed (minutes per hour of audio). Both machines are Apple M5, so build-machine speed is a fair preview; the final number is taken on the run machine (§23.0).
  - **Pass bar for December:** WER ≤ 12 %, names ≥ 90 %. Take the faster config unless the slower one is clearly better.
- **Decoding config** (in config, stored with every transcript run):
  ```yaml
  asr:
    model: kinit/whisper-large-v3-turbo-sk@v2.0   # or large-v3, whichever wins the benchmark
    compute_type: int8
    language: sk                    # forced (§5.1 step 4)
    beam_size: 5
    condition_on_previous_text: false   # avoids repetition loops
    vad_filter: true
    word_timestamps: true
    hotwords: "<per-reel term list, ≤ 150 tokens>"
    hallucination_blocklist: ["titulky vytvoril", "titulky vytvořil", "ďakujem za pozornosť", "ďakujem za pozretie", "odoberajte", "www."]
  ```
  Model weights are pinned to a revision and converted once into `/data/models/`; no third-party re-uploads.
- **Glossary hint:** pass a per-reel term list as `hotwords` (faster-whisper / WhisperX; applied to every 30 s window), written as one Slovak line, e.g. "Giro, etapa, Terst, Trieste, Rím, Zoncolan, Ľuboš, Katarína, lízatko." Terms: the speakers, the reel's stage towns and climbs (both exonym and original), project terms and current correction-memory targets. **Cap: 150 tokens (~40–60 terms)**; Whisper truncates anything over 223 tokens. `initial_prompt` alone isn't enough: with `condition_on_previous_text: false` it only affects the first window. Kept only if the benchmark shows better name accuracy.
- **Word timing:** after ASR, the container always runs forced alignment (WhisperX, Slovak model `comodoro/wav2vec2-xls-r-300m-sk-cv8`) on the text, whichever backend produced it. Words the aligner can't place (digits, symbols) get times interpolated from their neighbours and `timing: interpolated`.
- **Speaker labels** (*if time allows in phase 1*): pyannote `speaker-diarization-community-1` (1–4 speakers) through WhisperX → words assigned to speakers → each cluster named by cosine similarity to one voice print per person (`katarina` / `luboš` if the best score is above a threshold and clearly above the second, else `other`; thresholds in config, calibrated on C0031). Turns under 1.5 s in an unsure cluster get `unknown` and are shown for a decision instead of guessed.
- **Model, revision and config** are stored with every transcript run (`transcript` table, §18). Re-runs happen only on demand, when the benchmark shows a real gain; the previous run stays until the producer accepts the new one. Manual transcript fixes are stored separately in `transcript_edit`, anchored by time, so raw words are never overwritten. Re-applying them to a new run is left until a re-run actually happens.

### 5.1b Computer vision: OpenCV
[OpenCV](https://github.com/opencv/opencv) (plus [PySceneDetect](https://github.com/Breakthrough/PySceneDetect), built on it) runs inside the ingest jobs:
- **Shot and cut detection** for each clip.
- **Subject tracking for 9:16 crops:** face or person detection gives a suggested `focus_x` per shot (Giro_00's hook needed 0.545, set by eye).
- **First-frame check:** is the subject fully in frame on frame 1?
- **Color:** the grade is the camera's preset from the design language (DESIGN_LANGUAGE §6), applied by the agent. The Hub doesn't compute grade values (Edits' sliders aren't calibrated units).
- **Thumbnails** for contact sheets (frame embeddings later).
- **Sync fallback:** frame similarity between angles when audio is poor.

### 5.2 Multicam sync
- **Takes** group the clips recorded at the same time across cameras. A **shoot** is only the recording session the footage came from (date, devices, clock offsets), derived at ingest; the Hub doesn't plan shoots.
- Sync by **audio cross-correlation** (*if time allows in phase 1*): coarse on 100 Hz log-energy envelopes over the whole overlap (FFT, no prior needed; ±5 s around a stored offset if one exists), then fine with GCC-PHAT on 16 kHz audio within ±100 ms. Confidence = main peak / next peak outside ±0.5 s; accept at ≥ 3, otherwise ask for a manual offset. **Drift check:** repeat on the first and last 2 min of the take; if the offsets differ by more than one frame (40 ms at 25p), flag the take and store the drift. Transcript words only verify the result.
- The camera clock offset is stored per device per shoot with its confidence (e.g. DJI = Sony − 24.85 s; clock 1 h off). A manually entered offset per device per shoot always overrides and is enough for December if auto-sync isn't ready.
- The UI shows synced angles side by side and can jump between them.

### 5.3 Moments
A **moment** is a time range in a clip (or a synced take) with meaning. Media times are integer milliseconds (§18):

```yaml
moment:
  id: mom_0001
  take: take_giro00_main
  clip: giro00-sony-c0031
  src_in_ms: 490100
  src_out_ms: 496500
  transcript: "Prečo je toto lízatko ružové? … Máj."
  speakers: [katarina]
  tags: [beat:hook, tone:humor, prop:lollipop, topic:maj, time:evergreen]   # technical problems as tech: tags, e.g. tech:clipped
  rating: 5            # 1–5 usefulness for editing (hook strength, audio, framing), not a judgement of the host
  usable: true         # false = do-not-use (crude, private, broken audio)
  reason_excluded: null
  excluded_by: null    # katarina | luboš | agent_proposed
  used_in: [giro00]
  alt_angles: [{ clip: giro00-dji-0039, offset_ms: -24850 }]
  notes: "Lollipop visible from 0.8 s; she's at frame edge at 0.0 s"
```

- **Tag vocabulary** (prefix:value, so search and ranking stay predictable): `beat:` hook, who, promise, payoff, card_line, sign_off, cold_open, bumper, tease_next · `tone:` humor, tease, warm, serious, reaction, laugh · `topic:` / `stage:` / `place:` / `climb:` / `rider:` from the glossary · `prop:` lollipop, advent_calendar, cycling_calendar, bidon · `people:` luboš_offcam, luboš_on_dji, duo · `craft:` one_take, needs_cover, clean_in, clean_out · `time:` evergreen, dated · `tech:` clipped, noise, mic_rustle, plosive, out_of_frame, soft_focus, flicker. Technical problems are `tech:` tags, kept apart from the rating.
- **Cut points:** suggested moment in/out points snap to the middle of the nearest silence within ±150 ms of the first and last word (from `transcript_word`), or are padded by 80 ms if there's no silence, so initial consonants and word decays survive.

**Features**
- Auto-suggested moments: hooks (questions, surprising claims), punchlines (laughter after a line), sign-offs, list beats ("Dolomity, Alpy, Apeniny…").
- **Do-not-use ranges** (crude banter, private talk, bad audio), excluded from agent search.
- **Exclusions by a person are absolute.** A range excluded by Katarina (recorded by Ľuboš on her behalf) or by Ľuboš for himself stays excluded; only the same person can lift it. Agents can only propose exclusions (`excluded_by: agent_proposed`) until a person confirms. A whole take can be excluded in one action.
- **Reuse tracking:** which reels used a moment, and a warning before reusing one in the same project.
- **Unused gems:** a list of high-rated moments never used (e.g. the "geograficko-cyklisticko-politicko-geopoliticko" tongue-twister). Moments tagged `time:dated` ("zajtra", a date, a weekday) aren't offered as unused gems for later reels.

### 5.4 Search
- Full-text over transcripts (SQLite FTS5, tokenizer `unicode61 remove_diacritics 2`) with Slovak diacritic-insensitive matching ("zoncolan" finds "Zoncolan").
- **Inflection:** FTS5 has no Slovak stemmer, so each query term of ≥ 5 characters is also searched as a prefix without its last 2 characters (`lízatko` → `lízat*`, `Zoncolan` → `zoncola*`); exact matches rank first.
- Filters: speaker, camera, rating, tag, project, used/unused, date.
- *(Later, not for December)* Semantic search ("moments where Katarina teases Ľuboš") and visual search over frame embeddings ("Katarina holding the calendar").

---

## 6. Module B: projects, reels and the reel prompt

**Hierarchy:** a **project** (e.g. "Giro 2027 advent") contains many **reels**. Everything the Hub knows is attached at project level and inherited by every reel in it.

> Naming: "project" always means a Reels Hub project. An Edits project is called an **Edits project** and is linked to a reel.

### 6.1 Creating a project
Creating a project is a **one-time setup** per series; after that, every reel starts from §6.2.

```yaml
project:
  id: giro2027-advent
  title: "Giro d'Italia 2027 – adventný kalendár"
  platform: instagram
  account: katttyi
  run: { start: 2026-12-01, end: 2026-12-24, cadence: daily }
  reels_planned: 24
  folder: giro2027                           # relative to the media root (= ~/Movies/ReelsHub/giro2027, /media/giro2027 in the container)
  media_folders: [raw/sony, raw/dji, raw/audio]
  design_language: DESIGN_LANGUAGE.md@1.2
  music_signature: music-dolce-vita
  fact_domain: giro2027                      # stage table + sources
  glossary: [sk-cycling, sk-italy]
  posting_time: "19:00"                      # Europe/Bratislava; set once from in-app "Most active times" before the series, never moved during it
  experiment: exp_giro2027_ending            # the series' one pre-registered experiment (§13.2)
  brief: "One Giro 2027 stage per December day, hosted by Katarina…"
```

When a project is created, the Hub **establishes relations** automatically:
1. **Media:** registers the media folders and ingests all footage (transcripts, speakers, sync, shots, moments). Edits imports the files in place (§23.2).
2. **Assets:** links graphics, motion templates, music, fonts and tools the project uses (shared assets are referenced, not copied).
3. **Knowledge:** attaches the fact domain, glossary, design-language version and the playbook.
4. **History:** if the project continues earlier work, it inherits findings, taste profile and unused moments from the parent project.

New footage dropped into the project folder later is ingested and linked to the project automatically; it's linked to a reel when the producer adds it to that reel (§6.3).

### 6.2 Reels inside a project
- **Slots:** e.g. Day 1 intro, Days 2–22 one stage each (Stage 1 to Stage 21), Days 23–24 open.
- **Status pipeline:** `created → footage_added → analyzing → prompt_ready → editing → in_review → approved → exported → posted → analyzed`. Every status change is stored with a timestamp.
  - `created`: the producer clicked **New reel**; no footage yet. Katarina and Ľuboš shoot next.
  - `footage_added → analyzing → prompt_ready`: set automatically when footage is added (§6.3).
  - **Going back:** adding more footage at any point before `approved` sends the reel back to `analyzing` and rebuilds the prompt. Feedback sends `in_review` back to `editing`. A new version after approval sends the reel back to `in_review` (the old approval is invalidated, §11.3).
- **Fields:** slot, slot type (intro / stage / finale), stage, topic angle (story / place / how to get there), optional hook and promise notes (promise for the next reel), commercial flags, linked Edits project, linked footage, target runtime, runtime, planned posting date, Instagram caption, hashtags, posting time (defaults to the project's `posting_time`), experiment variant (§13.2).
- **Target runtime** defaults from DESIGN_LANGUAGE §10 by slot type: intro 45–60 s, stage 35–50 s (hard cap 60 s), finale 45–75 s.
- **Commercial flags** (checkboxes, filled in when the reel is created, editable later): paid partnership, gifted or hosted (free product, travel, tickets), affiliate links, boost planned, brand collab partners. If any is ticked, tier-1 Edits library music isn't allowed for that reel (§15.6). The flags are copied into the reel's `editors_notes.md` checklist (§11.4). An unpaid co-authored post with another creator is **not** a commercial flag; it's recorded as `collab: true` in the features (§12.2) and the posting checklist (§11.4). Whether the licensed library covers co-authored posts is still to be confirmed (§27).
- **Continuity check:** each reel's closing promise must match the next reel's topic. The Hub flags it when Day N promises something Day N+1 doesn't deliver.
- **Missing lines:** the Hub doesn't track pickups. If the edit needs a line Katarina didn't say in one piece, the editing agent lists the point to make under "Suggested pickups (not recorded)" in `editors_notes.md` (§11.4). Proposed wording is never put in captions or on screen as her speech.

### 6.3 Adding footage: the intelligence kicks in
After the shoot, the producer copies the cards into the project's media folder (`<project>/raw/…`, §23.2) and clicks **Add footage** on the reel (or an agent calls `add_footage`). The Hub pre-selects clips ingested since the reel was created that aren't linked to another reel; the producer confirms. From there everything runs **automatically**, with no further clicks:

1. **Analysis** (status `analyzing`): ingest of the linked clips finishes (proxies, transcripts, speaker labels, multicam sync, shots, §5.1–§5.2); the glossary and caption correction memory are applied to the transcripts (§8); moments are suggested and ranked for this reel's topic (§5.3).
2. **Gathering:** the Hub assembles everything relevant to the reel (table below).
3. **Prompt:** the reel prompt is built (§6.4) and the reel moves to `prompt_ready`. The producer can edit or regenerate it at any time (**Regenerate prompt** or `generate_reel_prompt`), e.g. after correcting a transcript or adding a fact.

Analysis progress and failures show on the reel and in **Today** (§20).

| Gathered | From |
|---|---|
| Reel brief: slot, stage, topic, hook and promise notes, target runtime, commercial flags | Reel (§6.2) |
| Stage facts with sources, open conflicts | Facts (§7) |
| Candidate moments (hooks, payoffs, sign-offs) from the reel's footage, ranked for this topic, plus unused gems from earlier footage | Footage index (§5) |
| Design tokens, caption rules, safe zones, motion presets | Design system (§9) |
| Graphic templates to use, e.g. `stage_route` for stage 5, and graphics already used in earlier reels | Graphics (§10), graphics overview (§20) |
| Music signature, mix rules, shortlist if a new track is needed | Music (§15) |
| Glossary and caption correction memory | Glossary (§8) |
| Tool quirks (Edits) | Playbook (§14) |
| What worked: findings, recommendations, last reels' metrics and their `editors_notes.md` (practices, deviations, open items, suggested pickups) | Analytics, learning, editor's notes (§12, §13, §11.4) |
| Continuity: what the previous reel promised, what this one must set up | Project plan |
| Open items carried over (e.g. "confirm Stage 1 crossing point") | Reviews (§11) |

**Ranking (simple):** filters first (the reel's own footage first, then earlier footage; usable, not excluded, not `third_party_unlicensed`, not already used in this project unless reuse is OK, speaker), then SQLite FTS5 (BM25) on the topic and stage keywords, then rating, then recency. No vector search and no LLM rerank for now.

### 6.4 The reel prompt (handover to the AI editor)
The Hub generates the **reel prompt** for Claude (or another agent) automatically once analysis finishes (§6.3). The producer hands it to his own Claude session: he copies it in, or the session reads it from `hub://reel/{id}/prompt`. That session edits with the tools the Hub provides (Reels Hub MCP + Edits MCP) and writes `editors_notes.md`. The prompt is **self-contained but lean**: stable rules first, then an ordered workflow, acceptance checks and the reel-specific context. It points to MCP resources for bulk data (transcripts, full fact table) instead of pasting them. Slovak text (transcripts, facts, glossary forms) is quoted verbatim; the rest may be English.

**Prompt structure (template, versioned):**
```markdown
# Reel {project.title} · {reel.slot}: {reel.topic}
<!-- template {template_version} -->

## Rules (always)
- Use only words Katarina (or Ľuboš) actually said. Quote Slovak verbatim; never paraphrase or translate it.
- Never join fragments from different sentences or takes into one sentence (no "frankenbites"). Cutting filler or false starts inside one continuous thought is fine.
- If a line is missing, don't invent it: list the point to make under "Suggested pickups (not recorded)" in editors_notes.md. Never put proposed wording in captions or on screen as her speech.
- Never synthesize Katarina's or Ľuboš's voice or face (no TTS, voice cloning, lip-sync or generated likeness).
- State only the facts listed below and cite their IDs. Facts marked "attributed only" may be said only with their attribution ("podľa slovinských médií…"). Anything marked Unconfirmed must not be stated as fact.
- This is a preview of a race months away: describe the route as planned ("plánovaná trasa", "pôjdu cez…"). Never state rider participation, favourites or outcomes as fact; at most quote a named person's stated intention with attribution.
- Don't use excluded ranges or third-party media. No organizer maps, logos or "oficiálny" wording.
- Do not render a final export. The producer approves a specific version in the Hub; export only after `export_allowed` returns true.
- You can't hear licensed music. Report measurements, not impressions.

## Workflow
1. If anything below is unclear, read `hub://reel/{reel.id}` (or call `get_reel`).
2. Pick hook, promise, payoff and closing from the candidate moments (`search_moments` for more).
3. Build the 9:16 draft in a new Edits project "{edits_project_name}": main cut → cutaways → graphics → music.
4. Finish all trims, then captions, then `fix_captions`. Then `lint_draft` and fix what it finds.
5. `create_version` with the cut list (minimum fields §11.1).
6. Draft the Instagram caption (rules §8.1; `lint_script` counts the hashtags). Write `editors_notes.md` for this reel (`update_editors_notes`, template §11.4), including the caption, the checklist and open items. Then `request_approval`.

## Acceptance checks
- Runtime {target_runtime} ± 10 % (stage episodes: hard cap 60 s). Subject fully in frame on frame 1; frame 1 is content (no fade, title or black).
- Hook: first word ≤ 0.3 s; the curiosity is stated by 3 s (the line may run to 6 s). No "who we are" beat outside the Day 1 intro.
- 100 % of speech captioned in Slovak (clean verbatim, DESIGN_LANGUAGE §4); glossary terms correct; captions at y = {caption_y}.
- Cards ≤ {max_card_s} s; music {under_speech} under speech, {silent_card} on silent cards.
- Every on-screen or caption claim has a fact ID. Every graphic, the music and its license are listed in editors_notes.md.
- Instagram caption: at most 5 hashtags.

## Style (design language {version})
{key tokens}. Full rules: hub://design-language/current

## Tool quirks (Edits)
{playbook items for the planned steps}

## Learned from previous reels
{3–5 recommendations with evidence}, e.g. "maps ≤ 3.5 s", "end on tomorrow's question"

## This reel
Goal: {reel.brief}. Audience: {audience}. Target runtime {target_runtime}.
Continuity: previous reel promised "{prev.closing_promise}". This reel must set up "{next.topic}".
Open items carried over: {open items with IDs}
Experiment: {experiment.variable} = {reel.experiment_variant} (§13.2), e.g. closing card "tease" or "statement"

### Candidate moments
| Beat | ID | Clip · in–out | Rating | Transcript (verbatim) |
{hook, promise, payoff, closing candidates, plus unused gems}

### Facts you may state
{verified facts: ID · claim · source}
Attributed only (say "according to {source}"): {secondary-only facts with IDs}
Unconfirmed (do not state as fact): {conflicting or unverified facts with IDs}
Pronunciation unchecked: {glossary terms in this reel with no `checked_by`}

### Music
{signature track or shortlist}; mix {levels}. Commercial flags: {flags}.

## Deliverables
Edits project name, version in the Hub, completed editors_notes.md (with Instagram caption, checklist, open items and suggested pickups).
```

**Features**
- **Preview, edit and regenerate** the prompt before handing it over; edits and regenerations are saved as prompt versions.
- **Lean by default:** the generator keeps the prompt short and links the rest via `hub://` resources. No fixed token budget.
- **Prompt history:** each reel stores the prompt that produced it, so prompt templates can be compared against performance (§13).
- **Golden tests:** the template is covered by snapshot tests (§24.2), so changes to it are reviewed.
- **Delivery:** copy to clipboard, save as `reels/<slot>/PROMPT.md` in the project folder, or let the Claude session read it from `hub://reel/{id}/prompt`. The reel moves to `editing` when the prompt is copied or read.

### 6.5 Project overview: what was built and when
One page per project (§20) answers "what have we built, and when?":
- **Reel list** (one row per reel, sorted by slot or date): slot, topic, status, and the dates **created**, **footage added**, **approved** and **posted** (from `status_change` and `publication`), with links to the reel's footage, graphics, music and `editors_notes.md`.
- **Calendar:** a month grid with status colors, posting times, and gaps or conflicts highlighted.

The graphics overview (§20) shows the same project from the asset side: every graphic and where it was used.

---

## 7. Module C: facts and sources

### 7.1 Fact store
```yaml
fact:
  id: fact_giro27_s1_slovenia
  subject: "Giro 2027 Stage 1"
  claim: "Stage 1 (Trieste–Trieste, 8 May 2027) enters Slovenia."
  status: verified             # verified | attributed | unverified | conflicting | outdated
  sources:
    - url: https://www.giroditalia.it/en/news/from-trieste-to-rome-giro-ditalia-2027-route-unveiled/
      kind: primary
      says: "crossing briefly into Slovenia"
      checked: 2026-11-12
    - url: https://www.giroditalia.it/news/da-trieste-a-roma-presentato-il-percorso-del-giro-ditalia-2027/
      kind: primary
      says: "uno sconfinamento in Slovenia"
      checked: 2026-11-12
  used_in: [giro00]
  review_by: 2026-11-30
```

**Seed facts for the `giro2027` domain** (from review packet 15, checked 2026-11-12; for the Stage 1 and Stage 2 reels, nothing changes in the published Giro_00):

| Fact ID | Claim | Status | Sources | Review by |
|---|---|---|---|---|
| `fact_giro27_s1_slovenia` | Stage 1 enters Slovenia (say: "odbočí do Slovinska") | verified | Organizer press releases EN and IT | 2026-11-30 |
| `fact_giro27_s1_lipica` | Stage 1 passes Lipica (~km 94.2) | attributed (say "podľa slovinských médií…") | Siol.net; Delo quoting the Slovenian federation (KZS) | 2026-11-30 |
| `fact_giro27_s1_slovenia_extent` | Where and how long: two incursions (Lipica and the Hrvatini climb, ~km 134) vs. "briefly" | conflicting until the official Stage 1 profile is checked; don't say "dvakrát" or "krátko" | Organizer "briefly"; route page silent; Siol and RTV SLO "twice" or "a large part" | 2026-11-30 |
| `fact_giro27_slo_agreement` | Slovenia and RCS Sport sign the final hosting agreement | unverified (pending); Stage 2 copy says "plánovaná" until it's announced | Siol.net: letter of intent only, final agreement targeted for 3 Dec 2026 | 2026-12-03 |

- **Open items** that go with them: on the Stage 1 reel, "open the official Stage 1 profile; if it labels Lipica and Hrvatini/Crevatini, add it as a primary source and set the extent fact to verified"; on the Stage 1 and Stage 2 reels, "Slovenian hosting agreement due 3 Dec 2026".

### 7.2 Features
- **Source tiers:** `primary` > `archive` > `secondary` > `lead`. Primary counts only for its own domain (organizer for route, km, climbs and dates; host authorities and federations for hosting; transport operators and police for services and closures); within the organizer, the more specific document wins (road book > profile > route page > press release > social). Archive is the organizer's albo d'oro and Giro archive. Secondary is press and statistics sites. **Lead** (Wikipedia, aggregators, tour sellers, fan sites, third-party GPX) is used only to find a primary source and never cited.
- **Status vs. use:** only primary counts as `verified` and may be stated as fact. A claim backed only by secondary sources with no primary contradiction is `attributed`: it may be said **with attribution** ("podľa slovinských médií…"), and `editors_notes.md` lists it as attributed. Everything else isn't said.
- **Conflict detection:** two sources disagreeing on the same subject puts the claim in a "Needs attention" queue.
- **Silence is not a conflict.** A source that doesn't mention a claim never makes it `conflicting`; conflict needs two sources that say different things about the same detail. Split broad claims ("enters Slovenia") from details ("where, how long, how many times"), so the broad claim can be `verified` while the detail is still open.
- **Re-check reminders:** race facts change (routes, km, access). Each fact has a review-by date and a **Re-checked** button (and `mark_fact_checked`) that sets `checked` to today and accepts an optional pasted quote (`says`). Automated page checks are best-effort: some sources block non-browser requests (giroditalia.it returned HTTP 403 on 2026-11-12). A failed automated check shows "couldn't check, please check manually" and never changes `status`.
- **Spectator advice** has its own type, with a flag for "race-day access unconfirmed".
- **Stage reference data:** structured table of stages (date, start, finish, km, type, rest days) imported from the organizer, versioned. Optional per-stage columns, filled by hand per reel when a map needs them:
  ```yaml
  climbs: [{ name: "Cattinara–Sella di Longera", km: 158.7, summit_m: 283, length_km: null, avg_pct: null, category: null, fact: fact_… }]
  places: [{ name: "Lipica", km: 94.2, country: SI, fact: fact_giro27_s1_lipica }]
  ```
  Each row points to a fact. `stage_route` (§10) draws only places and climbs whose fact is `verified` or `attributed`, and draws a border tick where `country` changes.
- **Script linting:** a reel script or caption is checked against the fact store, and unsupported claims are highlighted.

---

## 8. Module D: glossary and caption intelligence

- **Glossary:** canonical Slovak spellings, case forms and pronunciations for towns, climbs, riders, teams and terms.
  ```yaml
  - term: Terst
    original: Trieste
    type: city
    forms: [Terst, Terstu, v Terste, Terstom]   # nom, gen, loc with preposition, ins
    captions: as_said        # as_said | canonical; captions follow speech, titles, maps and post captions use the term
  - term: lízatko
    type: word
    heard_as: [lyžičko]
  - term: Zoncolan
    type: climb
    forms: [Zoncolan, Zoncolanu, na Zoncolane, Zoncolanom]
    pronunciation: "dzon-ko-LAN"   # Slovak respelling, stressed syllable in capitals
    source: "DiPI / RAI DOP"
    checked_by: null               # null → the prompt shows "pronunciation unchecked"
  - term: šak
    type: word
    keep_as_said: true             # example only; her real dialect words come from Katarina. Never standardized
  ```
  Matching uses all forms; a replacement keeps the case of the matched form. Terms without `forms` are indeclinable. Pronunciation sources: Italian DiPI online or RAI DOP; Slovene Fran.si; Slovak exonyms and declension ÚGKK SR and JÚĽŠ SAV; Forvo is a lead only.
- **Seed:** the Giro 2027 project starts with the `sk-italy` and `sk-cycling` glossaries from review packet 14 (Q6, 52 terms with case forms). Ľuboš asks Katarina for her dialect words and adds them as `keep_as_said` before the first automatic caption run (she doesn't use the Hub, §3).
- **Place-name policy:** on-screen titles, map labels and post captions use the Slovak exonym when it is on the ÚGKK exonym list **and** in current media use (Terst, Rím, Neapol, Miláno, Turín, Janov, Benátky, Florencia, Ľubľana, Sicília, Toskánsko, Dolomity, Alpy, Apeniny); otherwise the Italian original, inflected in Slovak (Bolzano → v Bolzane; Padova, not Pádua; Trento, not Trident). Never coin an exonym. Captions follow speech (DESIGN_LANGUAGE §4).
- **Correction memory:** every manual caption fix is stored as `{heard_phrase, correct_phrase, always}`, where the phrase includes at least one neighbouring word (e.g. `takúto lyžičko → toto lízatko`). `fix_captions` auto-applies a correction only when the whole phrase matches, or when the producer has marked a single-word rule `always` (e.g. `lyžičko → lízatko`, also covered by its glossary `heard_as`). Everything else is returned as a suggestion. Correction memory never rewrites raw transcript words; it applies to caption and displayed text only. Number formatting (`po 30 → po tridsiatke`) is a style rule (DESIGN_LANGUAGE §4) that `fix_captions` also applies, not a correction.
- **Style rules from the design language:** clean verbatim, numbers as words or digits, line breaks, speaker labels for off-camera voices, sound tags in [brackets], 3–8 words per phrase (DESIGN_LANGUAGE §4).
- **Caption QA:** missing diacritics, untranscribed speech, captions overlapping the UI-safe zones, captions over silent gaps, inconsistent speaker labels. The line-break and question rules (DESIGN_LANGUAGE §4) are applied by the agent; exceptions are noted in `editors_notes.md`. No automatic line-break checks for now.
- **Translation:** longer speech by others in another language is translated into concise Slovak and marked as translated. Katarina's own Italian words and phrases are captioned as said, never translated.

### 8.1 Instagram caption
The editing agent drafts the post caption as part of the edit (§6.4 workflow) and records it in the "Instagram caption" section of `editors_notes.md` (§11.4). Rules (also in DESIGN_LANGUAGE §13):
- First line is the hook, matching the spoken hook's topic; no hashtag or @.
- Every number, date or place claim has a fact ID, as for on-screen text.
- Last line is the tomorrow line ("Zajtra: {n+1}. etapa."), matching the next reel (§6.2 continuity check).
- Exactly one call to action (send, save, or a comment vote).
- **At most 5 hashtags** (Instagram's limit per post): original or international form, lowercase, no diacritics (`#giroditalia`). `lint_script(text, kind: caption)` counts them.
- A location tag where it fits (e.g. the stage start town).
- Slovak with glossary forms and the place-name policy above; no "oficiálny".
- Paid-partnership label if any commercial flag is set (§6.2).

---

## 9. Module E: design system as data

- Import `DESIGN_LANGUAGE.md` front matter and YAML blocks as **tokens**: color, type, layout, picture, audio, motion, structure.
- **Versioned:** each reel records the design-language version it used.
- **Style lint** for a draft (via Edits inspection or an exported frame sheet):
  - only the accent pink plus neutrals in graphics
  - titles and captions inside the safe zones
  - no text in the face band
  - music level within ±2 dB of the rule
  - card hold time ≥ minimum
  - first frame has the subject fully in frame
- **Motion presets** (when adopted): push-in on map cards, dot pop, text slide-up, with durations and easing as tokens.

---

## 10. Module F: graphics generator

- Wraps `tools/mkmap.py` and successors as **parameterized templates**:
  - `map_overview(cities=[Terst, Rím], highlight=None)`
  - `map_closeup(center=Terst, show_border=SI)`
  - `map_stage(stage=12)`, with the route rebuilt from fact-store towns and climbs on open data (see the guardrail below)
  - `stat_card("21 etáp")`, `climb_profile(stage, km_range)`
- Every render is registered as an asset (DESIGN_LANGUAGE §11), with its parameters, data source, license and `origin` (Natural Earth = public domain, `open_data`).
- Where each graphic is used is recorded in the reel's `editors_notes.md` (§11.4). The **graphics overview** (§20, `list_graphics_usage`) combines the asset registry with those notes.
- Text stays **out of** the PNG (it's added in Edits) unless it's a map label.
- **Guardrail:** routes are drawn from the fact store (towns, climbs, km from primary sources) on open data: Natural Earth (public domain) and, for road-level detail, OpenStreetMap (ODbL; credit "© OpenStreetMap contributors" in the caption). Elevation profiles come from an open DEM (e.g. Copernicus DEM, with attribution). Organizer maps, profile images, photos, logos and race footage are **never** shown, traced or screen-recorded.

### 10.1 Motion graphics renderer: HyperFrames
Motion graphics are built **outside Edits** and dropped into the timeline as clips.

- **Engine:** [HyperFrames](https://github.com/heygen-com/hyperframes) (HeyGen, Apache 2.0), run as a Node 22 CLI subprocess inside the Hub's container. A graphic is an HTML/CSS/JS composition. It's rendered frame by frame in headless Chrome and encoded with ffmpeg, so the same source always produces the same video. Requires Node 22+ and ffmpeg (with the ProRes encoder for transparent output).
- **Fonts:** compositions use only fonts registered as `font` assets with a license allowing video output, social platforms and installation in the container (default: SIL OFL; must cover Slovak diacritics and the en dash). Fonts from Edits (Monstera) and macOS system fonts (Avenir Next) are **never** extracted, copied into the image or loaded by HyperFrames or resvg. Text set in Monstera stays in Edits.
- **Why:** design tokens become CSS variables, `mkmap.py` SVGs animate natively (stroke-dashoffset for route draw-on, transforms for push-ins), and agents author HTML well. HyperFrames ships agent skills for Claude Code.
- **Template library** (each a parameterized composition):

| Template | Motion | Params |
|---|---|---|
| `card_map_cities` | 108 % eased push-in; city dots pop (scale 0 → 1.15 → 1, 0.3 s) in spoken order; glow pulses once | cities[], text lines, duration |
| `map_travel` | Pan and zoom from city A to city B | from, to, duration |
| `stage_route` | Pink route line draws start → finish; climbs marked as it passes; border tick where the country changes | stage, places and climbs from the stage table (only `verified` or `attributed` facts, §7.2), OSM geometry, km markers |
| `stat_card` | Number counts up or lands with a slide-up | value, label |
| `climb_profile` | Elevation profile (open DEM) draws left to right; gradient bands | stage, km range |
| `lower_third` | Text slides up 20–30 px with fade, 0.25 s | text |

- **Output formats:**

| Format | When | Status |
|---|---|---|
| Full-frame **MP4** (H.264, 2160×3840, at the Edits project's frame rate, §14) | Map cards that replace the shot | Works in Edits today |
| **MOV ProRes 4444 with alpha** | Overlays on footage (route on top of Katarina, lower thirds) | Listed by HyperFrames per package mirrors (not yet confirmed in official docs); **Edits import untested** |
| **WebM VP9 with alpha** | Browser previews in the Hub | Not for Edits |
| PNG sequence | Fallback / archive | Always works |

- **Fallbacks if Edits rejects alpha video:** (1) use full-frame cards; (2) composite the overlay onto the footage with ffmpeg before import. That shot is then no longer editable in Edits, so it's recorded as a "baked" asset.
- **Motion tokens** (added to the design language once tested):
  ```yaml
  motion:
    ease: cubic-bezier(0.22, 1, 0.36, 1)   # ease-out
    pop_s: 0.3
    text_in_s: 0.25
    push_in: { from: 1.00, to: 1.08, over: card_duration }
    one_motion_idea_per_graphic: true
  ```
- **Asset record:** every render stores template, params, source HTML hash, HyperFrames version, output format, alpha yes/no, fonts used, `origin`, `ai_generated` (true for anything made with generative AI) and where it was used.
- **First test:** rebuild the Giro_00 card "Štart v Terste, cieľ v Ríme" with push-in and dot pops; render MP4 and alpha MOV; test both in a copy of the Edits project.

---

## 11. Module G: reviews, feedback and approvals

### 11.1 Versions
Each draft is a **version** (v1, v2, …) with the Edits project ID, a cut-list snapshot, runtime and an optional low-res preview. The cut list records at least:
- **Clips and times:** every timeline item in order and by layer (main, overlays, text, captions, music), with timeline in/out and, for media, clip and source in/out (integer ms) and moment ID.
- **Transform:** scale and `focus_x` per clip (e.g. Giro_00's hook at 0.545).
- **Audio:** gain in dB and muted yes/no per clip, and which source (Sony lav / DJI WAV).
- **Music:** asset ID, where in the track it starts (source offset), timeline in/out, internal re-cuts (music doesn't ripple in Edits) and level changes (ramps, fades, silent-card lift).
- **Graphics:** asset IDs, with their timeline position.

Tier-1 music is recorded by its Edits ID, never as audio. The diff view (§11.2) compares two cut lists item by item.

### 11.2 Feedback items
```yaml
feedback:
  id: fb_giro00_r2_1
  reel: giro00
  version: v3
  author: Ľuboš           # or Katarina, when Ľuboš logs a remark of hers
  at_ms: 42700
  element: closing_card
  request: "Shorten from ~6 s; text: Štart v Terste, cieľ v Ríme."
  status: done            # open | in_progress | done | wont_do
  resolution: "Card 5.5 s → 3.5 s; swapped to Terst+Rím overview map"
  resolved_in: v4
```
- Feedback can be pasted as a list (like today's rounds); the agent splits it into items.
- **Diff view** between versions: what text, timing and assets changed.

### 11.3 Approval
- The producer approves a **specific version** in the Hub UI (`approved: v4, by: Ľuboš, at: …`). **No MCP tool can approve.** Agents can only call `request_approval`.
- A newer version invalidates the approval of older ones.
- The approval screen shows the version, open feedback, open items and the reel's `editors_notes.md` including its checklist (§11.4). The producer reads them before approving; open items are resolved or explicitly waived. Nothing is blocked automatically.
- **Export:** the existing rule applies: nothing is exported before approval (CLAUDE.md, agent rules §17.3, prompt rules §6.4). Export happens in Edits, which the Hub doesn't see, so the agent calls `export_allowed(version)` before exporting and stops if it returns false. No hooks or content hashes.
- Posting is manual (§19.4). The Hub has no publish tools.

### 11.4 Editor's notes (`editors_notes.md`)
Every reel folder gets an `editors_notes.md` (`<project>/reels/<slot>/editors_notes.md`, next to `PROMPT.md`). The editing agent starts it with the first version and completes it at the end of the edit, before `request_approval`. It documents everything used and every practice followed, so the next reel, the graphics overview and a later critique can rely on it. Giro_00's [`docs/reference/giro00/review_notes.md`](../reference/giro00/review_notes.md) is the model.

- **Tools:** `get_editors_notes(reel)` and `update_editors_notes(reel, markdown)` (§17.2). The producer can edit it in the Reel screen too.
- **Indexed:** the Hub stores the file's text in FTS5 and reads its "Graphics used" and "Clips used" tables into `asset_usage` for the graphics overview (§20).
- **Used by:** the next reels' prompts (§6.3), the learning loop (§13) and, on demand, the AI critique (§16).

**Template:**
```markdown
# {reel.slot} · {reel.topic}: editor's notes

**Version:** v{n} · {date} · Edits project `{edits_project}` · runtime {runtime_s} s
**Status:** draft | ready for approval | approved | posted
**Design language:** {version}

## Story and structure
| Beat | Timeline | What happens |
|---|---|---|
| Hook | 0:00–0:06.4 | "Prečo je toto lízatko ružové? … Máj." |

## Clips used
| Timeline | Clip | Source in–out | Moment | Notes |
|---|---|---|---|---|
| 0:00–0:06.4 | giro00-sony-c0031 | 490.100–496.500 s | mom_0001 | focus_x 0.545 so she's in frame on frame 1 |

## Captions
- Style, position, speaker labels.
- Glossary and correction fixes (heard → correct).
- Muted pass done: yes / no.

## Instagram caption
{caption text, Slovak} · hashtags: {max 5} · location: {town} · CTA: {send | save | comment} · collaborators: {handles or none} · fact IDs: {…}

## Suggested pickups (not recorded)
Lines the edit would need that Katarina didn't say in one piece. The point to make, not a script; never used in captions or on screen as her speech.

| Point to make | Why it's needed | Where it would go |
|---|---|---|

## Facts used
| Fact ID | Claim as said or shown | Use (verified / attributed) | Source |
|---|---|---|---|

## Graphics used
| Asset ID | File | Timeline | Template / params | Notes |
|---|---|---|---|---|
| map-italy-terst-rim | graphics/map_trieste_roma.png | 0:42.7–0:46.2 | map_overview(Terst, Rím) | Closing card |

## Music
- Track, artist, Edits ID, section used, levels (under speech, silent card, ramps, fades).
- License record: tier · source · licensee · allowed platforms · notes (§15.6).
- [ ] Delivery loudness measured on the export: −14 LUFS integrated (±1.5 LU), true peak ≤ −1 dBTP (`ffmpeg -i export.mp4 -af ebur128=peak=true -f null -`; numbers only, §15.3)

## Fonts
| Font | Where | License |
|---|---|---|

## Design-language practices
- Followed: …
- Deviations and why: …

## Edits quirks hit
- … (new ones also added to the playbook with `add_playbook_item`)

## Legal and disclosure checklist
- [ ] Music allowed for Instagram and for this reel's commercial flags; no tier-1 library music if any flag is ticked (§15.6)
- [ ] Commercial flags filled in; paid partnership label planned if required
- [ ] No Edits (tier-1) audio captured, stored or sent to any service (§22)
- [ ] Fonts in graphics made outside Edits are licensed for video and container use (§10.1)
- [ ] No organizer maps, profiles, photos, logos or race footage shown or traced; open-data credits in the caption if OSM was used (§10)
- [ ] No `third_party_unlicensed` media (§5.1)
- [ ] No "oficiálny" / "official" wording; AI label planned if any asset is `ai_generated`
- [ ] Only Katarina's and Ľuboš's real words; no frankenbites; no synthetic voice or face (§6.4)
- [ ] No range excluded by a person was used (§5.3)

## Posting checklist
- [ ] Posted at {project.posting_time}; Trial is off (series episodes, §13.2)
- [ ] Cover readable in the profile-grid crop
- [ ] Caption per §8.1 (max 5 hashtags); location tag {town}
- [ ] Share to Facebook on (license record allows Facebook); collaborators: {handles or none} (sets `collab`, §12.5)
- [ ] Shared to Stories and added to the series highlight; pins updated

## Open items
1. …
```

---

## 12. Module H: performance analytics

The point: **know which choices make Reels perform**, then feed that back into the next reel's prompt.

### 12.1 Data sources

| Source | How | What |
|---|---|---|
| **Instagram API with Instagram Login** (Professional account + Meta developer app) | **24 h snapshot** from the first post (API pull or a 2-minute manual form), then pulls at 72 h, 7 d, 28 d after posting | Per-Reel (API v27.0, product type `REELS`): `views`, `reach`, `likes`, `comments`, `shares`, `saved`, `reposts`, `total_interactions`, `ig_reels_avg_watch_time`, `ig_reels_video_view_total_time`, `reels_skip_rate`; `facebook_views` when shared to Facebook. **Follows and profile visits aren't available for Reels via the API**: the producer enters follows from in-app insights at 7 d, together with the retention curve |
| **Instagram in-app insights** | Manual: screenshot or CSV import | Retention curve (where viewers drop off), skip rate, traffic sources, audience split. Not fully exposed via the API; confirm per API version |
| **Account-level insights** | API pull, daily | Follower count, profile visits, audience demographics, active hours |
| **Manual notes** | UI | Context: posted late, collab, boosted, trending audio, external event |

> **API note:** metric names and availability change between API versions (e.g. "plays" was replaced by "views"). The importer must map metrics per version and record which version produced each number. Media insights are lifetime totals and can lag up to 48 h, so a later pull can't recover a 24 h value: the 24 h snapshot must be captured at 24 h (manually if the API isn't ready). Windows before 24 h aren't tracked.

> **Platform terms:** official Instagram API with Instagram Login only; no scraping of instagram.com, the app's private API or the Edits insights dashboard. The Meta app stays in Development mode, with Katarina's account given an app role. The long-lived token is refreshed automatically, with an alert 7 days before it expires. Instagram comments are **not imported**; only metric counts are stored.

### 12.2 Reel features (what we measure against)
Every posted Reel is described by **features** pulled from the Hub's own data, so no manual tagging is needed:

```yaml
features:
  runtime_s: 50.9
  hook_type: curiosity-question        # question | claim | reaction | visual | text-only
  hook_first_words: "Prečo je toto lízatko ružové?"
  time_to_first_word_s: 0.08
  subject_in_first_frame: partial
  cuts_per_10s: 1.6
  dji_cutaways: 3
  graphics: [map_overview, map_card]
  graphic_seconds: 7.8
  on_screen_text_lines: 2
  caption_style: "Word Highlight Box V3"
  music: { id: music-dolce-vita, level_under_speech: 0.2 }
  ends_with: sign-off                  # cliffhanger | question | sign-off | cta
  promise_next_reel: false
  topic: project-intro                  # stage-story | place | how-to-get-there | history
  stage: null
  humor_beats: 3
  posted_at: 2026-12-01T18:00+01:00
  weekday: Tue
  caption_length_chars: 520
  hashtags: 5                          # Instagram allows at most 5 (§8.1)
  slot_type: intro                     # intro | stage | finale
  experiment: null                     # e.g. { id: exp_giro2027_ending, variant: tease } (§13.2)
  cta_type: send                       # send | save | comment | none (from the Instagram caption)
  location_tag: Trieste
  collab: false                        # from the posting checklist
  shared_to_facebook: true
  trial: false
```

### 12.3 Derived metrics
- **Skip rate:** `reels_skip_rate` from the API (share of initial views that skipped in the first 3 s); hook rate = 1 − skip rate. The manual retention curve is used to locate drops after 3 s.
- **Hold rate:** average watch time ÷ runtime.
- **Completion:** share reaching the last 10 %.
- **Rewatch indicator:** total watch time ÷ (reach × runtime), above 1 means rewatches (`views` already counts replays).
- **Share rate, save rate, comment rate:** per 1,000 reach. Saves and shares are the strongest signals for informational project.
- **Follow conversion:** follows per 1,000 reach (manual, 7 d), a series-loyalty readout. Facebook plays are reported separately and never mixed into Instagram views.
- **Project stickiness:** viewers of reel N who also viewed N+1 (approximated by reach overlap and day-over-day trend).
- **Normalized score:** each metric compared to the account's trailing 30-day median, so growth over time doesn't skew comparisons.

### 12.4 Dashboards
1. **Reel card:** all metrics vs. account median, retention curve with **the cut list overlaid** (see the drop at 0:42 align with the map card).
2. **Project view:** day-by-day trend across the 24 reels, with stage type (mountain, sprint, time trial) as color.
3. **Feature impact:** which features correlate with hold rate and saves (hook type, runtime band, graphics share, cutaways, humor beats, posting time).
4. **Retention heatmap:** where drops cluster across reels (e.g. "maps longer than 4 s lose 12 %").
5. **Best time to post:** performance by weekday and hour, using account activity data.

### 12.5 Analysis approach (honest statistics)
- With dozens of Reels, effects are noisy. Show **effect size with uncertainty ranges**, not just "better/worse".
- Prefer **within-project comparisons** (same format, same audience) and controlled changes (see experiments).
- Never conclude from a single post. Require at least N posts per variant (configurable, default 5).
- Mark confounders: collabs, trending audio, external news (e.g. the route reveal), paid boosts.

### 12.6 Agent-facing insights
The agent can ask, e.g.:
- `get_insights(project="giro2027-advent", question="which hooks hold best?")`
- `explain_drop(reel="giro05", at_s=12)` returns what was on screen and in the audio at that moment, plus similar drops elsewhere.
- `recommend(reel="giro06")` returns concrete edits ("open on the reaction, not the intro line; keep map ≤ 3 s; end on tomorrow's question").

---

## 13. Module I: learning loop and experiments

### 13.1 Playbook of findings
Findings are stored with evidence:
```yaml
finding:
  id: find_001
  statement: "Curiosity-question hooks hold 18 % longer than intro-line hooks"
  evidence: { reels: [giro00, giro03, giro07, …], effect: "+18 %", range: "+6…+29 %" }
  status: supported            # hypothesis | supported | rejected | retired
  applies_to: [giro2027-advent]
  added_to_design_language: false
```
- **Promotion path:** hypothesis → supported (enough evidence) → proposed design-language change → human approves → design language version bump.
- **Editor's notes as input:** the practices and deviations recorded in each reel's `editors_notes.md` (§11.4) are the "what we did" side of a finding; metrics are the "what happened" side.

### 13.2 Experiments
- **One pre-registered experiment per series**, decided before the first post, set on each reel when it's created (`log_experiment`) and shown in the prompt's "This reel" section. Everything else follows the design language. Posting time is never an experiment variable in a daily series; it stays fixed (§6.1).
- **December experiment** (resolves R32; the owner wants a teaser on the closing card):
  ```yaml
  experiment:
    id: exp_giro2027_ending
    variable: ending_type
    variants:
      tease: "closing card asks about the next stage; the answer is a verified fact (fact ID) and is not given; ≤ 8 words, e.g. 'Zajtra: celá etapa mimo Talianska. Kde?'"
      statement: "closing card states today's takeaway, e.g. 'Štart v Terste, cieľ v Ríme.'"
    constant: [card 3.5 s with music lift, spoken sign-off, "caption last line 'Zajtra: {n+1}. etapa.'", posting time, runtime band]
    assignment: "odd stage numbers → tease, even → statement (Stages 1–21: 11 vs 10); Day 1 and Days 23–24 are not in the experiment"
    primary_metric: follows_per_1k_reach_7d          # manual, from in-app insights (§12.1)
    secondary: [comments_per_1k_reach_72h, hold_rate_72h]
    guard: shares_per_1k_reach_72h                    # flag if the tease arm is more than 20 % lower
    decision_rule: "make 'tease' the default only if the primary metric is higher and its uncertainty range excludes 0 (§12.5); otherwise keep 'statement'"
    deviation: "if the next stage's fact isn't verified, the producer switches the reel to 'statement' and marks it deviated; deviated reels are left out of the analysis"
  ```
  With about 10 reels per arm only large effects will show; an inconclusive result keeps the default.
- Instagram's **Trial Reels** (public professional account with ≥ 200 followers) are shown to non-followers only and stay off the profile and followers' feeds unless shared. Never use them for series episodes, which followers must get on the day. In December use them only for extra standalone material (e.g. the tongue-twister bumper); after December use them to test hooks on new content, recorded with `trial: true`.

### 13.3 Recommendations in the prompt
When a reel's prompt is built (§6.3), the Hub adds recommendations: suggested hook type, target runtime, map hold time and ending type, each linked to the findings behind it. The posting time stays fixed during a series (§6.1).

---

## 14. Module J: tool knowledge (Edits playbook)

A living, versioned knowledge base of **how our tools actually behave**, for agents and humans:

```yaml
playbook:
  - tool: edits
    version_seen: "2026.10.19-1"
    items:
      - "App sandbox cannot read ~/Personal; keep media under ~/Movies (Reels Hub library: ~/Movies/ReelsHub)."
      - "addMediaPanelItemsToTimeline with startTime lands on an overlay; call convertToMain."
      - "trimClip: positive delta shortens, negative extends."
      - "Overlays, text and captions ripple with main-track trims; music does NOT."
      - "Generate captions only after all trims; stale captions can't be deleted."
      - "Monstera-Black has no en dash; Edits text boxes wrap at ~70 % width."
      - "Royalty-free music: DownloadError 3 (2026-11-11). Licensed library works."
      - "Licensed audio is obfuscated: can't be analyzed offline; listen manually."
      - "Edits for Mac (released 2026-11-10): multi-track, keyframes, color wheels/curves, Log conversion, LUT import (formats unpublished), voice enhance, export HD/2K/4K, SDR/HDR. Weekly updates: re-check quirks per version."
      - "2K (1440×2560) export is enough for Sony-based 9:16; the Sony's 9:16 crop is only 1215 px wide."
      - "Frame rate: Giro_00 was cut in Edits from 25p footage (Sony and DJI) and published. Reported options are 24/30/60 fps (mobile app 2026.10.19-1; CineD for Edits for Mac). TO CHECK once on the run machine and record here: which project frame rates Edits offers (24/25/30?) and how it conforms 25p clips (dropped frames on gestures?)."
```
- Agents append items when they hit a new quirk (and list it under "Edits quirks hit" in the reel's `editors_notes.md`). Items carry the date and tool version and can be marked fixed.

---

## 15. Module K: music

Music sets the tone of the project, so it gets the same care as footage. **Policy: real, commercial music first.** Generic royalty-free stock is not the default and is used only when nothing licensed works.

### 15.1 Music sources (in order of preference)

| Tier | Source | Use for | Notes |
|---|---|---|---|
| **1 · Platform-licensed commercial catalog** | Edits / Instagram licensed library (e.g. "Dolce Vita" by Italian Atmosphere, used in Giro_00) | Default for Reels posted from the account | Real artists and recognizable tracks. Licensed only on Meta platforms; can be muted or blocked in some regions; not reusable on other platforms. Availability depends on account type (see 15.6) |
| **2 · Premium licensed catalogs** | Curated libraries with real artists and stems, e.g. Artlist, Musicbed, Epidemic Sound's curated/artist tiers | Signature project themes, cross-platform reuse, YouTube cuts | Paid license covers reuse anywhere; stems (separate drums, bass, melody) allow clean edits under speech. Curate hard: only artist-grade tracks |
| **3 · Direct licensing** | Licensing a specific commercial track from the label or publisher | A hero track for a whole season | Expensive and slow; only for something that defines the project |
| **4 · Royalty-free stock** | Generic stock libraries | Last resort only | Not used by default. The Hub hides this tier unless explicitly requested |

**Not used:** ripping songs from YouTube or other streaming services (e.g. with yt-dlp). It breaks platform terms and creates copyright risk for the channel. yt-dlp stays allowed only for material we own or have explicit rights to.

### 15.2 Audition pipeline

Licensed tracks in Edits are obfuscated, and preview services don't allow downloads or analysis, so the Hub **never analyzes tier-1 audio**. It uses **metadata** for the shortlist and **the producer's ears** for the decision.

**Two separate steps:**
- **Audition (decide what makes sense):** full-track listening happens in Edits, or by the producer on YouTube or Spotify in the normal player. Nothing is downloaded, not even temporarily. Downloading from YouTube breaks its terms of service regardless of what the copy is used for.
- **Use (put it in the Reel):** the chosen track is always added through Edits' licensed library, so the published Reel is covered by Meta's license.

1. **Brief:** the reel or project sets the target, e.g.:
   ```yaml
   music_brief:
     mood: [playful, warm, forward-moving]
     flavour: italian
     vocals: none-or-minimal      # vocals compete with Katarina
     bpm: [88, 110]
     energy: low-mid under speech, lift on silent cards
     avoid: [generic corporate ukulele, stock "upbeat acoustic"]
   ```
2. **Candidate search:** query the Edits catalog (`listMusicTracks`, licensed) plus metadata services (MusicBrainz for genre, instrumental flag and artist; GetSongBPM for tempo and key, with its required backlink in the UI). Spotify's audio-features API is closed to new apps, so it isn't planned.
3. **Analysis (licensed audio only):** audio features (tempo, beat strength, LUFS, vocal presence via Demucs, speech-clash score in 300 Hz–3 kHz, energy curve) are computed **only** from audio the Hub is licensed to hold: tier-2 catalog downloads, tier-3 masters, or our own recordings. For tier-1 (Edits) tracks the Hub uses **metadata only**: ISRC, duration and explicit flag (iTunes Search / Deezer JSON), BPM and key (GetSongBPM), genre and instrumental tags (MusicBrainz). iTunes and Deezer preview audio is **never downloaded, cached, stored or analyzed**.
4. **Shortlist:** the agent proposes **at most 3 tracks**, each with its metadata and a one-line reason (e.g. "instrumental per MusicBrainz, 96 BPM, Italian guitar"). Taste filters remove generic stock-sounding tracks (§15.4).
5. **Producer audition:** Ľuboš listens in Edits (`previewMusicTrack`) and rates each: keep / maybe / reject, with an optional note ("too cheesy", "perfect energy").
6. **Place and mix:** the agent adds the chosen track in Edits on its own audio lane, aligned to a strong section, and applies the mix rules (§15.3).
7. **Mix check:** playback metering confirms speech peaks vs. music level and checks the silent-card lift. Only the levels (dB per section) are stored, never the audio (§22).

The agent never claims to have "listened". It reports measurements; taste is the producer's call.

### 15.3 Mix rules (from the design language)
```yaml
music_mix:
  under_speech: 0.20            # Dolce Vita starting value only; the rule is 15–18 LU below dialogue
  music_under_speech_lu: -15..-18   # relative to dialogue; depends on how the track is mastered
  silent_card: 0.80
  ramps_s: 0.4
  fade_in_s: 0.3
  fade_out_s: 1.2
  continuity: one continuous take of the song; re-cut pieces so the source stays contiguous
  align: start on a downbeat or a strong section, not necessarily 0:00
  deliver: { integrated_lufs: -14, tolerance_lu: 1.5, true_peak_dbtp: -1.0 }   # measured on the export
```
- **Delivery loudness:** Meta publishes no target; −14 LUFS integrated (±1.5 LU) with true peak ≤ −1 dBTP is common practice (checked 2026-11-12). The export is measured locally with `ffmpeg -af ebur128=peak=true`; only the numbers go into `editors_notes.md` (§11.4, §22). Speech peaks alone (≈ −3 dBFS) don't tell loudness.

### 15.4 Taste memory
- Every audition is stored: track, source, metadata, rating, note, who rated.
- The Hub learns a **taste profile** (preferred tempo range, instrumentation, vocals tolerance, rejected styles) and ranks future candidates with it.
- **Blocklist** of tracks and styles that were rejected ("generic royalty-free", "corporate ukulele", "stock 'inspiring piano'").
- **Signature tracks:** the tracks that define a project (e.g. "Dolce Vita" for Giro 2027) are pinned and reused for recognition.

### 15.5 Performance link
- Each posted Reel records its track, section used and levels. Analytics (§12) compares hold rate, saves and shares by track, mood and tempo, and flags Reels where audio was muted or restricted.
- Findings feed the taste profile ("Italian-instrumental beds hold 10 % longer than electronic beds"), with the same evidence rules as §13.

### 15.6 Licensing and platform constraints
A short license record per track:
```yaml
music_license:
  track_id: music-dolce-vita
  tier: 1                          # 1 edits-licensed | 2 premium | 3 direct | 4 stock
  source: edits-licensed
  licensee: null                   # tier 2/3: legal name on the license
  platforms_allowed: [instagram, facebook]
  notes: "Meta platform license; personal, non-commercial; reels with it can't be boosted"
```
- **Account type matters:** on Instagram, Business accounts get a much smaller music library than Creator accounts. Keep the account type that allows commercial music, and confirm it still gives API access to insights (Creator accounts are Professional accounts).
- **Commercial flags:** if any of a reel's commercial flags is ticked (§6.2), tier-1 Edits library music isn't allowed; use tier 2 or 3 with a license that covers branded use. Decide before the edit: the music can't be swapped after posting in order to boost. An unpaid co-authored post with another creator (`collab: true`) is not a commercial flag and doesn't rule out tier-1 music; whether the licensed library covers co-authored posts is still to be confirmed (§27).
- **Cross-posting** (YouTube Shorts, TikTok) needs tier 2 or 3 music, or a different track per platform.
- The license record is copied into the reel's `editors_notes.md` and confirmed by the producer through its checklist before approval (§11.4). There is no automatic gate.

### 15.7 Music assets
```yaml
music_asset:
  id: music-dolce-vita
  title: "Dolce Vita"
  artist: "Italian Atmosphere"
  edits_audio_asset_id: "1123460523193316"
  duration_s: 160.2
  metadata:                       # tier 1: metadata only (§15.2)
    bpm: ~95                      # Edits beat count 254 over 160 s
    vocals: none (to confirm)
  analysis: null                  # only for tier 2/3 or own audio
  ratings: [{ by: Ľuboš, verdict: keep, at: 2026-11-11 }]
  used_in: [{ reel: giro00, section_s: [0, 50.9], levels: {under_speech: 0.2, card: 0.8} }]
  license: { ref: music_license }
```

---

## 16. Module L: AI critique

> **Phase 10, after December, on demand only.** The critique runs only when the producer triggers it on an exported or rendered video. It never runs automatically, and nothing in the December flow depends on it.

An AI reviewer **watches a rendered reel** and writes a critique when the producer asks for it. Its input is the render plus the reel's `editors_notes.md` (§11.4) and the design language. It acts as a demanding viewer, not as the decision maker.

### 16.1 What the critic receives
- **Picture:** frames sampled densely (e.g. 4 fps, plus every cut and every text change) from the render at 1080×1920, and full-resolution frames for the first second and the last 3 seconds.
- **Sound:** the transcript of the mixed audio, loudness curve (speech vs. music), silences, and music level per section. Loudness is measured locally from the render and only the numbers are sent; renders with tier-1 music are never uploaded to an external AI service (§22).
- **Editor's notes:** the reel's `editors_notes.md`: story, clips, facts, graphics, music and license, practices followed, deviations with reasons, checklist and open items.
- **Context:** the reel brief and prompt (§6.4), design language, facts used, the previous and next reel, and findings from analytics.
- **Two viewing modes:** sound on and **muted** (captions and text only), critiqued separately.

### 16.2 What it checks
| Area | Questions |
|---|---|
| **Hook (0–3 s)** | Is there a specific curiosity on frame 1? Is the subject fully in frame? Would a muted viewer understand it? |
| **Story** | Is the promise clear by ~20 s? Does the payoff arrive? Does the ending set up the next reel? |
| **Pacing** | Dead air, slow stretches, cuts per 10 s vs. what worked, a card held too long |
| **Katarina** | Is her strongest take kept long enough for its payoff? Are jokes cut before the punchline? Does any cut change what she meant? |
| **Captions** | Every line of speech captioned, Slovak spelling and diacritics, glossary terms, phrase breaks, sync with speech, off-camera speaker labels |
| **Design** | Token compliance, safe zones, text over faces, one accent color, legibility over bright backgrounds |
| **Graphics** | Does each graphic help understand a line? Readable alongside captions? Does it give away tomorrow's answer? |
| **Sound** | Speech intelligible on a phone speaker, music level, abrupt cuts or clicks, music fitting her delivery |
| **Facts** | Every claim spoken or shown is backed by a verified fact; unconfirmed claims are flagged |
| **Platform** | Runtime, Reels UI overlap, licensed-music restrictions, cover frame |
| **Continuity** | Matches what the previous reel promised; consistent with the rest of the project |
| **Notes vs. render** | Does the render match what `editors_notes.md` says was done? Deviations the notes explain aren't flagged as errors |

### 16.3 Output
```yaml
critique:
  reel: giro00
  version: v5
  mode: [sound_on, muted]
  overall: 7.5/10
  scores: { hook: 7, story: 8, pacing: 6, captions: 9, design: 8, sound: 7, facts: 9 }
  predicted_risk: "drop around 0:23–0:42: 19 s single talking shot with no visual change"
  items:
    - at_s: 0.0
      severity: major            # blocker | major | minor | nit
      area: hook
      finding: "Katarina is half out of frame on frame 1; the lollipop appears at 0.8 s."
      suggestion: "Start 0.3 s later or punch in so the lollipop is visible on frame 1."
      evidence: frame@0.0, frame@0.8
    - at_s: 23.2
      severity: minor
      area: pacing
      finding: "No visual change for 19 s during the trip-tips line."
      suggestion: "Add a map pop for Dolomity / Alpy / Apeniny or a DJI cutaway."
  strengths:
    - "DJI reveal of Ľuboš on 'ja a Ľuboš' lands the joke."
```
- Items show up in the Reel screen next to the producer's own feedback, marked **AI critique**.
- The producer turns the items he agrees with into feedback items for a new version, or into notes for the next reel's prompt. Final decisions stay with the producer.

### 16.4 Calibration
- **Predicted vs. actual:** after posting, the critique's predicted risks are compared with the real retention curve and metrics (§12). Critic accuracy is tracked per area.
- **Producer agreement:** each item can be marked agree / disagree, which tunes what the critic flags.
- **Rubric versions:** the checklist and weights are versioned like the design language, and changes need evidence.
- **Pinned model:** the critic's model ID is pinned in config (§21), so a model change is a deliberate config change.
- **Blind spots stated:** the critic can't judge taste in commercial music (licensed audio is obfuscated) and can't hear nuance the way a person does; it says so instead of guessing.

### 16.5 When it runs
Only on demand, never automatically:
1. The producer clicks **Critique** on a reel in the Hub and picks an exported or rendered video file, or explicitly asks an agent to call `critique_reel`. Agents never start a critique on their own, and no new version, approval or status change triggers one.
2. **Input:** the render, the reel's `editors_notes.md` and the design language (plus the context in §16.1).
3. **Typical uses:** on the final render before posting, or on an already posted reel to build the calibration set.

---

## 17. Agent interface (MCP server)

One MCP server `reels-hub`, streamable HTTP at `http://127.0.0.1:8787/mcp`. All tools are listed in one list (no toolsets).

### 17.1 Resources (read-only context)
| URI | Content |
|---|---|
| `hub://design-language/current` | Tokens + Markdown |
| `hub://playbook/edits` | Tool quirks |
| `hub://project/{id}` | Project plan, status, continuity |
| `hub://reel/{id}` | Brief, status and dates, linked footage, versions, feedback, open items, metrics |
| `hub://reel/{id}/prompt` | The reel's current prompt (§6.4) |
| `hub://reel/{id}/editors-notes` | The reel's `editors_notes.md` |
| `hub://graphics/{project}` | Graphics overview: every graphic used, with files and where it's used |
| `hub://stages/giro2027` | Stage reference table with sources |
| `hub://glossary/sk` | Spellings, corrections |

### 17.2 Tools

**Conventions:** names are `verb_noun` as listed below. List and search tools take `limit` (default 20) and `offset`. Tools that can take longer than about 20 s (ingest, transcription, renders) return a `job_id`; the agent polls `get_job`. Errors say what to do next (e.g. "version v4 is not approved; ask the producer to approve it in the Hub").

**Footage and moments**
- `search_moments(query, filters, limit?, offset?)` → ranked moments with transcript, angles, thumbnails (excluded ranges and `third_party_unlicensed` media are never returned)
- `get_transcript(clip_id, range?)` → words with timestamps and speakers (active transcript run, with manual fixes from `transcript_edit` applied)
- `get_take(take_id)` → synced clips and offsets
- `frame_sheet(clip_id, times[])` → image
- `tag_moment(clip_id, in_ms, out_ms, tags, rating, notes)` / `exclude_range(clip_id, in_ms, out_ms, reason)` (an agent's exclusion is stored as `agent_proposed` until a person confirms)
- `host_paths(clip_ids | asset_ids)` → Mac paths Edits can import (media root + relative path, §23.2)

**Projects and reels**
- `create_project(spec)` → links media folders, assets, fact domain, glossary, design language; starts ingest
- `get_project(id)` / `link_assets(project, asset_ids)`
- `create_reel(project, slot, brief?)` → reel with status `created` (§6.2)
- `add_footage(reel, clip_ids)` → links clips to the reel and starts the automatic analysis and prompt build; returns a `job_id` (§6.3)
- `list_reels(project, status?)` → reels with their dates (created, footage added, approved, posted), as in the project overview (§6.5)
- `get_reel(id)` / `update_reel(id, fields)`
- `generate_reel_prompt(reel, template_version?)` → regenerates the prompt Markdown + saved prompt version (§6.4)
- `check_continuity(project)`
- `get_editors_notes(reel)` / `update_editors_notes(reel, markdown)` (§11.4)
- `link_publication(reel, platform, media_id, posted_at, url?)` → records the post after manual posting (§19.4)

**Facts and language**
- `check_fact(claim)` → matching facts, status (verified / attributed / …), sources
- `add_fact(claim, sources[])` / `mark_fact_checked(fact_id, says?)` (the **Re-checked** button, §7.2)
- `lint_script(text, kind?)` → unsupported claims, glossary violations; with `kind: caption` also counts hashtags (max 5, §8.1)
- `fix_captions(captions[])` → corrected captions using glossary forms and the correction memory (phrase matches and `always` rules applied; other matches returned as suggestions, §8)

**Design and graphics**
- `get_style_tokens(section?)`
- `lint_draft(edits_project_id | frame_sheet)` → style violations
- `generate_map(template, params)` → asset
- `render_motion(template, params, format: mp4 | mov_alpha | webm_alpha | png_seq)` → `job_id`, then asset (HyperFrames)
- `register_asset(path, type, meta)` (meta includes `origin`, license, `ai_generated`)
- `list_graphics_usage(project?, asset_id?)` → every graphic with thumbnail URL, file, and which reels use it and where (§20)

**Music**
- `search_music(brief)` → candidates from the Edits licensed catalog and premium catalogs (royalty-free stock excluded unless `include_stock: true`)
- `analyze_track(track)` → bpm, vocals, loudness, speech-clash score, energy curve; **refuses** for tier-1 tracks (returns metadata only) and works only on tier 2/3 or own audio (§15.2)
- `shortlist_music(reel, brief)` → max 3 tracks with metadata and reasons
- `rate_track(track, verdict, note)` → updates the taste profile
- `get_music_license(track)` → tier, source, licensee, allowed platforms, notes
- `check_mix(edits_project_id)` → speech peaks vs. music levels from playback metering (levels only)

**Reviews**
- `create_version(reel, edits_project_id, cut_list)` (cut-list minimum fields §11.1)
- `log_feedback(reel, items[])` / `resolve_feedback(id, resolution)`
- `request_approval(version)` → tells the producer the version is ready; it doesn't approve
- `get_approval(version)`
- `export_allowed(version)` → boolean + reason; agents call it before exporting in Edits

**Analytics**
- `get_metrics(reel | project, window)`
- `get_retention(reel)` → curve + overlaid cut list
- `get_insights(scope, question)`
- `explain_drop(reel, at_s)`
- `recommend(reel)`
- `log_experiment(reel, variable, variant)`

**Playbook**
- `get_playbook(tool)` / `add_playbook_item(tool, text, version)`

**Jobs**
- `get_job(id)` → status, progress, error

**Critique** (phase 10, only when the producer asks, §16.5)
- `critique_reel(reel, render)` → scored critique with timestamped items (§16)
- `rate_critique_item(item, agree | disagree, note?)`
- `get_critique_accuracy(project?)` → predicted vs. actual drop points, producer agreement

### 17.3 Agent rules enforced by the server
- Read access by default. Writes are logged with agent ID, session and diff.
- **No MCP tool can approve a version.** Approval happens only in the Hub UI. Agents never export before approval; `export_allowed` tells them.
- **Exclusions:** ranges excluded by a person (`excluded_by: katarina | luboš`) are never returned to agents, and agents can't change `usable` on them. Agents can only propose exclusions. `third_party_unlicensed` media is hidden from agents the same way.
- Proposed lines are never written as transcript text, captions or on-screen speech; they go under "Suggested pickups (not recorded)" in `editors_notes.md` (§11.4).
- Agents never start an AI critique on their own (§16.5).

---

## 18. Data model

**Rules**
- Media times are **integer milliseconds** (`src_in_ms`, `t_in_ms`). Timestamps are UTC ISO-8601.
- File paths are stored **relative to the media root** (or to `/data` for internal files); Mac and container paths are derived (§23.2). No absolute paths in the DB.
- IDs are short readable ids or slugs (`mom_0001`, `giro00`); nothing more is required.

```
project ─┬─< reel ─┬─< version (cut_list json) ─< approval
         │         ├─< feedback
         │         ├─< open_item
         │         ├─< reel_clip >─ clip (the reel's footage)
         │         ├─< status_change (from, to, at)
         │         ├── editors_notes (1:1: file + FTS index)
         │         ├── features (1:1)
         │         ├─< publication ─< metric_snapshot (window, metric, value, source, api_version)
         │         ├─< retention_point (t_ms, pct)
         │         ├─< reel_prompt (template_version, text, sent_at)
         │         └─< critique ─< critique_item (phase 10)
         ├─< project_media_folder
         ├─< project_asset >─ asset
         ├── fact_domain · glossary_set · taste_profile
         └── design_language_version

shoot ─< take ─< clip ─┬─< transcript (run: engine, model, revision, config, active) ─< transcript_word (t_in_ms, t_out_ms, text, speaker, conf, timing)
                       ├─< transcript_edit (time-anchored manual fix)
                       ├─< moment (in_ms, out_ms, tags, rating, usable, excluded_by)
                       ├─< shot / silence
                       └── device (camera, clock_offset_ms)

asset (graphic | motion | music | sfx | font | tool) ─< asset_usage >─ reel / version
music_track ─┬─ music_license        ─< music_audition (rating, note, by)
             └─ music_analysis (tier 2/3 and own audio only)
taste_profile ─< blocklist_item       motion_template ─< motion_render
fact ─< fact_source        glossary_term        correction
finding ─< finding_evidence >─ reel          experiment >─ reel
playbook_item              agent_log          job
```

**Key tables (SQLite)**

| Table | Key fields |
|---|---|
| `clip` | id, rel_path, hash, camera, duration_ms, fps, res, color_transfer, start_tc, shoot_id, take_id, origin, availability, volume_id, flags (json: fps_mismatch, vfr, hdr_log), alt_audio_rel_path, clipped_ranges (json) |
| `transcript` | id, clip_id, engine, model, model_revision, config (json), created_at, active |
| `transcript_word` | transcript_id, t_in_ms, t_out_ms, text, speaker, confidence, timing (aligned / interpolated) |
| `transcript_edit` | clip_id, t_in_ms, t_out_ms, old_text, new_text, kind (text / speaker), by, at |
| `transcript_fts` | FTS5 over transcript text (`unicode61 remove_diacritics 2`), diacritic-insensitive |
| `moment` | id, clip_id, in_ms, out_ms, tags (json, prefixed vocabulary incl. `tech:`), rating, usable, reason, excluded_by, notes |
| `asset` | id, type, rel_path, origin, license (json), ai_generated, meta (json) |
| `asset_usage` | asset_id, reel_id, version_id, t_in_ms, t_out_ms, note (read from `editors_notes.md`) |
| `project` | id, title, folder (relative), platform, account, run (json), design_language_version, music_signature, posting_time, experiment (json), parent_project_id |
| `reel` | id, project_id, slot, slot_type, stage, status, brief (json), commercial (json flags), collab, edits_project, target_runtime_ms, runtime_ms, planned_post_date, posting_time, experiment_variant, hands_on_min, delayed_by_hub |
| `status_change` | reel_id, from_status, to_status, at |
| `reel_clip` | reel_id, clip_id, added_at |
| `editors_notes` | reel_id, rel_path, version_n, text, updated_at (text indexed with FTS5) |
| `reel_prompt` | id, reel_id, template_version, text, word_count, created_at, sent_at |
| `version` | id, reel_id, n, edits_project, cut_list (json, minimum fields §11.1), preview_rel_path, created_at |
| `approval` | version_id, by, at, invalidated_at |
| `feedback` | id, reel_id, version_id, author, at_ms, element, request, status, resolution, after_post |
| `fact` / `fact_source` | claim, status (verified / attributed / unverified / conflicting / outdated), review_by / url, kind (primary / archive / secondary / lead), says, checked |
| `stage` | fact_domain, n, date, start, finish, km, type, climbs (json, optional), places (json with country, optional) |
| `glossary_term` | term, original, type, forms (json), captions (as_said / canonical), heard_as (json), keep_as_said, pronunciation, source, checked_by |
| `correction` | heard_phrase, correct_phrase, always, created_at |
| `publication` | id, reel_id, platform, account, media_id, url, posted_at |
| `metric_snapshot` | publication_id, window, metric, value, source (api/manual), api_version, pulled_at |
| `retention_point` | reel_id, t_ms, pct, source (api/manual) |
| `features` | reel_id, json blob (see §12.2) |
| `music_license` | track_id, tier, source, licensee, platforms_allowed, notes |
| `finding` | statement, status, effect, range, applies_to |
| `critique` / `critique_item` | reel_id, version_id, render_rel_path, mode, scores (json), predicted_risk / at_s, severity, area, finding, suggestion, verdict (phase 10) |
| `job` | id, kind, params (json), status (queued / running / done / failed), progress, error, created_at, updated_at |
| `agent_log` | at, agent, tool, args, result_summary, diff |

---

## 19. Key workflows

### 19.0 The main flow
Every reel goes through the same steps. Creating the project is a one-time setup.

```
(one-time) Create project ──▶ media folders, assets, facts, glossary, design language linked
      │
      ▼
1. New reel in the project ──▶ status created (slot, stage, topic, optional hook/promise notes, flags)
      │
      ▼
2. Katarina and Ľuboš shoot (the plan is in their heads; the Hub does no shoot planning)
      │
      ▼
3. Add footage: cards copied into <project>/raw/…, clips linked to the reel ──▶ footage_added
      │
      ▼
4. Automatic analysis ──▶ analyzing
   ingest, proxies, transcripts, speaker labels, multicam sync, suggested moments,
   glossary/caption corrections, relevant facts, design rules, playbook,
   learnings from previous reels (§5, §6.3)
      │
      ▼
5. Reel prompt built automatically (§6.4) ──▶ prompt_ready (producer can edit or regenerate)
      │
      ▼
6. Producer's own Claude session edits with the Reels Hub MCP + Edits MCP ──▶ editing
   and writes editors_notes.md (§11.4)
      │
      ▼
7. Version ──▶ in_review ──▶ feedback rounds ──▶ approval in the Hub ──▶ approved
      │
      ▼
   Export ──▶ post (manual) ──▶ link publication ──▶ metrics (24 h, 72 h, 7 d, 28 d) ──▶ analyzed
      │
      ▼
   Findings + editors' notes ──▶ next reel's prompt

Always available: the project overview of what was built and when (§6.5)
On demand only: the producer triggers an AI critique of a render + editors_notes.md (§16)
```

### 19.1 Add footage → automatic analysis
1. After the shoot, copy the cards into the project's `raw/` folders (§23.2). The watcher ingests them and links the clips to the project.
2. On the reel, click **Add footage** (or `add_footage`); the Hub pre-selects the new clips and the producer confirms. Status: `footage_added`.
3. The Hub analyzes automatically (`analyzing`): proxies, transcripts, speaker labels, sync, shots, glossary and caption corrections, suggested moments ranked for the reel's topic (§6.3). Ľuboš may rate or exclude moments, but nothing waits for him.
4. Edits can import the clips in place through their Mac paths (`host_paths`, §23.2).

### 19.2 Prompt → draft
1. When analysis finishes, the Hub gathers the reel intelligence and builds the prompt (§6.3, §6.4). Status: `prompt_ready`. The producer reads it, edits or regenerates it if needed.
2. He hands it to his own Claude session: copy and paste, or the session reads `hub://reel/{id}/prompt`. Status: `editing`.
3. The agent follows the prompt: `search_moments` → hook, promise, payoff, sign-off; builds in Edits; generates graphics (`generate_map`, `render_motion`); places music; captions, then `fix_captions`.
4. `lint_draft`; the agent fixes what it agrees with and notes the rest.
5. `create_version` with the cut list, then `update_editors_notes` (complete, including the checklist, open items and suggested pickups), then `request_approval`. Status: `in_review`.

### 19.3 Review loop
1. Ľuboš pastes feedback → `log_feedback` splits it into items.
2. Agent applies them → `resolve_feedback` → new version → diff view → `editors_notes.md` updated.
3. Ľuboš reads `editors_notes.md` and its checklist and approves the version in the Hub → `export_allowed` returns true → the agent (or Ľuboš) exports in Edits.
4. Optional, on demand: Ľuboš triggers an AI critique of the render (§16.5).

### 19.4 Post and learn
1. Ľuboš posts in Instagram at the project's `posting_time` (manual; in-app scheduling allowed), following the posting checklist in `editors_notes.md` (§11.4), then records it with `link_publication` (or in the UI).
2. **From the first post**, the 24 h snapshot is captured at 24 h, via the API or the 2-minute manual form. Later pulls run at 72 h / 7 d / 28 d; the API can lag up to 48 h, so the 24 h value is never left to a later pull. The retention curve and the follows count (7 d) are entered manually.
3. Features are computed automatically. The reel card shows performance vs. median.
4. Weekly: `get_insights` → candidate findings → human promotes → design language updated.
5. Findings, metrics and the reel's `editors_notes.md` feed the next reel's prompt (§6.3).

---

## 20. User interface

| Screen | Purpose |
|---|---|
| **Today** | Reels due, new footage not yet added to a reel, analyses running or failed, clip flags (frame rate, VFR, HDR/Log), prompts ready, approvals waiting, open items, 24 h snapshots due, a warning when media free space is below 100 GB (§27) |
| **Library** | Clips by shoot/take, synced angles, transcript side panel, moment tagging, exclusions |
| **Search** | Text search with filters and previews (semantic and visual search later) |
| **Project overview** | What was built and when (§6.5): every reel with its status and dates (created, footage added, approved, posted) and links to its footage, graphics, music and `editors_notes.md`; calendar grid with continuity warnings |
| **Projects** | List of projects; **Create project** wizard (folders, assets, fact domain, design language, music signature) |
| **New reel** | Pick slot, enter topic, optional hook and promise notes, commercial flags → reel created |
| **Reel** | Brief, commercial flags, **Add footage** and linked clips, analysis progress, **reel prompt** (preview, edit, regenerate, copy), prompt history, versions, preview, feedback, open items, `editors_notes.md` (view and edit), approval button, metrics tab, **Critique** button (phase 10, on demand) |
| **Graphics** | Every graphic and asset used: thumbnail, file, which reels use it and where in the reel. Built from `editors_notes.md` and the asset registry (DESIGN_LANGUAGE §11) |
| **Critique** (phase 10) | Timeline with critique items as markers, sound-on and muted views, agree/disagree, critic accuracy |
| **Facts** | Claims by status, conflicts queue, re-check due, **Re-checked** button per fact |
| **Design** | Tokens, version history, lint results, graphic templates |
| **Analytics** | Manual 24 h snapshot form, project trends, feature impact, retention heatmap, findings |
| **Playbook** | Tool quirks with dates |
| **Agent log** | What agents read and changed |

- **Language per output:** UI labels in English (the producer is the only user). Anything that ends up on screen or in captions, and every suggested pickup line, is Slovak and uses glossary forms; captions follow what was said (clean verbatim, Trieste or Terst as spoken), titles, maps and post captions follow the place-name policy (§8). Reel prompts may be English, with Slovak quoted verbatim.
- Keyboard-first review: J/K/L scrubbing, `M` to mark a moment, `F` to add feedback at the playhead.

---

## 21. Tech stack

| Layer | Choice | Why |
|---|---|---|
| Runtime | **Python 3.12 + FastAPI**. HyperFrames runs as a **Node 22 CLI subprocess** in the same image; no second service | Ingest, ML, music analysis and DB are Python; HyperFrames is the only Node part and is batch work |
| DB | SQLite + FTS5; numbered SQL migration files, forward-only, with an automatic DB backup before migrating | Single file, local, fast full-text search. Vector search later |
| Jobs | A simple SQLite `job` table (status, progress, error) and a worker loop in the same container; jobs that were running are re-queued on restart; periodic work (metric pulls, fact re-checks) is enqueued by a timer. No APScheduler, no leases or pools | Ingest, transcription, renders, metric pulls; job state visible in the UI and via `get_job` |
| Media | ffmpeg / ffprobe | Proxies, thumbnails, audio extraction, sync |
| Transcription | WhisperX on faster-whisper (CPU, int8) with the Slovak fine-tune `kinit/whisper-large-v3-turbo-sk` or base `large-v3`, chosen by benchmark (§5.1a); forced alignment always in the container; mlx-whisper only via the optional Mac helper | Local Slovak with word timestamps |
| Speakers | pyannote `speaker-diarization-community-1` through WhisperX + one voice print per person for naming (§5.1a) | Katarina / Ľuboš labels |
| Computer vision | OpenCV (`opencv-python-headless`) + PySceneDetect | Shots, subject tracking for crops, first-frame check |
| Motion graphics | HyperFrames (Node 22+, headless Chrome, ffmpeg) | HTML/CSS/SVG compositions → MP4 / ProRes 4444 alpha |
| Music analysis | librosa (tempo, loudness, spectrum) + Demucs (vocal separation) | Only on audio we're licensed to hold (tier 2/3, own recordings) |
| Music metadata | Edits catalog, MusicBrainz, GetSongBPM, iTunes Search / Deezer (metadata only; previews never downloaded, stored or analyzed) | Candidates without ripping |
| LLM | Anthropic API called from the container (key as Podman secret `anthropic_key`); model ID pinned in config, never an alias | Feedback splitting, insights; critique in phase 10 |
| Graphics | Python SVG templates → PNG with resvg (container, OFL fonts only); `qlmanage`/`sips` only for Mac-side scripts | Works in Linux |
| Deployment | Podman container (single `linux/arm64` image) + named volume + `~/Movies/ReelsHub` bind mount, started on the run machine by `deploy.sh`; optional Mac transcription helper | §23 |
| Code, CI and registry | GitHub repo `ai-slop-code/reels-hub` (org ai-slop-code, owner identity LubosBa); **GitHub Actions** runs the full test suite on every pull request (the merge gate, §24.1) and on every merge to `main` builds the arm64 image and pushes it to **GitHub Container Registry** `ghcr.io/ai-slop-code/reels-hub` | One image, tested before merging, pulled by the run machine (§23.6) |
| UI | Server-rendered **Jinja2 + HTMX** on `localhost`, no JS build step | Simple, one language, works in any browser |
| Agent API | MCP server on **streamable HTTP only** at `/mcp`, in the same FastAPI app | Standard for agents; the server lives in the container |
| Backup | Daily (catch-up) SQLite backup to `/media/_backups/db/` (visible to Time Machine), plus one before every update or migration; restore rehearsed once before 27 Nov (§23.6) | The DB lives inside the Podman VM disk; masters are already on the Mac |

**Disk budget:** proxies about 1–2 % of masters; transcripts and thumbnails are negligible. Masters dominate (Giro_00: ≈ 37 GB for one reel, §27).

---

## 22. Security, privacy and safety

- **Local only.** The MCP server and UI bind to localhost; the MCP endpoint requires a token.
- **Secrets** (Meta API token, Anthropic API key, Hugging Face token for gated model downloads) are passed as Podman secrets, never baked into the image, stored in the DB or written to logs. The read-only GitHub token for pulling images (`read:packages`) lives in the macOS Keychain on the run machine (§23.6).
- **Ports** are published on `127.0.0.1` only; the MCP and UI aren't reachable from the network.
- **Footage privacy:** do-not-use ranges and private talk stay excluded from agent search and are never sent to any external service. Exclusions made by a person can only be lifted by that person (§5.3).
- **Voice prints are for speaker labels only.** They are never exported, never sent to an external service, and never used for speech synthesis, voice cloning or lip-sync. No tool in the Hub generates Katarina's or Ľuboš's voice or likeness.
- **Licensed audio:** the Hub never captures, records or stores tier-1 (Edits) music and never tries to bypass Edits' audio obfuscation. `check_mix` stores levels only (dB per section). Renders containing tier-1 music stay on the Mac and are never uploaded to external AI services.
- **Third-party media:** `third_party_unlicensed` items (race broadcast, organizer photos and maps, other creators' reels) are reference-only and never used in a reel (§5.1).
- **Instagram:** official API only, no comment import (§12.1).
- **External calls** (fact checks, Instagram API, Anthropic API) are logged. No personal data goes into URLs.
- **Approval** is recorded only in the Hub UI; no MCP tool can approve (§11.3).
- **Agent writes are reversible:** every change is stored as a diff in `agent_log`.

---

## 23. Deployment (Podman)

Reels Hub ships as **one container image** run with Podman. Edits, Claude and (optionally) GPU transcription stay on the Mac.

### 23.0 Build machine vs. run machine
| Machine | What it does | Hardware |
|---|---|---|
| **Build machine** (Apple M5, Podman 6, applehv) and **GitHub Actions** | Develop and test (§24.2). CI builds the release image; the build machine only builds images for local testing. Never runs the Hub with real footage | M5 |
| **Run machine** (the owner's older MacBook) | Holds Edits, the footage in `~/Movies/ReelsHub` and runs the Hub container. Needs Podman, a Podman machine sized per §23.3, Claude Code or Desktop, Edits + Edits MCP. No Python, Node or repo checkout; only `deploy.sh` and its launchd agent from the repo | Apple M5, 24 GB RAM, 1 TB SSD |

- Both machines are Apple silicon, so the image is **`linux/arm64`** and both use Podman 6 with the `applehv` provider. Confirm the run machine's Podman version and free disk before phase 0 ends.
- First deploy to the run machine at the end of phase 0, not first at the dress rehearsal. "Done when" checks that involve footage or speed (phase 0, the §5.1a benchmark) are measured **on the run machine**.

### 23.1 What runs where
```
┌──────────────────────────── Mac (host) ─────────────────────────────┐
│                                                                     │
│  Edits app ◀── Edits MCP ──┐                                        │
│                            │                                        │
│  Claude (Code / Desktop) ──┼──▶ http://127.0.0.1:8787/mcp ──┐       │
│                            │                                │       │
│  Browser ──────────────────┼──▶ http://127.0.0.1:8787       │       │
│                                                             │       │
│  [optional] transcribe-helper (mlx-whisper on Metal) ◀──────┤       │
│        http://host.containers.internal:8788                 │       │
│                                                             ▼       │
│  ┌──────────────── Podman machine (Linux VM) ─────────────────────┐ │
│  │  reels-hub container                                           │ │
│  │   UI · MCP server · CLI · worker loop (job table)              │ │
│  │   ingest: ffmpeg, OpenCV/PySceneDetect, faster-whisper (CPU)   │ │
│  │   HyperFrames (Node CLI + headless Chrome) · music analysis    │ │
│  │   Instagram importer · critique frame extraction (phase 10)    │ │
│  │                                                                │ │
│  │   /media  ◀── bind mount ── ~/Movies/ReelsHub   (footage)      │ │
│  │   /data   ◀── named volume reels-hub-data  (DB, proxies, …)    │ │
│  └────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────┘
```

| Component | Where | Why |
|---|---|---|
| UI, MCP server, DB, worker loop | Container | Single portable unit, easy to update and test |
| Ingest: ffmpeg, OpenCV, PySceneDetect, shot detection | Container | Pure CPU, Linux-friendly |
| HyperFrames rendering | Container (Node CLI subprocess) | Headless Chrome + ffmpeg; HyperFrames documents Docker rendering |
| Music analysis (librosa, Demucs) | Container | Tier 2/3 and own audio only; CPU is enough |
| Instagram importer, fact re-checks | Container | Network jobs |
| Transcription | Container (faster-whisper on CPU) **or** Mac helper (mlx-whisper on Metal) | The Mac GPU isn't available inside Podman's Linux VM; choose by benchmark |
| Edits + Edits MCP | Mac | Mac app; the container never drives it |
| Claude | Mac | Connects to both MCP servers |

### 23.2 Media library location (solves the Edits sandbox)
- All project media lives under **`~/Movies/ReelsHub/<project>/`**, a location Edits can read.
- It's bind-mounted into the container as `/media`. You copy footage into the Mac folder; the container sees it immediately and Edits can import the same files directly. **No hard-link staging is needed.**
- The DB stores each file's path **relative to the media root** (e.g. `giro2027/raw/sony/C0031.MP4`). Both real paths are derived from it:
  ```yaml
  clip:
    rel_path: giro2027/raw/sony/C0031.MP4
    # container: /media/giro2027/raw/sony/C0031.MP4
    # Mac (what Edits and Claude use): /Users/lubos/Movies/ReelsHub/giro2027/raw/sony/C0031.MP4
  ```
- The host media root is configured once as an **absolute** path, never with `~`: `REELS_HUB_HOST_MEDIA_ROOT=/Users/lubos/Movies/ReelsHub`. Edits can't use `~` paths, so the Hub refuses to start if the value isn't absolute.
- Generated files Edits needs (graphics, motion renders) are written to `/media/<project>/graphics/` so they're also Edits-readable.
- **Media marker:** on first setup the Hub writes `/media/.reels-hub-root`. If the marker is missing (VM started without the share, folder renamed), the watcher pauses, no clip is marked `offline`, and `/health` returns 503 with `media_mounted: false`.
- **Existing footage** (Giro_00: ≈ 37 GB) is brought into the library with hard links on the same APFS volume (`ln <file> ~/Movies/ReelsHub/giro00/raw/sony/`), not copies, so it takes no extra space and the existing Edits project's links keep working. The Hub only reads `raw/`.

### 23.3 Running it
One-time setup on the run machine (M5, 24 GB: 8 CPUs, 12 GB, 100 GB VM disk leaves room for macOS, Edits and Claude):
```bash
podman machine init --provider applehv --cpus 8 --memory 12288 --disk-size 100
```
```bash
podman machine start
```
```bash
podman volume create reels-hub-data
```
```bash
printf '%s' "$META_TOKEN" | podman secret create meta_token -
```
```bash
printf '%s' "$ANTHROPIC_API_KEY" | podman secret create anthropic_key -
```
```bash
printf '%s' "$HF_TOKEN" | podman secret create hf_token -
```
```bash
security add-generic-password -s reels-hub-ghcr -a lubosba -w
```
```bash
tmutil addexclusion ~/.local/share/containers
```
The `security` command stores the read-only GitHub token (`read:packages`) in the macOS Keychain; `deploy.sh` uses it to log in to `ghcr.io` when needed. The `tmutil` exclusion keeps Time Machine from copying the VM disk on every run; the real backup is in `/media/_backups` (§23.6). Then install the login agent from the repo (`deploy/sk.reelshub.podman.plist` into `~/Library/LaunchAgents/`) and run `deploy.sh <tag>` (§23.6).

The **only** copy of the run command lives in `deploy.sh`; shown here for reference:
```bash
podman run -d --name reels-hub --restart=always --stop-timeout=60 -p 127.0.0.1:8787:8787 -v "$HOME/Movies/ReelsHub":/media -v reels-hub-data:/data --secret meta_token --secret anthropic_key --secret hf_token -e REELS_HUB_HOST_MEDIA_ROOT="$HOME/Movies/ReelsHub" -e TRANSCRIBE_BACKEND=cpu -e TZ=Europe/Bratislava --health-cmd /app/bin/healthcheck --health-interval=30s --health-retries=3 --health-start-period=120s --health-on-failure=restart ghcr.io/ai-slop-code/reels-hub:<tag>
```
- `$HOME` is expanded by the shell, so the container receives an absolute path. No `:z` on the bind mount (SELinux relabelling isn't needed on macOS).
- The health check is set in the run command, not in the Containerfile (Podman's default OCI image format ignores `HEALTHCHECK`). `/health` returns JSON with `version`, `git_sha`, `schema_version`, `media_mounted`, `media_free_gb`, `data_free_gb` and job counts; it returns 503 only if the DB can't be opened or the media marker is missing.
- The Podman VM doesn't start on its own on macOS. The launchd agent `sk.reelshub.podman.plist` (RunAtLoad) runs `podman machine start` and then `podman start reels-hub` at login.
- During a series, set the run machine to prevent automatic sleeping on power adapter when the display is off, so analysis started after copying cards finishes.
- Podman secrets live inside the VM: keep the tokens in the macOS Keychain or a password manager, and re-create the secrets after any `podman machine rm` or re-init.
- Claude Code connects with the MCP server URL `http://127.0.0.1:8787/mcp` (streamable HTTP, token header).

### 23.4 Mac-specific constraints and how we handle them
| Constraint | Impact | Handling |
|---|---|---|
| **No Apple GPU (Metal) in the container** | mlx-whisper / whisper.cpp-Metal can't run inside | `TRANSCRIBE_BACKEND=cpu` (faster-whisper int8) by default; `TRANSCRIBE_BACKEND=host` sends jobs to the optional Mac helper. Benchmark on C0031 decides the default |
| **File access through the VM is slower** | Large MP4s read more slowly | Partial hashing (head + tail + size); proxies made once and cached in `/data`; analysis runs on proxies |
| **File-change events don't reliably cross into the VM** | Watcher may miss new files | Poll the media folders every 10 s instead of relying on inotify; **Add footage** triggers an immediate scan; only fully copied files are registered (§5.1) |
| **Mac-only tools unavailable** (`qlmanage`, `sips`, Keychain) | Map rendering and secrets | SVG → PNG with resvg (or HyperFrames); secrets via Podman secrets |
| **VM resource limits** | Transcription and renders compete for CPU/RAM | Size the Podman machine from the run machine's hardware (§23.3: 8 CPUs, 12 GB on the M5 with 24 GB); the worker runs one heavy job at a time |
| **Container restarts mid-job** | Transcription or render lost | Jobs still marked `running` are re-queued on start |
| **Disk inside the VM** | `/data` grows with proxies | Proxies ≈ 1–2 % of masters; size the machine disk and show usage in the UI |
| **linux/arm64 container** | `torchcodec` (used by pyannote.audio ≥ 4 to read files) has no Linux aarch64 wheels | Decode audio with ffmpeg to 16 kHz mono and pass waveforms to pyannote and WhisperX in memory |
| **Gated model weights** | pyannote community-1 needs a Hugging Face token to download | Download once (token as Podman secret `hf_token`) into `/data/models`, run with `HF_HUB_OFFLINE=1`; CC-BY-4.0 attribution on the About page |
| **DB lives inside the VM disk** | `podman machine rm`, `reset` or re-creating the machine deletes the `reels-hub-data` volume | The copy in `/media/_backups/db/` is the real backup (§23.6); back up before any `podman machine` change |

### 23.5 Optional Mac transcription helper
- A tiny service (`reels-hub-transcribe`) installed with `pipx` or Homebrew on the Mac, running mlx-whisper on the GPU and listening on `127.0.0.1:8788`.
- The container calls `http://host.containers.internal:8788/transcribe` with a **host path**; the helper reads the file directly from `~/Movies/ReelsHub` and returns segment-level text JSON; word timing is added by the container's alignment step (§5.1a).
- Same API as the in-container backend, so switching is one environment variable.
- Only built if the benchmark shows CPU transcription is too slow for the daily cadence.

### 23.6 Image, release, deploy and backups
- **Image:** multi-stage `Containerfile`, `linux/arm64` only (§23.0). Stages:
  - `node`: `node:22-bookworm-slim`, `npm ci` with `hyperframes` pinned to an exact version in `package-lock.json`; never `npx` at runtime.
  - `runtime`: `python:3.12-slim-bookworm` pinned by digest; apt `ffmpeg chromium fonts-noto-core` with `--no-install-recommends` (OFL fonts only, §10.1); `PUPPETEER_SKIP_DOWNLOAD=1` and Chromium at `/usr/bin/chromium` passed to HyperFrames (Puppeteer's bundled Chrome may have no linux-arm64 build; check with `hyperframes doctor`); `uv sync --frozen --no-dev` in a layer before `COPY src/`, with a uv cache mount; `opencv-python-headless`; torch, if needed, from the CPU index `https://download.pytorch.org/whl/cpu`.
  - `test`: `FROM runtime` + dev dependencies + `tests/`, never shipped.
  - A `.containerignore` excludes `.git`, `.venv`, `node_modules`, `dist/` and large fixtures. Labels `org.opencontainers.image.version` and `org.opencontainers.image.revision` (git SHA) are shown by `/health`.
  - **Models aren't baked into image layers** where avoidable: Whisper, alignment and pyannote weights are downloaded once into `/data/models` by `reels-hub models pull` (revision pinned in config) and survive image updates. The exact split is the builder's choice.
- **Release (CI):** the code lives in the GitHub repo `ai-slop-code/reels-hub` (org ai-slop-code, owner identity LubosBa).
  - On every **pull request**, GitHub Actions runs the full test suite (§24.2). A green run is required to merge (§24.1).
  - On every **merge to `main`**, GitHub Actions builds the `linux/arm64` image on the native `ubuntu-24.04-arm` runner (QEMU emulation only as a fallback if that ever fails; R121) and pushes it to `ghcr.io/ai-slop-code/reels-hub`, tagged with the commit SHA and `latest`, plus `vX.Y.Z` when a release is tagged.
- **Deploy (run machine):** one small script, `deploy.sh <tag>`, kept in the repo (`deploy/`) and holding the only `podman run` command (§23.3). It:
  1. logs in to `ghcr.io` with the Keychain token if needed and pulls `ghcr.io/ai-slop-code/reels-hub:<tag>`;
  2. takes a DB backup (`pre-update-*`, see Backups);
  3. remembers the running tag, stops (`-t 60`) and removes the container, and runs the new tag;
  4. waits up to 120 s for `/health` to report the new version;
  5. on failure, restores the pre-update backup and runs the previous tag again.
  On start, the Hub backs up the DB and then runs any new numbered migration files (forward-only). During a series, deploy only per §24.5.
- **Backups:** the named volume `reels-hub-data` lives inside the Podman VM disk, so `podman machine rm`, `reset` or re-creating the machine deletes it; the copy in `/media/_backups/db/` is the real backup.
  - **DB:** `VACUUM INTO` a temp file, `PRAGMA integrity_check`, then rename to `/media/_backups/db/hub-YYYYMMDD-HHMM.sqlite`. Keep 14 daily copies plus every `pre-migrate-*` and `pre-update-*` copy. Derived files (proxies, contact sheets) aren't backed up; they can be rebuilt.
  - **Timing:** the worker runs the backup when the last one is older than 24 h (a sleeping MacBook catches up on wake), and always before an update or migration.
  - **Restore:** a documented command (`reels-hub restore <file>`: stop the container, copy the file into the volume with a throwaway container, start again). Rehearsed once before the 27 Nov dress rehearsal.
  - **Rule:** back up before any `podman machine` change.
- **The image build and a container smoke test** (start, `/health`, MCP handshake, ingest of a fixture clip) are part of the test suite (§24.2), so every branch is checked in the container before merging.

---

## 24. Development workflow

**Name:** the product is **Reels Hub**. Repository `reels-hub`, Python package `reels_hub`, CLI `reels-hub`, MCP server name `reels-hub`.

### 24.1 Branching rules (mandatory)
1. `main` is always releasable. **No direct commits to `main`.**
2. **Every change or feature gets its own branch** from the latest `main`:
   - `feature/<short-name>` for features (e.g. `feature/reel-prompt-generator`)
   - `fix/<short-name>` for bug fixes
   - `chore/<short-name>` for tooling, docs, dependencies
3. Work, commit and test on that branch only. Keep each branch to one feature.
4. **Merge back to `main` only through a pull request, when the feature is finished and all tests pass** (full suite, not just the new tests). The GitHub Actions run on the pull request is the merge gate. The repo has no GitHub-enforced branch protection (GitHub Free, R119), so the gate is the chained command `gh pr checks --watch --fail-fast && gh pr merge --squash --delete-branch` (the merge runs only if the checks pass; never `gh pr merge` alone, never `--admin`), and a committed `.githooks/pre-push` hook (`git config core.hooksPath .githooks`) refuses direct pushes to `main`. Rebase on or merge the latest `main` first so CI tests the combined code. If two branches added a migration with the same number, renumber yours after rebasing.
5. Delete the branch after merging. Tag releases on `main` (`v0.1.0`, …); CI pushes the image for every merge and a version tag for every release (§23.6).
6. If the suite fails on `main` after a merge, fix it on a `fix/` branch immediately; nothing else merges until `main` is green.

### 24.2 Tests
| Layer | What | Tooling |
|---|---|---|
| Unit | Parsers, sync math (known-offset fixture), fact conflicts, token checks, mix calculations, path derivation, hashtag count | pytest |
| Database | Numbered forward-only migrations apply to an empty DB and to the previous release's DB; backup is written before migrating; constraints and FTS queries | pytest + temp SQLite |
| Ingest | Small fixture clips (2–5 s at 540p of Sony + DJI, plus one 2 s 4K HEVC clip) through probe → transcript → sync → moments, run **inside the built image** so its own ffmpeg, OpenCV and Chromium are tested, not the host's | pytest in the `test` image stage; fixture clips generated by a script (ffmpeg lavfi) at test time, no binaries committed; real snippets only local and git-ignored (R120) |
| MCP contract | Every tool's schema; no tool can approve; `export_allowed` false before approval; excluded ranges never returned | MCP client in tests |
| Prompt generator | Snapshot ("golden") tests of generated reel prompts for fixture projects | pytest snapshot |
| Editor's notes | Template is created; the graphics and clips tables are parsed into `asset_usage` | pytest |
| Critique (phase 10) | Rubric runs on fixture reels with known issues (e.g. half-out first frame) | pytest |
| Graphics | Render templates and compare against reference frames generated at test time, not committed (R120) | HyperFrames render + image diff |
| UI | Key flows: create project, new reel, add footage, review, approve, project overview, graphics overview | Playwright |
| Container | Image builds; ingest and graphics tests inside the `test` image; smoke test of the runtime image (fake transcriber): container starts, `/health`, MCP handshake, fixture clip registered with the right host path, container can write to the media share; backup → restore round trip optional | podman build + run in the test script |
| Lint and types | Style and type checks | ruff, mypy |

- One command runs everything: `reels-hub test` (or `make test`). **GitHub Actions runs it on every pull request**; a failure blocks the merge through the chained merge command (§24.1); the same command runs locally on the build machine.
- **Container tests are isolated from the real Hub:** unique container name, random host port (`-p 127.0.0.1::8787`), a throwaway volume and a temp media folder under `$HOME` (only `$HOME` is shared into the Podman VM by default), all removed by a `trap`. They never touch the `reels-hub` container or the `reels-hub-data` volume.
- Tests never touch real footage or real accounts; external APIs are mocked.
- Tests use a **fake transcriber and a fake LLM** by default. One optional, marked test per real engine runs it on a 5 s fixture.

### 24.3 Definition of done (per feature)
- Feature works end to end in the UI and through MCP where relevant.
- Tests added for the new behavior; full suite green.
- Docs updated: this spec (if behavior changed), `CHANGELOG.md`, and the agent playbook if agents use it.
- Merged to `main`, branch deleted.

### 24.4 Instructions for AI agents working on the repo
The repo's `CLAUDE.md` should contain:
```markdown
# Reels Hub
- Keep it simple: one user, one Mac. Build the simplest thing that supports the main flow (spec §2, §19.0).
- Never commit to main. Create a branch per change: feature/…, fix/… or chore/….
- Run `reels-hub test` before opening a pull request. Merge to main only through a pull request with a green GitHub Actions run, when the feature is complete.
- Rebase on main and re-run tests before merging; delete the branch afterwards.
- Keep one feature per branch. Update CHANGELOG.md and the spec when behavior changes.
```

### 24.5 Updates during a running series
- During a series, update the running Hub only when **2 approved reels are in the buffer** (§2 principle 10).
- Update with `deploy.sh <tag>` (§23.6): it backs up the DB first and rolls back to the previous tag (restoring that backup) if `/health` doesn't come up.

---

## 25. Roadmap

Every phase ships in a **light version** first: the smallest thing that serves the main flow (§19.0). Robustness comes later, when a real problem shows up (§2 principle 11).

| Phase | Scope (light version) | Outcome | Done when |
|---|---|---|---|
| **0 · Foundations** | Podman image + volumes, SQLite schema with numbered migrations, `job` table and worker loop, polling watcher (fully copied files only), ffprobe with clip flags, proxies, media-root path mapping; GitHub Actions (tests on pull requests, arm64 image to GHCR on merge), `deploy.sh`, DB backup and restore; first deploy to the run machine | `podman run` gives a working Hub on the run machine; footage registered and Edits-ready | A Giro_00-sized drop is registered with proxies in ≤ 30 min (measured on the run machine, §23.0), and a host path imports in Edits without copying |
| **1 · Transcripts and moments** | ASR benchmark (§5.1a), local Whisper (Slovak fine-tune candidate) with per-reel hotwords and forced alignment, FTS search with Slovak prefix fallback, moment tagging with the tag vocabulary, do-not-use ranges with `excluded_by`, manual clock offset per device per shoot, clipping flag; speakers and audio auto-sync if time allows | Finding the hook takes minutes | Searching "lizatko" returns C0031 at 490.1 s in under 1 s |
| **2 · MCP v1** | Streamable HTTP server; read tools for moments, transcripts, design tokens, playbook, glossary; `host_paths`, `get_job` | Agents build drafts with full context | A fresh agent finds the Giro_00 hook and an importable Mac path without browsing the file system |
| **3 · Facts and glossary** | Fact store with source tiers and attributed facts, conflicts, **Re-checked** button, stage table, glossary with case forms and the seed glossaries, context-bound caption correction memory, `fix_captions` | Fewer factual and caption errors | Stage 1 "enters Slovenia" shows as `verified` and "where / how long" as `conflicting`; `fix_captions` turns "lyžičko" into "lízatko" (glossary) and "po 30" into "po tridsiatke" (style rule) |
| **4 · Reviews and approvals** | Versions, feedback items, approval in the Hub UI, `export_allowed`, simple diff | Clean feedback rounds, exports only after approval | `export_allowed` is false before approval and again after a newer version is created |
| **5 · Analytics v1** | Instagram importer with token refresh (metric names per API v27.0, incl. `reels_skip_rate`), 24 h snapshot (API or manual form), later window pulls, manual retention and follows import, reel card | We see what works | Every posted reel has a 24 h snapshot |
| **6 · Learning loop** (ongoing) | Findings list, weekly review, recommendations into the prompt | Each Reel improves the next | The next reel's prompt shows the latest findings and the previous reel's metrics |
| **7 · Graphics and motion** | Static map templates around `mkmap.py`, asset registry, **graphics overview**; one HyperFrames `card_map_cities` test (MP4 + alpha MOV in a copy of Giro_00) | On-brand graphics, and we see what we've used | The graphics overview lists every Giro_00 graphic with the reel and timeline position that used it |
| **8 · Music** | Music brief, Edits catalog search through the agent, metadata, shortlist of 3, taste notes, license records, mix check (levels only) | Better music in minutes, no stock "garbage" | A shortlist of 3 with license records in ≤ 5 min; no audio file written |
| **9 · Projects, reel prompt and notes** | Project from YAML, reels with statuses, New reel, Add footage with automatic analysis and prompt build, intelligence gathering, prompt template + golden tests, `editors_notes.md`, project overview | From added footage to a ready prompt without manual steps; every reel documented and visible in the overview | Prompt ready < 2 min after the footage's analysis finishes, with no producer clicks; the Giro_00 golden test passes; a fresh agent's draft comes with a complete `editors_notes.md` |
| **10 · AI critique** (after December) | Critique of a render + `editors_notes.md`, only when the producer triggers it; calibration against metrics | A demanding second opinion when wanted | The Giro_00 fixture's half-out first frame is flagged |

### 25.1 Plan for December
- **By 1 December, all phases except phase 10 work**, each in its light version. Build order: 0 → 1 → 2 → 3 → 9 → 4 → 5 → 7 → 8 → 6. Phase 3 comes before 9 because the prompt depends on the fact store.
- **Phase 10 (critique) comes after December** and runs only on demand (§16.5).
- **Metrics from the first post:** the 24 h snapshot is captured from Day 1, via the API or the manual form (§19.4).
- **Experiment:** the closing-card experiment (§13.2) is set on each stage reel from Stage 1.
- **Restore rehearsal:** restore the DB from `/media/_backups/db/` once on the run machine before 27 Nov (§23.6).
- **Dress rehearsal (27 Nov):** create the `giro2027-advent` project, click **New reel** for the Stage 1 reel (Day 2), add the Stage 1 footage, let the Hub analyze it and build the prompt, hand the prompt to a fresh Claude session and get a reviewable draft with a complete `editors_notes.md`. Record producer hands-on time and the agent's clarifying questions.
- **Go/no-go (28 Nov):** go if the "done when" checks of phases 0–4 and 9 pass. If no-go, December runs the Giro_00 manual workflow (Edits + Claude + hand-written notes, including `editors_notes.md`), and the Hub is used only for what passed. No reel waits for a Hub feature (§2 principle 10).

Every phase is built as one or more `feature/…` branches and merged to `main` only when complete and the full suite passes (§24).

---

## 26. Success metrics for the Hub itself

| Metric | Today (Giro_00) | Target | How it's measured |
|---|---|---|---|
| Reels posted on schedule | – | 24/24 | Planned posting date vs. `publication.posted_at` |
| Posts delayed by a Hub problem | – | 0 | `delayed_by_hub` flag on the reel |
| Producer hands-on time per reel (footage → approved) | ~4–6 h (to confirm) | ≤ 60 min | Minutes entered by the producer when approving |
| Factual or caption corrections after posting | – | 0 | Feedback items logged after posting (`after_post`) |

---

## 27. Risks and open questions

| Risk / question | Mitigation / decision |
|---|---|
| **19 days to 1 December** (2026-11-12 → 2026-12-01) for phases 0–9 | Light versions only (§25); dress rehearsal 27 Nov, go/no-go 28 Nov. **Fallback:** the Giro_00 manual workflow (Edits + Claude + hand-written notes) plus whatever passed. No reel waits for a Hub feature |
| Instagram API access needs a Professional account + Meta developer app, and metric names change by version | Confirm account type; build the importer with version mapping (API v27.0 names, §12.1); follows for Reels aren't in the API and are entered manually; keep manual CSV/screenshot import and the manual 24 h form as fallback |
| 24 h metrics can't be backfilled (lifetime totals, up to 48 h lag) | Capture the 24 h snapshot at 24 h from the first post, by API or manual form (§19.4) |
| Retention curves may not be available via the API | Manual import from in-app insights; consider screenshot OCR |
| Small sample sizes → misleading "insights" | Uncertainty ranges, minimum N, within-project comparison, experiments |
| Edits exports happen outside the Hub, so the Hub can't block them | Agent rule "never export before approval" (CLAUDE.md, §6.4, §17.3) plus `export_allowed`; the producer posts manually |
| Edits sandbox and API changes | Playbook with versions; media library kept in `~/Movies/ReelsHub` |
| No Mac GPU inside Podman | CPU faster-whisper by default; optional Mac helper with mlx-whisper; benchmark decides |
| Slower file access and missed file events through the Podman VM | Partial hashing, cached proxies, polling watcher |
| Licensed music can't be analyzed, and previews can't be downloaded | Metadata only for tier 1; store human audition notes; producer has final say |
| Temptation to rip songs (yt-dlp etc.) | Explicitly out of scope for commercial music (terms of service + copyright); only own or licensed material |
| Commercial music restricted by account type, region or sponsorship | License record per track; commercial flags per reel; legal checklist in each `editors_notes.md` |
| Edits may not import alpha video | Test first; fall back to full-frame cards or ffmpeg compositing (baked asset) |
| HyperFrames alpha output confirmed only via package mirrors | Verify with a test render before building templates |
| Slovak transcription quality on slang and names | Slovak fine-tune candidate, per-reel hotwords, glossary + context-bound correction memory; pick the model that measures best on our own clips (§5.1a) |
| Scope creep | Simple over robust (§2 principle 11); light versions first; critique after December |
| Single user or shared with Katarina? | **Decided:** Ľuboš is the only Hub user. No auth, localhost only. Katarina is the on-camera host; she doesn't use the Hub and gets no generated documents (§3) |
| Where masters live long-term? | **Decided:** in `~/Movies/ReelsHub/<project>` until the last reel's 28 d window closes, then on an external SSD; `availability` and `volume_id` per clip; re-attach by hash; no NAS (§5.1). **Disk space (R66):** Giro_00 alone was ≈ 37 GB of masters for one reel, so 24 similar reels ≈ 900 GB, close to the run machine's 1 TB. `/health` reports `media_free_gb`; **Today** warns below 100 GB. Masters of reels already `posted` may move to the external SSD early (their clips go `offline`, proxies and transcripts stay). Time Machine must be large enough for `~/Movies/ReelsHub`, or SD cards are kept until the reel is posted |
| Posting manual or scheduled through Meta? | **Decided:** posting stays manual (Edits / Instagram app, in-app scheduling allowed). The Content Publishing API can't attach licensed library music. The Hub records the publication after posting; no `publish_*` tools |
| Does the Edits licensed library (tier-1 music) cover unpaid co-authored (collab) posts? | **Open** (R106): confirm with the Instagram licensed-music terms before the first collab. Until confirmed, an unpaid collab isn't a commercial flag, but check before posting one with "Dolce Vita" |
| Edits frame rate: which project rates (24/25/30) Edits offers and how it conforms our 25p footage | **Open** (R70): check once on the run machine and record it in the playbook (§14). Cameras stay at 25p |
| GitHub-hosted arm64 runners for a private repo | **Decided** (R59, R121): the owner confirmed `ubuntu-24.04-arm` works for the repo; CI and the release build run there, QEMU emulation only as a fallback if it ever fails |

---

## 28. Changelog

### v0.6 (2026-11-12)
Applied from the round-2 decision log (R58–R118, packets 06, 07, 09, 11, 14, 15) in [`docs/decisions.md`](../decisions.md):
- **Deployment (§23, §21, §22):** new §23.0 build machine vs. run machine (both Apple M5; run machine 24 GB, 1 TB; `linux/arm64`, Podman 6 with applehv) (R58). Release path is CI + registry: GitHub repo `reels-hub`, GitHub Actions runs the full suite on every pull request and builds the arm64 image on every merge to `main`, pushed to `ghcr.io/ai-slop-code/reels-hub` (SHA, `latest`, version tags); the run machine pulls with a read-only Keychain token and runs `deploy.sh` (pull, backup, replace, wait for `/health`, roll back on failure) (R59, changed by owner). Machine sized 8 CPUs / 12 GB / 100 GB with applehv; no `:z`; `--restart=always`, stop timeout, TZ, health check in the run command; launchd login agent; no auto-sleep during a series; re-create secrets after a machine re-init (R60). DB backups survive the VM disk: daily catch-up `VACUUM INTO` to `/media/_backups/db/`, keep 14, before every update or migration, Time Machine excludes the VM disk, restore rehearsed once before 27 Nov (R61). Media marker `/media/.reels-hub-root` (R62). Image recipe with Debian Chromium, pinned HyperFrames, uv layers, CPU torch, models in `/data/models` rather than image layers (R63). Giro_00 footage brought in by hard links (R67). arm64 `torchcodec` and gated pyannote rows; `hf_token` secret (R90).
- **Dev workflow (§24):** CI on pull requests is the D10 merge gate; container tests run inside the built image and are isolated from the real Hub (R59, R64).
- **Ingest (§5.1, §5.1b, §5.2):** watcher registers only fully copied files, immediate scan on Add footage, ignore patterns, xxh3 hash (R62). Probe flags frame-rate differences against the reel's other clips, VFR and HDR/Log; house standard 25p on both cameras (R69, R70). Proxy encoding with 0.5 s keyframes, source fps and timecode, all audio channels; no edit proxies (R65). Clipping flag `tech:clipped`; DJI WAV attached as alternate audio source (R72). Grade = the camera's preset, no computed grades (R78). Sync by audio cross-correlation with a one-frame drift flag, if time allows (R71).
- **Transcription (§5.1a, §21):** light benchmark (~5 min reference, WER, names, speed) (R81); `kinit/whisper-large-v3-turbo-sk` vs. base large-v3 and a decoding config (R82); per-reel `hotwords` capped at 150 tokens (R83); forced Slovak, `check_language` flag (R84); speaker labelling with one print per person and `unknown` for short unsure turns (R86); `transcript` runs and time-anchored `transcript_edit` (R87); forced alignment always in the container, helper returns text only (R89).
- **Moments and search (§5.3, §5.4):** prefixed tag vocabulary incl. `tech:` and `time:dated`; cut points snap to silence (R73); Slovak prefix fallback for inflected forms (R88).
- **Facts (§7):** silence is not a conflict; Stage 1 split into "enters Slovenia" (verified), Lipica (attributed) and extent (conflicting) (R110, R117); source tiers with `lead` and `attributed` use (R111); **Re-checked** button, automated checks best-effort (R113); optional `climbs` and `places` with country in the stage table (R115); seed fact for the Slovenian hosting agreement due 3 Dec 2026 and Stage 1/2 open items (R118).
- **Glossary and captions (§8, new §8.1):** context-bound correction memory with an `always` flag; "po 30" is a style rule (R92); glossary entries with case forms, `captions: as_said`, `heard_as`, checked pronunciation, valid YAML (R93); clean-verbatim captions and translation only for others' longer speech (R94); place-name policy (R95); seed glossaries `sk-italy` and `sk-cycling` plus Katarina's dialect words (R100); new §8.1 Instagram caption rules with **max 5 hashtags**, drafted in the edit and recorded in `editors_notes.md` (R101, R116).
- **Reel prompt (§6.4):** preview-tense rule (R114); attributed facts and "pronunciation unchecked" lines (R111, R93); caption step and deliverable (R101); hook and runtime acceptance checks (R104); experiment line (R103).
- **Reels and projects (§6.1, §6.2):** project `posting_time` (R105); slot type and target runtime by slot (R104); "brand collab partners"; unpaid co-authored posts are `collab: true`, not a commercial flag (R106).
- **Versions and notes (§11):** minimum cut-list fields (R75); `editors_notes.md` gets "Instagram caption" and "Posting checklist" sections (R101, R105) and a delivery-loudness line (R77).
- **Analytics and experiments (§12, §13):** metric names per API v27.0, `reels_skip_rate`, `reposts`, `facebook_views`, follows entered manually at 7 d, rewatch over reach (R102); feature keys from existing data, hashtag example fixed (R108); one pre-registered closing-card experiment `ending_type` (tease vs. statement), resolving R32 (R103); Trial Reels never for series episodes (R109).
- **Music (§15.3, §15.6):** delivery loudness −14 LUFS ±1.5, ≤ −1 dBTP; music 15–18 LU under dialogue, 0.20 only a starting value (R77); collab clarification (R106).
- **Playbook (§14):** Edits for Mac capabilities and 2K export (R79); Giro_00 was cut from 25p footage; Edits project frame rates and 25p conform to check once on the run machine (R70).
- **Data model (§18):** `transcript`, `transcript_edit`, clip flags and alternate audio, fact status `attributed`, `stage`, `glossary_term`, `correction`, project and reel fields (R87, R69, R72, R111, R115, R93, R92, R104, R105, R106).
- **UI (§20):** Today shows clip flags and a low-disk warning; Facts gets the Re-checked button (R69, R66, R113).
- **Roadmap (§25):** phase 0 includes CI, `deploy.sh`, backups and the first deploy, measured on the run machine; phase 3 "done when" updated; restore rehearsal before 27 Nov (R58, R59, R61, R65, R110).
- **Risks (§27):** masters disk space with early move of posted reels' masters and a 100 GB warning (R66, option b); open questions on collab music coverage (R106), Edits frame rates (R70) and arm64 runners for private repos (R59).
- **DESIGN_LANGUAGE 1.2:** cameras at 25p, 50p only for slow motion (R70); punch-in headroom tokens (R74); delivery loudness (R77); clean-verbatim captions (R94); exonym policy for map labels (R95); Slovak number formatting (R96); line-break, question and quote rules, applied by the agent without automatic checks (R97); foreign terms and inflection (R98); stage-episode structure and runtime by slot (R104); new §13 Instagram post caption with max 5 hashtags (R101, R116).
- **R32** (series experiment, deferred in v0.5) is resolved by R103.

**Deferred:** R68 (Mac helper packaging, only if needed), R76 (cut lint), R80 (critique rubric additions, phase 10), R85 (one primary audio source per take), R91 (laughter detection), R99 (Hunspell dictionary), R107 (weighted reel score), R112 (fact volatility classes). **Notes:** R116 is applied as a lesson only (the max-5-hashtags rule); Giro_00 is already published and its files are unchanged. R117 and R118 are applied as seed facts and open items for the Stage 1 and Stage 2 reels, with no Giro_00 action.

#### v0.6 bootstrap decisions (2026-11-12)
Owner's answers before the build (R119–R122 in [`docs/decisions.md`](../decisions.md)); version stays 0.6:
- **Merge gate without branch protection (§24.1):** GitHub Free, private repo, no enforced protection; merges only via `gh pr checks --watch --fail-fast && gh pr merge --squash --delete-branch`; a committed pre-push hook refuses pushes to `main` (R119).
- **No pictures in the repo (§24.2):** test clips and images generated by scripts at test time, no binaries committed, no Git LFS; real snippets only local and git-ignored; Giro_00 reference graphics stay out of the repo (R120).
- **Native arm64 CI (§23.6, §27):** `ubuntu-24.04-arm` for CI and the release build, QEMU only as a fallback (R121).
- **Dependencies (§21):** the kit's pre-approved dependency list is approved (R122).
- **Repository (§21, §23.6):** the code repo is `ai-slop-code/reels-hub` (private, GitHub Free org), images at `ghcr.io/ai-slop-code/reels-hub` (R123).

### v0.5 (2026-11-12)
Applied from the review decision log in [`docs/decisions.md`](../decisions.md):
- **Principles:** "Never block a post" (R25) and "Simple over robust" (R56) added to §2; approval wording updated (R1, R2, R28).
- **Users:** Ľuboš is the only user; Katarina is the on-camera host, doesn't use the Hub and gets no generated documents (R7); language per output (R8) in §3 and §20.
- **Architecture and stack:** Python 3.12 + FastAPI + Jinja2/HTMX, MCP on streamable HTTP only, HyperFrames as a Node CLI subprocess (R12); simple SQLite `job` table instead of APScheduler (R13); paths relative to one absolute host media root (R14); model ID pinned in config (R33); numbered forward-only migrations with automatic backup (R18) in §4, §21, §23.
- **Data model (§18):** integer milliseconds, relative paths, `publication` table, `excluded_by`, `origin` (R15, R3, R48); `availability` / `volume_id` (R27); `reel_clip` links footage to a reel (R57); no `pickup` table (R5); `status_change` and success-metric fields (R30); short `music_license` (R42); `editors_notes` and `asset_usage` (R53, R54); `job` (R13); comment table removed (R49).
- **Footage (§5):** person-set exclusions are absolute, agents only propose (R3); `origin` for clips and assets (R48); masters location (R27); semantic and visual search moved to later (R35).
- **Per-reel flow (§19.0, §6, §19.1, §19.2):** the owner's flow is the backbone: create reel → shoot → add footage → automatic analysis → prompt (`prompt_ready`) → the owner's Claude session edits with the Hub and Edits MCPs and writes `editors_notes.md` → approval → post → metrics. New status pipeline `created → footage_added → analyzing → prompt_ready → editing → in_review → approved → exported → posted → analyzed`; §6.5 project overview of what was built and when (R57). No shoot planning: no shoot sheet, Shoot screen, props or shoot grouping, no `to_shoot` / `planned` / `shot` / `scheduled` statuses (R6 rejected).
- **Reels (§6):** pickups only as "Suggested pickups (not recorded)" in `editors_notes.md`, no pickup table or tool (R5); commercial flags as checkboxes (R43); simple ranking with FTS5 + filters + recency (R35); revised prompt template with no-frankenbite and no-synthesis rules and a final `editors_notes.md` step, no token budgets (R34, R4, R10, R51).
- **Graphics (§10):** no tracing of organizer maps (R47); font licensing (R46); `ai_generated` flag (R51); graphics overview (R54).
- **Reviews (§11):** approval of a specific version in the Hub, no MCP approval, no hooks or hashes (R1, R2); no `publish_*` (R28); no "host OK" check (R7); new §11.4 `editors_notes.md` with template, "Suggested pickups (not recorded)" and legal checklist (R53, R5, R52, R42–R48, R51).
- **Analytics (§12, §19.4):** 24 h snapshot from the first post by API or manual form, no 1 h window, no backfill (R29); official API with Instagram Login, Development mode, token refresh alert; Instagram comments not imported (R49).
- **Music (§15):** no iTunes/Deezer preview download or analysis, `analyze_track` replaces `analyze_preview` (R41); short license record and checklist instead of a gate (R42, R52); tier-1 audio never captured or stored (R44).
- **Critique (§16):** phase 10, after December, only on demand, input = render + `editors_notes.md`; automatic triggers removed from §16, §19 and the prompt (R55).
- **MCP (§17):** existing `verb_noun` names kept, one tool list, default page size 20; added `add_footage`, `list_reels`, `get_editors_notes`, `update_editors_notes`, `link_publication`, `list_graphics_usage`, `get_job`; added resource `hub://reel/{id}/prompt`; removed `publish_*` (R17, R28, R49, R57).
- **Safety (§22):** voice prints only for speaker labels, no synthetic host (R10); licensed audio (R44); third-party media (R48).
- **Dev workflow (§24):** fake transcriber and fake LLM in tests (R19); new §24.5 updates during a series (R26).
- **Roadmap (§25):** all phases except 10 in a light version by 1 Dec, "done when" per phase, dress rehearsal 27 Nov, go/no-go 28 Nov, Giro_00 manual fallback (R22, R23, R24).
- **Metrics (§26):** reduced to on-schedule posts, posts delayed by the Hub, producer hands-on time and corrections after posting (R30).
- **Risks (§27):** open questions closed (R7, R27, R28); 19-day risk and fallback recorded (R23).

**Deferred:** R9, R16, R20, R21, R31, R32, R36, R37, R38, R39, R45, R50. **Rejected:** R6 (no pre-shoot planning in the Hub), R11 (moot: comments aren't imported), R40.
