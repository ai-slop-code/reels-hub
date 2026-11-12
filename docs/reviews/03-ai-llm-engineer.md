# Review packet 03: AI / LLM engineer

**Priority:** must review before implementation
**Time needed:** 2–3 h
**Decisions already made:** D2 AI builds it, D3 cost no constraint, D6 prompt injection out of scope (see [README](README.md#decisions-already-made-please-dont-reopen)).

## Why you
The reel prompt generator, the AI critique and the agent tool surface are the heart of Reels Hub. They decide whether an AI editor produces a good first draft.

## Read
- [§6.3–6.4 New reel and the reel prompt](../spec/REELS_HUB_SPEC.md#6-module-b-projects-reels-and-the-reel-prompt)
- [§16 AI critique](../spec/REELS_HUB_SPEC.md#16-module-l-ai-critique)
- [§17 Agent interface](../spec/REELS_HUB_SPEC.md#17-agent-interface-mcp-server)
- [§13 Learning loop](../spec/REELS_HUB_SPEC.md#13-module-i-learning-loop-and-experiments)
- [§14 Edits playbook](../spec/REELS_HUB_SPEC.md#14-module-j-tool-knowledge-edits-playbook)
- Reference: how the Giro_00 intro was actually built (`../reels/giro00-intro/review_notes.md`)

## Questions
1. **Prompt generator:** is the template in §6.4 the right structure? What belongs inline vs. as `hub://` resources the agent fetches? Is ~2,500 words a sensible budget?
2. **Context ranking:** how should the Hub choose which moments, facts and findings go into the prompt? Rules, embeddings, or an LLM pre-pass?
3. **Critique model:** which model(s) for watching a reel from sampled frames + transcript + audio data? How many frames, at what resolution, in one call or several? How do you make sound-on vs. muted passes meaningful?
4. **Critique reliability:** how do we evaluate the critic (golden reels with known issues, agreement with the producer, predicted vs. actual drop points)? What's the minimum evaluation set before we trust it?
5. **Agent tool surface:** are ~40 MCP tools manageable for an agent? Suggest grouping, naming and descriptions that agents use correctly. Which tools need examples in their descriptions?
6. **Guardrails as code:** approval gate, "only Katarina's real words", pickups stored separately. Which of these should be enforced by the server vs. stated in the prompt?
7. **Learning loop:** how do prompt versions, critique scores and Instagram performance feed back into the next prompt without overfitting to a handful of reels?
8. **Model choice and versions:** record model IDs per prompt and critique run? Plan for upgrades (e.g. re-running critique on old reels)?

## Expected output
- Revised prompt template and ranking approach.
- Critique design: inputs, model, rubric, evaluation plan.
- Recommendations for MCP tool grouping and descriptions.

## Your input

### Summary
The overall AI design is sound. The prompt handover, critique-before-producer and the learning loop are the right parts to have, and the Giro_00 notes show the agent behaviour the spec wants to repeat. Four gaps would hurt the first build, though:
1. **§16.1 is too heavy to run.** At 4 fps for a 50 s reel, the critic gets ~200 full-HD frames. That exceeds the 100-image request limit on 200k-context Claude models and buries the signal. The critic needs change-driven sampling, separate passes, and deterministic checks before any LLM judgement.
2. **The approval gate can be bypassed.** It only guards Hub tools, but export happens in **Edits** through the Edits MCP. It needs a client-side hook. A non-export preview render also needs to exist, or the critic has nothing to watch.
3. **The spec never says who calls the LLM, or which model.** The Hub itself needs an LLM runtime with pinned model IDs, and every prompt, critique and ranking run needs provenance.
4. **The ~45-tool MCP surface needs organising.** It should be split into toolsets with consistent names, annotations and examples. It also needs the missing tools that the guardrails depend on (`add_pickup`, `add_open_item`, `get_reel_context`).

Finally, the learning loop should feed the **process** (feedback items, rounds, critique hits), not just Instagram metrics. With 24 reels, metrics alone will overfit.

### Answers

#### Q1. Prompt generator: structure, inline vs. resources, budget
**The structure is right. I would change five things:**
1. **Put stable content first and reel-specific content last.** Rules, workflow and the definition of done barely change between reels, so they belong at the top. Brief, moments, facts and continuity go at the bottom. Prompts stay comparable across reels, diffs between prompt versions stay readable, and prompt caching works if the agent's client uses it.
2. **Replace "Use these tools" with an ordered workflow.** The agent already sees tool schemas through MCP. Listing tool names in the prompt wastes words and goes stale when tools are renamed. What the agent doesn't know is the **order** and the **stop points**, for example "captions only after the last trim" and "stop and ask before using an unverified fact".
3. **Add an "Acceptance checks" section** with measurable criteria the agent checks itself before handover: runtime within ±10 % of target; subject fully in frame on frame 1; 100 % of speech captioned; no `blocker`/`major` critique items left unaddressed; every on-screen claim carries a `fact_id`; music under speech at 0.20 ±2 dB. Giro_00 needed three feedback rounds partly because "done" was implicit.
4. **Give every inline item a stable ID** (`mom_…`, `fact_…`, `find_…`, `pb_…`), so the agent can cite them in review notes. The Hub can then measure which inline items were actually used, and that measurement feeds ranking (Q2) and the learning loop (Q7).
5. **Write the instructions in English and quote all Slovak verbatim in quotation marks.** Katarina's words and caption text must never be paraphrased or translated. Saying this explicitly in the template prevents "helpful" rewording.

**Inline vs. resource:**

| Inline (in the prompt) | As `hub://` resource or tool call |
|---|---|
| Task, goal, target runtime, audience | Full transcripts (`get_transcript`) |
| Workflow order and stop points, acceptance checks, rules | Full fact table, stage table (`hub://stages/…`) |
| **Top 6–8 candidate moments**: id, clip, `src_in`–`src_out`, rating, one-line verbatim transcript, why it was ranked | All other moments (`search_moments`) |
| **Facts allowed** (≤ 10, with `fact_id` and one source each) and **all** unverified or conflicting claims in this slot's subject area | Sources in full, fact history |
| Continuity: previous reel's closing promise (verbatim), what this reel must set up | Full project plan (`hub://project/{id}`) |
| Open items carried over | Feedback history of earlier reels |
| 3–5 learnings with evidence and status | All findings, metrics, past critiques |
| Edits playbook items **relevant to the planned steps** (≤ 8), plus all items flagged `critical` | Full playbook (`hub://playbook/edits`) |
| Design: 6–10 key tokens (accent colour, caption style and position, safe-zone numbers, card hold time, music levels) | Full design language (`hub://design-language/current`) |
| Glossary terms likely in this reel (≤ 15) | Full glossary and correction memory |

Many MCP clients make resources harder for the model to use than tools: Claude Code exposes them through @-mentions, not automatic fetching (from memory, **unverified** for the current version). Every resource the prompt relies on should therefore **also** be reachable through a tool, e.g. `get_reel_context(reel, section)`.

**Budget:** ~2,500 words is an acceptable **hard cap** but too much as a target. Context size isn't the problem. The prompt is a document the producer must actually read before sending (§6.4 "Preview and edit"), and long prompts dilute the rules. I recommend a **target of 1,200–1,800 words and a hard cap of 2,500**, with a budget per section (see P4). Measure in **tokens** as well as words, because Slovak quotes tokenize at roughly 2–3× the token count of English words (my estimate, **unverified**). Store `word_count` and `token_count`.

#### Q2. Context ranking
Use a **hybrid pipeline: deterministic filters → hybrid retrieval → feature score → optional LLM rerank**, logged per prompt. Embeddings alone can't tell what a hook is. An LLM alone isn't reproducible and can't be snapshot-tested.

**Moments:**
1. **Hard filters (code):** `usable = true`; not in a do-not-use range; not already used in this project unless `reuse_ok`; speaker = katarina for hook candidates.
2. **Retrieval (code):** build a query from the slot: stage towns and climbs from the stage table, the topic angle, glossary terms and the hook idea. Run FTS5 (BM25, diacritic-folded) and vector search with a multilingual embedding model (e.g. `BAAI/bge-m3` or `intfloat/multilingual-e5-large`; both multilingual including Slovak, from memory, **unverified**, so benchmark on our transcripts). Merge with reciprocal rank fusion (k = 60). Keep the top 40.
3. **Feature score (code, weights in YAML, versioned):** `0.35·relevance + 0.25·rating/5 + 0.15·role_fit + 0.10·duration_fit + 0.10·unused_gem + 0.05·angle_available − reuse_penalty`.
   - `role_fit` compares tags with the beat: a hook needs `hook`/`curiosity`/`question`; a sign-off needs `sign-off`.
   - `duration_fit` is measured per beat: hook 2–7 s, promise 3–8 s, payoff 8–25 s.
4. **LLM rerank (optional, on by default because cost isn't a constraint):** one structured-output call that gets the top 30 with transcripts plus the brief. It returns ≤ 8 picks, one per beat with up to 2 alternatives, each with a one-line reason. If the call fails or times out (> 30 s), fall back to the code ranking. Golden tests (§24.2) run with the LLM step mocked, so snapshots stay deterministic.

**Facts:** no ranking needed. Facts link to the stage or subject through the structured stage table. Include every `verified` fact for the slot's subject, capped at 10 by `kind: primary` first. **Always** include every `unverified`/`conflicting` fact for the subject, because those are the ones an agent must not state.

**Findings:** only `supported` findings whose `applies_to` covers the project, sorted by the **lower bound** of the effect range (not the point estimate), max 5. Findings with status `hypothesis` appear only when the reel is assigned an experiment (§13.2), labelled "experiment variant".

**Playbook:** tag items with workflow steps (`import`, `trim`, `overlay`, `captions`, `music`, `export`) and severity (`critical | normal`). Include items whose steps match the planned workflow, plus all `critical` ones.

**Logging:** save a `context_manifest` (included IDs, scores, reasons, excluded-but-close IDs) with each `reel_prompt`. Without it, nobody can later explain why the agent never saw a moment.

#### Q3. Critique model, frames, passes
**Model:** the **strongest Claude model with vision available on the Anthropic API**, with the exact model ID pinned in config (Q8). Since D3 removes cost as a constraint, the critic doesn't need to be a cheaper model.
- Claude takes **images, not video or audio**. "Watching" therefore means sampled frames plus audio described as data.
- Checked 2026-11-12 via secondary sources, because the official Anthropic docs returned 403 to my fetch (so **partly unverified**):
  - 100 images per request on 200k-context models, more (reported 600) on 1M-context models;
  - images on older models are downscaled to a 1,568 px long edge, ≈ 1,600 tokens each;
  - newer models accept up to ~2,576 px at about `w·h/750` tokens.
  - Sources: [fast.io](https://fast.io/resources/claude-image-limit/), [Mochify](https://mochify.app/guides/llm-image-token-costs).
- §16.1's "4 fps at 1080×1920" gives ~200 frames (+ cut and text frames) for a 50 s reel, ≈ 300–550k image tokens. That is over the image limit on 200k models, and in practice the model attends poorly to most of them.

**Sampling: driven by changes, not by a fixed rate.** For a ≤ 90 s reel:

| Set | Frames | Resolution | Purpose |
|---|---|---|---|
| Hook | t = 0.00, 0.25, 0.50, 1.00, 1.50, 2.00, 3.00 s (7) | 1080×1920 | Frame-1 framing, first curiosity, text legibility |
| Ending | last 3 s at 2 fps (6) | 1080×1920 | Sign-off, closing card, cover-frame candidate |
| Structure | First frame after every cut, mid-point of every shot > 3 s, every caption, on-screen text or graphic change. Drop a frame if it is < 0.3 s from another one **and** SSIM > 0.95. Cap 48 | 720×1280 | Pacing, design, captions, graphics |
| Timeline strip | 1 fps, tiled 3×2 per sheet (360×640 per cell), timestamp burned into each cell (~9 sheets for 50 s) | 1080×1280 per sheet | Rhythm, "no visual change for N s", muted comprehension |

Each frame is captioned in the request with `t=12.40s · shot 7 · cut_item id`, so findings can be traced back to specific frames.

**Passes:** run several focused calls plus one synthesis call, not one huge call.
1. **Deterministic checks first, in code, no LLM:**
   - OpenCV: subject in frame on frame 1, text in the face band, safe-zone violations, card hold times, cuts per 10 s, longest stretch without visual change;
   - caption QA (§8): coverage against the transcript, diacritics, glossary;
   - `check_mix` levels;
   - `lint_script` on all on-screen texts and captions.

   Their results go **into** the LLM passes as facts, so the model doesn't re-guess what code can measure, and they appear as their own critique items with `source: rule`.
2. **Hook pass:** hook frames + the first 5 s of transcript and audio data + the brief.
3. **Story and pacing pass:** structure frames + full transcript with speaker labels + cut list + audio timeline + previous reel's promise and next reel's topic.
4. **Captions and design pass:** frames at every caption or text change + design tokens + caption rules.
5. **Muted pass:** see below.
6. **Synthesis:** a text-only call that merges and deduplicates items, assigns severity, writes `predicted_risk`, and drops items without valid evidence (P9).

**Fast mode:** passes 1–3 only, structure frames capped at 20, frames taken from a proxy-reconstructed timeline (see P2). Target < 2 min. **Full mode:** all passes on the preview render.

**Making sound-on meaningful:** the critic can't hear, so give it an **audio timeline as text in 0.5 s rows**:
- speech active (VAD)
- short-term loudness (LUFS-S) of speech and of music, and the dB difference between them
- silence gaps > 0.4 s
- clipping
- level jumps > 6 dB within 50 ms (clicks or cut-offs)
- words per second
- laughter or reaction events (if detected)

Rows are tagged with the active cut item. The critic can then reason about "music too loud under the punchline at 23 s" or "dead air at 31 s" with evidence. It must state the blind spots from §16.4 (music taste, delivery nuance) as a fixed `strengths/limits` line, not guess.

**Making muted meaningful:** the muted pass must **withhold the transcript, the audio timeline and the brief**. It gets only the frames as rendered (captions and on-screen text visible) and the timeline strip.
- **Step A:** the model writes what a muted viewer understands by 3 s, by 20 s and at the end, in 1–2 sentences each.
- **Step B** (a separate call): compare that with the brief's intended hook, promise and closing. Each gap becomes a finding (`area: hook | story`, `mode: muted`).

Without withholding information, the "muted" critique is just the sound-on critique with a different label. The Giro_00 notes ("the hook, the promise and the ending all read without sound") are exactly what step A + B test.

**Optional second opinion:** Gemini accepts real video with audio (default 1 fps, configurable per request; audio ≈ 32 tokens/s; checked 2026-11-12 at [Gemini video understanding](https://aistudio.google.com/docs/video-understanding)). It could add a genuine sound-on view, including music under speech. It is a second cloud processor of footage, though, so I list it as a question (P11), off by default.

#### Q4. Critique reliability and evaluation
Evaluate the critic on three levels, in this order:

1. **Detection on a golden set (before the critic is used in the workflow).**
   - **Real history:** Giro_00's versions with the issues the producer actually raised:
     - closing card 5.5 s → 3.5 s
     - title removed
     - card text and map mismatch (border close-up vs. "Štart v Terste, cieľ v Ríme")
     - hook framing offset 0.545
     - captions "lyžičko" / "po 30"
     - "Čau!" without a speaker label

     That gives ~6 labelled issues across 3–4 versions.
   - **Defect injection:** start from the approved Giro_00 cut (and later reels) and inject one known defect per variant with ffmpeg or a cut-list edit. Use 12 defect types × 2 placements = 24 variants:
     - subject half out of frame on frame 1
     - 8 s without visual change
     - a caption line removed
     - glossary misspelling ("Trieste" instead of "Terst")
     - missing diacritics
     - text in the face band
     - card held 6 s
     - music at 0.6 under speech
     - a 1.2 s dead-air gap
     - an unverified claim on screen ("Stage 1 ends in Slovenia")
     - a joke cut before the punchline
     - a closing that doesn't match the next reel's topic
   - **Clean controls:** 4 approved reels with no injected defect, to measure false positives.
   - **Metrics and gates:**
     - recall of injected `blocker`/`major` defects **≥ 80 %** overall and ≥ 60 % per area;
     - **≤ 1 false `major`+ per clean reel** on average;
     - **stability:** the same input run 3× gives a major-item Jaccard of ≥ 0.7 and per-area scores within ±1 point (on the 1–5 scale).
   - **Minimum set before trusting it:** the 24 injected variants, the 4 clean controls and the Giro_00 history. It runs as the §24.2 "Critique" test tier. It's an LLM test, so run it on demand and before any model or rubric change, not in every pre-merge run, with mocked responses for the normal suite.
2. **Agreement with the producer (from the first real reel):** agree/disagree per item, plus **coverage**: the share of producer feedback items the critic had already flagged on the same version (match = same area and |Δt| ≤ 2 s). Track both per area. The §26 target "≥ 70 % agree" is sensible. Add "coverage ≥ 50 % of producer items by reel 10".
3. **Predicted vs. actual retention (directional only).**
   - A predicted risk window counts as a **hit** if the retention curve's drop rate in that window is ≥ 1.5× the reel's median drop rate per second (excluding the first 3 s).
   - Report the hit rate against a baseline of random windows of equal length.
   - With manual retention import and ≤ 24 reels, **don't** use this to tune the critic before ~15 posted reels with retention curves. Below that, report it but don't act on it.

Only ratings from the producer count for calibration (see P7). An agent marking its own critique items "disagree" would contaminate the measure.

#### Q5. Agent tool surface
About 45 tools is workable for current Claude models **if** the tools are well described, but every tool schema costs context (~150–400 tokens each, so 7–15k tokens) on every turn, and similar tools (`lint_script` / `lint_draft` / `check_fact` / `fix_captions`) cause wrong picks. Recommendations, following Anthropic's guidance on writing tools for agents ([anthropic.com/engineering/writing-tools-for-agents](https://www.anthropic.com/engineering/writing-tools-for-agents), from memory, not re-fetched):

1. **Toolsets.** The server exposes a profile chosen by URL or config: `/mcp?toolset=editor` (default for the reel prompt, ≈ 22 tools), `analyst` (metrics, insights, findings, experiments), `admin` (project creation, fact editing, playbook curation, asset registration). Fewer visible tools means fewer wrong picks.
2. **Names: `<group>_<verb>[_<noun>]`**, all snake_case. The group is the first word, so related tools sort together and the agent can tell apart the Hub's tools and Edits' tools: `moments_search`, `moments_tag`, `moments_exclude`, `transcript_get`, `reel_get_context`, `reel_create_version`, `facts_check`, `captions_fix`, `critique_run`, `music_shortlist`, `review_log_feedback`, `approval_status`. Keep old names as aliases for one release if anything was already built.
3. **MCP tool annotations** on every tool: `readOnlyHint`, `destructiveHint`, `idempotentHint`, `openWorldHint`. Supported since MCP spec 2025-03-26 (from memory). Claude Code can auto-allow read-only tools.
4. **Responses:** a `detail: concise | full` parameter (default concise), pagination with `limit` (default 10) and `cursor`, IDs in every row, and host paths included where Edits needs them, so the agent doesn't need a separate `host_paths` call in the common case.
5. **Errors that tell the agent what to do next:** e.g. `"Version v4 is not approved. Call approval_request(version='v4') and wait; the producer approves in the Hub UI."` and `"Moment mom_0042 is in a do-not-use range (reason: private). Pick another or ask the producer."`
6. **Descriptions** in three parts: *when to use / when not to use (name the alternative tool) / what it returns*. Keep them ≤ 80 words, plus examples where needed.

**Tools that need examples in their description:**
- `moments_search`: filter grammar, e.g. `{"query":"lízatko ružové","filters":{"speaker":"katarina","tags_any":["hook"],"min_rating":4,"unused_in_project":"giro2027-advent"}}`
- `reel_create_version`: the `cut_list` schema is the most error-prone input in the whole surface. Give one complete 3-item example (main clip, overlay, caption) and validate strictly.
- `review_log_feedback`: an example of pasted text → items, with `at_s` and `element`.
- `render_motion` / `generate_map`: one example per template with its params.
- `frame_sheet`: `times` in seconds against the clip, not the timeline. State this explicitly.
- `reel_update`: which fields are writable by agents (not `status: approved`).
- `insights_get`: example questions, and that it returns findings with uncertainty, not advice.
- `playbook_add_item`: the required fields (tool, version_seen, step tag, text).
- `moments_exclude`: that `reason` is required.

**Missing tools that the spec's rules depend on:** `pickup_add(reel, text, purpose, placement_hint)`, `open_item_add(reel, text, kind)`, `reel_get_context(reel, section?)` (the resource fallback from Q1), and `handover_submit(reel, version, notes, open_items, pickups, sources)` for the §6.4 deliverables. The §6.4 deliverables currently have no structured target, so they would end up in free text.

#### Q6. Guardrails as code vs. prompt
Rule of thumb: **anything checkable, or with consequences that can't be undone, is enforced by the server. Judgement goes in the prompt.**

| Guardrail | Server (hard) | Prompt (soft) |
|---|---|---|
| Approval before export or publish | **Server.** No MCP tool can create an approval; approvals are created only from the UI session. `export_allowed` checks the exact version **and** the cut-list hash. **Plus a client hook for Edits export** (P2), because the Hub can't see Edits MCP calls | Restate in Rules |
| Only Katarina's real words | **Server.** `reel_create_version` validates that every caption item's text matches the transcript words under it, after normalising and applying glossary/correction-memory substitutions, with a word error rate ≤ 10 %. Any on-screen text in quotation marks or with a speaker label must likewise match transcript words. Mismatches become `open_item`s that block approval | "Never paraphrase; propose new lines with `pickup_add`" |
| Pickups stored separately | **Server.** `pickup_add` is the only write path for proposed lines, and transcript tables accept no writes from MCP | Mention the tool |
| Do-not-use ranges | **Server.** Hidden by default; access needs `include_excluded: true` + `reason` (logged); `reel_create_version` rejects cut items overlapping them | – |
| Facts | **Server.** `lint_script` runs automatically on on-screen text and captions at `reel_create_version`; unsupported claims become open items | "State only facts listed; cite fact IDs" |
| Captions after trims, card ≤ max hold, music levels | Server **checks** (lint, `check_mix`) and reports | Workflow order in the prompt |
| Run critique before handover | Server records whether a critique exists for the version; `approval_request` warns if none | Prompt |
| Fix critique items you agree with | – | Prompt (judgement) |
| "Never claim to have listened" | – | Prompt + the critic's fixed limits line |
| Human-only signals (approve, `rate_critique_item` for calibration, `rate_track` for taste, finding promotion) | **Server.** Record `rated_by` (human via UI vs. agent via MCP). Only human ratings feed calibration and the taste profile. Promoting a finding needs a UI action | – |

#### Q7. Learning loop without overfitting
1. **Two separate feedback channels:**
   - **Reel features → performance** (§12–13): this is what Instagram data can speak to. It informs **what to make** (hook type, runtime band, map hold).
   - **Prompt template / critic → process quality:** this is what the template actually affects. Measure it with dense, per-reel signals:
     - producer feedback items per version, by area
     - feedback rounds
     - critique blockers at handover
     - time to first draft
     - share of inline context the agent used (from the `context_manifest`)

     That gives 10–30 data points per reel instead of 1. Don't correlate template versions with views. At N ≤ 24 with one template change mid-project, the result would be noise.
2. **Statistics for findings:**
   - Compare against the account's trailing median, normalised (§12.3 already does this).
   - Use partial pooling / shrinkage (e.g. a Bayesian hierarchical model or empirical-Bayes shrinkage towards 0).
   - Promote to `supported` only when the 80 % interval excludes 0 **and** n ≥ 5 per arm. Put the **lower bound** into prompts.
   - Findings decay: re-test after 30 days or 10 new reels, then `retired` if they no longer hold.
3. **Rules get into prompts only through the promotion path.** Nothing flows from metrics into the prompt automatically. The Hub proposes, and the producer approves a finding into the prompt's "Learned" section (max 5). The same applies to template changes: a template change is a branch plus snapshot update (D10), justified by process metrics.
4. **Recurring producer feedback is the fastest learning signal.** If the same feedback category, e.g. "card too long", appears in ≥ 3 reels, the Hub proposes a template rule or an acceptance check. Giro_00's "card 5.5 s → 3.5 s" would have become "cards ≤ 3.5 s" by reel 3.
5. **Offline replay for template changes** (cost isn't a constraint): before switching template vN → vN+1, regenerate prompts for 3 past slots. Have the agent produce a cut-list-only draft (no Edits build) and run the critic. Switch only if the critique blockers and majors don't get worse. This is cheap insurance against regressions.

#### Q8. Model IDs and upgrades
Yes, record them for **every** AI-produced artefact, immutably:
- **Hub-side LLM runs** (ranker, critique passes, insights, feedback splitting): provider, **pinned model ID** (a dated snapshot ID, never an alias such as `-latest`), parameters (temperature, max tokens, thinking budget), prompt/rubric template version, input hash, output, token usage, latency.
- **Agent-side drafts:** the Hub can't see which model the client uses. MCP `clientInfo` gives only the client name and version. So `reel_create_version` takes a required `agent: {client, model}` field, filled from the agent's own self-report, and the session ID is logged.
- **Embeddings and transcripts:** model + version per index row (§5.1a already does this for transcripts). An embedding model change means a full re-embed into a new index column, switched in one step.

**Upgrade plan:** a new critic model or rubric version must first pass the Q4 golden set at least as well as the current one: recall not lower, false positives not higher, stability within limits. Then it re-runs on the last 10 posted reels. Old critiques are never overwritten: new rows link to them with `supersedes`, and dashboards show one critic version at a time. Calibration statistics are kept **per critic version**.

### Proposals

#### P1. Critic inputs: change-driven sampling, focused passes, rules before LLM
- **Type:** change
- **Section:** §16.1, §16.5
- **Proposal:** Replace the fixed 4 fps / 2 fps sampling with the frame budget, pass structure, audio timeline and muted-pass withholding described in Q3.
- **Suggested spec text:** Replace the §16.1 bullets "Picture", "Sound" and "Two viewing modes" with:
  > - **Rules first (no LLM):** OpenCV and lint checks (subject in frame on frame 1, face band, safe zones, card hold, cuts per 10 s, longest static stretch), caption QA (§8), `check_mix`, `lint_script` on all on-screen text. Results become critique items with `source: rule` and are passed to the LLM as facts.
  > - **Picture (change-driven sampling, ≤ 90 s reel):**
  >   ```yaml
  >   critique_frames:
  >     hook:      { times_s: [0, 0.25, 0.5, 1.0, 1.5, 2.0, 3.0], res: 1080x1920 }
  >     ending:    { last_s: 3, fps: 2, res: 1080x1920 }
  >     structure: { at: [after_each_cut, mid_shot_over_3s, caption_change, text_change, graphic_change],
  >                  dedupe: { min_gap_s: 0.3, ssim_over: 0.95 }, cap: 48, res: 720x1280 }
  >     strip:     { fps: 1, grid: 3x2, cell: 360x640, burn_in_timestamp: true }
  >     label_each_frame: "t=<s> · shot <n> · cut_item <id>"
  >   ```
  > - **Sound (as data, the critic cannot hear):** a 0.5 s audio timeline with VAD, speech LUFS-S, music LUFS-S, speech-minus-music dB, silences > 0.4 s, clipping, level jumps > 6 dB in 50 ms, words per second, laughter events, each row tagged with the active cut item.
  > - **Passes:** hook → story and pacing → captions and design → muted → synthesis (text only: merge, dedupe, severity, predicted risk). Fast mode runs rules + hook + story with ≤ 20 structure frames from the proxy timeline (target < 2 min); full mode runs all passes on the preview render.
  > - **Muted pass withholds the transcript, audio timeline and brief.** Step A: describe what a muted viewer understands at 3 s, 20 s and the end. Step B (separate call): compare with the brief; each gap is a finding with `mode: muted`.
- **Why:** 4 fps × 1080×1920 ≈ 200+ images for a 50 s reel exceeds the 100-image limit on 200k-context Claude models (secondary sources checked 2026-11-12; see Q3). Fewer, well-chosen and labelled frames give better attention. Withholding information is what makes the muted pass different from the sound-on pass.
- **Priority:** before phase 10

#### P2. Close the approval gate on the Edits side and add a preview render
- **Type:** change
- **Section:** §11.3, §17.3, §16.5
- **Proposal:** (a) The Hub ships a Claude Code `PreToolUse` hook (and a `permissions.deny` fallback) that blocks Edits MCP export or publish tools unless `export_allowed(version)` returns true for the current cut-list hash. (b) Separate a **preview render** (≤ 1080p, written to `/media/<project>/previews/`, allowed without approval) from **final export** (gated). (c) Fast critique can use a timeline reconstructed by ffmpeg from the version's cut list and the Hub's proxies, so it needs no Edits render at all.
- **Suggested spec text:** Append to §11.3:
  > - **Edits-side enforcement:** export happens in Edits, outside the Hub. The Hub ships a Claude Code hook (`.claude/settings.json`, `PreToolUse`, matcher on the Edits MCP export/publish tools) that calls `GET /api/export_allowed?version=…&cut_list_hash=…` and blocks the call unless it returns `allowed: true`. A `permissions.deny` rule for the same tools is the fallback for clients without hooks. Exact Edits MCP tool names are recorded in the playbook.
  > - **Preview vs. export:** a *preview render* (≤ 1080×1920, to `/media/<project>/previews/<reel>/<version>.mp4`, for review and critique) does not need approval. A *final export* (full resolution, for posting) does. The approval stores the cut-list hash; any change to the hash invalidates it.
  > - **Fast critique without a render:** the Hub reconstructs a draft timeline from the version's cut list and its proxies with ffmpeg (no Edits overlays or captions; marked `approximate: true`).
- **Why:** As written, the agent can call the Edits MCP export directly and the Hub never sees it, so the most important guardrail can be bypassed. In addition, §16.5 needs frames of a draft before approval, which conflicts with "do not render or export until approved". Hook mechanism and matcher syntax are from memory (**unverified** against the current Claude Code docs); Edits MCP tool names are unknown to me.
- **Priority:** must-have before build

#### P3. Hub-side LLM runtime, pinned models and run provenance
- **Type:** addition
- **Section:** §21 (new row), §18 (new table), §16.3
- **Proposal:** State that the Hub calls the Anthropic API itself for critique, ranking rerank, insights and feedback splitting. Keep models in a config registry with pinned IDs, and log every run.
- **Suggested spec text:** Add to the §21 table:
  > | LLM runtime | Anthropic API called from the container (key as Podman secret `anthropic_key`); models pinned by dated ID in `config/models.yaml`, never aliases; structured output via tool-use JSON schema, validated with Pydantic, one retry on invalid output | Critique, context rerank, insights and feedback splitting run inside the Hub, independent of the editing agent |

  Add to the §18 key tables:
  > | `llm_run` | id, purpose (critique_pass / rerank / insights / feedback_split), provider, model_id, params (json), template_or_rubric_version, input_hash, output (json), tokens_in, tokens_out, latency_ms, created_at, supersedes |

  Add to `reel_prompt`: `context_manifest (json), token_count, generator_version`. Add to `version`: `agent_client, agent_model (self-reported), cut_list_hash`. Add to `critique`: `critic_version (model_id + rubric_version + sampling_version), llm_run_ids`.

  Add to §16.4:
  > - **Upgrades:** a new critic model or rubric must match or beat the current one on the golden set (§16.6) before it becomes default, then re-runs the last 10 posted reels. Old critiques are kept and linked via `supersedes`; calibration stats are reported per critic version.
- **Why:** The spec has `critique_reel` as a Hub tool but never says which model runs it or where the key lives. Without pinned IDs, model upgrades silently change the critic and break calibration.
- **Priority:** must-have before build

#### P4. Revised reel prompt template with section budgets
- **Type:** change
- **Section:** §6.4
- **Proposal:** Replace the template with one that puts stable content first, uses a workflow instead of a tool list, adds acceptance checks and inline IDs, and sets budgets per section.
- **Suggested spec text:** Replace the template block with:
  > ```markdown
  > # Reel {project.title} · {reel.slot}: {reel.topic}
  > <!-- template {template_version} · generator {generator_version} · context {context_hash} -->
  >
  > ## Rules (always)
  > - Use only words Katarina (or Ľuboš) actually said. Quote Slovak verbatim; never paraphrase or translate it. Propose new lines with `pickup_add`; never put them in captions.
  > - State only facts listed below and cite their IDs. Anything marked Unconfirmed must not be stated as fact.
  > - Do not use do-not-use ranges. Do not export; preview renders only. The producer approves in the Hub.
  > - Report measurements, not impressions: you cannot hear licensed music.
  >
  > ## Workflow
  > 1. Read context: `reel_get_context({reel.id})` if anything below is unclear.
  > 2. Pick hook, promise, payoff, closing from the candidate moments (search more with `moments_search`).
  > 3. Build the 9:16 draft in a new Edits project "{edits_project_name}": main cut → cutaways → graphics → music.
  > 4. Finish all trims, then captions, then `captions_fix`.
  > 5. `reel_create_version` → `critique_run(mode: fast)` → fix what you agree with → note what you skip and why.
  > 6. `handover_submit` with notes, open items, pickups and sources. Stop and ask the producer if an acceptance check can't be met.
  >
  > ## Acceptance checks
  > - Runtime {target_runtime} ± 10 %. Subject fully in frame on frame 1.
  > - 100 % of speech captioned; glossary terms correct; captions at y = {caption_y}.
  > - Cards ≤ {max_card_s} s; music {under_speech} under speech, {silent_card} on silent cards.
  > - No unaddressed blocker or major critique items. Every on-screen claim has a fact ID.
  >
  > ## Style (design language {version})
  > {6–10 key tokens}. Full rules: hub://design-language/current
  >
  > ## Tool quirks (Edits)
  > {≤ 8 playbook items for the planned steps + all critical items, each with its ID}
  >
  > ## Learned from previous reels
  > {≤ 5 supported findings: statement · lower-bound effect · n · finding ID}
  > {experiment variant for this reel, if any}
  >
  > ## This reel
  > Goal: {reel.brief}. Audience: {audience}. Target runtime {target_runtime}.
  > Continuity: previous reel promised "{prev.closing_promise}". This reel must set up "{next.topic}".
  > Open items carried over: {open items with IDs}
  >
  > ### Candidate moments
  > | Beat | ID | Clip · in–out | Rating | Transcript (verbatim) | Why |
  > {6–8 rows: ≤ 3 hook, ≤ 2 payoff, ≤ 2 closing, plus unused gems}
  >
  > ### Facts you may state
  > {≤ 10 verified facts: ID · claim · one source}
  > Unconfirmed (do not state as fact): {all unverified / conflicting facts for this subject, with IDs}
  >
  > ### Music
  > {signature track or shortlist with IDs}; mix {levels}.
  >
  > ## Deliverables
  > Via `handover_submit`: Edits project name, version, runtime, music, open items, pickups, sources, critique items skipped with reasons.
  > ```
  Replace the "Token budget" bullet with:
  > - **Budget:** target 1,200–1,800 words, hard cap 2,500 words and 5,000 tokens (both stored). Fixed sections ≤ 600 words; candidate moments ≤ 500; facts ≤ 350; learned ≤ 150; quirks ≤ 200; style ≤ 150. Overflow is moved to `hub://` resources, which are also reachable via `reel_get_context(reel, section)`.
- **Why:** See Q1. Stable content first keeps prompts comparable and cacheable. A workflow and acceptance checks address the implicit "done" that caused three Giro_00 rounds. IDs make usage measurable.
- **Priority:** before phase 9

#### P5. Context ranking pipeline with a logged manifest
- **Type:** addition
- **Section:** §6.3
- **Proposal:** Specify the four-stage ranking (filters → FTS5 + vector with reciprocal rank fusion → weighted feature score → optional LLM rerank with fallback), and store a `context_manifest` per prompt.
- **Suggested spec text:** Add after the §6.3 table:
  > **Ranking (versioned in `config/ranking.yaml`):**
  > ```yaml
  > ranking:
  >   moments:
  >     filters: [usable, not_do_not_use, not_used_in_project_unless_reuse_ok, hook_speaker_katarina]
  >     retrieve: { fts5_bm25: 40, vector: 40, fuse: rrf, rrf_k: 60, keep: 40 }
  >     score: { relevance: 0.35, rating: 0.25, role_fit: 0.15, duration_fit: 0.10, unused_gem: 0.10, angle_available: 0.05, reuse_penalty: 0.3 }
  >     duration_fit_s: { hook: [2, 7], promise: [3, 8], payoff: [8, 25], closing: [2, 8] }
  >     llm_rerank: { enabled: true, input_top: 30, output: "≤ 8 (1 per beat + ≤ 2 alternatives)", timeout_s: 30, fallback: score }
  >   facts:  { verified_cap: 10, prefer: primary, always_include: [unverified, conflicting] }
  >   findings: { status: supported, sort_by: effect_lower_bound, cap: 5 }
  >   playbook: { match: planned_steps, always_include: critical, cap: 8 }
  > ```
  > Each `reel_prompt` stores a `context_manifest`: included IDs with score and reason, plus the top 5 excluded candidates per category. Golden tests mock the LLM rerank.
- **Why:** Embeddings don't understand beats or roles; an LLM alone isn't reproducible. The manifest is what makes the learning loop and debugging possible.
- **Priority:** before phase 9

#### P6. MCP tool surface: toolsets, naming, annotations, examples, missing tools
- **Type:** change
- **Section:** §17.2
- **Proposal:** Adopt toolsets, `<group>_<verb>` names, MCP annotations, concise/full responses with pagination, instructive errors, examples in the listed descriptions, and add the four missing tools.
- **Suggested spec text:** Add at the top of §17.2:
  > **Conventions.** Tool names are `<group>_<verb>[_<noun>]` (e.g. `moments_search`, `reel_create_version`, `critique_run`). Each tool declares MCP annotations (`readOnlyHint`, `destructiveHint`, `idempotentHint`, `openWorldHint`). Descriptions state *when to use / when not (name the alternative) / what it returns*, ≤ 80 words; `moments_search`, `reel_create_version`, `review_log_feedback`, `render_motion`, `generate_map`, `frame_sheet`, `reel_update`, `insights_get`, `playbook_add_item` and `moments_exclude` include a complete example input. List tools take `limit` (default 10), `cursor` and `detail: concise | full`. Errors state the next valid action.
  >
  > **Toolsets** (selected with `/mcp?toolset=`): `editor` (default; moments, transcript, reel context, facts check, captions, graphics, music shortlist, versions, critique, pickups, open items, handover, approval status, playbook read), `analyst` (metrics, retention, insights, explain_drop, recommend, experiments, findings), `admin` (project creation, asset registration, fact editing, playbook curation).
  >
  > **Added tools**
  > - `reel_get_context(reel, section?)` → the same context as the reel prompt and its `hub://` resources, for clients that don't fetch resources
  > - `pickup_add(reel, text, purpose, placement_hint?)` → stored as type `pickup`, shown to Katarina in "pickups to record"
  > - `open_item_add(reel, text, kind: fact | speaker | pickup | other)`
  > - `handover_submit(reel, version, notes, open_items[], pickups[], sources[], skipped_critique_items[])`
- **Why:** About 45 flat tools with overlapping names (`lint_script`, `lint_draft`, `check_fact`, `fix_captions`) invite wrong picks and cost 7–15k tokens of schemas per turn. The guardrail "pickups stored separately" has no tool to store pickups through.
- **Priority:** must-have before build (phase 2 builds the MCP surface)

#### P7. Guardrails as code, including human-only signals
- **Type:** change
- **Section:** §17.3
- **Proposal:** Turn the checkable rules into server-side validation, and mark which signals only a human may produce.
- **Suggested spec text:** Append to §17.3:
  > - **No MCP tool can approve.** Approvals are created only from the UI session; `approval_request` only notifies.
  > - **Real-words check:** `reel_create_version` compares each caption item, and any quoted or speaker-labelled on-screen text, with the transcript words under it (normalised, glossary and correction memory applied). WER > 10 % creates a blocking `open_item`.
  > - **Fact lint on save:** `reel_create_version` runs `lint_script` on captions and on-screen text; unsupported claims become blocking open items.
  > - **Do-not-use:** cut items overlapping a do-not-use range are rejected; access requires `include_excluded: true` and a logged `reason`.
  > - **Transcripts are read-only to agents.** Proposed lines go only through `pickup_add`.
  > - **Human-only signals:** every rating stores `rated_by_kind: human | agent`. Only human ratings feed critic calibration (§16.4), the taste profile (§15.4) and finding promotion (§13.1).
  > - `approval_request` warns when the version has no critique.
- **Why:** Rules that can be checked shouldn't depend on the prompt being followed. Agent self-ratings would silently corrupt calibration and taste data.
- **Priority:** must-have before build

#### P8. Critic evaluation set and trust thresholds
- **Type:** addition
- **Section:** §16.4 (new §16.6), §24.2
- **Proposal:** Define the golden set (Giro_00 history + 24 injected-defect variants + 4 clean controls), metrics and thresholds that must be met before the critique is shown in the review screen.
- **Suggested spec text:** Add §16.6:
  > ### 16.6 Evaluation before trust
  > ```yaml
  > critic_eval:
  >   golden_set:
  >     history: giro00 v1–v5 with producer feedback items as labels
  >     injected:  # 12 defect types × 2 placements on approved reels
  >       [frame1_half_out, static_8s, caption_line_missing, glossary_misspelling, missing_diacritics,
  >        text_in_face_band, card_hold_6s, music_0.6_under_speech, dead_air_1.2s,
  >        unverified_claim_on_screen, joke_cut_before_punchline, closing_mismatch_next_reel]
  >     clean_controls: 4
  >   gates:
  >     recall_major_plus: ">= 0.80 overall, >= 0.60 per area"
  >     false_major_per_clean_reel: "<= 1.0"
  >     stability_3_runs: { major_item_jaccard: ">= 0.7", area_score_spread: "<= 1" }
  >   live:
  >     producer_agreement: ">= 0.70 (human ratings only)"
  >     coverage_of_producer_items: ">= 0.50 by reel 10 (same area, |Δt| <= 2 s)"
  >     retention_hit_rate: "report vs random windows; act only after >= 15 posted reels with curves"
  >   runs: on demand and before any model / rubric / sampling change; normal test suite uses recorded responses
  > ```
- **Why:** Without a labelled set, "≥ 70 % agreement" can only be measured after the critic has already shaped drafts. Defect injection gives labelled data on day 1 from one reel.
- **Priority:** before phase 10

#### P9. Critique output: anchored 1–5 scores, computed overall, validated evidence
- **Type:** change
- **Section:** §16.3
- **Proposal:** Replace the free `7.5/10` scores with 1–5 per area anchored to rubric descriptions, compute `overall` in code from the items, require evidence that points to supplied frames or timeline rows, and add a pairwise "better than previous version?" judgement.
- **Suggested spec text:** In the §16.3 YAML, replace `overall: 7.5/10` and `scores:` with:
  > ```yaml
  >   scores: { hook: 4, story: 4, pacing: 3, captions: 5, design: 4, graphics: 4, sound: 3, facts: 5, platform: 5, continuity: 4 }  # 1–5, anchored in rubric vN
  >   overall: { blockers: 0, majors: 1, minors: 3, ready_for_producer: true }   # computed in code, not by the model
  >   vs_previous: { version: v4, verdict: better, reason: "hook now shows the lollipop on frame 1" }
  >   critic_version: { model_id: "<pinned id>", rubric: 1.0, sampling: 1.0 }
  > ```
  Add below the YAML:
  > - Each rubric area defines anchors for scores 1, 3 and 5.
  > - Every item's `evidence` must reference frames or audio-timeline rows that were supplied (`frame@t`, `audio@t`, `rule:<id>`). Items with invalid evidence, or `at_s` outside the runtime, are dropped and counted as `invalid_items` in the run log.
  > - `ready_for_producer` = no blockers and ≤ 2 majors.
- **Why:** LLM absolute scores on a 10-point scale are poorly calibrated and drift between runs. Pairwise comparison between versions is far more reliable. The current scores also omit graphics, platform and continuity, although §16.2 checks them. Validating evidence stops hallucinated timestamps.
- **Priority:** before phase 10

#### P10. Learning loop: process metrics, shrinkage, decay, offline replay
- **Type:** change
- **Section:** §13.1, §13.3, §6.4 (Prompt history)
- **Proposal:** Separate "features → performance" findings from "template → process" evaluation, use shrinkage and lower bounds, decay findings over time, auto-propose rules from recurring producer feedback, and replay offline before switching templates.
- **Suggested spec text:** Add §13.4:
  > ### 13.4 Improving prompts and the critic
  > - **Template and critic quality is measured by process metrics:** producer feedback items per version by area, feedback rounds, critique blockers at handover, time to first draft, share of inline context used (from `context_manifest`). Instagram metrics are not compared across template versions.
  > - **Findings:** effects normalised against the trailing 30-day median and shrunk towards 0 (empirical Bayes); `supported` requires n ≥ 5 per arm and an 80 % interval excluding 0. Prompts quote the lower bound. Findings are re-tested after 30 days or 10 reels and `retired` if they no longer hold.
  > - **Recurring feedback:** a feedback category raised in ≥ 3 reels creates a proposed acceptance check or template rule for the producer to approve.
  > - **Template changes:** before switching templates, regenerate prompts for 3 past slots, produce cut-list-only drafts, run the critic, and switch only if blockers and majors don't increase. Changes go through a branch and snapshot update (D10).
- **Why:** 24 reels can't support template-vs-views comparisons, but producer feedback gives 10–30 labelled signals per reel. Lower bounds and decay prevent one lucky reel from becoming a rule.
- **Priority:** before phase 6

#### P11. Optional native audio-video second opinion
- **Type:** question
- **Section:** §16.1
- **Proposal:** Decide whether to allow an optional, off-by-default second critic pass with a model that takes real video and audio (e.g. Gemini, 1 fps default with configurable frame rate, audio included). This would add genuine sound-on judgement: delivery, music against speech.
- **Suggested spec text:** Add to §16.1:
  > - **Optional (off by default):** `critique.native_av: { enabled: false, provider: gemini, fps: 2 }` sends the **preview render only** (never raw footage or do-not-use ranges) for a sound-on pass. Its items are tagged `critic: native_av` and calibrated separately.
- **Why:** Claude can't hear, so the sound-on pass is limited to measurements. A native audio-video model is the only way to get audio judgement from AI. However, it adds a second cloud processor of footage, so the owner should decide in light of D4's "runs locally". Gemini details were checked 2026-11-12 at [aistudio.google.com/docs/video-understanding](https://aistudio.google.com/docs/video-understanding).
- **Priority:** later

**Sign-off:** approve with changes
