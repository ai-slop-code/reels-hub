# Review packet 05: product owner

**Priority:** must review before implementation
**Time needed:** ~1.5 h
**Decisions already made:** D1–D10 (see [README](README.md#decisions-already-made-please-dont-reopen)). Cost and timeline are not constraints; this review is about **scope, order and what "done" means**.

## Why you
With AI doing the building, the risk shifts from "can we afford it" to "are we building the right things in the right order, and will we actually use them".

## Read
- [§1 Why](../spec/REELS_HUB_SPEC.md#1-why-lessons-from-giro_00_intro), [§2 Principles](../spec/REELS_HUB_SPEC.md#2-principles), [§3 Users](../spec/REELS_HUB_SPEC.md#3-users-and-roles)
- [§19.0 Main flow](../spec/REELS_HUB_SPEC.md#19-key-workflows)
- [§25 Roadmap](../spec/REELS_HUB_SPEC.md#25-roadmap), [§26 Success metrics](../spec/REELS_HUB_SPEC.md#26-success-metrics-for-the-hub-itself), [§27 Risks and open questions](../spec/REELS_HUB_SPEC.md#27-risks-and-open-questions)

## Questions
1. **December must-haves:** which features must work on Day 1 of the Giro project (1 Dec)? Which can arrive mid-series?
2. **Priority order:** rank the modules by value to you. Is the roadmap order right (foundations → transcripts → MCP → facts → reviews → analytics → learning → graphics → music → prompt → critique)?
3. **Acceptance per phase:** for each phase, what would make you say "this is done"? (E.g. "New reel produces a prompt that Claude can follow without extra questions.")
4. **Success metrics:** are the targets in §26 the right ones? Add or remove metrics.
5. **Open questions in §27:** single user or shared with Katarina; where masters live long term; manual vs. scheduled posting. Can you decide these now?
6. **Future projects:** after Giro 2027, what comes next (Tour, Vuelta, other topics)? What should the Hub reuse between projects?
7. **Release rhythm:** how often do you want new features merged and deployed during the December series without disrupting daily production?

## Expected output
- Ranked feature list with "December / mid-series / later" labels.
- Acceptance criteria per phase.
- Decisions on the open questions in §27.

## Your input

### Summary
The spec gets the vision and module list right, and §19.0 is a clear main flow. As a delivery plan for **1 December 2026 (19 days from today, 12 Nov)** it isn't ready yet. §25 lists about 6 weeks of phase estimates before December. It has no acceptance criteria and no "minimum Day-1 kit". It also never says what happens if the Hub breaks mid-series. The changes that matter most:
1. Cut a **Day-1 kit** out of phases 0–3 + 9 and label every other feature *mid-series* or *later*.
2. Make the Hub **never block a post**: keep a buffer of finished reels and a manual fallback.
3. Add **testable acceptance criteria** for each phase and a **go/no-go dress rehearsal on 27 Nov**.
4. Set a **release rhythm** for 1–24 Dec.
5. Settle the three open questions in §27.

I also found one factual gap that changes the roadmap. Instagram media insights are lifetime-only, so the 1 h / 24 h / 72 h snapshots **can't be backfilled** later, despite what §25 says.

### Answers

#### Q1. December must-haves
Context: Giro_00 (the Day 1 intro, 1 Dec) is already edited outside the Hub. So the Hub's real first job is the **Stage 1 reel (Day 2, 2 Dec)**, and in practice whatever reel is produced first in the last week of November. The Day-1 kit below is what must work for that reel. Everything else is labelled.

**December (must work by 27 Nov, the dress rehearsal date):**
| # | Feature | Phase | Why it can't wait |
|---|---|---|---|
| 1 | Podman container, `~/Movies/ReelsHub` library, host/container path mapping, nightly backup | 0 | Without it, the Giro_00 sandbox problem comes back on day one |
| 2 | Ingest: probe, proxy, contact sheet, **transcript with word timestamps + glossary hint** | 1 | Transcribing was the biggest time sink in §1 |
| 3 | **Manual clock offset per device per shoot** (enter "DJI = Sony − 24.85 s" once), applied to all clips of that shoot | 1 (lite) | Every shoot is Sony + DJI. A manual offset takes 1 min. Auto-sync can come later |
| 4 | FTS search over transcripts (diacritic-insensitive), moment tagging + rating + do-not-use ranges | 1 | Finding the hook is the core value |
| 5 | MCP read tools: `search_moments`, `get_transcript`, `get_take`, `frame_sheet`, `host_paths`, `get_style_tokens`, `get_playbook`, glossary resource | 2 | The agent can't use the Hub without them |
| 6 | Stage reference table (21 stages, source + checked date) + fact records with status and conflicts (manual entry is fine) | 3 (lite) | Every reel from Day 2 to Day 22 is a stage reel |
| 7 | Glossary + correction memory + `fix_captions` | 3 | Caption fixes are daily, repetitive work |
| 8 | Edits playbook as a resource, plus `add_playbook_item` | 2 | Cheap to build, and it prevents repeating Giro_00 mistakes |
| 9 | Project defined in a **YAML file** (no wizard), reels with slot, status and closing promise | 9 (lite) | Only one project in December |
| 10 | **New reel → prompt** (template, ≤ 2,500 words, previous reel's promise inlined), saved as `PROMPT.md` + prompt history | 9 | This is the feature that ties everything together |
| 11 | `create_version` + `log_feedback` / `resolve_feedback` (no diff view yet) | 4 (lite) | Feedback rounds were the third biggest pain in §1 |
| 12 | Static map templates wrapping `mkmap.py` (`map_overview`, `map_closeup`), registered as assets | 7 (lite) | Every stage reel needs a map, and the tool already exists |
| 13 | **24 h metric snapshot** for each posted reel (minimal API pull or a 2-minute manual form) | 5 (lite) | It can't be backfilled (see P9) |
| 14 | **Shoot sheet** for Katarina (pickups, shot list, props per shoot day) as Markdown | 6.2 | The host's only need in §3 |

**Mid-series (merged 2–20 Dec under the release rhythm in Q7):**
- Approval gate with `export_allowed`. Low urgency because exports and posting are manual in Edits.
- Version diff view.
- AI critique, **fast mode only**.
- Analytics v1: full window pulls, manual retention import, reel card vs. median.
- Auto multicam sync.
- Speaker labels.
- `lint_script`.
- Continuity check across the whole project.
- Calendar view (a sorted list is enough until then).
- `card_map_cities` HyperFrames test.

**Later (after 24 Dec):**
- Semantic and visual search, frame embeddings, color match, subject tracking for `focus_x`, voice prints.
- Full critique and calibration.
- Learning-loop dashboards, feature impact, retention heatmap.
- Music pipeline: preview analysis, taste memory. In December the signature track "Dolce Vita" and the mix rules are just data inside the prompt.
- Motion template library.
- Comment intelligence.
- Create-project wizard.
- Bilingual UI labels.
- `stage_route` with official traces.

#### Q2. Priority order
Ranked by value to the producer in December, with the label:

| Rank | Module | Label |
|---|---|---|
| 1 | Foundations: library, ingest, path mapping (§5.1, §23) | December |
| 2 | Transcripts + FTS + moments (§5.1a, §5.3, §5.4 text only) | December |
| 3 | Reel prompt + project/reel records (§6.3–6.4) | December |
| 4 | MCP read interface (§17, read subset) | December |
| 5 | Facts: stage table + conflicts (§7) | December |
| 6 | Glossary + correction memory (§8) | December |
| 7 | Playbook (§14) | December |
| 8 | Feedback items + versions (§11.1–11.2) | December |
| 9 | Static map graphics (§10) | December |
| 10 | Analytics snapshot capture (§12.1, 24 h only) | December |
| 11 | AI critique, fast (§16) | Mid-series |
| 12 | Analytics v1 dashboards (§12.4 items 1–2) | Mid-series |
| 13 | Approval gate (§11.3) | Mid-series |
| 14 | Auto-sync, speaker labels (§5.2, §5.1) | Mid-series |
| 15 | Design lint (§9) | Later |
| 16 | Learning loop + experiments (§13) | Later (but **decide the one series experiment before 1 Dec**, see P13) |
| 17 | Motion graphics (§10.1) | Later |
| 18 | Music pipeline (§15.2–15.5) | Later |
| 19 | Semantic / visual search (§5.4) | Later |

The roadmap order is mostly right, with three fixes:
- **Phase 3 (facts) must come before phase 9 (prompt).** The prompt's "Facts you may state" section needs the fact store. Right now §25 numbers it 9 but places it "right after phase 2", which is confusing. Renumber by delivery order (P1).
- **Pull a small part of phase 4 (feedback items) into December.** Leave the gate for mid-series.
- **Pull a 24 h snapshot of phase 5 into December**, because of the backfill gap.

Music (phase 8, "can start early") should **not** start early. December already has a signature track and fixed mix rules, so the music module adds little value until a second project needs new tracks.

#### Q3. Acceptance per phase
Each criterion is testable, and most can be automated in the suite. The full YAML is in P3. In short:

| Phase | "Done" means |
|---|---|
| 0 Foundations | Clean Mac → `podman run` → `/health` green in ≤ 10 min. A Giro_00-sized drop (13 min Sony + 2 × 13 min DJI) is registered with proxies and contact sheets in ≤ 30 min. A path from `host_paths` imports into Edits with no copy. Container restart loses nothing. One backup restore has been tested. |
| 1 Transcripts and moments | On C0031, WER is no worse than the benchmark winner and all 6 glossary names come out right. 40 min of audio is transcribed in ≤ 60 min. Searching "lizatko" returns 490.1 s in < 1 s. The DJI offset is within ±1 frame (±0.042 s) of 24.85 s. Ľuboš finds the Giro_00 hook cold in ≤ 2 min. |
| 2 MCP v1 | A fresh Claude session with only the Hub MCP + Edits MCP gets the hook moment and an importable Mac path without browsing the file system. Every tool has a contract test. Every call shows up in `agent_log`. |
| 3 Facts and glossary | 21 stages imported with URL + checked date. Stage 1 Slovenia shows as `conflicting`. `fix_captions` turns "lyžičko"→"lízatko" and "po 30"→"po tridsiatke". A fact past its `review_by` date shows up on Today. |
| 9 Prompt | New reel → prompt in < 2 min, ≤ 2,500 words. Golden test for Giro_00 passes. **Dress rehearsal:** a fresh agent builds the Stage 1 draft from the prompt with ≤ 1 clarifying question and no claim that isn't in the fact store. |
| 4 Reviews | Pasting Giro_00 round 1 (4 bullets) creates 4 items. `export_allowed` is false until approval, and any edit after approval invalidates it. The v3→v4 diff shows "card 5.5 s → 3.5 s". |
| 5 Analytics | 24 h snapshot stored for ≥ 23 of 24 reels, with `api_version` recorded. A retention screenshot can be imported in ≤ 3 min. The reel card shows each metric vs. median. |
| 6 Learning | No finding is promoted without N ≥ 5 per variant and an uncertainty range that excludes 0. The series experiment is logged on all 24 reels. |
| 7 Graphics | Static: every stage reel's map comes from a template, and none is drawn by hand. Motion: `card_map_cities` renders the same hash twice. The result of the Edits alpha import is in the playbook. Ľuboš rates it better than the static card before the template library starts. |
| 8 Music | Shortlist of 3 in ≤ 5 min. At least 1 of the 3 is rated keep for ≥ 70 % of briefs. A test asserts that no full-track file is ever written. |
| 10 Critique | On the Giro_00 fixture, the half-out first frame is flagged as major. The fast pass takes ≤ 3 min. Producer agreement is ≥ 70 % over the first 50 rated items. |

#### Q4. Success metrics
The §26 targets point the right way, but three things are missing:
- **Reliability**: the Hub must never cost a post.
- **Producer time**: this is what the whole Hub is meant to save. "Agent time" isn't the bottleneck; Ľuboš's hands-on time is.
- **How each metric is measured.**

Changes:
- **Add:**
  - Reels posted on schedule: 24/24.
  - Posts delayed by the Hub: 0.
  - Producer hands-on time per reel, from footage to approved: target ≤ 60 min. Baseline: Giro_00 took "one long session", roughly 4–6 h (**to be confirmed by Ľuboš**).
  - Share of reels whose draft started from a Hub prompt: ≥ 90 %.
  - Clarifying questions the agent asks per prompt: ≤ 1.
  - Factual corrections after posting: 0.
- **Change:**
  - "Findings promoted per month: 1–2" is a quota, and quotas encourage false findings with N ≈ 24. Change it to "0–2, every one passing the §12.5 evidence rule".
  - "Reused moments / graphics: tracked, growing" can't be tested. Change it to "≥ 2 unused-gem moments used in the series; map templates used in ≥ 20 of 21 stage reels".
  - "Metrics linked within 24 h: 100 %" doesn't work, because the API delays data up to 48 h. Change it to "24 h snapshot stored for ≥ 95 % of reels".
- **Keep:** caption corrections < 3, feedback rounds ≤ 2, critique agreement ≥ 70 % (counted only after 50 rated items), New reel → prompt < 2 min.
- **Measure automatically:** timestamp every reel status change and every version and feedback round. Then the Hub computes its own metrics and nobody has to keep a stopwatch.

Also track one **audience outcome without a target**: median hold rate and saves per 1,000 reach for reels 13–24 vs. reels 1–12. That's the honest test of whether the learning loop helps.

#### Q5. Open questions in §27
All three can be decided now (P6–P8):
- **Single user or shared with Katarina:** single user (Ľuboš) for the December project. No auth, localhost only, English UI labels with Slovak content. Katarina gets a generated **Shoot sheet** (Markdown, sent to her phone however they already share files) and a read-only "What worked" summary, without logging in. Revisit before the May race-reels project if she wants to tag moments herself.
- **Where masters live:** on the MacBook under `~/Movies/ReelsHub/<project>` during production and until the 28 d metric window closes (≈ 21 Jan 2027). After that, move them to an external SSD. The Hub keeps proxies, transcripts and contact sheets, and marks clips `offline` with a volume ID. Re-attach works by hash. No NAS support is built.
  - Assumption to check: the free disk space on the Mac. Giro_00 alone was ≈ 40 min of 4K across 3 files. 24 reels in about 8–10 shoot days could reach **300–500 GB** (**unverified estimate**, it depends on Sony bitrate).
- **Posting:** manual, from Edits or the Instagram app. Use Instagram's in-app scheduling if the timing needs it. **Drop `publish_*` from scope.**
  - Reason (checked 2026-11-12): in the Content Publishing API, "Music tagging is only available for original audio". So a reel published through the API can't carry Edits' licensed "Dolce Vita" as licensed audio. That conflicts with D8 and §15.6 ([IG User Media reference](https://developers.facebook.com/docs/instagram-platform/instagram-graph-api/reference/ig-user/media)).
  - The Hub records `posted_at` and `ig_media_id` after the fact.

#### Q6. Future projects
The likely sequence:
1. **Giro 2027 race companion, 8–30 May 2027.** The same 21 stages, live or next-day reels. This is the obvious follow-up, and it reuses almost everything: stage table, glossary, map templates, unused moments, findings, signature track.
2. **Tour de France 2027 (July)** and **Vuelta 2027 (Aug–Sep)**, as smaller advent-style or recap series.
3. Non-cycling travel topics: "how to get there" turned out to be one of the three reel angles.

What should be reused between projects, by scope level:
| Scope | Reused | Not reused |
|---|---|---|
| **Account** (katttyi) | Design language, Edits playbook, music taste profile + blocklist, caption correction memory, critique rubric, findings marked `applies_to: account` | – |
| **Domain** (e.g. `cycling`, `giro2027`) | Glossary sets (`sk-cycling`, `sk-italy`), stage/fact tables, map and motion templates | Facts past `review_by` (re-check first) |
| **Project** | Unused-gem moments (offered, not auto-used), signature track | Reel slots, continuity chain, experiments |

Spec implication: keep anything domain-specific out of hard-coded keys. For example, `hub://stages/giro2027` in §17.1 should become `hub://stages/{fact_domain}`. Findings need an explicit `scope: account | domain | project` (P11).

#### Q7. Release rhythm
- **Two deploy windows a week**, Sunday and Wednesday at 20:00–22:00 (after the 18:00 post has its first-hour numbers). Only deploy a tagged release from `main`.
- **Buffer rule:** only deploy when at least 2 future reels are already approved, so a bad release can't cost a post.
- **Before every deploy:** run `sqlite3 .backup` and note the previous image tag. Rollback = re-run the previous tag and restore the backup, ≤ 10 min, rehearsed once before 1 Dec.
- **Migrations during 1–24 Dec are additive only.** No dropped or renamed columns, no changes to the prompt-template schema without a golden-test update.
- **Hotfixes** are allowed outside the windows only for blockers that stop the daily reel. They still go through `fix/…` and the full suite (D10).
- **Freeze from 21 Dec until the series ends.** The last three reels are the finale and aren't worth risking.
- **Every release note says** which of the producer's daily steps changed, in a line or two.

### Proposals

#### P1. Day-1 kit and delivery-ordered roadmap
- **Type:** change
- **Section:** §25
- **Proposal:** Split §25 into releases by date instead of the phase list, and renumber phases in delivery order. Mark which parts of each phase are in the December kit.
- **Suggested spec text:** Replace the sentence "**Target before December 1:** phases 0–2, the project and reel prompt (phase 9) and the facts store (phase 3), so the 24-day project runs on the Hub. Critique (phase 10) and analytics (phase 5) can start mid-project; early posts are backfilled from the API." with:
  ```markdown
  ### 25.1 Releases for the Giro 2027 advent project
  ```
  ```yaml
  releases:
    R1_day1_kit:            # code complete 25 Nov, dress rehearsal 27 Nov, go/no-go 28 Nov
      - phase0: all
      - phase1: [transcripts_with_glossary_hint, manual_clock_offset_per_device_per_shoot, fts_search, moment_tagging, do_not_use_ranges]
      - phase2: [search_moments, get_transcript, get_take, frame_sheet, host_paths, get_style_tokens, get_playbook, add_playbook_item, glossary_resource]
      - phase3: [stage_table, fact_records_with_status_and_conflicts, glossary, correction_memory, fix_captions]
      - phase9: [project_from_yaml, reel_records, new_reel_prompt, prompt_history, prompt_golden_tests]
      - phase4: [create_version, log_feedback, resolve_feedback]
      - phase7: [map_overview, map_closeup]          # static, wraps mkmap.py
      - phase5: [snapshot_24h]                        # API pull or manual form
      - shoot_sheet_markdown
    R2_mid_series:          # merged 2–20 Dec, deploy windows only (§24.5)
      - phase4: [approval_gate, export_allowed, diff_view]
      - phase10: [critique_fast]
      - phase5: [window_pulls, manual_retention_import, reel_card]
      - phase1: [auto_multicam_sync, speaker_labels]
      - phase3: [lint_script]
      - phase9: [continuity_check, calendar_view]
      - phase7: [card_map_cities_test]
    R3_after_series:        # from 27 Dec
      - everything else in §25
  ```
  Plus: "Phase 3 (facts) is built before phase 9 (prompt), because the prompt depends on the fact store."
- **Why:** Today is 12 Nov. The phases §25 targets before December add up to about 6 weeks of estimates against 19 days. Without an explicit cut, AI builders will finish the most interesting parts first, not the most necessary ones.
- **Priority:** must-have before build

#### P2. Risk: the D2 timeline against 19 calendar days
- **Type:** risk
- **Section:** §27
- **Proposal:** Record the timeline risk once and give it a concrete fallback. D2 itself isn't reopened.
- **Suggested spec text:** Add a row to the §27 table: `| Day-1 kit not proven by the 27 Nov dress rehearsal (19 days from spec v0.4) | Go/no-go on 28 Nov. If no-go, December runs the Giro_00 manual workflow (Edits + Claude + hand-made notes) and the Hub is used only for what passed: typically transcripts and search. No reel waits for a Hub feature. |`
- **Why:** If the gap shows up only on 1 Dec, the consequence is a missed or rushed daily post in a 24-day series where continuity is the format.
- **Priority:** must-have before build

#### P3. Acceptance criteria per phase
- **Type:** addition
- **Section:** §25 (new §25.2)
- **Proposal:** Add machine-checkable acceptance criteria for each phase. Where possible, they become tests in §24.2. Section §24.3 (definition of done per feature) stays as it is; this adds definition of done **per phase**.
- **Suggested spec text:**
  ```markdown
  ### 25.2 Acceptance criteria (a phase is done only when all are met)
  ```
  ```yaml
  acceptance:
    phase0:
      - clean_install_to_health_green_min: 10
      - giro00_size_drop_registered_with_proxies_min: 30     # 13 min Sony + 2×13 min DJI
      - host_path_imports_in_edits_without_copy: manual_check_once
      - container_restart_data_loss: none
      - backup_restore_tested: once
    phase1:
      - c0031_wer: "<= benchmark winner (§5.1a)"
      - glossary_names_correct: "6/6 (Terst, Rím, Zoncolan, Ľuboš, lízatko, etapa)"
      - transcription_throughput: "40 min audio in <= 60 min"
      - fts_query_lizatko_returns_490_1_s_under_s: 1
      - dji_offset_error_s: 0.042        # ±1 frame at 24 fps vs. 24.85 s
      - producer_finds_giro00_hook_cold_min: 2
    phase2:
      - fresh_agent_gets_hook_and_importable_path_without_fs_browsing: true
      - contract_test_per_tool: true
      - every_call_in_agent_log: true
    phase3:
      - stages_imported_with_url_and_checked_date: 21
      - stage1_slovenia_status: conflicting
      - fix_captions_known_corrections: ["lyžičko→lízatko", "po 30→po tridsiatke"]
      - overdue_review_by_on_today_screen: true
    phase9:
      - new_reel_to_prompt_min: 2
      - prompt_max_words: 2500
      - golden_test_giro00: pass
      - dress_rehearsal_stage1: "fresh agent drafts with <= 1 clarifying question and 0 claims outside the fact store"
    phase4:
      - giro00_round1_paste_creates_items: 4
      - export_allowed_before_approval: false
      - edit_after_approval_invalidates: true
      - diff_v3_v4_shows: "closing_card 5.5 s → 3.5 s"
    phase5:
      - snapshot_24h_stored_share: 0.95
      - api_version_recorded: true
      - retention_screenshot_import_min: 3
    phase6:
      - promotion_requires: "N >= 5 per variant and range excluding 0"
      - series_experiment_logged_on_reels: 24
    phase7:
      - stage_reel_maps_from_templates: "21/21"
      - motion_render_deterministic: "same hash twice"
      - edits_alpha_import_result_in_playbook: true
    phase8:
      - shortlist_3_min: 5
      - briefs_with_at_least_one_keep: 0.70
      - full_track_files_written: 0
    phase10:
      - giro00_fixture_half_out_first_frame: major
      - fast_pass_min: 3
      - producer_agreement_after_50_items: 0.70
  ```
- **Why:** Q3 asks what "done" means. Without these, an AI builder will mark phases done when the code merges, not when the producer's work actually gets faster.
- **Priority:** must-have before build

#### P4. Never block a post: buffer and manual fallback
- **Type:** addition
- **Section:** §2
- **Proposal:** Add a tenth principle that keeps the Hub off the posting critical path.
- **Suggested spec text:** Append to §2: `10. **Never block a post.** The Hub speeds up production but is never required to post. Keep at least 2 approved reels ahead of the posting date during a series. If the Hub is down, the manual workflow (Edits + Claude + Markdown notes in the project folder) still works, and the Hub catches up afterwards by importing the version and ig_media_id.`
- **Why:** In a daily series, one missed day breaks the continuity chain ("Zajtra: 1. etapa"). A buffer also makes the release rhythm (P5) safe.
- **Priority:** must-have before build

#### P5. Release rhythm during a series
- **Type:** addition
- **Section:** §24 (new §24.5)
- **Proposal:** Define how releases reach the running Hub while a series is in production.
- **Suggested spec text:**
  ```markdown
  ### 24.5 Releases during a running series
  - Deploy windows: Sunday and Wednesday 20:00–22:00, tagged releases from `main` only.
  - Deploy only when ≥ 2 future reels are approved (§2 principle 10).
  - Before each deploy: `sqlite3 .backup`, note the previous image tag. Rollback = re-run the previous tag + restore the backup (≤ 10 min, rehearsed before the series starts).
  - During a series, DB migrations are additive only (no dropped or renamed columns).
  - Hotfixes outside the windows only for blockers of the daily reel; they still follow §24.1.
  - Freeze from 3 days before the series ends.
  - Each release note lists the producer's daily steps that changed.
  ```
- **Why:** This answers Q7. D10 says how code reaches `main`, but nothing says how `main` reaches the running Hub during the 24 days.
- **Priority:** must-have before build

#### P6. Decision: single user for December
- **Type:** change
- **Section:** §27, §3, §20
- **Proposal:** Settle the open question: single user, no auth, Katarina served by generated documents.
- **Suggested spec text:** Replace the §27 row `| **Open:** single user or shared with Katarina? | Affects auth and UI language |` with `| **Decided:** single user (Ľuboš) for Giro 2027 advent. No auth, localhost only, English UI labels and Slovak content. Katarina gets a generated Shoot sheet (Markdown) per shoot day and a weekly "What worked" summary. Revisit before the May 2027 race project. | – |`. In §20, change "Bilingual UI labels (SK/EN), Slovak content." to "English UI labels, Slovak content. SK labels later, if Katarina becomes a user."
- **Why:** Auth and a bilingual UI add work but no value for one user on one Mac. Katarina's real needs in §3 are met by documents.
- **Priority:** must-have before build

#### P7. Decision: where masters live
- **Type:** change
- **Section:** §27, §5.1, §18
- **Proposal:** Masters stay on the Mac during production plus the metric window, then move to an external SSD. Clips track whether they're online.
- **Suggested spec text:** Replace the §27 row `| **Open:** where masters live long-term (NAS, external SSD)? | Affects watcher paths and hashing |` with `| **Decided:** masters live in ~/Movies/ReelsHub/<project> until the 28 d metric window of the last reel closes, then move to an external SSD. Clips get availability (online/offline) and volume_id; files that come back are re-attached by hash. Proxies, transcripts and contact sheets stay on the Mac. No NAS support. | Check free disk before each series (estimate 300–500 GB for 24 reels) |`. In §18 `clip`, add `availability, volume_id`.
- **Why:** This avoids building multi-volume watchers before they're needed, and keeps search and the prompt working after the archive move.
- **Priority:** before phase 0

#### P8. Decision: posting stays manual; drop `publish_*`
- **Type:** change
- **Section:** §27, §11.3, §17.2
- **Proposal:** Posting is manual from Edits or the Instagram app. Remove the `publish_*` tools from scope.
- **Suggested spec text:** Replace the §27 row `| **Open:** posting stays manual, or schedule through Meta? | If automated, publishing must go through the approval gate |` with `| **Decided:** posting stays manual (Edits / Instagram app, in-app scheduling allowed). The Content Publishing API can't attach licensed library music ("Music tagging is only available for original audio", checked 2026-11-12), which conflicts with D8. The Hub records posted_at and ig_media_id after posting. | – |`. In §11.3, change "MCP `export_*` and `publish_*` tools **refuse**" to "MCP `export_*` tools **refuse**".
- **Why:** [IG User Media reference](https://developers.facebook.com/docs/instagram-platform/instagram-graph-api/reference/ig-user/media), Reels limitations, checked 2026-11-12. It also removes a whole integration from scope.
- **Priority:** must-have before build

#### P9. Early-window metrics can't be backfilled
- **Type:** change
- **Section:** §25, §12.1, §19.4
- **Proposal:** Capture a 24 h snapshot from the first post, and drop the 1 h window.
- **Suggested spec text:** In §25, remove "early posts are backfilled from the API". Add to R1: "`snapshot_24h`: from the first post, store the 24 h values (views, reach, likes, comments, shares, saved, ig_reels_avg_watch_time, reels_skip_rate) via the API or a 2-minute manual form." In §12.1 and §19.4, change "1 h, 24 h, 72 h, 7 d, 28 d" to "24 h, 72 h, 7 d, 28 d (the API can delay data up to 48 h; early windows are best-effort and flagged)".
- **Why:** Checked 2026-11-12 in the [IG Media Insights reference](https://developers.facebook.com/docs/instagram-platform/reference/instagram-media/insights): "Period is automatically set to `lifetime`… and cannot be changed", and "Data… can be delayed up to 48 hours". So a pull on 10 Dec returns lifetime totals, not the 24 h values of the 1 Dec reel, and within-series comparisons for early reels would be lost.
  - The same page lists `reels_skip_rate` for Reels. That partly covers the "hook rate" that §27 assumes needs manual import (the data analyst, packet 08, should confirm).
  - `follows` isn't listed for REELS, so "follows from the post" in §12.1 isn't available from the API.
- **Priority:** must-have before build

#### P10. Success metrics: add reliability and producer time; measure automatically
- **Type:** change
- **Section:** §26
- **Proposal:** Add rows, fix the untestable ones, and timestamp the reel status pipeline so the metrics compute themselves.
- **Suggested spec text:** Add rows to the §26 table:
  - `| Reels posted on schedule | – | 24/24 |`
  - `| Posts delayed by a Hub problem | – | 0 |`
  - `| Producer hands-on time per reel (footage → approved) | ~4–6 h (to confirm) | ≤ 60 min |`
  - `| Reels whose draft started from a Hub prompt | 0 % | ≥ 90 % |`
  - `| Clarifying questions from the agent per prompt | – | ≤ 1 |`
  - `| Factual corrections after posting | – | 0 |`
  - `| Median hold rate and saves/1k reach, reels 13–24 vs. 1–12 | – | Tracked, no target |`

  Replace:
  - `| Reused moments / graphics per month | 0 | Tracked, growing |` → `| Unused-gem moments used / stage maps from templates | 0 | ≥ 2 per series / ≥ 20 of 21 |`
  - `| Reels with metrics linked within 24 h of posting | 0 % | 100 % |` → `| Reels with a stored 24 h snapshot | 0 % | ≥ 95 % |`
  - `| Findings promoted to the design language per month | 0 | 1–2, evidence-backed |` → `| Findings promoted to the design language | 0 | 0–2 per series, each passing §12.5 |`

  Add below the table: `All metrics are computed by the Hub from timestamped status transitions (§6.2), versions, feedback rounds and prompt records; no manual time tracking.`
- **Why:** The Hub's purpose is producer time and on-time posts, and §26 measures neither. A promotion quota with N ≈ 24 encourages false findings.
- **Priority:** before phase 0 (the timestamps must exist in the schema from day one)

#### P11. Scope levels for cross-project reuse
- **Type:** change
- **Section:** §6.1, §13.1, §17.1
- **Proposal:** Give reusable knowledge an explicit scope and remove Giro-specific hard-coding.
- **Suggested spec text:** In §17.1, change `hub://stages/giro2027` to `hub://stages/{fact_domain}`. In §13.1, change `applies_to: [giro2027-advent]` to `scope: account | domain | project` and `applies_to: [...]`. Add to §6.1 point 4 (History): "Inherited by scope: account (design language, playbook, taste profile, correction memory, critique rubric), domain (glossary sets, fact and stage tables after re-check, graphic templates), project (unused moments offered, not auto-used). Next planned project: Giro 2027 race companion, 8–30 May 2027."
- **Why:** The May race project reuses almost everything. If the schema assumes one project, the AI builder will hard-code it, and migrating later costs more than adding a scope column now.
- **Priority:** before phase 0

#### P12. Shoot sheet for Katarina
- **Type:** addition
- **Section:** §6.2, §17.2
- **Proposal:** Generate a per-shoot Markdown sheet: the reels covered, the topic per reel, pickups to record (from `pickup` records), props, and last week's top finding in one line.
- **Suggested spec text:** Add to §6.2 after "Shoot planning": "- **Shoot sheet:** `generate_shoot_sheet(project, shoot_date)` writes `shoots/<date>/SHOOT_SHEET.md`. It lists reels covered, topic and closing promise per reel, pickups (verbatim proposed wording, marked *not recorded*), props, and one 'what worked' line. Written for the host; Slovak; fits one phone screen per reel."
- **Why:** §3 says the host needs "what to record next, pickup lines, what worked". Nothing in the roadmap delivers that. Giro_00 already produced a suggested pickup that had nowhere to go.
- **Priority:** before phase 9 (in R1)

#### P13. Decide one experiment before the series starts
- **Type:** addition
- **Section:** §13.2
- **Proposal:** Pre-register a single experiment for the 24-day series, so the learning loop has usable data by January.
- **Suggested spec text:** Add to §13.2: "- **Per series, one pre-registered experiment**, decided before the first post and stored as `experiment` records. Giro 2027 advent: `ending_type`, cliffhanger question on screen vs. spoken sign-off only, alternating by day for Stages 1–21 (≈ 10–11 per variant). Primary metric: share rate per 1k reach at 72 h. Everything else follows the design language unchanged."
- **Why:** With 24 reels and N ≥ 5 per variant (§12.5), there's room for one clean comparison. Ad-hoc changes give none. The Instagram strategist (packet 07) may pick a different variable, but the decision has to be made before 1 Dec.
- **Priority:** before phase 0 (decision only, no code)

#### P14. Dress rehearsal and go/no-go gate
- **Type:** addition
- **Section:** §25
- **Proposal:** Before the series starts, prove the Day-1 kit end to end on real work.
- **Suggested spec text:** Add to §25.1: "**Dress rehearsal (27 Nov):** create the giro2027-advent project from YAML, ingest the Stage 1 shoot, click New reel for Day 2, hand the prompt to a fresh Claude session, and produce a reviewable draft. Record producer hands-on time and the agent's clarifying questions. **Go/no-go (28 Nov):** go if the phase 0–3 and 9 acceptance criteria (§25.2) pass and hands-on time ≤ 2 h; otherwise apply the §27 fallback."
- **Why:** This is the only way to find out before 1 Dec whether the prompt is really self-contained and whether ingest keeps up with the daily cadence.
- **Priority:** must-have before build

**Sign-off:** approve with changes
