# Review packet 06: video editor / post-production

**Priority:** before phases 0–1 (ingest) and 4 (reviews)
**Time needed:** ~2 h
**Decisions already made:** see [README](README.md#decisions-already-made-please-dont-reopen).

## Why you
The Hub prepares footage, picks moments and hands an AI editor a plan for Edits. It needs a working editor's eye on what's realistic, what's missing and what will break in real post-production.

## Read
- [§5 Footage index and moments](../spec/REELS_HUB_SPEC.md#5-module-a-footage-index-and-moments)
- [§9 Design system as data](../spec/REELS_HUB_SPEC.md#9-module-e-design-system-as-data) and [`DESIGN_LANGUAGE.md`](../spec/DESIGN_LANGUAGE.md) §6 Picture, §9 Sound
- [§11 Reviews, feedback and approvals](../spec/REELS_HUB_SPEC.md#11-module-g-reviews-feedback-and-approvals)
- [§14 Edits playbook](../spec/REELS_HUB_SPEC.md#14-module-j-tool-knowledge-edits-playbook)
- [§16 AI critique](../spec/REELS_HUB_SPEC.md#16-module-l-ai-critique)
- Reference: `../reels/giro00-intro/review_notes.md` (how Giro_00 was cut)

## Questions
1. **Proxies:** 540p H.264 for UI and agents. Right spec? Should the Hub also create edit-friendly proxies for Edits, or always use the 4K masters?
2. **Multicam:** Sony 25p + DJI 23.976p in a 24 fps project. Frame-rate handling, sync by transcript words. What would you do differently?
3. **Color:** the DJI cutaways were graded by hand to match Sony. Should the Hub suggest grades (OpenCV histogram match), apply a LUT per camera, or just flag mismatches?
4. **Audio:** Sony lav carries dialogue; DJI has its own mic `.WAV`. Use the DJI WAV as backup? Loudness target for Reels (we're at about −3 dBFS speech peaks)? Noise reduction?
5. **Moments:** is "moment" (tagged time range with rating) the right unit for you? What tags would you use day to day?
6. **Cut list snapshots:** what must a version record contain so you can understand and restore an edit (clips, in/out, overlays, captions, music, levels)?
7. **Critique checklist (§16.2):** what's missing from an editor's point of view (e.g. jump-cut rhythm, eyeline, mouth noises, breath edits)?
8. **Edits as the editor:** is Edits enough for daily reels? When would you want DaVinci Resolve or Final Cut support?

## Your input

*Reviewer: video editor / post-production (AI reviewer acting in the role). Reviewed spec v0.5, DESIGN_LANGUAGE 1.1 and the Giro_00 review notes on 2026-11-12.*

**Facts checked on 2026-11-12 (web):**
- Edits for Mac shipped on 10 Nov 2026. It has a multi-track timeline with keyframes and waveforms, color wheels, curves, Log conversion and LUT import, voice enhance, an MCP connection, and export at HD/2K/4K, **24/30/60 fps only** (no 25/50), SDR/HDR. Instagram hasn't published supported LUT formats or export codecs. Source: [CineD, 10 Nov 2026](https://www.cined.com/instagram-edits-for-mac-released-multi-track-timeline-lut-import-and-watermark-free-4k-export/), [Instagram for Creators: best camera and export settings](https://creators.instagram.com/blog/best-camera-settings-instagram-reels).
- Edits resolutions: HD 1080×1920, 2K 1440×2560, 4K 2160×3840. An Instagram staff member recommends 2K for Reels because viewers don't see 4K. Source: [Social Media Today, 20 May 2025](https://www.socialmediatoday.com/news/edits-video-editing-app-enhanced-cropping-quality-features/748663/).
- Meta publishes **no loudness target** for Reels. The common practice is about −14 LUFS integrated (some use −16 for short-form) with a true peak at or below −1 dBTP. Sources: [Marxx guide (checked 3 Nov 2026)](https://marxx.ai/guides/how-to-normalize-audio-for-instagram), [Sound Design RV, Sep 2026](https://www.sounddesignrv.com/en/insights/what-lufs-to-deliver-a-video-instagram-youtube-tv-cinema/).
- **Unverified:** what Edits does with 25p clips in a 24 fps project (probably drops one frame per second); whether the Edits MCP can duplicate a project; hardware decode of Sony 10-bit 4:2:2 H.264 on Apple silicon; which DJI device writes the `.WAV` and whether it's 32-bit float.

### Summary
The spec is realistic for a 45–60 s talking-head series cut in Edits. Moments as the unit of reuse, editors_notes.md and the gathered prompt are what a working editor would want. Ingest and versioning are still thin on the details that break real post-production:
- **Frame rate:** the Sony shoots 25p into a 24 fps project, and Edits can't run at 25.
- **Sync precision:** transcript words are only accurate to 2–5 frames, which is visible on the DJI cutaways where Ľuboš speaks.
- **Audio QC:** Giro_00's source hit +1.6 dBFS, which means clipping.
- **Cut list:** too loose to rebuild an edit. It lacks transforms, levels and music source offsets, and music doesn't ripple in Edits.

My most important changes are a concrete cut-list schema (P7), a deterministic cut-list lint that catches most craft errors before any critique exists (P8), audio cross-correlation sync with a drift check (P3), and a probe that flags frame-rate, VFR and HDR mismatches at ingest (P1). None of these adds a service, a queue or a gate. They are small checks on data the Hub already has.

### Answers

#### Q1. Proxies
**540p H.264 is the right size for the UI and agents. Pin down how it's encoded, and don't make edit proxies for Edits.**

- **UI/agent proxy:** 960×540 (keep the source aspect: DJI 4:3 becomes 720×540).
  - H.264 High, CRF 23, `-g 12 -keyint_min 12` (a keyframe every 0.5 s at 24/25p) so browser scrubbing and J/K/L land on the right frame.
  - Keep the **source frame rate** (no conform) and copy the source timecode into the proxy (`-timecode`).
  - AAC 128 kbps 48 kHz, keeping **all source audio channels** so ch1 lav and ch2 camera mic can still be compared.
  - `-movflags +faststart`. Size: about 1.5–2 % of the Sony 4K masters. That matches §21.
- **Frame-accurate checks** (first frame in frame, focus_x, critique frames) must grab frames from the **master**, not the proxy. One `ffmpeg -ss` seek per frame is cheap. Contact sheets every 2 s from the proxy are fine.
- **No edit proxies for Edits:**
  1. Edits has no proxy/relink workflow, so whatever you import is what gets exported.
  2. Reframing a 16:9 source to 9:16 already uses almost all the resolution (see below).
  3. Giro_00 was cut on 4K masters on this Mac.
  - If Edits ever chokes on Sony 10-bit 4:2:2 H.264 (software decode on many Apple silicon chips, **unverified**), the fallback is a 1080p **ProRes 422 Proxy** mezzanine at the same frame rate. Treat it as a playbook fix, not a pipeline.
- **Resolution headroom for reframing:**
  - The Sony 3840×2160 filled to 9:16 is a 1215×2160 crop. Instagram plays at most 1080 wide, so any punch-in beyond **1.12×** on the Sony drops below delivery resolution.
  - The DJI 3840×2880 crop is 1620×2880, which leaves 1.5× headroom.
  - This should be a design token (P6). It decides whether a jump cut can be hidden with a punch-in or needs a cutaway.
- **Export:** 2K (1440×2560) is enough for a Sony-based 9:16 edit; 4K adds export time and nothing the viewer sees. Shared directly from Edits to Instagram it avoids an extra re-encode (Instagram's own advice). Sharing from Edits by the producer still counts as manual posting (R28).

#### Q2. Multicam: 25p + 23.976p in a 24 fps project
- **The real problem is the Sony's 25p, not the DJI's 23.976p.**
  - 23.976 → 24 is a 0.1 % difference; time-based playback drops one frame every ~42 s, which nobody sees.
  - 25 → 24 most likely drops **one frame every second** (unverified for Edits; it's the standard behaviour of time-based timelines). On a static talking head that's nearly invisible. On hand gestures, the lollipop move or a pan it reads as a stutter once a second.
  - Edits can't run a 25 fps project (24/30/60 only), and a 30 fps project would duplicate frames, which is worse.
- **What I'd do:**
  1. **Shoot both cameras at 24p (23.976 or 24)** from the next shoot. On the Sony that usually means switching the NTSC/PAL selector to NTSC (on many bodies this asks to reformat the card; **unverified** per model).
  2. Keep the shutter at **1/50 s** (172.8° at 24p) so the 50 Hz kitchen lights don't flicker.
  3. This is a camera setting, not shoot planning, so it belongs in DESIGN_LANGUAGE §6 (P1).
  - If the Sony stays at 25p, accept the dropped frames, keep talking-head shots static, and record the observed Edits behaviour in the playbook after one test (a clap and a waved hand, 25p clip in a 24 fps project).
- **The Hub's job is to notice:** the probe compares each clip's fps with the project fps and flags mismatches. It also flags **VFR** phone footage (`r_frame_rate ≠ avg_frame_rate`) and **HDR/Log** transfer (`color_transfer` = `arib-std-b67` / `smpte2084`, or DJI D-Log M). Each of these quietly shifts sync or look in an SDR 24p timeline (P1).
- **Sync:**
  - Transcript word timings from Whisper are accurate to roughly ±50–200 ms, which is **1–5 frames at 24 fps**. That's fine for finding the region, but not for a DJI cutaway where Ľuboš's mouth is visible ("Môže byť").
  - Use transcript words (or the clock difference) as the **coarse** offset to within ±2 s, then **audio cross-correlation** of the two scratch tracks (16 kHz mono, onset envelope) inside that window. That gives sample-level precision in ~50 lines of numpy.
  - **Re-check at a second point** near the end of the take, as the Giro_00 notes already do by hand. Consumer camera clocks drift around 20–50 ppm, about 1 frame over a 13-minute take. If start and end offsets differ by more than 1 frame (42 ms), store the drift and flag the take.
  - Keep the manual offset field as the override (P3).

#### Q3. Color
**Flag mismatches. Don't compute grades with OpenCV, and don't do per-camera LUTs yet.**
- Edits' adjustment sliders are unitless and version-dependent, so an OpenCV histogram match can't be translated reliably into "exposure +0.5, temperature +0.15". The numbers would look precise and be wrong.
- What works:
  1. **One fixed preset per camera** in DESIGN_LANGUAGE §6 (already there for the DJI: exposure 0.5, shadows 0.3, temperature 0.15, contrast 0.1). The agent applies it to every DJI cutaway.
  2. The Hub **flags** a DJI clip when its synced frames differ from that camera's **reference shoot** by more than a threshold. Compare mean L\*a\*b\* of the centre 50 % of synced Sony and DJI frame pairs: |ΔL\*| > 5 or |Δb\*| > 4 (warm/cool). That catches the day someone changed the DJI's white balance or the lights. The producer then fixes it by eye in Edits.
- **LUTs later:** Edits for Mac now imports LUTs (format unpublished). Once the DJI preset is stable, bake it once by hand into a `lut-dji-to-sony` asset so it's applied in one step. A LUT is only worth automating if a camera starts shooting Log (D-Log M), which also needs the HDR/Log probe flag from Q2.
- Keep "Sony grade: none" and "don't grade it cooler to match the graphics" (DESIGN_LANGUAGE §2). Matching goes DJI → Sony, never both towards a neutral.

#### Q4. Audio
- **Clipping:** the Giro_00 notes say source sample peaks reached **+1.6 dBFS**. In a fixed-point camera file that means flat-topped samples, i.e. **clipping baked into the source**; pulling gain down afterwards doesn't fix it. The Hub should detect it at ingest: count runs of ≥ 3 consecutive samples at or above −0.1 dBFS, and mark those ranges `audio:clipped` on transcript segments and moments. A clipped hook is a bad hook (P4).
- **Use the DJI `.WAV` as backup: yes.**
  - Ingest it as an **alternate audio source in the same take**, synced with the same offset as its parent clip.
  - Use it for: (a) passages where the Sony lav clipped, rustled or dropped out; (b) **Ľuboš's off-camera lines**, which the DJI mic (next to him) hears far better than Katarina's lav.
  - In Giro_00 the DJI audio was muted everywhere. I'd allow it on Ľuboš's reply at about −6 dB under the Sony bed rather than muting it.
  - If the WAV comes from a DJI Mic transmitter's 32-bit float recording (**unverified**), it can't clip and is the best source for any clipped passage.
  - The Hub reports per segment which source is cleaner (clip count, noise floor) and nothing more. The editor picks.
- **Loudness target:**
  - "−3 dBFS speech peaks" is a peak figure, not loudness. Meta publishes no target (checked above).
  - Use **−14 LUFS integrated, true peak ≤ −1 dBTP**, with dialogue sitting around −16 to −15 LUFS short-term.
  - Measure on the **exported file** locally with `ffmpeg -af ebur128=peak=true`. Only numbers are stored, which R44 allows.
  - Tolerance ±1.5 LU. Short-term loudness should not jump more than 3 LU between adjacent sentences (that's what makes phone-speaker viewers reach for the volume).
- **Music level in LU relative to dialogue, not as an Edits gain factor:**
  - "0.20 under speech" only meant "≈ 15 dB below dialogue" for Dolce Vita's mastering level. A different track at 0.20 can be 6 dB louder or quieter.
  - Keep 0.20 as the starting value, but the rule is: music bed **15–18 LU below dialogue** under speech, and about −20 LUFS short-term on silent cards (P9).
- **Noise reduction:** off by default. A lav in a kitchen is usually clean (noise floor below about −60 dBFS).
  - If the floor between words is above **−55 dBFS** (fridge, extractor fan), use Edits' voice enhance at the lowest effective setting and A/B on a phone speaker; heavy NR makes Slovak sibilants lispy.
  - The Hub only measures the noise floor per clip. It doesn't process or replace audio (that would mean re-importing cleaned WAVs into Edits, which isn't worth it).
- **Small rules for the playbook:** a 1–2 frame audio fade on every dialogue cut to avoid clicks (if Edits has no per-clip audio fade, cut in the silence between words instead), and never cut a laugh's tail.

#### Q5. Moments
**Yes, a moment is the right unit, with four additions:**
1. **Word-snapped in/out with handles.** Store the word-accurate range (`src_in_ms` = first word onset, `src_out_ms` = last word offset) and let the cut use default handles of **−120 ms before / +250 ms after**. Cuts tighter than ~40 ms before an onset eat Slovak initial consonants ("p", "t", "k"). Cuts right at the last word's end chop the decay and sound abrupt.
2. **Tech flags separate from rating:** `tech: [clipped, noise, mic_rustle, plosive, out_of_frame, soft_focus, flicker, blink_at_in]`. Rating stays "editorial usefulness". A 5-rated line with `clipped` is still worth knowing about.
3. **`fact_ids`:** a moment where Katarina states a fact ("21 etáp", "Štart v Terste") links to the fact. If that fact becomes `conflicting` or `outdated`, the moment shows a warning. This is exactly the Stage 1 Slovenia case.
4. **`angles` derived from the take**, not stored (as R15 already says for `alt_angles`), so a later sync correction doesn't leave stale offsets.

**Tags I'd use every day**, as a fixed vocabulary with prefixes so search and ranking stay predictable:

| Prefix | Values |
|---|---|
| `beat:` | `hook`, `who`, `promise`, `payoff`, `card_line`, `sign_off`, `cold_open`, `bumper`, `tease_next` |
| `tone:` | `humor`, `tease`, `warm`, `serious`, `reaction`, `laugh` |
| `topic:` / `stage:` / `place:` / `climb:` / `rider:` | free values from the glossary (`stage:1`, `place:terst`, `climb:zoncolan`) |
| `prop:` | `lollipop`, `advent_calendar`, `cycling_calendar`, `bidon` |
| `people:` | `luboš_offcam`, `luboš_on_dji`, `duo` |
| `craft:` | `one_take` (works without internal cuts), `needs_cover` (jump cut needs a cutaway), `clean_in`, `clean_out` |
| `time:` | `evergreen`, `dated` (mentions a date, "zajtra", a weekday) |

`time:dated` matters for the "unused gems" list: a line saying "zajtra" can't be reused later in the series without a pickup.

#### Q6. Cut-list snapshots
To understand **and** rebuild an edit, a version needs (schema in P7):
- **Header:** Edits project ID and name, Edits app version, design-language version, prompt version, timeline fps, canvas, runtime in ms.
- **Every timeline item** with `t_in_ms`/`t_out_ms`, and for media `clip`/`asset`, `src_in_ms`/`src_out_ms`, speed, moment ID. Ordered by layer (main, overlays 1…n, text, captions, music, sfx).
- **Transform** per clip: scale, focus_x, focus_y (Giro_00's 0.545 is exactly what gets lost today).
- **Grade** per clip: preset name or explicit values.
- **Audio per clip:** gain in dB, muted yes/no, which source (Sony lav / DJI WAV).
- **Text items:** literal text with `\n`, font, size in Edits units, color, y position, animation.
- **Captions:** style name, y, and each phrase with text, timing and speaker label. Captions are the most edited thing and the hardest to recreate.
- **Music:** asset ID, **track source offset** (where in the song it starts), timeline in/out, internal re-cuts (because music doesn't ripple), level keyframes (time, level) including ramps and fades.
- **Graphics:** asset ID plus a file hash, so "which map PNG was it?" has an answer even after a re-render.
- **Export block** (filled only after approval): resolution, fps, SDR/HDR, file path, hash, measured LUFS / true peak.

**Restore:**
- The cut list must be complete enough that an agent can rebuild the edit in a fresh Edits project through the Edits MCP. Tier-1 music comes back by Edits ID, never as audio.
- If the Edits MCP can duplicate a project (**unverified**), also duplicate it at each `create_version` as `<slot>_v<n>`. That's the cheapest real restore.
- The diff view (§11.2) then compares two cut lists item by item.

#### Q7. Critique checklist (§16.2): what's missing
Critique is deferred to phase 10 (R55, R36–R38 deferred), so I split this in two:

**(a) Mechanical checks that don't need an AI and should run in `lint_draft` on the cut list from phase 4 (P8):**
- flash frames: any item shorter than 3 frames (125 ms)
- 1-frame gaps or black between main-track clips
- cuts **inside a word** or under 40 ms before a word onset (using `transcript_word`)
- caption phrase start more than ±80 ms from the speech onset
- caption on screen under 0.8 s, or reading speed above ~15 characters/s
- card hold below `card_hold_s`
- music not covering the runtime, or a music edit point not on a beat (when beats are known)
- punch-in beyond the resolution headroom
- DJI cutaway outside the 0.9–2.8 s rule
- a range with `tech:clipped` used
- an excluded range used

**(b) Judgement rows to add to §16.2 for when the critic exists (P12):**
- **Cutting:** jump cuts with too small a change (under ~10 % size or position change reads as a "pop"; either punch in ≥ 1.08× or cover it); props or hands jumping across a jump cut (lollipop in hand, then not); cuts on a blink or mid-gesture; breaths left at the head of a cut, or breaths all removed so she never breathes.
- **Cutaways:** DJI lip-sync where a mouth is visible; eyeline and screen direction (Ľuboš looking left in one cutaway and right in the next); the cutaway shows what the line says.
- **Audio edits:** clicks at cuts, room-tone holes, level jumps over 2 LU between adjacent clips, mouth clicks and lip smacks at phrase starts, plosives, laughs cut off.
- **Music edit:** internal re-cuts audible, ending on a musical phrase or a clean fade, not mid-bar.
- **Loop:** the last frame back to the first frame. Reels loop; a jarring loop costs rewatches.

#### Q8. Edits as the editor
**Edits is enough for this series.** For a 45–60 s, 2-camera, talking-head reel with captions, 1–2 map cards and one licensed bed, Edits for Mac (10 Nov 2026) now has what's needed: multi-track, keyframes, color wheels, curves and LUTs, voice enhance, MCP. It's also the only place tier-1 music can be used.

Its real limits for us:
- no 25 fps
- no interchange format (XML/OTIO/EDL), so an edit can't be moved to another editor
- no loudness meter documented (**unverified**)
- a first desktop release with weekly updates, which means playbook churn mid-series (the `version_seen` field matters)

I'd want **DaVinci Resolve** support (not Final Cut, unless Ľuboš already knows it) when any of these happens:
1. Cross-post masters with tier-2 music for YouTube/TikTok (R45, deferred).
2. More than 2 cameras, or Log footage that needs real matching.
3. Audio repair beyond voice enhance (a clipped lav on the hook).
4. Long-form or 16:9 recaps.
5. Edits or its MCP breaks during a series and a fallback editor is needed.

Don't build any of that now. Keep the cut list (P7) close enough to OTIO that an exporter is a later afternoon's work (R21 stays deferred).

### Proposals

#### P1. Probe flags frame-rate, VFR and HDR mismatches; cameras at 24p
- **Type:** addition
- **Section:** §5.1 (step 2) and DESIGN_LANGUAGE §6
- **Proposal:** Add `fps` to the project and compare it at probe time. Flag clips at a different rate, with variable frame rate, or with HDR/Log transfer. Record the camera setting in the design language.
- **Suggested spec text:**
  - §5.1 step 2, old: `2. Probe it: duration, codec, resolution, fps, audio channels, camera model and start timecode.`
  - new: `` 2. Probe it: duration, codec, resolution, fps, audio channels, camera model, start timecode, bit depth, chroma subsampling and color transfer. Flag the clip on the reel and in **Today** if (a) its fps differs from the project fps by more than 0.1 % (e.g. Sony 25p in a 24 fps project: Edits drops about one frame per second), (b) it's variable frame rate (`r_frame_rate` ≠ `avg_frame_rate`, typical for phones), or (c) it's HDR or Log (`color_transfer` arib-std-b67 / smpte2084, DJI D-Log M) in an SDR project. Flags inform; they don't block. ``
  - §6.1 project YAML, add after `platform: instagram`: `  fps: 24                                    # Edits supports 24 / 30 / 60 only`
  - DESIGN_LANGUAGE §6, add after the `picture:` YAML block: `- **Camera settings (from the next shoot):** both cameras at 24p (23.976 or 24), shutter 1/50 s to avoid 50 Hz light flicker, SDR (no HLG/Log) unless a LUT for that camera is registered. Edits has no 25 fps project, so 25p Sony footage drops a frame every second.`
- **Why:** Edits exports and projects are 24/30/60 only ([CineD](https://www.cined.com/instagram-edits-for-mac-released-multi-track-timeline-lut-import-and-watermark-free-4k-export/)). 25p in 24 stutters on movement, VFR phone clips drift out of sync, and HDR clips look washed out or blown in an SDR timeline. All three are invisible until the edit.
- **Priority:** before phase 0

#### P2. Proxy encoding spec; no edit proxies
- **Type:** change
- **Section:** §5.1 (step 3)
- **Proposal:** Specify the proxy encoding so scrubbing is frame-accurate and audio channels survive. Take frame-accurate checks from masters. State that Edits always uses the masters.
- **Suggested spec text:**
  - old: `3. Make a proxy: 540p H.264 for the UI and agents, plus a contact sheet every 2 s.`
  - new: `` 3. Make a proxy for the UI and agents: 540 px high, source aspect, H.264 High CRF 23, keyframe every 0.5 s (`-g 12` at 24/25p), source frame rate (no conform), source timecode, AAC 128 kbps 48 kHz with all source audio channels, faststart. Plus a contact sheet every 2 s. Frame-accurate checks (first frame, focus_x, critique frames) read single frames from the master. Edits always imports the masters; the Hub makes no edit proxies (fallback if Edits can't play a codec: a 1080p ProRes 422 Proxy copy, recorded as a playbook item). ``
- **Why:** Long-GOP proxies scrub to the wrong frame, which breaks `M`/`F` at the playhead and the J/K/L review in §20. Dropping ch2 loses the comparison between lav and camera mic. Edits has no proxy relink, so edit proxies would end up in the export.
- **Priority:** before phase 0

#### P3. Sync: coarse by words, fine by audio cross-correlation, two-point drift check
- **Type:** change
- **Section:** §5.2
- **Proposal:** Make audio cross-correlation the precise step, with transcript words only narrowing the search window. Check the offset at the start and end of each take.
- **Suggested spec text:**
  - old: `- Sync by **transcript alignment** (matching distinctive words) or audio cross-correlation, with a confidence score. The camera clock offset is stored per device per shoot (e.g. DJI = Sony − 24.85 s; clock 1 h off). For December a manually entered offset per device per shoot is enough.`
  - new: `- Sync in two steps: **coarse** from matching distinctive transcript words (or the stored clock offset) to within ±2 s, then **fine** by cross-correlating the two cameras' scratch audio (16 kHz mono) inside that window. Transcript timings alone are only accurate to 1–5 frames, which shows on cutaways with a visible mouth. The offset is stored per device per shoot with a confidence score (e.g. DJI = Sony − 24.850 s; clock 1 h off). **Drift check:** the offset is measured again near the end of each take; if the two differ by more than one frame (42 ms at 24 fps), the take is flagged and the drift stored. A manually entered offset per device per shoot always overrides (enough for December if auto-sync isn't ready).`
- **Why:** The Giro_00 cutaway of Ľuboš saying "Môže byť" needs lip-sync within 1 frame. Whisper word timings (±50–200 ms) can't guarantee that; cross-correlation gets ~1 ms. Consumer clocks drift about 1 frame per 13-minute take.
- **Priority:** before phase 1

#### P4. Audio QC at ingest and the DJI WAV as an alternate source
- **Type:** addition
- **Section:** §5.1 (new step after 6) and §5.1 Sidecars
- **Proposal:** Measure clipping, noise floor and loudness per clip. Attach the DJI WAV as a synced alternate audio source and report which source is cleaner per segment.
- **Suggested spec text:**
  - §5.1, add step 6a: `` 6a. **Audio QC:** find clipped ranges (3 or more consecutive samples at or above −0.1 dBFS), the noise floor between words, and short-term loudness per transcript segment. Clipped ranges get `tech: clipped` on the overlapping moments. Only numbers are stored. ``
  - §5.1 Sidecars, old: `` - **Sidecars:** read DJI `.LRF` (proxy) and `.WAV` (mic) and attach them to the parent clip. ``
  - new: `` - **Sidecars:** read DJI `.LRF` (proxy) and `.WAV` (mic) and attach them to the parent clip. The WAV is an **alternate audio source** in the take, synced with its parent's offset. Per transcript segment the Hub notes which source is cleaner (clipping, noise floor), so the editor can take a clipped passage, or Ľuboš's off-camera lines, from the DJI mic. The Hub never mixes or processes audio itself. ``
- **Why:** Giro_00's Sony source hit +1.6 dBFS, so it clipped. Clipping can't be fixed with gain, and nobody knows until they listen. Ľuboš's off-camera replies are recorded better by the DJI mic next to him than by Katarina's lav.
- **Priority:** before phase 1

#### P5. Moment fields: word-snapped range, tech flags, fact links, tag vocabulary
- **Type:** change
- **Section:** §5.3 (moment YAML) and §18 (`moment`)
- **Proposal:** Snap moments to word boundaries with default cut handles. Keep technical problems apart from the rating. Link stated facts. Use a fixed tag-prefix vocabulary.
- **Suggested spec text:**
  - In the §5.3 moment YAML, replace `  tags: [hook, curiosity, prop:lollipop, topic:maj, humor]` with:
    ```yaml
      tags: [beat:hook, tone:humor, prop:lollipop, topic:maj, time:evergreen]
      tech: []             # clipped | noise | mic_rustle | plosive | out_of_frame | soft_focus | flicker | blink_at_in
      fact_ids: []         # facts stated in this range; a moment warns when one becomes conflicting or outdated
    ```
  - Add after the YAML block: `` - **Ranges are word-snapped:** `src_in_ms` is the first word's onset and `src_out_ms` the last word's end (from `transcript_word`). Cuts use default handles of 120 ms before and 250 ms after, so initial consonants and word decays survive. ``
    `` - **Tag vocabulary** (prefix:value): `beat:` hook, who, promise, payoff, card_line, sign_off, cold_open, bumper, tease_next · `tone:` humor, tease, warm, serious, reaction, laugh · `topic:` / `stage:` / `place:` / `climb:` / `rider:` from the glossary · `prop:` · `people:` luboš_offcam, luboš_on_dji, duo · `craft:` one_take, needs_cover, clean_in, clean_out · `time:` evergreen, dated. `time:dated` moments ("zajtra", a date) aren't offered as unused gems for later reels. ``
  - §18 `moment` row, old: `id, clip_id, in_ms, out_ms, tags (json), rating, usable, reason, excluded_by, notes` → new: `id, clip_id, in_ms, out_ms, tags (json), tech (json), fact_ids (json), rating, usable, reason, excluded_by, notes`
- **Why:** Free-form tags drift ("hook", "Hook", "opening") and break ranking. A 5-rated clipped hook needs to look different from a clean one. A moment stating a fact that later becomes conflicting (Stage 1 Slovenia) must not be reused blindly.
- **Priority:** before phase 1

#### P6. Reframe and cutaway tokens: punch-in headroom
- **Type:** addition
- **Section:** DESIGN_LANGUAGE §6 (`picture:` YAML), used by §6.4 acceptance checks
- **Proposal:** Record how far each camera can punch in before dropping below 1080 px delivery width, and the minimum change that makes a jump cut read as deliberate.
- **Suggested spec text:**
  - In DESIGN_LANGUAGE §6 `picture:`, add under `main_cam:`: `    max_punch_in: 1.12              # 9:16 crop is 1215×2160; beyond 1.12× it's under 1080 px wide`
  - add under `bts_cam:`: `    max_punch_in: 1.50              # 9:16 crop is 1620×2880`
  - add at the end of `picture:`: `  jump_cut: { min_punch_in: 1.08, else: dji_cutaway }   # a same-size jump cut with a small shift reads as a glitch`
- **Why:** The design language says jump cuts are on-brand but doesn't say how to make them read as deliberate. The Sony only has 12 % headroom, so an agent will easily over-zoom without a stated limit.
- **Priority:** before phase 9

#### P7. Cut-list schema for versions
- **Type:** change
- **Section:** §11.1 and §18 (`version.cut_list`)
- **Proposal:** Replace the one-line description with a schema complete enough to rebuild the edit through the Edits MCP. Duplicate the Edits project per version if the MCP supports it.
- **Suggested spec text:**
  - old (§11.1): `Each draft is a **version** (v1, v2, …) with the Edits project ID, a cut-list snapshot (clips, in/out, overlays, captions, music), runtime and an optional low-res preview.`
  - new:
    ````markdown
    Each draft is a **version** (v1, v2, …) with the Edits project ID, a cut-list snapshot, runtime and an optional low-res preview. The cut list must be complete enough that an agent can rebuild the edit in a new Edits project through the Edits MCP (tier-1 music by its Edits ID, never as audio). If the Edits MCP can duplicate a project, `create_version` also keeps a copy named `<slot>_v<n>`.

    ```yaml
    cut_list:
      schema: 1
      edits_project: Giro_00_Intro
      edits_version_seen: "2026.11.10"
      design_language: "1.1"
      prompt_version: 3
      timeline: { fps: 24, canvas_px: [2160, 3840], runtime_ms: 50900 }
      main:
        - { t_in_ms: 0, t_out_ms: 6400, clip: giro00-sony-c0031, src_in_ms: 490100, src_out_ms: 496500, speed: 1.0, moment: mom_0001,
            transform: { scale: 3.16, focus_x: 0.545, focus_y: 0.50 }, grade: none, audio: { source: sony_lav, gain_db: -2.0, muted: false } }
      overlays:
        - { layer: 1, t_in_ms: 10700, t_out_ms: 13500, clip: giro00-dji-0039, src_in_ms: 284050, src_out_ms: 286850, speed: 1.0,
            transform: { scale: 2.37, focus_x: 0.27, focus_y: 0.50 }, grade: dji_preset, audio: { muted: true } }
      graphics:
        - { asset: map-italy-terst-rim, file_hash: "xxh64:…", layer: main, t_in_ms: 42700, t_out_ms: 46200, transform: { scale: 1.0 } }
      text:
        - { t_in_ms: 42700, t_out_ms: 46200, text: "Štart v Terste,\ncieľ v Ríme.", font: Monstera-Black, size: 30, color: "#FFFFFF", y: 0.66, animation: none }
      captions:
        style: "Word Highlight Box V3"
        y: 0.73
        items:
          - { t_in_ms: 0, t_out_ms: 1450, text: "Prečo je toto lízatko ružové?", speaker: katarina }
      music:
        - { asset: music-dolce-vita, track_in_ms: 0, t_in_ms: 0, t_out_ms: 50900, recuts: [],
            levels: [[0, 0.0], [300, 0.2], [42300, 0.2], [42700, 0.8], [46200, 0.8], [46600, 0.2], [49700, 0.2], [50900, 0.0]] }
      sfx: []
      export: null   # after approval: { resolution: 2K, fps: 24, range: SDR, rel_path, hash, lufs_i, true_peak_dbtp }
    ```
    Times are integer ms; `levels` are [timeline ms, Edits level] pairs; `recuts` list internal music edits (music doesn't ripple in Edits). The diff view compares two cut lists item by item.
    ````
- **Why:** Today's description (clips, in/out, overlays, captions, music) would lose exactly what took time in Giro_00: focus_x 0.545, the DJI grade, dialogue −2 dB, the music re-cut and its 0.2/0.8 ramps. Without a schema, "restore v3" isn't possible and the diff view has nothing to compare.
- **Priority:** before phase 4

#### P8. Cut-list lint for craft errors in `lint_draft`
- **Type:** addition
- **Section:** §9 (Style lint) and §17.2 (`lint_draft`)
- **Proposal:** Add deterministic editing checks that run on the cut list plus `transcript_word`. No AI or render needed.
- **Suggested spec text:** In §9, after the style-lint list, add:
  `` - **Cut lint** (on the version's cut list and word timings, no render needed): items shorter than 3 frames (flash frames); gaps or black between main-track clips; a cut inside a word or less than 40 ms before a word onset; caption start more than 80 ms from the speech onset, captions shorter than 0.8 s or faster than about 15 characters per second; card hold below `card_hold_s`; DJI cutaway outside 0.9–2.8 s; punch-in beyond `max_punch_in`; same-size jump cut (scale change under `jump_cut.min_punch_in` with no cutaway); music not covering the runtime; a used range with `tech: clipped` or an excluded range. Results are listed in editors_notes.md under open items if not fixed. ``
  §17.2, old: `` - `lint_draft(edits_project_id | frame_sheet)` → style violations `` → new: `` - `lint_draft(edits_project_id | frame_sheet | version)` → style violations and cut-lint findings (§9) ``
- **Why:** These are the errors that automated editing actually produces (clipped consonants, 1-frame gaps, stale captions). They're cheap to catch from data the Hub already has, and the AI critic that could catch them is deferred to after December.
- **Priority:** before phase 4

#### P9. Loudness target and export check
- **Type:** change
- **Section:** §15.3 (`music_mix`), DESIGN_LANGUAGE §9, §17.2 (Music)
- **Proposal:** Express targets in LUFS/LU, not only Edits gain factors. Add a local measurement of the exported file (numbers only).
- **Suggested spec text:**
  - §15.3, add to the `music_mix` YAML:
    ```yaml
      deliver: { integrated_lufs: -14, tolerance_lu: 1.5, true_peak_dbtp: -1.0 }
      music_under_speech_lu: -15..-18    # relative to dialogue; 0.20 is only the Dolce Vita starting value
      max_jump_between_sentences_lu: 3
    ```
  - §17.2 Music, add: `` - `check_export(reel, path)` → resolution, fps, duration vs. version runtime, integrated LUFS and true peak (ffmpeg ebur128, measured locally); numbers are stored on the version, the audio never is (§22) ``
  - DESIGN_LANGUAGE §9, add after the YAML: `- **Delivery loudness:** −14 LUFS integrated (±1.5 LU), true peak ≤ −1 dBTP, measured on the export. Meta publishes no target; this is common practice (checked 2026-11-12). Speech peaks alone (≈ −3 dBFS) don't tell loudness.`
- **Why:** The same 0.20 factor puts a differently mastered track several dB louder or quieter under speech. Peaks say nothing about perceived loudness. Measuring the exported file locally is allowed under R44 (levels only, local).
- **Priority:** before phase 8

#### P10. Color: per-camera preset plus a mismatch flag, no computed grades
- **Type:** change
- **Section:** §5.1b (Color match)
- **Proposal:** Replace "suggest grade values" with "flag mismatches against the camera's reference shoot"; the grade itself comes from the design-language preset.
- **Suggested spec text:**
  - old: `- **Color match:** compare histograms of synced Sony and DJI frames and suggest grade values (exposure, temperature) for the DJI cutaways.`
  - new: `- **Color check:** for synced Sony/DJI frame pairs, compare mean L*a*b* of the centre 50 % of the frame with the same camera pair's reference shoot. Flag the clip if |ΔL*| > 5 or |Δb*| > 4. The grade itself is the camera's preset from the design language (DESIGN_LANGUAGE §6), applied by the agent; the Hub doesn't compute slider values (Edits' sliders aren't calibrated units). Once a preset is stable it may be saved as a LUT asset for Edits (format to be confirmed).`
- **Why:** Histogram matching can't be translated reliably into Edits slider values. What actually goes wrong between shoots is a changed white balance or light, and a flag catches that.
- **Priority:** later

#### P11. Edits playbook: Edits for Mac capabilities and frame-rate test
- **Type:** addition
- **Section:** §14 (playbook YAML)
- **Proposal:** Record the Edits for Mac release facts the prompt depends on, and one open test.
- **Suggested spec text:** Add to `items:` in §14:
  ```yaml
        - "Edits for Mac (released 2026-11-10): multi-track, keyframes, color wheels/curves, Log conversion, LUT import (formats unpublished), voice enhance, export HD/2K/4K at 24/30/60 fps SDR/HDR. Weekly updates: re-check quirks per version."
        - "No 25/50 fps project or export. 25p clips in a 24 fps project: behaviour to test (expected: one dropped frame per second)."
        - "2K (1440×2560) export is enough for Sony-based 9:16; Sony's 9:16 crop is only 1215 px wide."
  ```
- **Why:** The playbook was written against the mobile app (version_seen 2026.10.19-1); the desktop app changes what agents can do (keyframed push-ins, LUTs) and what will change weekly. Source: [CineD, 10 Nov 2026](https://www.cined.com/instagram-edits-for-mac-released-multi-track-timeline-lut-import-and-watermark-free-4k-export/).
- **Priority:** before phase 9

#### P12. Critique rows for editing craft
- **Type:** addition
- **Section:** §16.2
- **Proposal:** Add the editing-craft areas the critic should judge (the mechanical ones are in P8).
- **Suggested spec text:** Add rows to the §16.2 table after **Pacing**:
  ```markdown
  | **Cutting** | Jump cuts with too small a change (reads as a glitch)? Props or hands jumping across a cut? Cuts on a blink or mid-gesture? Breaths left at cut heads, or all breaths removed? |
  | **Cutaways** | DJI lip-sync where a mouth is visible; consistent eyeline and screen direction; does the cutaway show what the line says? |
  | **Audio edits** | Clicks at cuts, room-tone holes, level jumps over 2 LU between clips, mouth clicks, plosives, laughs cut off |
  | **Music edit** | Re-cuts audible? Ends on a phrase or a clean fade, not mid-bar? |
  | **Loop** | Does the last frame → first frame loop read cleanly? |
  ```
- **Why:** The current list covers story, captions and design, but none of the craft errors a viewer feels without naming them. These are the main reason an AI-assembled cut reads as amateur.
- **Priority:** before phase 10

**Sign-off:** approve with changes (P1–P5 before phases 0–1, P6–P8 before phases 9 and 4; the rest before their phases)
