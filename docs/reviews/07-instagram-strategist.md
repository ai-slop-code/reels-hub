# Review packet 07: Instagram growth strategist

**Priority:** before phases 5–6 (analytics, learning) and 10 (critique)
**Time needed:** ~1.5 h
**Decisions already made:** see [README](README.md#decisions-already-made-please-dont-reopen). D5: comments imported as available.

## Why you
The Hub will judge reels (critique) and learn from performance (analytics). Both need to measure what actually drives reach and loyalty on Instagram, not what's easy to count.

## Read
- [§12 Performance analytics](../spec/REELS_HUB_SPEC.md#12-module-h-performance-analytics)
- [§13 Learning loop and experiments](../spec/REELS_HUB_SPEC.md#13-module-i-learning-loop-and-experiments)
- [§16 AI critique](../spec/REELS_HUB_SPEC.md#16-module-l-ai-critique), especially 16.2
- [§6.2 Reels inside a project](../spec/REELS_HUB_SPEC.md#6-module-b-projects-reels-and-the-reel-prompt) (daily cadence, continuity)
- [`../reels/giro00-intro/instagram_caption.txt`](../reference/giro00/instagram_caption.txt) (Giro_00 caption)

## Questions
1. **Metrics that matter** for an informational daily series: views, reach, hold rate, saves, shares, follows. Which should drive decisions, and with what weight?
2. **Hook:** what do you look for in the first 1–3 s? Add concrete rules to the critique rubric.
3. **Runtime:** our intro is 50.9 s. What's your guidance for a 24-day series (teaser vs. stage episodes)?
4. **Series mechanics:** "tomorrow" hooks, numbering (Day 1/24), pinned reels, highlights, carousels. What helps people follow a daily series?
5. **Captions and hashtags:** review the Giro_00 caption. What should the Hub generate and check for each reel?
6. **Posting:** time slots, Trial Reels, collabs (e.g. with Slovak cycling accounts), cross-posting to Facebook.
7. **Account type:** Creator vs. Business, given commercial music (§15.6) and API access for insights.
8. **Comments:** what's worth mining (questions, stage requests, sentiment), and how should insights flow into the next reel?

## Your input

> Reviewed against spec v0.5. This packet was written for v0.4. The header's "D5: comments imported" is out of date: R49 means no comments are imported, so Q8 is answered for v0.5.
>
> **Checked on 2026-11-12 (sources linked):**
> - [Meta media insights reference](https://developers.facebook.com/docs/instagram-platform/reference/instagram-media/insights) (API v27.0)
> - [Instagram API with Instagram Login overview](https://developers.facebook.com/docs/instagram-platform/instagram-api-with-instagram-login)
> - [Trial reels help page](https://help.instagram.com/1013292530224018/)
> - [Licensed music library help page](https://help.instagram.com/402084904469945/)
> - The 5-hashtag limit ([Social Media Today](https://www.socialmediatoday.com/news/instagram-implements-new-limits-on-hashtag-use/808309/))
> - Mosseri's ranking signals, through secondary write-ups ([Buffer, Oct 2026](https://buffer.com/resources/instagram-algorithms/), [ZoomSphere](https://www.zoomsphere.com/blog/instagram-algorithm-2026-what-actually-gets-reach))
> - Linked Reels removed on 28 Oct 2026 and the limited "Series" test, through a secondary source ([CreatorFlow, Oct 2026](https://creatorflow.so/blog/instagram-series-feature/))
>
> Anything marked **unverified** is my experience, not something I checked today.

### Summary
The analytics and learning design is sound: within-project comparisons, uncertainty ranges and a minimum N are the right instincts. But it measures some things the API doesn't provide and misses the one first-3-seconds metric it does provide:
- Follows aren't available for Reels through the API.
- `reels_skip_rate` is available, and it's the cleanest hook metric we have.

The biggest gap for December is the Instagram caption. The reel has caption and hashtag fields, but no step of the flow writes or checks them. The Giro_00 caption has 8 hashtags, which is over Instagram's current limit of 5 per post.

For a daily series, decisions should rest on shares per reach, hold, skip rate and saves. Views and reach are outcomes, not levers.

For the deferred decision **R32**, I recommend keeping 05's `ending_type`, narrowed to the text on the existing closing card (a question that teases tomorrow vs. a statement). The spoken sign-off stays in every reel. The primary metric should be follows per 1k reach, not share rate. Stage episodes should also drop the "who we are" beat and aim for 35–50 s.

### Answers

#### Q1. Metrics that matter
Instagram ranks Reels mainly on watch time, likes per reach and sends per reach. Sends matter most for reaching non-followers, and that's where most Reels reach comes from (Mosseri, via Buffer and ZoomSphere above). An informational daily series also needs **saves** (people keep the practical tips) and **follows** (people come back tomorrow). Each metric drives a different decision:

| Metric (per 1k reach unless noted) | Source | Drives which decision | Weight in the reel score |
|---|---|---|---|
| Shares ("sends") | API `shares` | Topic and angle: is this worth sending to a friend? | 30 % |
| Hold rate = avg watch time ÷ runtime | API `ig_reels_avg_watch_time` | Pacing, length, middle section | 25 % |
| Skip rate (first 3 s) | API `reels_skip_rate` | Hook and first frame | 15 % (inverted) |
| Saves | API `saved` | Practical value (how to get there, dates, places) | 15 % |
| Likes | API `likes` | Resonance with existing followers | 15 % |
| Follows | **Manual** (in-app insights; the API has no `follows` for Reels) | Series loyalty, ending type | Separate readout, not in the score |
| Views, reach, non-follower share | API | Outcome. Report it, but don't optimize edits for it | – |
| Comments | API count | Inflated by the caption CTA, so a weak signal on its own | – |

- Compare each metric with the median of the **previous 5 episodes of the same project**, not a 30-day account median. A series starting from a small account has an unstable account baseline, and audience behavior changes inside a series.
- Read decision metrics at **72 h**. The 24 h snapshot is an early warning only, because shares and saves keep accumulating.

#### Q2. Hook: the first 1–3 s
Concrete rules for the critique rubric. Each one can be checked on the render or the transcript:
1. **Frame 1 is content.** Katarina is fully in frame (or the prop she's talking about is). No fade-in, title card, logo or black frame. The first frame is also the default cover, so it must work as a still.
2. **First spoken word by 0.3 s** (`time_to_first_word_s ≤ 0.3`). No breath or "Ahojte" first.
3. **The first sentence states a specific curiosity in ≤ 8 words / ≤ 3 s** and names something concrete from this stage: a place, a climb or a number. "Prečo je toto lízatko ružové?" passes. "Dnes vám povieme o 5. etape" fails.
4. **No series housekeeping before the hook.** "Who we are", day numbers or greetings come after the hook line, or not at all (see Q3). A small "Etapa N/21" label on screen is fine.
5. **Readable muted by 0.5 s.** The first caption is on screen by 0.5 s, inside the caption safe zone. Any extra hook text is ≤ 6 words.
6. **Visual change by 3–4 s** (cut, punch-in, DJI cutaway or map pop), so the second beat doesn't look like a static talking head.
7. **The question isn't answered before about 50 % of runtime.** The payoff closes the gap; the hook mustn't give it away.
8. **Calibration:** the critic's hook score is compared with the reel's `reels_skip_rate` (P10, §16.4).

DESIGN_LANGUAGE §10 currently says "hook 0–6 s". The hook line can run to 6 s, but the curiosity must be clear by 3 s (P4).

#### Q3. Runtime
- **Intro (Giro_00, 50.9 s):** fine. A series trailer earns the extra time with the "who we are" beat and the DJI reveal.
- **Stage episodes (Days 2–22):** **35–50 s target, 60 s hard cap.** Use one idea per stage: the one story, place or "how to get there" angle. Leave the full stage profile out.
- **Drop the "who" beat after Day 1.** Most viewers of a stage episode arrive from recommendations, and a repeated introduction is where they swipe. Ľuboš stays as a cutaway reaction or in the sign-off, not as an intro.
- The 3.5 s silent card plus about 3 s of sign-off leaves a 6–7 s tail. That's acceptable only because the card carries the experiment (R32). Don't add more tail.
- **Finale (Days 23–24):** a recap can run 45–75 s. It's still well under the 3-minute limit beyond which Reels aren't recommended to non-followers (help-center quote, via secondary sources).
- One data point, not a law: Socialinsider's 2026 benchmark (about 140k business Reels, via moonb.io) puts 45–60 s highest for engagement. For talking-head information content my experience is 30–45 s (**unverified**). Hence a 35–50 s band, with runtime **not** experimented on in December.

#### Q4. Series mechanics
- **Every episode must stand alone.** Most viewers meet the series at episode N, not episode 1.
- **Numbering:** use the stage, not the advent day. "Etapa 5/21" on the cover and as a small label; "deň 6/24" only in the caption. Two numbers on screen confuse viewers.
- **Tomorrow hook:**
  - Always in the caption's last line ("Zajtra: 6. etapa.").
  - On the closing card per the R32 experiment.
  - The continuity check in §6.2 already guards that the next reel delivers.
- **Pinned reels (up to 3):**
  - Giro_00 (the trailer) pinned all December.
  - The latest episode.
  - The best-performing episode, swapped weekly.
- **Stories and highlight:** after each post, share the reel to Stories ("Nová etapa je vonku 👇") and add it to a "Giro 2027" highlight, so the highlight becomes the episode list in order. Stories reach followers the feed missed. It's manual and takes 1 minute.
- **Native series features:** Linked Reels was removed on 28 Oct 2026. Instagram "Series" is a limited test since June 2026. Use it if it appears on the account, but don't depend on it (secondary source above).
- **Carousels (optional):** at most one per week, e.g. Sunday "Týždeň 1: etapy 1–5", built only from map graphics already made (the graphics overview, §20, makes this cheap). Carousels earn saves. Skip them if time is short; they aren't a Hub feature.
- **Same posting time every day** (Q6). The habit matters more than the ideal hour.

#### Q5. Captions and hashtags
**Giro_00 caption review:**
- ✅ The first line "Prečo je lízatko ružové? 🍭" mirrors the spoken hook. That's right.
- ✅ The series promise is clear ("24 dní … všetkých 21 etáp").
- ✅ It has a tomorrow line ("Zajtra začíname 1. etapou.").
- ✅ The humor ("spotení chlapi") fits the voice.
- ❌ **8 hashtags.** Instagram has allowed at most 5 per post or Reel since December 2025 (verified). Cut to 5: `#giroditalia #giro2027 #cyklistika #adventnykalendar #taliansko`. Put Trieste in the **location tag** instead of `#trieste`; `#slovensko` adds nothing. Hashtags help search, not reach (Mosseri).
- ⚠️ **The CTA can't be answered on Day 1.** Viewers don't know the stages yet, so "Ktorú etapu by ste chceli vidieť naživo?" will get few replies. Use a send CTA on Day 1 ("Pošlite to niekomu, s kým by ste išli v máji na Giro 🚴"). Keep the stage question for Day 22, where the answers can pick Day 23's topic.

**What the Hub should generate and check for each reel** (P1). The editing agent drafts the caption as part of the deliverables, and the rules below run as a lint:
- First line ≤ 60 characters, the hook, with no hashtag or @. The exact truncation point in the Reels viewer varies (**unverified**).
- Facts in the caption need fact IDs, the same as on-screen claims.
- Exactly one CTA, chosen by topic:
  - story → send
  - how to get there → save
  - Day 22 → comment vote
- Tomorrow line, 3–5 hashtags (2 fixed plus 1–3 topical), location tag, Slovak glossary forms and diacritics, no "oficiálny".
- Collaborators tagged; paid-partnership label when a commercial flag is set (R51).

#### Q6. Posting
- **Time slot:** one fixed slot every day of the series. Default **19:00 Europe/Bratislava**, adjusted once before 1 Dec to the account's top hour in the in-app "Most active times". The 19:00 default is a generic evening peak for Slovak leisure audiences (**unverified**).
  - Never move the slot during the series. A moving time ruins comparisons, so §13.2 shouldn't list posting time as an experiment variable inside a daily series (P3).
  - In-app scheduling is fine (§19.4).
- **Trial Reels:**
  - Requires a public professional account with ≥ 200 followers (verified).
  - Trial reels go to non-followers first and **don't appear to followers or on the profile** unless shared.
  - That's wrong for daily episodes, because followers must get the episode on its day. Trial reels may also get limited reach if Instagram detects the same content was shared before.
  - In December, use them only for extra standalone material (e.g. the unused tongue-twister bumper). After December, use them for hook tests on new content (P9).
- **Collabs with Slovak cycling accounts:**
  - Worth 2–4 times in the series, on episodes where the partner adds something real (e.g. they've ridden that climb or been to that finish).
  - A co-authored post goes to both audiences; reach and metrics are combined, so mark it `collab: true` (already a confounder in §12.5).
  - The current co-author limit is **unverified**.
  - There's a real conflict with the commercial flags: see P6.
- **Cross-posting to Facebook:**
  - Turn on the Facebook share or recommend toggle when posting. The tier-1 license record already allows `[instagram, facebook]`, and it's free reach.
  - The API reports Facebook plays separately (`facebook_views`, `crossposted_views`; verified). Keep them out of the Instagram `views` comparisons.
  - YouTube and TikTok stay out (R45 deferred).

#### Q7. Account type
**Creator.**
- Business accounts are restricted to a much smaller commercial-safe catalog (Meta Sound Collection) and lose most of the licensed library. That would kill "Dolce Vita" (verified, Instagram help).
- Creator accounts are professional accounts and fully supported by the Instagram API with Instagram Login, including media insights, without a linked Facebook Page (verified).
- Trial reels have the same 200-follower bar for both types.
- If brand deals come later, handle them per reel with the commercial flags and tier-2/3 music. Don't switch the account type.

#### Q8. Comments
v0.5 doesn't import comments (R49); only the comment **count** is stored. That's acceptable. Comments are the most CTA-inflated signal and the least useful for ranking. What's worth keeping needs no import:
- **Stage requests and questions:** Ľuboš writes 2–3 notable ones into the reel's existing **manual notes** (§12.1), e.g. "3× asked about tickets for the Zoncolan stage".
- **Day 22 vote:** the answers to the Day 22 question pick Day 23's topic. One manual tally.
- **Factual corrections from viewers:** log them as feedback with `after_post` (already a §26 metric).

These notes reach the next prompt through the existing "learned from previous reels" path (§6.3). No proposal, because R49 stands.

### Proposals

#### P1. Instagram caption as an editing deliverable, with caption rules
- **Type:** addition
- **Section:** §6.4 (Workflow, Acceptance checks, Deliverables), §11.4, §8
- **Proposal:** The editing agent drafts the Instagram caption, hashtags and location tag and records them in `editors_notes.md`. `lint_script` also checks caption rules. Without this, nothing in the flow fills the reel's caption fields, and the Giro_00 caption would be blocked today (8 hashtags, limit 5).
- **Suggested spec text:**
  - §6.4 Workflow step 6, old: "6. Write `editors_notes.md` for this reel (`update_editors_notes`, template §11.4), including the checklist and open items. Then `request_approval`." → new: "6. Draft the Instagram caption (rules in §8.1) and run `lint_script` on it. Write `editors_notes.md` for this reel (`update_editors_notes`, template §11.4), including the caption, the checklist and open items. Then `request_approval`."
  - §6.4 Deliverables, old: "Edits project name, version in the Hub, completed editors_notes.md (with checklist, open items and suggested pickups)." → new: "Edits project name, version in the Hub, completed editors_notes.md (with Instagram caption, checklist, open items and suggested pickups)."
  - §11.4 template, add after "## Captions":
    ```markdown
    ## Instagram caption
    {caption text, Slovak} · hashtags: {3–5} · location: {town} · CTA: {send | save | comment} · collaborators: {handles or none} · fact IDs: {…}
    ```
  - New §8.1:
    ```yaml
    instagram_caption_rules:
      first_line: "the hook, ≤ 60 characters, matches the spoken hook's topic; no hashtag or @"
      facts: "every number, date or place claim has a fact ID listed in editors_notes.md"
      tomorrow_line: "last line 'Zajtra: {n+1}. etapa.' (matches the next reel, §6.2 continuity check)"
      cta: "exactly one: send (story), save (how to get there), comment (Day 22 vote only)"
      hashtags: { min: 3, max: 5, fixed: ["#giroditalia", "#giro2027"] }   # Instagram limit: 5 per post
      location_tag: "stage start town"
      length_chars: [250, 700]
      language: "Slovak, glossary forms, diacritics checked; no 'oficiálny'"
      disclosure: "paid-partnership label if any commercial flag is set (§6.2)"
    ```
    plus one sentence: "`lint_script(text, kind: caption)` applies these rules."
- **Why:** The caption is part of what the algorithm and viewers see. Hashtags over 5 are blocked (Social Media Today, verified 2026-11-12). Claims in the caption carry the same factual risk as on-screen text (§26 counts corrections).
- **Priority:** before phase 9

#### P2. Correct the metric map to what the API provides
- **Type:** change
- **Section:** §12.1, §12.3
- **Proposal:** Use the API's `reels_skip_rate` for the hook. Add `reposts` and `facebook_views`. State that follows aren't in the API for Reels and take them manually. Fix the rewatch formula.
- **Suggested spec text:**
  - §12.1 first row, "What" column, old: "Per-Reel: views, reach, likes, comments, shares, saves, total interactions, average watch time, total watch time; follows from the post where available" → new: "Per-Reel (API v27.0, product type `REELS`): `views`, `reach`, `likes`, `comments`, `shares`, `saved`, `reposts`, `total_interactions`, `ig_reels_avg_watch_time`, `ig_reels_video_view_total_time`, `reels_skip_rate`; `facebook_views` when shared to Facebook. **Follows and profile visits are not available for Reels via the API**: the producer enters follows from in-app insights at 7 d, together with the retention curve."
  - §12.3, old: "- **Hook rate:** share of viewers still watching at 3 s (from the retention curve when available)." → new: "- **Skip rate:** `reels_skip_rate` from the API (share of initial views that skipped in the first 3 s); hook rate = 1 − skip rate. The manual retention curve is used to locate drops after 3 s."
  - §12.3, old: "- **Rewatch indicator:** total watch time ÷ (views × runtime), above 1 means rewatches." → new: "- **Rewatch indicator:** total watch time ÷ (reach × runtime), above 1 means rewatches (`views` already counts replays)."
  - §12.3, add: "- **Follow conversion** (manual, 7 d) is a series-loyalty readout; Facebook plays are reported separately and never mixed into Instagram views."
- **Why:** Meta's media-insights reference (v27.0, checked 2026-11-12) lists `follows` and `profile_visits` for FEED and STORY only, and `reels_skip_rate` for REELS. Building the importer on the current text would leave the follow field always empty and ignore the one first-3-seconds metric that exists.
- **Priority:** must-have before phase 5

#### P3. R32: the one series experiment (ending type, on the closing card)
- **Type:** change (resolves deferred R32)
- **Section:** §13.2
- **Proposal:** Keep 05's variable `ending_type`, narrowed to the **text of the existing silent closing card**:
  - The spoken sign-off stays in every reel. It's a design-language beat, and the host's natural "Čaute" isn't something to switch off.
  - Primary metric: follows per 1k reach, not share rate. A tease card is meant to bring people back, not to get the reel forwarded.
  - Alternate by stage number.
  - Pre-register that an inconclusive result keeps the producer's default.
  - Remove posting time from the list of experiment variables.
- **Suggested spec text:** replace §13.2's first bullet "**One change at a time** per reel (hook type, runtime band, map length, ending type, posting time)." with:
  > - **One pre-registered experiment per series**, decided before the first post, set on each reel when it's created (`log_experiment`) and shown in the prompt's "This reel" section. Everything else follows the design language. Posting time is never an experiment variable in a daily series; it stays fixed.
  > ```yaml
  > experiment:
  >   id: exp_giro2027_ending
  >   variable: ending_type
  >   variants:
  >     tease: "closing card asks about the next stage; the answer is a verified fact (fact ID) and is not given; ≤ 8 words, e.g. 'Zajtra: celá etapa mimo Talianska. Kde?'"
  >     statement: "closing card states today's takeaway, e.g. 'Štart v Terste, cieľ v Ríme.'"
  >   constant: [card 3.5 s with music lift, spoken sign-off, caption last line 'Zajtra: {n+1}. etapa.', posting time, runtime band]
  >   assignment: "odd stage numbers → tease, even → statement (Stages 1–21: 11 vs 10); Day 1 and Days 23–24 are not in the experiment"
  >   primary_metric: follows_per_1k_reach_7d          # manual, from in-app insights (§12.1)
  >   secondary: [comments_per_1k_reach_72h, hold_rate_72h]
  >   guard: shares_per_1k_reach_72h                    # flag if the tease arm is more than 20 % lower
  >   decision_rule: "make 'tease' the default only if the primary metric is higher and its uncertainty range excludes 0 (§12.5); otherwise keep 'statement'"
  >   deviation: "if the next stage's fact isn't verified, the producer switches the reel to 'statement' and marks it deviated; deviated reels are left out of the analysis"
  > ```
- **Why:**
  - **Cheapest possible test.** The card is already in every episode, it's one text box, it needs no extra shooting (R6), and runtime and structure stay identical.
  - **Genuinely uncertain.** In Giro_00 round 1 the producer removed the on-screen tease, partly because the Slovenia crossing was unconfirmed. Common practice says cliffhangers build return viewing. Settling that is exactly what one experiment is for.
  - **The metric fits the variable.** A tease is about coming back, so follows is the closest measurable proxy. The API has no per-viewer return data, and share rate (05's proposal) would mostly measure topic noise.
  - **Why not the hook.** The hook (skip rate) is better measured, but "cold open vs. greeting" isn't uncertain: Giro_00 already uses a cold open. Testing it would knowingly spend reach on 10 reels.
  - **Balance.** Odd/even assignment spreads mountain, sprint and time-trial stages across both arms.
  - **Honest limit.** With about 10 per arm only large effects (roughly ≥ 40 %) will show, so the decision rule protects the owner's taste when the result is inconclusive.
  - **Needs owner confirmation:** whether the round-1 removal of the tease was taste or only fact caution. If it was taste and he won't run teases on 11 reels, fall back to no December experiment rather than a different one.
- **Priority:** must-have before build (decision only, before 1 Dec)

#### P4. Stage-episode structure and runtime
- **Type:** change
- **Section:** DESIGN_LANGUAGE §10 (and the default `target_runtime` in §6.2)
- **Proposal:**
  - The curiosity must land by 3 s.
  - The "who" beat is for the intro only.
  - Runtime target per episode type.
- **Suggested spec text:** DESIGN_LANGUAGE §10, replace the `structure` block with:
  ```yaml
  structure:
    - beat: hook          # curiosity stated by 3 s (line may run to 6 s); frame 1 is content; first word ≤ 0.3 s; captioned
    - beat: who           # Day 1 intro only; stage episodes: none (Ľuboš appears as a cutaway reaction or in the sign-off)
    - beat: promise       # what this episode gives, by ~8 s in stage episodes; one map or graphic max
    - beat: payoff        # one idea: the stage story / place / how to get there
    - beat: card          # silent 3.5 s map card, music up; text per the series experiment (spec §13.2)
    - beat: sign_off      # natural "Čaute" exchange; keep Ľuboš's off-camera reply; ≤ 3 s
  target_runtime_s:
    intro: 45–60
    stage: 35–50          # hard cap 60
    finale: 45–75
  ```
  Add to §6.2 Fields: "Target runtime defaults from DESIGN_LANGUAGE §10 by slot type (intro, stage, finale)."
- **Why:** Viewers of stage episodes mostly arrive mid-series from recommendations. A repeated self-introduction and a hook that only lands at 6 s are the two most common swipe points. Shorter stage episodes also help the ≤ 60 min hands-on target (§26).
- **Priority:** before phase 9

#### P5. Posting checklist and a fixed posting time
- **Type:** addition
- **Section:** §19.4, §6.1, §11.4
- **Proposal:**
  - Add a fixed `posting_time` to the project.
  - Add a short, manual posting checklist in `editors_notes.md`. No code beyond one field and template text.
- **Suggested spec text:**
  - §6.1 project YAML, add: `posting_time: "19:00"   # Europe/Bratislava; set once from in-app "Most active times" before the series, never moved during it`
  - §19.4 step 1, old: "1. Ľuboš posts in Instagram (manual; in-app scheduling allowed), then records it with `link_publication` (or in the UI)." → new: "1. Ľuboš posts in Instagram at the project's `posting_time` (manual; in-app scheduling allowed), following the posting checklist in `editors_notes.md`, then records it with `link_publication` (or in the UI)."
  - §11.4 template, add:
    ```markdown
    ## Posting checklist
    - [ ] Posted at {project.posting_time}; Trial is off (series episodes)
    - [ ] Cover: Katarina + "Etapa {n}/21" readable in the profile-grid crop
    - [ ] Caption per §8.1; ≤ 5 hashtags; location tag {town}
    - [ ] Share to Facebook on (license record allows Facebook)
    - [ ] Collaborators invited: {handles or none} (sets `collab`, a confounder §12.5)
    - [ ] Shared to Stories and added to the "Giro 2027" highlight; pins: Giro_00 + latest + best
    ```
- **Why:** A habit-forming daily series lives on a fixed time and on being findable (cover, highlight, pins). These are the cheapest growth levers and are easy to forget at 19:00. Flags like collab and Facebook sharing are also confounders the analysis needs (§12.5).
- **Priority:** before phase 5

#### P6. Unpaid creator collabs shouldn't trip the commercial flag
- **Type:** risk
- **Section:** §6.2 (Commercial flags), §15.6
- **Proposal:** Clarify that "collab partners" means a brand or commercial partner. An unpaid co-authored post with another creator (e.g. a Slovak cycling account) isn't a commercial flag. Legal (packet 04) should confirm.
- **Suggested spec text:** §6.2, old: "paid partnership, gifted or hosted (free product, travel, tickets), affiliate links, boost planned, collab partners." → new: "paid partnership, gifted or hosted (free product, travel, tickets), affiliate links, boost planned, brand collab partners. An unpaid co-authored post with another creator is not a commercial flag; it's recorded as `collab: true` in the features (§12.2) and the posting checklist (§11.4)."
- **Why:** As written (R43), any collab blocks tier-1 music. A no-money collab with a cycling club would then force dropping the signature track "Dolce Vita" mid-series, which breaks recognition. That would make collabs, the best low-cost growth lever for a niche Slovak series, practically unusable.
- **Priority:** before phase 9 (rule text only)

#### P7. A reel score with explicit weights and a series baseline
- **Type:** change
- **Section:** §12.3 ("Normalized score")
- **Proposal:**
  - One documented score for the dashboard and `recommend`, weighted toward the signals Instagram ranks on.
  - Compared with the previous 5 episodes of the same project.
  - Decisions still use the single metric tied to the beat.
- **Suggested spec text:** §12.3, old: "- **Normalized score:** each metric compared to the account's trailing 30-day median, so growth over time doesn't skew comparisons." → new:
  > - **Reel score (72 h):** each metric as a ratio to the median of the previous 5 posted reels of the same project (Days 1–5: the account's last 10 reels), capped at 3×, then weighted:
  > ```yaml
  > reel_score:
  >   window: 72h
  >   weights: { shares_per_1k_reach: 0.30, hold_rate: 0.25, skip_rate_inverse: 0.15, saves_per_1k_reach: 0.15, likes_per_1k_reach: 0.15 }
  >   readouts_not_scored: [reach, views, non_follower_share, comments, follows_per_1k_reach_7d]
  > ```
  > Decisions use the metric tied to the beat: hook → skip rate, middle → retention drops and hold rate, ending → follows, topic → shares and saves.
- **Why:** Mosseri names watch time, likes per reach and sends per reach as the top signals; sends matter most for non-follower reach. Saves carry the informational value. A 30-day account median is unstable for a small account entering its first series. Reach is the outcome, so scoring it rewards luck rather than edit choices.
- **Priority:** before phase 6

#### P8. Features the analysis needs
- **Type:** addition
- **Section:** §12.2
- **Proposal:** Add the distribution and series features that confound or explain performance. Most come from the posting checklist (P5) and the caption (P1), with no manual tagging.
- **Suggested spec text:** add to the §12.2 `features` YAML:
  ```yaml
    slot_type: stage                     # intro | stage | finale
    experiment: { id: exp_giro2027_ending, variant: tease }
    cta_type: send                       # send | save | comment | follow | none
    hook_text_on_screen: false
    who_beat: false
    cover: { label: "Etapa 1/21", from_frame_ms: 0 }
    location_tag: Trieste
    collab: false
    shared_to_facebook: true
    trial: false
  ```
- **Why:** Without these, a collab or Facebook-boosted reel looks like a better edit, and the experiment can't be analyzed per variant.
- **Priority:** before phase 6

#### P9. Trial Reels: not for December episodes
- **Type:** change
- **Section:** §13.2
- **Proposal:** Use Trial Reels for hook tests only after December, and never for series episodes.
- **Suggested spec text:** §13.2, old: "- Instagram's **Trial Reels** (shown to non-followers first), where available, are a cheaper way to test hooks; track them as variants." → new: "- Instagram's **Trial Reels** (public professional account with ≥ 200 followers) are shown to non-followers only and stay off the profile and followers' feeds unless shared. Never use them for series episodes, which followers must get on the day. In December use them only for extra standalone material (e.g. the tongue-twister bumper); after December use them to test hooks on new content, recorded with `trial: true`."
- **Why:** Instagram help center (checked 2026-11-12): followers don't see trial reels, and reach may be limited if the same content was shared before. That rules out "trial two hooks, then post one" for daily episodes.
- **Priority:** later

#### P10. Hook rules in the critique rubric
- **Type:** change
- **Section:** §16.2 (Hook row), §16.4
- **Proposal:** Replace the generic hook questions with checkable rules and calibrate the hook score against `reels_skip_rate`.
- **Suggested spec text:**
  - §16.2 Hook row, old: "| **Hook (0–3 s)** | Is there a specific curiosity on frame 1? Is the subject fully in frame? Would a muted viewer understand it? |" → new: "| **Hook (0–3 s)** | Frame 1 is content (no fade, title, logo or black) and works as a cover; subject fully in frame; first word ≤ 0.3 s; first sentence ≤ 8 words / ≤ 3 s, names something concrete from this stage; no greeting, 'who we are' or day number before it; first caption on screen by 0.5 s, extra hook text ≤ 6 words; visual change by 3–4 s; the question isn't answered before ~50 % of runtime |"
  - §16.4, add: "- **Hook calibration:** the critic's hook score is compared with the reel's `reels_skip_rate` (§12.3)."
- **Why:** Each rule maps to a frame, transcript timestamp or caption timestamp, so the critic can check it without taste judgements. Skip rate gives a direct per-reel ground truth for the first 3 s.
- **Priority:** before phase 10

**Sign-off:** approve with changes
