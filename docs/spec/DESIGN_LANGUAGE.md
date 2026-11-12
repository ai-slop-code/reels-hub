---
series: "Giro d'Italia 2027 – December Reels"
series_id: giro2027-advent
host: Katarina
crew: Ľuboš (camera, off-camera voice)
language: sk
format: instagram-reel
aspect: "9:16"
canvas_px: [2160, 3840]
capture_fps: 25                 # both cameras (§6); 50p only for intended slow motion
edits_project_fps: null         # to check once on the run machine (Reels Hub spec §14)
reference_episode: Giro_00_Intro
reference_runtime_s: 50.9
doc_version: 1.2
updated: 2026-11-12
---

# Design language: Giro 2027 Reels

This is the house style taken from the Day 1 intro (`Giro_00_Intro`). Use it for every Reel in the series and for future cycling series.
Values marked **(measured)** are what the intro actually uses. Values marked **(default)** are rules to follow where the intro set no precedent.

The front matter and the YAML blocks below are machine-readable, so an asset-tracking app can import them directly.

---

## 1. Brand core

| Principle | What it means on screen |
|---|---|
| **An invitation, not a broadcast** | Katarina's own words, humor and jump cuts. No polished presenter VO and no stock voice. |
| **Maglia rosa as the thread** | Pink is the only accent color. It marks the active word, cities on maps and emphasis. Nothing else is colored. |
| **Calm maps, loud person** | Graphics are flat, dark and quiet so Katarina stays the energy. Maps are never busy. |
| **Behind the scenes is part of the story** | The second camera (DJI) shows Ľuboš and the set, used when it reveals something the main camera missed. |
| **Sound-off first** | Every beat must make sense muted: captions on all speech, and a short line on every silent beat. |

---

## 2. Color tokens

```yaml
color:
  pink:        "#F27BAA"   # maglia rosa accent: city dots, map labels, emphasis titles, map border dashes
  navy:        "#0F1C2B"   # sea / background of all graphics; also dark text ("ink")
  land:        "#24323F"   # neighbouring countries
  land_line:   "#3A4A5A"   # borders between neighbouring countries
  land_alt:    "#33475A"   # highlighted neighbour (e.g. Slovenia on close-ups)
  italy:       "#EFE6DA"   # Italy fill (warm off-white)
  italy_line:  "#FFFFFF"   # Italy outline
  sea_label:   "#8FA3B8"   # sea / water names
  text:        "#FFFFFF"   # all on-screen titles over footage or navy
```

**Rules**
- Pink (`#F27BAA`) is the only saturated color. Never use a second accent.
- White text goes over footage or navy. Navy text goes only on the Italy fill, with an Italy-colored halo.
- The footage itself is warm (pink T-shirt, wood kitchen). Don't grade it cooler to match the graphics; the contrast is intended.

---

## 3. Typography

| Role | Font | Where it's set | Notes |
|---|---|---|---|
| Captions | **Monstera-Black** | Edits caption style `Word Highlight Box V3` | Sentence case. Diacritics verified (Ľ, Š, ť, ô, á). |
| On-screen titles | **Monstera-Black** | Edits `setTextFont` | Same face as captions so everything reads as one system. |
| Map labels | **Avenir Next** (Helvetica Neue fallback) | Baked into PNG by `tools/mkmap.py` | Bold 700 for places, Medium 500 for water. |

```yaml
type:
  caption:
    edits_style: "Word Highlight Box V3"
    font: "Monstera-Black"
    case: sentence
    hides_end_punctuation: true      # style limitation: '?' and '.' at line end are not shown
  title:
    font: "Monstera-Black"
    color: "#FFFFFF"                 # or pink for the single most important line
    sizes_edits_units:               # Edits text size units, at 2160x3840 canvas (measured)
      map_headline: 48               # e.g. "21 etáp" (pink)
      card_line: 30                  # e.g. "Štart v Terste, / cieľ v Ríme."
      subtitle: 26
      top_title: 28                  # two-line title at top of frame
    max_lines: 3
    max_chars_per_line: 22           # Monstera wraps early; break lines by hand with \n
  map_label:
    font: "Avenir Next"
    city: { size_px: 54, weight: 700, color: "#FFFFFF", halo: "#0F1C2B", halo_px: 10 }
    country: { size_px: 58, weight: 700, letter_spacing: 6, case: upper }
    water: { size_px: 44, weight: 500, color: "#8FA3B8" }
```

**Glyph gotchas (measured)**
- Monstera-Black has **no en dash (–)**. Write `od 8. do 30. mája`, not `8. – 30. mája`.
- Break long titles yourself with line breaks. Edits text boxes wrap at about 70 % of frame width.

**Font licensing**
- Monstera-Black is an Edits font: use it only inside Edits. Never extract it or copy it into other tools.
- Avenir Next is a macOS system font: use it only in the Mac-side `mkmap.py` pipeline. Never copy it into the Reels Hub container.
- Graphics made outside Edits (HyperFrames, container-rendered maps) use only registered fonts licensed for video, social and server use (default SIL OFL), covering Slovak diacritics and the en dash. Record the font and its license in the reel's `editors_notes.md`.

---

## 4. Captions

```yaml
captions:
  language: sk
  coverage: all_intelligible_speech     # hook, off-camera lines, DJI dialogue, sign-off
  position_y: 0.73                      # normalized centre, clear of face and Reels UI
  phrase_length_words: 3-8
  break_at: natural_phrase_boundaries
  speaker_label: "Meno: "               # only for off-camera speakers, e.g. "Ľuboš: Môže byť."
  numbers:
    words: [idiomatic_ages_and_decades, approximate_quantities, determiner_one]   # "po tridsiatke", "pár dní", "každý deň jedna etapa"
    digits: [counts_with_noun, exact_ages, measurements, years, dates]            # "24 dní", "21 etáp", "má 28 rokov", "172 km"
    ordinals: "digit + dot: 1. etapa, 8. mája; never at line end"
    decimal_separator: ","            # 3 418,9 km
    thousands_separator: nbsp         # 3 419 km (always, from 1 000)
    unit_spacing: "172 km, 8 %, 25 €; adjective: 8-percentné"
    time: "14:30"
    ranges: "od 8. do 30. mája"       # Monstera has no en dash
  fidelity: clean_verbatim            # her words and word order; no fillers, stutters or false starts
  keep: [discourse_particles, dialect_words, her_italian_words, affectionate_forms]
  fix_silently: [spelling, diacritics, case_and_agreement_endings]
  never: [change_words, reorder, fix_facts_in_captions, translate_her_italian]
  place_names: as_said                # Trieste stays Trieste if she said it; titles, maps and post use exonyms (§7)
  line_breaks:
    never_split: [preposition+noun, number+unit_or_noun, first+last_name, "Giro d'Italia", ordinal+noun]
    never_end_line_with: [single_letter_words, ordinal_number]   # v k s z o u a i; "30." loses its dot
    prefer_break_before: ["že", "ktorý", "ale", "lebo", "keď"]
  questions: >
    The style hides a line-final "?". A question without a question word (prečo, kde, kedy, ako,
    koľko, kto, čo, ktorý, či) or tag (nie?, však?, hej?) must not end a caption line; move the
    break or set it as a title, and note it in editors_notes.md.
  quotes: "„…“"                       # glyphs unverified in Monstera; if missing, avoid quotes
  sound_tags: "[cvakanie voľnobežky]"   # square brackets, lowercase, only when they explain a reaction
  highlight: pink active word (style default)
```

**Fidelity:** captions are clean verbatim. Keep her words, word order, humor, meaningful particles, her Italian words and her dialect words (glossary `keep_as_said`). Drop hesitation sounds, stutters, false starts and pure fillers. Silently fix spelling, diacritics and case endings ("21 etapy" → "21 etáp"). Never fix a fact in a caption: a factual slip goes into `editors_notes.md` as an open item, and the line is re-cut or dropped. Place names are captioned as she said them (Trieste or Terst).

**Foreign terms.** No italics (captions, titles, post). Original spelling and diacritics (Pogačar, Roglič). Italian common nouns lowercase (maglia rosa). "Giro" declines like *mesto* (byť na Gire, ísť na Giro, víťaz Gira); "Giro d'Italia", "Tour de France" and "Strade Bianche" are indeclinable; "Vuelta" declines. Male rider surnames decline by Slovak rules (Pogačara, s Gannom, Cicconeho). Straight apostrophe in d'Italia; none in hashtags.

**Workflow**
1. Do all trims first, **then** generate captions. Captions made before a trim keep stale timings and leave ghost captions that can't be deleted.
2. Run `generateCaptions(source: video, language: sk)`.
3. Correct against the word-level transcript, especially town names, climbs, riders, and slang the model mishears (e.g. "lízatko" came out as "lyžičko").
4. Split and merge at phrase boundaries, then re-apply the caption style. Splits reset the style.
5. Do a muted pass with a frame sheet of the whole timeline. The opening, the promise and the ending must all read without sound.

---

## 5. Layout and safe zones (9:16)

```yaml
layout:                    # normalized 0–1, origin top-left, element centres
  reels_top_ui:      [0.00, 0.07]   # keep clear
  top_title_y:       0.088–0.13     # titles above Katarina's head
  face_band:         [0.15, 0.35]   # Katarina's face in the filled Sony frame; no text
  map_band:          [0.12, 0.69]   # Italy overview occupies this band
  card_text_y:       0.58–0.76      # text on map cards, below the land
  caption_y:         0.73
  reels_bottom_ui:   [0.80, 1.00]   # username / description; keep clear
  reels_right_rail:  { x: [0.88, 1.0], y: [0.55, 0.90] }  # like/comment buttons
```

- Center all text horizontally (x = 0.5).
- Never stack a title and a caption in the same band. If a card line sits at 0.76, there is no caption during that card.
- Map city labels sit to the right of the dot, offset by about 34 px. On close-ups, put the label left of the dot (`anchor=end`) so it stays on land.

---

## 6. Picture

```yaml
picture:
  main_cam:
    id: sony
    source: "3840x2160 25p, kitchen set"
    fit: fill                       # 16:9 → 9:16 crop, scale ≈ 3.16
    focus_x: 0.50                   # 0.545 when Katarina is off-centre (hook shot)
    grade: none                     # shot is already warm and correctly exposed
    max_punch_in: 1.12              # 9:16 crop is 1215×2160; beyond 1.12× it's under 1080 px wide
  bts_cam:
    id: dji
    source: "3840x2880 25p, wide behind-the-scenes"
    fit: fill                       # scale ≈ 2.37
    focus_x: 0.24–0.30              # Ľuboš / tripod side of frame
    audio: muted                    # Sony carries all dialogue
    grade: { exposure: 0.5, shadows: 0.3, temperature: 0.15, contrast: 0.1 }   # preset, applied as is
    max_punch_in: 1.50              # 9:16 crop is 1620×2880
    clock_offset: "DJI = Sony − 24.85 s (DJI clock 1 h off; re-measure per shoot)"
  frame_rate: { both_cameras: 25p, slow_motion: 50p }   # no 24p switch, no NTSC mode
  jump_cut: { min_punch_in: 1.08, else: dji_cutaway }   # a same-size jump cut with a small shift reads as a glitch
  cutaway_rule: >
    Cut to DJI only when it reveals something the Sony missed: who Ľuboš is,
    his reaction, the role swap. Hold 0.9–2.8 s, keep Sony audio underneath.
```

- **Frame rate:** shoot **25p on both cameras** (Sony and DJI). Use 50p only for shots intended as slow motion. Giro_00 was edited in Edits from 25p footage and published. Which project frame rate Edits uses (24/25/30) and how it conforms 25p is checked once on the run machine and recorded in the Edits playbook (Reels Hub spec §14). The Hub flags clips whose frame rate differs from the reel's other clips, and VFR or HDR/Log clips.
- **Grade:** each camera's grade is its preset above, applied by hand in Edits. No computed grade values.

- **First frame:** the subject must be fully in frame from frame 1. Adjust `focus_x` per shot rather than accept a half-out first frame.
- **Jump cuts are on-brand.** Make them read as deliberate with a punch-in of at least 1.08× (within `max_punch_in`), or hide them with a DJI cutaway when the cut is distracting.
- **Props are part of the look:** pink tee, advent calendar, cycling calendar, bidons, Chupa Chups lollipop. Keep the kitchen set consistent across episodes.

---

## 7. Graphics: maps

All maps come from `tools/mkmap.py`. It's a pure-Python SVG generator with no dependencies, rendered to PNG with macOS `qlmanage` and cropped with `sips`.

```yaml
maps:
  generator: tools/mkmap.py
  data: "Natural Earth 1:10m admin-0 countries v5.1.2 (public domain)"
  canvas: [1080, 1920]
  projection: equirectangular, cos(mid-latitude) scaled
  style:
    sea: navy; neighbours: land; italy: italy fill + white outline
    city_dot: { r: 16, fill: pink, stroke: "#FFFFFF 5px", glow: [r*2 @35%, r*3.2 @22%] }
    highlighted_border: { stroke: pink, width: 7, dash: "18 12" }
  views:
    italy_overview: { lon: [6.2, 19.2], lat: [36.3, 47.4], band_px: [230, 1330] }
    trieste_closeup: { lon: [12.95, 14.75], lat: [45.05, 46.25] }
  naming: "map_<place>[_<place>][_border].png"
  labels_language: sk   # exonyms per the Reels Hub spec §8 place-name policy: Terst, Rím, TALIANSKO, SLOVINSKO, Jadranské more; otherwise the Italian original (Bolzano)
```

**Rules**
- **No precise route traces** from Natural Earth. For a stage route, rebuild it from the official list of towns and climbs on OpenStreetMap data (credit "© OpenStreetMap contributors" in the caption).
- **Never trace, show or screen-record the organizer's maps**, stage profiles, photos or logos.
- **Place names on maps and titles:** the Slovak exonym only if it's on the ÚGKK list and in current media use (Terst, Rím, Neapol, Miláno, Turín, Janov, Benátky, Florencia, Ľubľana); otherwise the Italian original, inflected in Slovak (v Bolzane; Padova, not Pádua). Never coin an exonym.
- **Show only what the line needs:** one or two dots per card. Light up cities in the order they're spoken (e.g. Terst, then Rím on "21 etáp").
- **Don't give away tomorrow's answer.** A teaser map shows the place, not the route.
- Text on maps is added in Edits, not baked into the PNG, so it stays editable.

**Render pipeline (macOS)**
```bash
python3 -I tools/mkmap.py <ne_10m_admin_0_countries.geojson> graphics/
```
```bash
cd graphics && for f in *.svg; do qlmanage -t -s 1920 -o . "$f" >/dev/null 2>&1; sips -c 1920 1080 "$f.png" --out "${f%.svg}.png" >/dev/null; rm "$f.png"; done
```
The SVGs are drawn on a padded square canvas because `qlmanage` renders square thumbnails; the crop restores 1080×1920.

---

## 8. Motion and on-screen text

```yaml
motion:
  text_animation: none (hard in / hard out)   # measured; captions carry the animation
  title_hold_s: 2.5                           # minimum for a two-line title
  card_hold_s: 3.5                            # map card with two short lines
  map_sequence: cut between PNG states (no keyframed zoom yet)
  transitions: hard cuts only
```

---

## 9. Sound

```yaml
audio:
  dialogue:
    source: sony (lav)
    gain: 0.78–0.82                 # source peaks hit +1.6 dBFS; pulls to ≈ −3 dBFS peak on playback
  music:
    track: { title: "Dolce Vita", artist: "Italian Atmosphere", edits_id: "1123460523193316", license: licensed }
    character: Italian instrumental, steady beat (≈95 BPM), light percussion
    lane: separate audio track (replaceable)
    level_under_speech: 0.20        # ≈ 15 dB below dialogue peaks for Dolce Vita (measured); a starting value only
    level_under_speech_lu: -15..-18 # the rule: music 15–18 LU below dialogue, whatever the track's mastering
    level_on_silent_card: 0.80      # ≈ −6 to −8 dBFS peaks
    ramps_s: 0.4                    # into / out of the loud card section
    fade_in_s: 0.3
    fade_out_s: 1.2
  deliver: { integrated_lufs: -14, tolerance_lu: 1.5, true_peak_dbtp: -1.0 }   # measured on the export
  sfx: only when it explains a reaction; caption it in [brackets]
```

- **Delivery loudness:** −14 LUFS integrated (±1.5 LU), true peak ≤ −1 dBTP, measured on the export (`ffmpeg -af ebur128=peak=true`, numbers only). Meta publishes no target; this is common practice (checked 2026-11-12). Speech peaks alone (≈ −3 dBFS) don't tell loudness.

- **Keep one music bed per series** for recognition. Change it only per season or per series.
- Licensed (commercial) music downloads in Edits. The royalty-free tab failed with `DownloadError 3` as of 2026-11-11. Licensed tracks can't be analyzed offline, so listen before approving.

---

## 10. Story structure (episode template)

```yaml
structure:
  - beat: hook          # curiosity stated by 3 s (line may run to 6 s); frame 1 is content; first word ≤ 0.3 s; captioned
  - beat: who           # Day 1 intro only; stage episodes: none (Ľuboš appears as a cutaway reaction or in the sign-off)
  - beat: promise       # what this episode gives, by ~8 s in stage episodes; one map or graphic max
  - beat: payoff        # one idea: the stage story / place / how to get there
  - beat: card          # silent 3.5 s map card, music up; text per the series experiment (Reels Hub spec §13.2): tease or statement
  - beat: sign_off      # natural "Čaute" exchange; keep Ľuboš's off-camera reply; ≤ 3 s
target_runtime_s:
  intro: 45–60
  stage: 35–50          # hard cap 60
  finale: 45–75
```

- Most viewers meet a stage episode mid-series from recommendations, so every episode must stand alone and must not open with a repeated introduction.

**Editorial rules**
- Use only words Katarina actually said. Any proposed line is labeled a **pickup** in the reel's `editors_notes.md` and never shown as her speech.
- Never join fragments from different sentences or takes into one sentence. Cutting filler or false starts inside one continuous thought is fine.
- Leave crude banter out of the cut. It's fine on set, not on the channel.
- Facts come from giroditalia.it (stage pages and route announcement). Spectator access comes from transport operators or local authorities. Put the links in the reel's `editors_notes.md`.
- Render only after explicit producer approval of that version.

---

## 11. Asset registry (for the tracking app)

```yaml
assets:
  - id: giro00-sony-c0031
    type: footage
    camera: sony
    path: raw/sony/C0031.MP4
    duration_s: 772.8
    content: "Full intro monologue (advent calendar, lollipop/máj, 24 dní / 21 etáp, trip tips, sign-off)"
    reusable_moments:
      - { src_s: [490.1, 496.5], tag: hook-lollipop-maj, used_in: giro00 }
      - { src_s: [304.6, 318.4], tag: intro-po-tridsiatke, used_in: giro00 }
      - { src_s: [684.0, 688.5], tag: promise-24dni-21etap, used_in: giro00 }
      - { src_s: [721.5, 740.9], tag: promise-tipy-vylet, used_in: giro00 }
      - { src_s: [743.0, 747.75], tag: signoff-lubosko, used_in: giro00 }
      - { src_s: [518.0, 537.7], tag: tongue-twister-geopoliticko, used_in: null }   # unused gem
      - { src_s: [463.9, 489.7], tag: advent-chupa-chups, used_in: null }
      - { src_s: [764.7, 769.5], tag: luboš-kameraman-cameo, used_in: null }
    exclude: [[85, 115], [204, 232], [762.5, 764.1]]   # crude banter
  - id: giro00-sony-c0030
    type: footage
    camera: sony
    path: raw/sony/C0030.MP4
    content: "Pre-roll / framing test"
  - id: giro00-dji-0039
    type: footage
    camera: dji
    path: raw/dji/DJI_20261111212649_0039_D.MP4
    sync: "sony_s − 24.85"
    content: "BTS wide of the main take; Ľuboš at tripod"
  - id: giro00-dji-0038
    type: footage
    camera: dji
    path: raw/dji/DJI_20261111211157_0038_D.MP4
    content: "Set-up, lighting and framing discussion"
  - id: map-italy-terst
    type: graphic
    path: graphics/map_trieste.png
    source_svg: graphics/map_trieste.svg
  - id: map-italy-terst-rim
    type: graphic
    path: graphics/map_trieste_roma.png
    used_in: [giro00]
  - id: map-terst-slovinsko
    type: graphic
    path: graphics/map_trieste_border.png
    note: "Close-up for the Stage 1 border episode"
  - id: music-dolce-vita
    type: music
    title: "Dolce Vita"
    artist: "Italian Atmosphere"
    edits_audio_asset_id: "1123460523193316"
    license: licensed-instagram
  - id: tool-mkmap
    type: tool
    path: tools/mkmap.py
episodes:
  - id: giro00
    title: "Úvod série"
    edits_project: Giro_00_Intro
    runtime_s: 50.9
    status: posted
    notes: review_notes.md
    caption: instagram_caption.txt
```

From Giro_01 on, every reel ends with an `editors_notes.md` (template: [Reels Hub spec §11.4](REELS_HUB_SPEC.md#11-module-g-reviews-feedback-and-approvals)). Its "Graphics used" table refers to the asset IDs above, so the Reels Hub graphics overview can show which reels use each asset and where. Giro_00's `review_notes.md` is the model.

---

## 12. Production workflow notes

- **Sandbox:** Edits can't read `~/Personal`. Hard-link the footage into `~/Movies/<Episode>_raw/` (no extra disk space), and copy graphics there.
- **Sync** the two cameras by matching one distinctive word in both transcripts (e.g. "Drahí"). Re-check at a second point.
- **Edits API quirks (as of 2026-11-11):**
  - `addMediaPanelItemsToTimeline` with `startTime` lands on an overlay; call `convertToMain` afterwards.
  - `trimClip` uses a positive delta to shorten and a negative delta to extend.
  - Overlays, text and captions ripple with main-track trims; **music does not**, so re-cut it by hand.
  - `moveToLayer` can move text into the caption track; check layer order after.
- **Folder layout per episode:**
  ```
  Giro_XX_<Name>/
    raw/{sony,dji}/
    graphics/          # PNG + SVG
    tools/             # shared scripts (mkmap.py)
    editors_notes.md   # story, clips, graphics, music + license, practices, checklist, open items (Giro_00: review_notes.md)
    instagram_caption.txt
    DESIGN_LANGUAGE.md # copy or link from the series root
  ```

---

## 13. Post caption (Instagram)

The editing agent drafts the post caption as part of the edit and records it in the reel's `editors_notes.md` (Reels Hub spec §8.1).

```yaml
post_caption:
  first_line: the hook, matching the spoken hook's topic; no hashtag or @
  facts: every number, date or place claim has a fact ID
  last_line: "Zajtra: {n+1}. etapa."     # matches the next reel
  cta: exactly one (send | save | comment vote)
  hashtags: { max: 5, form: "original or international, lowercase, no diacritics" }   # Instagram's limit per post
  location_tag: where it fits (e.g. the stage start town)
  language: Slovak, glossary forms, place names per §7; no "oficiálny"
  disclosure: paid-partnership label if any commercial flag is set
```

- **Max 5 hashtags per post.** Instagram blocks more (lesson from Giro_00, whose caption draft had 8).
