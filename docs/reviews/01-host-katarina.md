# Review packet 01: Katarina (host, main user)

**Priority:** must review before implementation
**Time needed:** ~45 min
**Decisions already made:** see [README](README.md#decisions-already-made-please-dont-reopen). D4: your consent for voice prints and footage processing is recorded.

## Why you
Reels Hub is built around your voice, your takes and your channel. If the flow doesn't fit how you prepare, shoot and react to feedback, it won't get used.

## Read
- [§1 Why: lessons from Giro_00_Intro](../spec/REELS_HUB_SPEC.md#1-why-lessons-from-giro_00_intro): what slowed down the first reel
- [§3 Users and roles](../spec/REELS_HUB_SPEC.md#3-users-and-roles)
- [§6 Projects, reels and the reel prompt](../spec/REELS_HUB_SPEC.md#6-module-b-projects-reels-and-the-reel-prompt)
- [§16 AI critique](../spec/REELS_HUB_SPEC.md#16-module-l-ai-critique)
- [§19 Key workflows](../spec/REELS_HUB_SPEC.md#19-key-workflows): especially 19.0
- Optional: the Giro_00 intro draft and `../reels/giro00-intro/review_notes.md`

## Questions
1. **Your part of the flow:** what do you want to see before a shoot (shot list, pickups, which stage facts to mention)? Should the Hub prepare a one-page shoot sheet for you?
2. **Your words:** the Hub only uses things you actually said and marks proposed lines as "pickups". Is that the right rule? How do you want pickups delivered (text, teleprompter in Edits, voice memo)?
3. **AI critique of your delivery:** the critic checks things like "punchline cut too early" or "strongest take kept long enough". Which kinds of critique do you want to see, and which should go only to Ľuboš?
4. **Moments and ratings:** the Hub rates your takes 1–5 and marks some ranges "do not use" (for example private banter). Are you comfortable with that? Who decides what's excluded?
5. **Your own access:** do you want to use the Hub yourself (e.g. a phone-friendly review page), or is Ľuboš the only user?
6. **Tone:** what must every reel keep so it still feels like you, for example humor, the kitchen set, Ľuboš appearing, pink as the accent?
7. **Language:** should the interface be Slovak, English or both?
8. **Comments:** the Hub reads comments to find questions and topic ideas. Anything you don't want it to do with them (e.g. auto-replying)?

## Your input

> Written as a simulation of Katarina's view, based on how she comes across in `reels/giro00-intro/review_notes.md`, the Instagram caption and `DESIGN_LANGUAGE.md`. Points only the real Katarina can confirm are marked **needs Katarina**. External facts checked on 2026-11-12 (sources linked inline).

### Summary
The spec is very strong on the producer and agent side (footage, facts, approvals, analytics), but the host shows up mostly as *material*, not as a user. My side of the flow (preparing a shoot, recording pickups, confirming my own lines) has no screen, no deliverable and no status in the reel pipeline, even though every reel depends on footage that doesn't exist yet when the reel is "planned". The most important changes: (1) a one-page **shoot sheet** and a `to_shoot → shot` step in the pipeline, (2) a hard **"no frankenbites"** rule so my words are never re-spliced into sentences I didn't say, (3) a real **pickup lifecycle** where I say the idea in my own words, not read the AI's wording, (4) a **host veto** on excluded ranges and a split between critique for me and critique for Ľuboš, and (5) comments, voice prints and my face/voice are **read-only and never synthesized**. With those, I'd use it.

### Answers

#### Q1. What I want before a shoot
Yes, I want a **one-page shoot sheet per shoot day**, not per reel. We'll shoot the 24 reels in batches (my guess: 4–6 reels per session in the kitchen, **needs Katarina** for the real number), so the sheet must cover all reels in that batch, in recording order. Per reel, max one block of ~8 lines:
- **Slot and topic** (e.g. "Deň 6 · 5. etapa · Ako sa tam dostať").
- **Opening idea**: the curiosity to start on, as a *question or prop*, not a script (e.g. "lízatko → máj" worked; the Hub should propose the prop/question pair).
- **Max 3 facts to mention**, only `verified` ones, each in one short line with the Slovak form and pronunciation (e.g. "Terst (nie Trieste)", "Zoncolan = dzon-ko-LAN"). Anything `conflicting` is listed separately as **"nehovoriť ako fakt"** (don't say as fact), like the Stage 1 Slovenia crossing.
- **What yesterday's reel promised** and **what this one should tease for tomorrow** (one line each), so continuity happens on camera, not only on a card.
- **Pickups** for already-edited reels (see Q2), max 2 per reel.
- **Props and wardrobe**: pink tee, which calendar/bidon/lollipop, and a "same as last time" photo of the set from the last shoot's first frame so the kitchen looks consistent.
- **Ľuboš beats**: where a DJI reveal or an off-camera reply would help (e.g. "ask Ľuboško something at the end").
Format: A4 printable + phone view, in Slovak. The sheet should fit on one page for the whole batch header plus half a page per reel; if it doesn't fit, the Hub is over-preparing me. I don't want a full script; I improvise, and the humor comes from that.

#### Q2. My words and pickups
The rule "only things I actually said" is **right and must be absolute**. Two additions:
1. It must also cover **splicing**: cutting two of my half-sentences together so they say something new is the same as putting words in my mouth (see P2). Jump cuts that drop filler inside one thought are fine.
2. Proposed pickup wording is only a **suggestion of the point to make**. I'll say it my way; the recorded version is what counts. The Hub should match my recording back to the pickup by meaning, not by exact words.
Delivery: **text on the shoot sheet**, plus a copy-paste block for a teleprompter. Note the Edits teleprompter only works when recording in the Edits camera on the phone ([Edits tutorial](https://edits.instagram.com/tutorials/teleprompter/), checked 2026-11-12); our main camera is the Sony, so for Sony takes the text goes on paper or a phone teleprompter app next to the lens. No voice memos from the Hub (a synthetic voice reading lines to me would be odd, and I don't want my voice synthesized at all). Keep each pickup ≤ 2 sentences / ≤ 12 s, because longer ones don't sound like me.

#### Q3. AI critique of my delivery
For **me** (only things I can act on at the next shoot, max 3 per week, always with one strength first):
- I start talking before the camera/frame is ready, or I'm half out of frame on the first frame (the 0.545 hook problem).
- The hook line was weaker than an alternative I said in the same take ("your take 2 opened faster").
- A joke landed best in a specific take, so I can repeat that style.
- Audio: I turned away from the mic, spoke over Ľuboš, or a line was too fast to caption.
- Facts I said wrong on camera (better to know at the shoot than in the edit).
For **Ľuboš only**: punchline cut too early, take kept too short, pacing, cuts, music, scores, predicted drop-offs, everything about the edit. Those are edit decisions, not my delivery.
**Never** (for anyone): my looks, weight, clothes beyond the prop list, accent, "smile more", "more energy" without a timestamped example, or comparisons with other creators. The §16.2 row named "Katarina" should become an edit check, not a judgement of me (see P5).

#### Q4. Moments, ratings and exclusions
Ratings are fine **if they mean "usefulness for this edit"**, not "how good Katarina was", and if I don't see a 1–5 score on my face by default. The label in the UI should read like "best for hook / usable / weak audio", not stars next to my name.
Exclusions: I decide what's excluded about me; Ľuboš decides about him; either of us can exclude shared banter, and **an exclusion by either of us wins** over an agent or the other person's rating. Agents may *propose* exclusions (crude, private, bad audio), never remove one. Excluded ranges should stay out of agent search, out of `unused gems`, out of critique frames and out of any cloud call, which §22 already mostly says. I'd also like a quick **"mute this whole take"** for takes that went off the rails, rather than marking 30 s ranges one by one. **Needs Katarina:** whether she wants to review the agent's proposed exclusions herself or trust Ľuboš to do it.

#### Q5. My own access
Ľuboš stays the main user. I don't want another app to log into. What I want instead, all generated by the Hub and sent to me by Ľuboš (AirDrop / message):
- the **shoot sheet** (Q1),
- a **"potvrď" list** (confirm list): lines where the speaker is unclear (like the "Čau!" at 0:52.1 in Giro_00), facts I'm about to say, and pickups waiting for me,
- a **weekly host digest**: 3 critique items for me (Q3), the top 3 comment questions, and the next week's slots.
I'd reply in chat and Ľuboš pastes it in, recorded as feedback with `author: Katarina`. A phone-friendly review page on our home Wi-Fi would be nice *later*, but it conflicts with the localhost-only rule in §22, so it shouldn't block December. **Needs Katarina:** whether she wants a final "host OK" before a reel with a new pickup or a reused old moment goes out (P8).

#### Q6. What must stay so it still feels like me
- **My words and my humor**, unscripted, including teasing Ľuboš ("nie, Ľuboško?").
- **Ľuboš is in every reel** in some form: DJI reveal, off-camera reply, or a sign-off exchange. The "Môže byť." moment is the show.
- **The natural "Čaute" sign-off**, never replaced by a generic CTA card.
- **The kitchen set, the pink tee and pink as the only accent.** Maps stay calm; I'm the loud part.
- **At least one laugh per reel**, even in a fact-heavy stage.
- **Facts are light**: history, geography, how to get there, said like to a friend, not like a broadcaster. Max 3 hard facts said by me per reel; the rest can live on cards or in the caption.
- **No AI voice, no voice cloning, no lip-sync edits, no AI-generated "me".** If something is missing, I record a pickup or it goes on a card.
- Crude banter stays on set, not on the channel (already in DESIGN_LANGUAGE §10).
These should be machine-checked (P6), not just written down.

#### Q7. Language
- Everything that reaches **me** (shoot sheet, pickups, confirm list, host digest, host critique items) in **Slovak**, with Slovak exonyms from the glossary (Terst, Rím).
- The **producer UI** can stay bilingual SK/EN as §20 says.
- The **reel prompt** for Claude can stay English, but anything that will end up on screen or in my mouth must be Slovak and checked against the glossary.

#### Q8. Comments
Reading comments for questions and stage requests is great ("Ktorú etapu by ste chceli vidieť naživo?" was our own CTA). The Hub must **not**:
- reply, like, hide, delete or DM anyone, and not turn comments off. The API *can* do all of that with the same comment permission ([Meta comment moderation guide](https://developers.facebook.com/docs/instagram-platform/comment-moderation), checked 2026-11-12), so it must be blocked in code, not just by convention.
- quote a commenter's name or comment on screen without us choosing to (a shout-out is a nice idea, but our call each time).
- draft replies "in my voice". I answer comments myself. A list of "questions worth answering" is enough, with a link to open the comment in Instagram.
- tell me about mean comments by default. Hostile comments should be hidden from my digest unless I ask (Ľuboš sees them). **Needs Katarina.**

### Proposals

#### P1. Shoot sheet and a "to shoot" step in the pipeline
- **Type:** addition
- **Section:** §6.2, §19 (new §19.5), §20, §17.2
- **Proposal:** Add a shoot-day deliverable for the host and make "is the footage recorded?" part of each reel's status, because the 24 reels depend on batches of shoots that the pipeline currently skips (it goes from `planned` straight to `prompt_ready`).
- **Suggested spec text:**
  - §6.2, replace the status line: old → `idea → planned → prompt_ready → editing → in_review → approved → exported → scheduled → posted → analyzed` · new → `idea → planned → to_shoot → shot → prompt_ready → editing → in_review → approved → exported → scheduled → posted → analyzed` (a reel can return from `in_review` to `to_shoot` when it needs a pickup).
  - New §19.5:
    ```markdown
    ### 19.5 Shoot day → shoot sheet
    1. Producer groups reels with status `to_shoot` (plus open pickups from reels in review) into a **shoot**.
    2. The Hub generates a **shoot sheet** in Slovak (A4 PDF + Markdown at `<project>/shoots/<date>/SHOOT_SHEET.md` + phone view):
       - header: date, reels in recording order, props and wardrobe, a reference frame of the set from the last shoot;
       - per reel (≤ half a page): slot, topic, opening idea (prop or question, not a script), max 3 verified facts with Slovak form and pronunciation, "do not say as fact" list (conflicting facts), yesterday's promise and tomorrow's tease, Ľuboš beat, pickups (≤ 2, ≤ 12 s each).
    3. After the shoot, new footage is ingested; reels covered by the shoot move to `shot` when a take matching the reel's topic or pickup is found (agent proposes, producer confirms).
    ```
  - §17.2 Projects and reels, add: `generate_shoot_sheet(project, reel_ids[], date)` → Markdown + PDF path.
  - §20 table, add row: `| **Shoot** | Plan a shoot day, generate the shoot sheet, tick off recorded reels and pickups |`
- **Why:** In Giro_00 the closing card stayed silent because the pickup idea came after the shoot; with 24 daily reels, missing a line at the shoot means a card instead of me. The host role in §3 ("what to record next, pickup lines") has no feature backing it.
- **Priority:** must-have before build (needed before the first December batch is shot)

#### P2. No frankenbites: never splice my words into new sentences
- **Type:** change
- **Section:** §6.4 (Rules), §16.2, §17.3, DESIGN_LANGUAGE §10
- **Proposal:** Extend "use only words Katarina actually said" to forbid cuts that join fragments from different sentences or takes into a sentence with a new meaning. Allow removing filler and false starts inside one continuous thought. The critic and `lint_draft` flag any cut inside a sentence across >2 s of source gap or across takes.
- **Suggested spec text:**
  - §6.4 Rules, add after "Use only words Katarina actually said; propose pickups separately.": `- Never join fragments from different sentences or takes into one sentence (no "frankenbites"). Cuts inside one continuous thought to remove filler or false starts are allowed. If a line is needed that she didn't say in one piece, propose a pickup.`
  - §17.3, add: `- **Splice check:** \`create_version\` flags any main-track cut that joins two speech fragments of the same speaker where the source gap is > 2 s or the fragments come from different takes; the version can't be approved until each flagged cut is confirmed by the producer.`
  - §16.2 Katarina row (see P5) includes: "Does any cut change what she meant (fragments joined across sentences or takes)?"
- **Why:** Search over moments + an agent that optimizes runtime makes splicing very tempting (the agent already assembled Giro_00 from 6 source ranges). One spliced sentence on a public channel is worse for me than a longer reel.
- **Priority:** must-have before build

#### P3. Pickup lifecycle: an idea to say, not a script to read
- **Type:** change
- **Section:** §6.2, §17.2, §18
- **Proposal:** Make pickups a tracked object with a lifecycle and a "point to make" next to the suggested wording; matching to the recording is semantic, and only the recorded transcript ever reaches captions.
- **Suggested spec text:** add to §6.2 after "Shoot planning":
  ```yaml
  pickup:
    id: pk_giro00_01
    reel: giro00
    purpose: "closing card is silent; tease tomorrow's two-country question"
    point: "Tomorrow: Terst. Start and finish in the same city, yet the riders are in two countries. How? Tomorrow."
    suggested_wording: "Zajtra začíname v Terste…"   # suggestion only; host says it her way
    max_seconds: 12
    status: proposed        # proposed | on_sheet | recorded | matched | used | dropped
    shoot: null
    matched_moment: null    # set when a recorded take is matched by meaning
  ```
  and the rule: `Only the transcript of the matched recording is used in captions and cut lists; suggested_wording is never shown as her speech. Delivery: shoot sheet text plus a plain-text teleprompter block. The Edits teleprompter applies only to phone takes recorded in Edits; for Sony takes print it or use a phone teleprompter next to the lens.`
  §17.2 add: `add_pickup(reel, purpose, point, suggested_wording?)`, `match_pickup(pickup_id, moment_id)`.
- **Why:** Read-out lines sound like a presenter, which DESIGN_LANGUAGE §1 rules out ("no polished presenter VO"). Edits teleprompter scope: [edits.instagram.com/tutorials/teleprompter](https://edits.instagram.com/tutorials/teleprompter/) (checked 2026-11-12).
- **Priority:** before phase 9

#### P4. Host veto on exclusions; ratings mean "usefulness for the edit"
- **Type:** change
- **Section:** §5.3, §17.3, §18
- **Proposal:** Record who excluded a range; an exclusion by the person on screen (or either person for shared banter) can't be reversed by an agent or by the other person. Agents can only propose exclusions. Add "exclude whole take". Rename the rating meaning.
- **Suggested spec text:**
  - §5.3 YAML, replace `rating: 5            # 1–5` → `rating: 5            # 1–5 usefulness for editing (hook strength, audio, framing), not a judgement of the host` and add after `reason_excluded`: `excluded_by: null      # katarina | luboš | agent_proposed`
  - §5.3 Features, add: `- **Host veto:** a range excluded by Katarina (or by Ľuboš for himself) stays excluded; only the same person can lift it. Agent exclusions are proposals until a person confirms. A whole take can be excluded in one action.`
  - §17.3, add: `- Agents can't set \`usable: true\` on a range excluded by a person, and can't use it in a version even with a reason.`
  - §18 `moment` table: add `excluded_by`.
- **Why:** Giro_00 already had three crude-banter ranges plus private talk; who controls those is a trust question, and today §17.3 lets an agent pull them "with a reason".
- **Priority:** must-have before build

#### P5. Split critique into host-facing and producer-only
- **Type:** change
- **Section:** §16.2, §16.3, §18
- **Proposal:** Rename the "Katarina" area to an edit check, add an `audience` field to critique items, and define what may never be critiqued.
- **Suggested spec text:**
  - §16.2, replace the row `| **Katarina** | Is her strongest take kept long enough for its payoff? Are jokes cut before the punchline? |` → `| **Host in the edit** | Is her strongest take kept long enough for its payoff? Are jokes cut before the punchline? Does any cut change what she meant? (producer-only) |` and add a row `| **Host delivery** (host-facing) | Subject in frame before she speaks; a stronger alternative line exists in the same take; speech too fast to caption; turned away from the mic; a fact said wrong on camera |`
  - §16.3 item YAML, add: `audience: producer       # producer | host`
  - §16.2, add below the table: `**Out of scope for the critic:** appearance, body, clothing beyond the prop list, accent or voice quality, "more energy / smile more" without a timestamped example, comparisons with other creators. Host-facing items are in Slovak, max 3 per weekly host digest, each with a timestamp and preceded by one strength.`
- **Why:** The critic is meant to be demanding; demanding about the edit helps us, demanding about me in a vague way just makes me stop wanting to shoot.
- **Priority:** before phase 10

#### P6. Host voice guardrails as checkable rules, including "no synthetic Katarina"
- **Type:** addition
- **Section:** §9, §16.2, §22
- **Proposal:** Turn the "feels like me" items into tokens that lint and critique check, and state explicitly that voice prints are only for speaker labels.
- **Suggested spec text:**
  - §9, add:
    ```yaml
    host_guardrails:
      humor_beats_min: 1
      luboš_presence: required          # DJI cutaway, off-camera reply or sign-off exchange
      sign_off: natural_exchange        # "Čaute" exchange kept; no generic CTA card instead
      hard_facts_spoken_max: 3          # more go on cards or in the caption
      set: kitchen                      # flag other locations for producer confirmation
      accent_color: pink_only
      synthetic_host: forbidden         # no TTS, voice cloning, lip-sync or generated likeness
    ```
  - §22, add: `- **Voice prints are for speaker labels only.** They are never exported, never sent to an external service, and never used for speech synthesis, voice cloning or lip-sync. No tool in the Hub generates Katarina's or Ľuboš's voice or likeness.`
- **Why:** D4 covers consent to voice prints and footage processing for this tool; it shouldn't be read as consent to synthesis. The brand core already says "no stock voice" (DESIGN_LANGUAGE §1); making it data lets `lint_draft` and the critic enforce it.
- **Priority:** must-have before build (the §22 line); before phase 10 (the critic checks)

#### P7. Comments are read-only, enforced in code
- **Type:** change
- **Section:** §12.1, §17.3, §22
- **Proposal:** The Instagram client only implements read endpoints for comments; no reply, hide, delete, DM or disable tools exist. No reply drafting "in Katarina's voice".
- **Suggested spec text:** §17.3, add: `- **Comments are read-only.** The Instagram client implements only GET endpoints for comments and replies. No MCP tool may reply to, like, hide, delete or disable comments or send private replies, and none drafts replies in the host's voice. Comment questions surface as reel ideas with a link to open the comment in Instagram; the host answers herself. Quoting a commenter on screen needs a producer decision per reel.`
- **Why:** The comment permission the importer needs for reading also allows `POST /{comment-id}/replies`, hide, delete and disabling comments ([Meta: Comment moderation](https://developers.facebook.com/docs/instagram-platform/comment-moderation), checked 2026-11-12). An auto-reply under my name would be the fastest way to lose the "invitation, not broadcast" tone. Doesn't touch D5 (what we import), only what we do with it.
- **Priority:** before phase 5

#### P8. Host access through generated outputs; resolve the §27 open question
- **Type:** change
- **Section:** §3, §20, §27, §11.3
- **Proposal:** Close "single user or shared with Katarina?" as: single producer user; the host is served by generated documents (shoot sheet, confirm list, weekly host digest) and her replies are logged as feedback with `author: Katarina`. Add an optional host check to approval for reels with a new pickup or a reused moment from an earlier reel.
- **Suggested spec text:**
  - §27, replace the row `| **Open:** single user or shared with Katarina? | Affects auth and UI language |` → `| Single user or shared with Katarina? | **Decided:** Ľuboš is the only Hub user. Katarina gets generated Slovak documents (shoot sheet, confirm list, weekly host digest) and replies through Ľuboš; her replies are logged as feedback with \`author: Katarina\`. A LAN phone view is a later option and must keep §22's token rule. |`
  - §20 table, add: `| **Host digest** | Weekly Slovak page for Katarina: next slots, pickups waiting, lines to confirm (unclear speaker, facts she'll say), max 3 host-facing critique items, top 3 comment questions |`
  - §11.3, add: `- **Host check (optional, per project):** if a version contains a matched pickup or a moment first used in another reel, \`request_approval\` adds an open item "host OK" that the producer resolves after asking Katarina.`
- **Why:** Avoids building auth and a second UI before December, while still giving me the three things I need. The "Čau!" speaker question in Giro_00 is exactly the kind of item only I can answer. **Needs Katarina** on whether the host check is on by default.
- **Priority:** must-have before build (the decision), before phase 4 (host check), before phase 9 (digest)

#### P9. Slovak for everything host-facing
- **Type:** change
- **Section:** §20
- **Proposal:** Specify the language per output instead of one bilingual line.
- **Suggested spec text:** §20, replace `- Bilingual UI labels (SK/EN), Slovak content.` → `- Producer UI: bilingual labels (SK/EN). Everything host-facing (shoot sheet, pickups, confirm list, host digest, host-facing critique items) is Slovak only and uses glossary forms (Terst, Rím). Reel prompts may be English; any text that ends up on screen, in captions or in a pickup is Slovak and passes the glossary check.`
- **Why:** I prepare and shoot in Slovak; an English shoot sheet means translating in my head on set.
- **Priority:** before phase 9

**Sign-off:** approve with changes
