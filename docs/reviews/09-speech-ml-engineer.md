# Review packet 09: speech / ML engineer

**Priority:** before phase 1 (transcripts and moments)
**Time needed:** ~2 h
**Decisions already made:** D4 consent for voice prints; D7 faster-whisper / WhisperX / pyannote accepted; D9 runs in Podman (no Mac GPU inside) (see [README](README.md#decisions-already-made-please-dont-reopen)).

## Why you
Everything downstream (moments, captions, critique, search) depends on accurate Slovak transcripts with word timing and speaker labels.

## Read
- [§5.1, 5.1a, 5.1b, 5.2, 5.4](../spec/REELS_HUB_SPEC.md#5-module-a-footage-index-and-moments): ingest, transcription engine, computer vision, sync, search
- [§8 Glossary and caption intelligence](../spec/REELS_HUB_SPEC.md#8-module-d-glossary-and-caption-intelligence)
- [§23.4–23.5 Mac constraints and transcription helper](../spec/REELS_HUB_SPEC.md#23-deployment-podman)

## Questions
1. **Benchmark design:** test set from Giro_00 (C0031, 13 min, plus DJI). Metrics: word error rate, proper-name accuracy, word-timing error, speaker accuracy, speed. What else, and how big should the set be?
2. **Engines:** mlx-whisper (Mac GPU, via helper) vs. faster-whisper / WhisperX (CPU in Podman). Expectations for Slovak with large-v3? Any Slovak-tuned models worth testing?
3. **Glossary hint:** passing names as an initial prompt. Does it help, and how long can the list be before it hurts?
4. **Speaker labels:** pyannote diarization plus voice prints for Katarina and Ľuboš. Recommended setup for two known speakers plus occasional others?
5. **Word timestamps:** captions need accurate word timing after edits. WhisperX alignment vs. native timestamps?
6. **Search:** text and frame embeddings for Slovak. Which models run well locally (CPU in Podman)?
7. **Sync:** transcript-based camera sync (Sony vs. DJI offset). Better done with audio cross-correlation? Combine both?
8. **Re-runs:** when a better model ships, re-transcribe everything? How do we keep manual corrections?

## Your input

*Reviewer: AI acting as a senior speech / ML engineer, against spec v0.5. Sources checked on 2026-11-12 are linked; anything I couldn't check is marked **unverified**.*

### Summary
The speech stack is the right family (Whisper + forced alignment + pyannote), but four things in §5.1a are likely to fail on first contact. (1) **Base `large-v3` is weak on Slovak conversational speech.** Public numbers show 16–20 % WER for it. The open Slovak fine-tunes from KInIT (MIT / Apache-2.0) cut that to about 6–8 %, and the turbo variant is about 4× cheaper to decode, which is what makes **CPU-only transcription in Podman** realistic. That one benchmark entry probably decides whether the §23.5 helper is needed at all. (2) **The benchmark reference doesn't exist yet.** The "corrected Edits transcript" covers only the ~45 s that made it into the reel, not 13 minutes, so the owner needs to budget about 3–4 h to build a real reference. (3) **The glossary "initial prompt" is mostly ignored after the first 30 s window** in faster-whisper's sequential mode. Use per-window `hotwords`, capped at about 150 tokens. (4) **Camera sync should be audio cross-correlation first.** Transcript word timing (±100–300 ms) isn't frame-accurate. Smaller fixes: transcribe one primary audio source per take, force `language="sk"` instead of detecting it per segment, and keep the raw transcript separate from corrections so re-runs don't destroy manual fixes.

### Answers

#### Q1. Benchmark design
**The reference is the main cost.** Giro_00's "corrected Edits transcript" covers only the captioned ranges (~45 s of speech). A 13-minute WER needs a full verbatim reference.

**Test set (~25 min, ~3,500 words):**
| Part | Length | Why |
|---|---|---|
| Sony C0031, full | 13 min (~2,000 words) | Main case: Katarina to camera, Ľuboš off-camera |
| DJI 0039, two excerpts with Ľuboš talking and cross-talk ("Môže byť", the "Čau!" at the end) | 2 × 3 min | Distant speaker, short turns, second mic |
| First December footage (Stage 1 dress-rehearsal shoot), any outdoor clip | ~5 min | Different place and noise; protects against overfitting to one room |

Size check: at ~8 % WER, 3,500 words gives a 95 % interval of roughly ±1–1.5 pp. Words are correlated, so it's wider than the binomial ±0.9 pp. That separates 7 % from 12 %, but not 7 % from 8 %. Because every engine runs on the same audio, compare them **paired**, per minute. A difference that holds in at least 80 % of the 1-minute chunks is real.

**How to build the reference cheaply (~3–4 h):** take the draft from one engine, then Ľuboš corrects it while listening, at 0.75× speed. Write it in the agreed orthography: numbers as spoken words, names in glossary form, fillers kept ("ehm" → `[ehm]`). To limit bias toward the drafting engine, show its low-confidence words (p < 0.5) highlighted and fix those by ear. Store references in `/data/bench/`, never in Git (§24.2: tests don't touch real footage).

**Metrics (add the ones in bold):**
| Metric | How | Target to "pass" (initial, adjust after the first run) |
|---|---|---|
| WER | jiwer; NFC, lowercase, punctuation stripped, diacritics **kept** | ≤ 12 % |
| **CER** | Same normalization | Report only |
| **Diacritic error rate** | WER on the diacritics-kept text minus WER on the diacritics-stripped text | ≤ 2 pp (captions and search depend on it) |
| Name / glossary accuracy | Recall of the exact glossary form for every glossary-term occurrence in the reference (~30–50 occurrences) | ≥ 90 % |
| **Glossary leakage** | Glossary terms in the output that aren't in the reference (a side effect of prompting) | 0–1 per 25 min |
| **Hallucination rate** | Words output where the reference has ≥ 1 s of non-speech, plus repeated-phrase loops | ≤ 1 per 25 min |
| **Short-turn recall** | Share of turns ≤ 1.5 s ("Môže byť", "Čau") that come out at all | ≥ 80 % |
| Word timing error | Hand-mark 100 word onsets in Audacity labels (~45 min of work); median and P90 absolute onset error, % within 100 ms | Median ≤ 60 ms, P90 ≤ 150 ms |
| Speaker accuracy | DER (pyannote.metrics, collar 0.25 s) on C0031 with hand-made turns (RTTM, ~30 min of work), plus **word-level speaker accuracy** | Word-level ≥ 95 % for Katarina and Ľuboš |
| Speed | Real-time factor (RTF) and peak RAM **on the owner's MacBook**, inside the actual Podman machine, for the full 39-min Giro_00 drop | Drop transcribed in ≤ 30 min (RTF ≤ 0.75) |
| **Determinism** | Same config run twice: identical text | Must be identical (greedy or beam with temperature 0) |

**Run it on the target machine.** The Hub is built on an M5 but runs on the owner's MacBook in Podman. Speed numbers from the build Mac are meaningless for the CPU-vs-helper decision. Record the MacBook's chip, RAM and the Podman machine size with every result.

**Decision rule:** prefer the faster or simpler config unless the slower one wins by ≥ 2 pp WER, or by ≥ 5 pp on name accuracy, in the paired comparison.

#### Q2. Engines
Expectations (from published numbers; **our conversational, two-person, outdoor audio will be worse**):
| Model | Published Slovak WER | Source |
|---|---|---|
| `openai/whisper-large-v3` (base) | CV24 19.7 %, KInIT internal 16.2 % | [kinit/whisper-large-v3-sk](https://huggingface.co/kinit/whisper-large-v3-sk) card |
| `openai/whisper-large-v3-turbo` (base) | CV24 29.2 %, internal 18.4 %, FLEURS 10.7 % | [kinit turbo-sk](https://huggingface.co/kinit/whisper-large-v3-turbo-sk), [NaiveNeuron turbo-sk](https://huggingface.co/NaiveNeuron/whisper-large-v3-turbo-sk) cards |
| **`kinit/whisper-large-v3-turbo-sk`** (v2.0, MIT, 809 M params) | CV24 9.3 %, internal 5.6 % (noise-augmented training) | [model card](https://huggingface.co/kinit/whisper-large-v3-turbo-sk) |
| `kinit/whisper-large-v3-sk` (Apache-2.0, 1.55 B) | CV24 7.7 %, internal 5.7 % | [model card](https://huggingface.co/kinit/whisper-large-v3-sk) |
| `NaiveNeuron/whisper-large-v3-turbo-sk` (MIT) | FLEURS 6.4 %, CV21 13.2 %; parliament-biased | [model card](https://huggingface.co/NaiveNeuron/whisper-large-v3-turbo-sk), [arXiv 2509.19270](https://arxiv.org/abs/2509.19270) |
| `nvidia/parakeet-tdt-0.6b-v3` (CC-BY-4.0, 25 EU languages incl. sk) | FLEURS 8.8 % | [model card](https://huggingface.co/nvidia/parakeet-tdt-0.6b-v3) |

All checked 2026-11-12. The fine-tunes' own numbers are vendor-reported. Treat them as "likely 2× better than base", not as our WER.

**Slovak-tuned models are worth testing, and one should be the lead candidate:** `kinit/whisper-large-v3-turbo-sk`, pinned to `revision="v2.0"`. Turbo has 4 decoder layers instead of 32, so CPU decoding is several times faster than large-v3. That's what makes CPU in Podman viable.

**Benchmark matrix (keep it to 4 runs + 1 prompt ablation):**
| Run | Engine | Where |
|---|---|---|
| A | faster-whisper `large-v3`, int8, through the WhisperX pipeline | Container, CPU |
| B | **`kinit/whisper-large-v3-turbo-sk` converted to CTranslate2 int8**, WhisperX pipeline | Container, CPU |
| C | mlx-whisper with the best of A/B's weights converted to MLX (fp16) | Mac helper, GPU |
| D | `kinit/whisper-large-v3-sk` CT2 int8 (only if B is within 2 pp of the best) | Container, CPU |
| B0 | B without the glossary hint | Container, CPU |

Optional, if time allows: Parakeet v3 via `parakeet-mlx` or ONNX. It's fast, with good native timestamps, but there's no prompt or hotword biasing, so names depend on correction memory.

**Conversion (one-off, done by the image build or on first run):** `ct2-transformers-converter --model kinit/whisper-large-v3-turbo-sk --revision v2.0 --output_dir /data/models/kinit-turbo-sk-v2-ct2 --quantization int8 --copy_files tokenizer.json preprocessor_config.json`. Don't use third-party CT2 re-uploads (unknown revision). MLX conversion of an HF fine-tune: the mlx-examples `convert.py` route is **unverified** for HF-format checkpoints. Budget 1 h or use an existing `mlx-community` conversion if one matches the pinned revision.

**Known fine-tune risks to check in the benchmark:**
- Fine-tunes often lose timestamp-token behaviour, which breaks sequential long-form decoding. The WhisperX path (VAD chunks ≤ 30 s, `without_timestamps=True`, then wav2vec2 alignment) avoids this.
- They also lose other languages ("catastrophic forgetting", per the KInIT card). Italian names said in a Slovak sentence are fine. Italian sentences won't be.

**Speed expectations (unverified, measure):** on an 8-vCPU arm64 Podman VM, faster-whisper int8 runs at roughly RTF 0.5–1.0 for large-v3 and roughly 0.15–0.35 for turbo. mlx-whisper turbo on Apple GPU is roughly 0.03–0.08. Turbo-sk on CPU likely transcribes the 39-min Giro_00 drop in 10–15 min, well inside the daily cadence. The §23.5 helper then stays unbuilt, which matches "simple over robust".

**Decoding settings (faster-whisper / WhisperX), fixed in config:**
```yaml
asr:
  model: kinit/whisper-large-v3-turbo-sk@v2.0   # winner of the benchmark
  compute_type: int8
  language: sk                    # forced; see P4
  beam_size: 5
  temperature: [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]
  condition_on_previous_text: false   # avoids repetition loops
  compression_ratio_threshold: 2.4
  log_prob_threshold: -1.0
  no_speech_threshold: 0.6
  vad_filter: true                # Silero VAD
  vad_parameters: { min_silence_duration_ms: 500, speech_pad_ms: 200 }
  hotwords: "<per-reel glossary, ≤ 150 tokens>"   # see Q3
  word_timestamps: true
  hallucination_blocklist: ["titulky vytvoril", "titulky vytvořil", "ďakujem za pozornosť", "ďakujem za pozretie", "odoberajte", "www."]
```
The blocklist holds Whisper's known "subtitle credit" hallucinations for cs/sk. It's **unverified** for these Slovak models specifically, so drop segments that match it only when they're also low-confidence.

#### Q3. Glossary hint
**It helps, but the spec's "initial prompt" mechanism mostly doesn't apply.** In faster-whisper's sequential mode, `initial_prompt` is treated as previous text. With `condition_on_previous_text=False` (recommended against loops), it's dropped after the first 30 s window. `hotwords` is injected into **every** window. Both are capped at **half the 448-token decoder context, i.e. 223 tokens**, and longer input is silently truncated. I checked the [faster-whisper `get_prompt` source](https://github.com/SYSTRAN/faster-whisper/blob/master/faster_whisper/transcribe.py) on 2026-11-12. WhisperX's batched mode passes `initial_prompt` to every chunk, so either works there. Use `hotwords` so it's explicit. mlx-whisper follows openai-whisper, where `initial_prompt` affects only the first window unless conditioning is on.

**How long:**
- Slovak with diacritics costs ~2–3 Whisper tokens per word, so 223 tokens is ~70–90 terms.
- Keep it **≤ 150 tokens (~40–60 terms)** to leave headroom.
- **Pick terms per reel, not the whole glossary:** the speakers' names, the stage's towns and climbs, project terms ("etapa", "Giro"), and the current correction-memory targets ("lízatko").
- Write it as one natural Slovak line with commas ("Giro, etapa, Terst, Rím, Zoncolan, Ľuboš, Katarína, lízatko."), not as a bullet list.

**When it hurts:**
- Long or irrelevant lists raise **leakage**: glossary words appear in noise or replace similar-sounding common words.
- Over ~60 terms the gain flattens (**unverified**, practitioner experience).
- Measure it with run B vs B0 (glossary-leakage metric). Keep the hint only if name accuracy rises and leakage stays ≤ 1 per 25 min.

Correction memory (§8) remains the safety net for what the hint misses.

#### Q4. Speaker labels
**Recommended setup:**
1. **Diarization:** [`pyannote/speaker-diarization-community-1`](https://huggingface.co/pyannote/speaker-diarization-community-1) (pyannote.audio ≥ 4, CC-BY-4.0, gated: accept terms once, then cache offline). Use `min_speakers=1, max_speakers=4`. Don't force 2, because passers-by and guests exist. Use its **exclusive** (non-overlapping) output for word assignment if your pyannote version exposes it (**unverified** naming). WhisperX's `assign_word_speakers` then puts a speaker on every word.
2. **Naming clusters with voice prints:** for each cluster, take the mean speaker embedding (the pipeline's own embeddings, or `pyannote/wespeaker-voxceleb-resnet34-LM`) and compare by cosine similarity with the enrolled prints. Label `katarina` / `luboš` if the best score ≥ **0.55** and beats the second by ≥ **0.10**; otherwise `other`. These are starting values: calibrate both on C0031.
3. **Enrollment:** 60–120 s of clean speech per person, from at least 3 clips, stored **per mic source** (`sony`, `dji`, `phone`). Channel mismatch is the main cause of wrong labels: Ľuboš recorded behind the Sony sounds very different from Ľuboš on the DJI mic.
4. **Learning from corrections:** when the producer relabels a span ≥ 2 s, add its embedding as an exemplar for that person and mic. Keep at most 30 exemplars per person and mic, and score by the highest similarity to any exemplar (nearest neighbour). No retraining.
5. **Short turns:** embeddings below ~1.5 s are unreliable. Give turns < 1.5 s the label of a cluster only if the cluster is confidently named. Otherwise use `unknown` with low confidence, so the UI asks instead of guessing. This is exactly the Giro_00 "Čau!" case.
6. **Cheap extra cue (later):** once Sony and DJI are synced, compare the speech level on the two mics. Ľuboš is much louder on the mic next to him. A level difference ≥ 6 dB is a strong tie-breaker for short turns.

Voice prints stay local and are used only for labels (D4, R10). Store them in `/data`, not in the DB export or backups that leave the Mac.

#### Q5. Word timestamps
**v0.5 change:** captions are made in Edits after trims, and `fix_captions` corrects text only (§6.4, §17.2). The Hub's word timing therefore drives **moment in/out points, cut suggestions, search hits and sync checks**, not caption timing. The accuracy need is still about one frame (40 ms at 25 fps) at cut points.

- **Native Whisper word timestamps** (cross-attention DTW): typically 100–300 ms off, and word ends get stretched into pauses (**unverified** figures, widely reported). Not good enough for cut points.
- **WhisperX wav2vec2 alignment:** typically ~50 ms median at boundaries. For Slovak, WhisperX's default align model is `comodoro/wav2vec2-xls-r-300m-sk-cv8` (checked in [alignment.py](https://github.com/m-bain/whisperX/blob/main/whisperx/alignment.py), 2026-11-12). It's a character-CTC model trained on Common Voice 8:
  - **Digits and characters outside its vocabulary** ("30", "Giro'") don't align. Interpolate their times from neighbours and flag them `timing: interpolated`.
  - Alignment on CPU is cheap: ~1–3 min per 13 min (**unverified**).
- **Recommendation:** split ASR and alignment into separate steps. Always run the wav2vec2 alignment **in the container**, whichever engine produced the text (container CPU or the Mac helper). Fall back to native timestamps per segment if alignment fails. The helper then only needs to return text segments.
- **Cut points:** don't cut exactly at word boundaries. Snap `src_in_ms` / `src_out_ms` to the middle of the nearest silence within ±150 ms (VAD or energy), or pad by 80 ms if there's no silence. This hides the remaining alignment error.

#### Q6. Search embeddings
v0.5 change: vector search is deferred (R35, §5.4 "later"). For December, the bigger search problem is **Slovak inflection**: FTS5 `unicode61 remove_diacritics 2` folds diacritics but doesn't stem. "lízatko" won't find "lízatka" or "lízatkom", and "Zoncolan" won't find "Zoncolane". **Cheap fix:** for query terms ≥ 5 characters, also search a prefix of the term minus its last 2 characters (`lízat*`, `zoncola*`), ranked below exact matches. See P9.

When vector search comes (local, CPU):
| Use | Model | Notes |
|---|---|---|
| Text (transcript segments, moments) | `intfloat/multilingual-e5-base` (278 M) | Good multilingual retrieval, fast on CPU via sentence-transformers or ONNX. Prefix inputs with "query: " / "passage: " |
| Text, better but heavier | `BAAI/bge-m3` (568 M) | Better recall, ~2–3× slower; still fine for a few thousand segments |
| Frames, with Slovak text queries | `google/siglip2-base-patch16-224` (multilingual tokenizer) or `sentence-transformers/clip-ViT-B-32-multilingual-v1` | Slovak query quality is **unverified**. Test 20 queries before choosing |
| Storage | `sqlite-vec` in the same DB | Matches the "SQLite only" stack |

Embed **segments** (5–20 s windows on sentence boundaries), not words. Embed the contact-sheet frames (every 2 s), which already exist.

#### Q7. Sync
**Audio cross-correlation first, transcript only as a check.** Transcript word times are ±100–300 ms off (or ~50 ms after alignment), which is 2–7 frames. Cross-correlation is sample-accurate and cheap:
1. Extract 16 kHz mono from both clips (already done for ASR).
2. **Coarse:** cross-correlate the onset envelopes (or log-energy at 100 Hz) with an FFT over the whole overlap. This is fast for 13 min and needs no prior, so the 1 h clock error doesn't matter. If a stored offset exists for this device and shoot, search only ±5 s around it.
3. **Fine:** GCC-PHAT on raw 16 kHz audio within ±100 ms of the coarse peak, giving ~1 ms resolution.
4. **Confidence:** peak divided by the next-best peak outside ±0.5 s. Accept when ≥ 3; otherwise ask for the manual offset.
5. **Drift:** repeat on the first and last 2 min. Different clocks drift about 10–50 ppm, which is up to ~40 ms over 13 min (**unverified** for these cameras). If the start and end offsets differ by > 20 ms, store `drift_ppm` and warn. Don't resample.
6. **Transcript check:** ≥ 80 % of distinctive words (≥ 6 letters, appearing once in both transcripts) should agree within 200 ms. Otherwise flag the sync.

It's about 50 lines of numpy/scipy with one unit test (a known-offset fixture), so it fits phase 1. The manual offset stays as the fallback, as the spec already says.

#### Q8. Re-runs and manual corrections
- **Don't re-transcribe everything automatically.** Re-run a project only when the benchmark shows a gain over the current model of ≥ 2 pp WER or ≥ 5 pp name accuracy. Do it on demand (one job per project), and keep the previous run until the producer accepts the new one.
- **Keep raw ASR and corrections separate.** Raw words are immutable per run. Corrections are a small table of edits anchored by **time range**, not word index:
  `transcript_edit(clip_id, t_in_ms, t_out_ms, old_text, new_text, kind: text|speaker, by, at)`.
- **Re-applying corrections to a new run:** take the new run's words overlapping `[t_in_ms − 200, t_out_ms + 200]`.
  - If their normalized text equals `old_text`, apply the edit.
  - If it equals `new_text`, the new model got it right: mark the edit `superseded`.
  - Otherwise mark it `conflict` and show it in the UI. Expect a handful per hour of audio.
- **Correction memory (§8) is a different thing.** It's global and context-free ("heard → correct"), so it must not rewrite raw transcripts blindly. "po 30 → po tridsiatke" is right in one sentence and wrong in another. Apply it to the **displayed / caption text** and to `fix_captions`, and require the context words to match when the rule stores them.
- **Moments are safe.** They're anchored in ms, so a re-run doesn't move them. Their `transcript` snapshot text is just refreshed from the active run.

### Proposals

#### P1. Replace the benchmark paragraph with a concrete protocol
- **Type:** change
- **Section:** §5.1a
- **Proposal:** Define the test set, the reference, the metrics, the target machine and the decision rule. The current text compares against a reference that only covers ~45 s.
- **Suggested spec text:**
  old: "- **Decision by benchmark, not by preference:** run `large-v3` through mlx-whisper and WhisperX on Giro_00 C0031 and compare against the corrected Edits transcript (word error rate, names, timing accuracy, speaker accuracy, minutes per hour of audio). Keep the best for Slovak."
  new:
  "- **Decision by benchmark, not by preference** (`reels-hub bench-asr`, run once before phase 1 and again before any model change):
    - **Test set (~25 min):** Sony C0031 in full (13 min), two 3-min DJI 0039 excerpts with Ľuboš and cross-talk, and ~5 min of the first December footage. The Edits transcript covers only the ~45 s used in Giro_00, so the producer corrects a full verbatim reference (~3–4 h: draft from one engine, corrected by ear; numbers as spoken words, names in glossary form). He also hand-marks 100 word onsets and the speaker turns of C0031. References live in `/data/bench/`, never in Git.
    - **Metrics:** WER and CER (NFC, lowercase, no punctuation, diacritics kept), diacritic error rate, glossary-name accuracy, glossary leakage, hallucinations per 25 min, recall of turns ≤ 1.5 s, word-onset error (median, P90), DER and word-level speaker accuracy, RTF and peak RAM, run-to-run determinism.
    - **Machine:** speed is measured on the owner's MacBook inside the real Podman machine, not on the build Mac.
    - **Rule:** take the fastest config that is within 2 pp WER and 5 pp name accuracy of the best (paired, per-minute comparison). Pass bar for December: WER ≤ 12 %, names ≥ 90 %, word-level speaker accuracy ≥ 95 %, Giro_00 drop (39 min) transcribed in ≤ 30 min."
- **Why:** without a full reference, WER and timing can't be computed. Speed measured on the M5 build machine says nothing about the MacBook in Podman.
- **Priority:** must-have before build (phase 1)

#### P2. Add Slovak fine-tunes to the candidates and fix the decoding config
- **Type:** change
- **Section:** §5.1a (table), §21 (Transcription row)
- **Proposal:** Add `kinit/whisper-large-v3-turbo-sk` (and `kinit/whisper-large-v3-sk`) as candidates, run through CTranslate2 int8 in the container. Pin model revisions and put the decoding settings in config.
- **Suggested spec text:**
  Add a row to the §5.1a table:
  "| [kinit/whisper-large-v3-turbo-sk](https://huggingface.co/kinit/whisper-large-v3-turbo-sk) (MIT) and [kinit/whisper-large-v3-sk](https://huggingface.co/kinit/whisper-large-v3-sk) (Apache-2.0) | Slovak fine-tunes; published WER about a third of base large-v3 on Slovak; turbo decodes several times faster | CPU via CTranslate2 int8 (converted once with `ct2-transformers-converter`), or MLX | **Lead candidate** for CPU in Podman |"
  Add after the table:
  "- **Benchmark runs:** A = large-v3 (WhisperX, CPU), B = kinit turbo-sk v2.0 (WhisperX, CPU), C = best weights on mlx-whisper (Mac helper), D = kinit large-v3-sk (only if B is close), B0 = B without the glossary hint.
  - **Decoding config** (stored with every transcript):
    ```yaml
    asr:
      model: kinit/whisper-large-v3-turbo-sk@v2.0
      compute_type: int8
      language: sk
      beam_size: 5
      temperature: [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]
      condition_on_previous_text: false
      compression_ratio_threshold: 2.4
      log_prob_threshold: -1.0
      no_speech_threshold: 0.6
      vad_filter: true
      vad_parameters: { min_silence_duration_ms: 500, speech_pad_ms: 200 }
      word_timestamps: true
      hallucination_blocklist: ["titulky vytvoril", "titulky vytvořil", "ďakujem za pozornosť", "ďakujem za pozretie", "odoberajte", "www."]
    ```
  - Model weights are pinned to a revision and converted once into `/data/models/`; no third-party re-uploads."
  §21 Transcription row, old: "mlx-whisper / whisper.cpp **vs.** WhisperX on faster-whisper (large-v3), chosen by benchmark (§5.1a)" → new: "WhisperX on faster-whisper with a Slovak fine-tune (kinit turbo-sk) or large-v3, **vs.** mlx-whisper on the Mac helper, chosen by benchmark (§5.1a)"
- **Why:** base large-v3 shows 16–20 % WER on Slovak sets vs 5.6–7.7 % for the KInIT fine-tunes (model cards, checked 2026-11-12). Turbo makes CPU-only viable, which likely removes the need for the §23.5 helper.
- **Priority:** must-have before build (phase 1)

#### P3. Glossary hint as per-window hotwords with a size cap
- **Type:** change
- **Section:** §5.1a
- **Proposal:** Use per-window hotwords chosen per reel, capped at 150 tokens, instead of an initial prompt with the whole glossary.
- **Suggested spec text:**
  old: "- **Glossary hint:** pass the project glossary as the initial prompt (\"Terst, Rím, Zoncolan, Ľuboš, lízatko, etapa\") so names come out right the first time."
  new: "- **Glossary hint:** pass a per-reel term list as `hotwords` (faster-whisper / WhisperX; applied to every 30 s window), written as one Slovak line, e.g. \"Giro, etapa, Terst, Rím, Zoncolan, Ľuboš, Katarína, lízatko.\" Terms: the speakers, the reel's stage towns and climbs, project terms and current correction-memory targets. **Cap: 150 tokens (~40–60 terms)**; Whisper truncates anything over 223 tokens. `initial_prompt` alone is not enough: with `condition_on_previous_text: false` it only affects the first window. Kept only if the benchmark (B vs B0) shows better name accuracy and glossary leakage ≤ 1 per 25 min."
- **Why:** checked in faster-whisper's `transcribe.py` (2026-11-12): the prompt is cut at `max_length // 2`, and `initial_prompt` sits in the previous-text slot that is reset when conditioning is off.
- **Priority:** must-have before build (phase 1)

#### P4. Force Slovak and drop per-segment language detection
- **Type:** change
- **Section:** §5.1 step 4, §8 (Translation)
- **Proposal:** Transcribe with `language="sk"` always. Whisper's language ID on short segments often confuses Slovak with Czech, and the Slovak fine-tunes can't transcribe other languages anyway. Flag possible foreign speech from low confidence instead.
- **Suggested spec text:**
  old: "4. Transcribe: Slovak by default, word-level timestamps, language detection per segment."
  new: "4. Transcribe in Slovak (`language: sk`, forced) with word-level timestamps. No per-segment language detection: on short segments it confuses Slovak with Czech. Segments with mean word probability < 0.4 are flagged `check_language` in the UI; the producer can re-run that range with base `large-v3` and a chosen language, and the result is marked as such."
- **Why:** stops sk→cs misdetections from corrupting captions and search. Keeps the §8 translation feature possible without automatic detection.
- **Priority:** must-have before build (phase 1)

#### P5. Audio cross-correlation as the primary sync method
- **Type:** change
- **Section:** §5.2
- **Proposal:** Sync angles by audio cross-correlation (coarse envelope plus fine GCC-PHAT), with a confidence and a drift check. Transcript words only verify the result. The manual offset stays as the fallback.
- **Suggested spec text:**
  old: "- Sync by **transcript alignment** (matching distinctive words) or audio cross-correlation, with a confidence score. The camera clock offset is stored per device per shoot (e.g. DJI = Sony − 24.85 s; clock 1 h off). For December a manually entered offset per device per shoot is enough."
  new: "- Sync by **audio cross-correlation**: coarse on 100 Hz log-energy envelopes over the whole overlap (FFT, no prior needed; ±5 s around a stored offset if one exists), then fine with GCC-PHAT on 16 kHz audio within ±100 ms. Confidence = main peak / next peak outside ±0.5 s; accept at ≥ 3, otherwise ask for a manual offset. Drift check: repeat on the first and last 2 min; if they differ by > 20 ms, store `drift_ppm` and warn. Transcript words only verify the result (≥ 80 % of distinctive words within 200 ms). The camera clock offset is stored per device per shoot (e.g. DJI = Sony − 24.85 s; clock 1 h off). A manually entered offset remains the fallback."
- **Why:** transcript word times are 2–7 frames off, while cross-correlation is sample-accurate. It's ~50 lines of numpy/scipy, so it's cheaper than the transcript matcher.
- **Priority:** before phase 1 (auto-sync is "if time allows" in phase 1; this is the simpler way to do it)

#### P6. One primary audio source per take
- **Type:** addition
- **Section:** §5.1, §5.2, §5.4
- **Proposal:** Pick the source to transcribe per take: the DJI mic `.WAV` sidecar if it exists, else the camera with the best speech level. Other angles get the same words through the sync offset. This avoids transcribing the same conversation 3× (Giro_00: 39 min of audio for 13 min of speech) and stops search returning duplicate hits.
- **Suggested spec text:** add to §5.1 after step 5:
  "- **Primary audio per take:** once a take's clips are synced, the Hub transcribes one primary source: the external mic `.WAV` if present, else the clip with the highest speech level (camera channel chosen per device in config, not blindly downmixed). Other angles in the take reference the primary transcript through their offset. Clips without a take are transcribed on their own. Search returns one hit per take, with all angles listed."
- **Why:** cuts CPU time by ~2–3× on multicam shoots, which matters with no GPU in Podman. One transcript per take also makes speaker labels and corrections consistent across angles.
- **Priority:** before phase 1

#### P7. Speaker-labelling setup with per-mic voice prints
- **Type:** change
- **Section:** §5.1 step 5, §21 (Speakers row)
- **Proposal:** Specify the pipeline, thresholds, per-mic enrollment, how corrections feed the prints, and an `unknown` label for short turns.
- **Suggested spec text:**
  old (§5.1 step 5): "5. Label speakers (Katarina / Ľuboš / other), with voice prints that learn from corrections."
  new: "5. Label speakers: pyannote `speaker-diarization-community-1` (min 1, max 4 speakers) → words assigned to speakers (WhisperX `assign_word_speakers`) → each cluster named by cosine similarity to voice prints (`katarina` / `luboš` if best ≥ 0.55 and ≥ 0.10 above the second, else `other`; thresholds calibrated on C0031). Voice prints: 60–120 s per person, stored **per mic source** (sony, dji, phone). A producer relabel of a span ≥ 2 s adds an exemplar (max 30 per person and mic; scored by nearest exemplar). Turns < 1.5 s in an unconfident cluster get `unknown` and are shown for a decision instead of guessed."
  §21 Speakers row, old: "WhisperX (pyannote) or an embedding-based voice print" → new: "pyannote community-1 diarization (through WhisperX) + per-mic voice prints for naming (§5.1)"
- **Why:** channel mismatch (Ľuboš behind the Sony vs on the DJI mic) and sub-1.5 s turns ("Môže byť", "Čau!") are where labels fail. Giro_00 already hit the "Čau!" case.
- **Priority:** before phase 1 (spec allows speakers "if time allows")

#### P8. Raw transcript runs plus a correction layer
- **Type:** change
- **Section:** §18 (tables), §5.1a ("Model and version"), §8 (Correction memory)
- **Proposal:** Add one small `transcript` row per clip and run, plus a `transcript_edit` table anchored by time. Raw words are never overwritten. Corrections are re-applied to new runs by time and text match. Correction memory changes displayed / caption text only.
- **Suggested spec text:**
  §18, old: "| `transcript_word` | clip_id, t_in_ms, t_out_ms, text, speaker, confidence |"
  new:
  "| `transcript` | id, clip_id, engine, model, model_revision, config (json), created_at, active |
  | `transcript_word` | transcript_id, t_in_ms, t_out_ms, text, speaker, confidence, timing (aligned / interpolated) |
  | `transcript_edit` | clip_id, t_in_ms, t_out_ms, old_text, new_text, kind (text / speaker), by, at, status (applied / superseded / conflict) |"
  §5.1a, old: "- **Model and version** are stored with every transcript so it can be re-run when a better model ships."
  new: "- **Model, revision and config** are stored with every transcript run. Re-runs are on demand per project, only when the benchmark shows ≥ 2 pp WER or ≥ 5 pp name accuracy gain; the previous run stays until the producer accepts the new one. Manual edits (`transcript_edit`) are re-applied by time range: if the new words equal `old_text` the edit is applied, if they equal `new_text` it is marked superseded, otherwise it is shown as a conflict."
  §8, add to Correction memory: "Correction memory never rewrites raw transcript words; it applies to displayed and caption text and in `fix_captions`, and only where the stored context matches."
- **Why:** §5.1a promises re-runs, but the data model has nowhere to store the model, and nothing keeps manual fixes. Context-free replacements ("po 30 → po tridsiatke") are wrong in other sentences. This is three tables, not the segment/provenance machinery rejected in R15.
- **Priority:** must-have before build (phase 1 schema)

#### P9. Slovak inflection in full-text search
- **Type:** change
- **Section:** §5.4
- **Proposal:** Add a prefix fallback for inflected forms. FTS5 folds diacritics but doesn't stem Slovak.
- **Suggested spec text:** add to §5.4 after the first bullet:
  "- **Inflection:** Slovak has 6–7 cases, and FTS5 has no Slovak stemmer. Each query term of ≥ 5 characters is also searched as a prefix without its last 2 characters (`lízatko` → `lízat*`, `Zoncolan` → `zoncola*`); exact matches rank first. Index tokenizer: `unicode61 remove_diacritics 2`."
- **Why:** without it, "lízatko" misses "lízatka" and "lízatkom", and the agent's `search_moments` silently loses hits.
- **Priority:** before phase 1

#### P10. Forced alignment as its own step, always in the container
- **Type:** change
- **Section:** §5.1a, §23.5
- **Proposal:** Separate alignment from ASR. The container always runs WhisperX's wav2vec2 alignment (`comodoro/wav2vec2-xls-r-300m-sk-cv8`) on whatever text the engine returned. Digits and out-of-vocabulary tokens get interpolated times. Cut points snap to silence.
- **Suggested spec text:** add to §5.1a:
  "- **Word timing:** after ASR, the container runs forced alignment (WhisperX, Slovak model `comodoro/wav2vec2-xls-r-300m-sk-cv8`) on the text, whichever backend produced it. Words the aligner can't place (digits, symbols) get times interpolated from neighbours and `timing: interpolated`. Suggested moment in/out points snap to the middle of the nearest silence within ±150 ms, or are padded by 80 ms."
  §23.5, old: "…the helper reads the file directly from `~/Movies/ReelsHub` and returns word-level JSON." → new: "…the helper reads the file directly from `~/Movies/ReelsHub` and returns segment-level text JSON; word timing is added by the container's alignment step (§5.1a)."
- **Why:** native Whisper word times aren't good enough at cut points. This keeps the helper trivial and makes both backends give the same timing quality.
- **Priority:** before phase 1

#### P11. Risk: arm64 Linux container and gated pyannote weights
- **Type:** risk
- **Section:** §23.4, §23.6
- **Proposal:** Record two build traps.
  1. On Apple Silicon the Podman VM is linux/arm64, and `torchcodec` (pyannote.audio ≥ 4's audio decoder) has no Linux aarch64 wheels (WhisperX `pyproject.toml`, checked 2026-11-12). Decode with ffmpeg to 16 kHz mono and pass waveforms in memory.
  2. pyannote community-1 is gated. Download it once with an HF token, then run with `HF_HUB_OFFLINE=1` from `/data/models`.

  Also: the ASR stack needs ~5–6 GB RAM at peak (turbo int8 + pyannote + aligner, **unverified**), so the Podman machine must fit the owner's MacBook RAM. 8 GB is enough for transcription.
- **Suggested spec text:** add rows to the §23.4 table:
  "| **linux/arm64 container** | `torchcodec` (used by pyannote.audio ≥ 4 to read files) has no Linux aarch64 wheels | Decode audio with ffmpeg to 16 kHz mono; pass waveforms to pyannote and WhisperX in memory; container smoke test runs diarization on the fixture |
  | **Gated model weights** | pyannote community-1 needs an HF token to download | Download once (token as Podman secret `hf_token`), cache in `/data/models`, run with `HF_HUB_OFFLINE=1`; CC-BY-4.0 attribution in the About page |"
- **Why:** both break the first container build on the owner's Mac. The build Mac (M5) is also arm64, so they show up early. Better to plan for them.
- **Priority:** must-have before build (phase 0/1)

#### P12. Laughter and non-speech tags (later)
- **Type:** addition
- **Section:** §5.3 (Features), §8
- **Proposal:** Whisper doesn't reliably output laughter, so "punchlines (laughter after a line)" has no input. Add a small CPU audio tagger (PANNs CNN14 or AST on AudioSet, the "Laughter" class) on VAD non-speech and mixed regions. It feeds punchline suggestions and `[smiech]` sound tags.
- **Suggested spec text:** add to §5.3 Features: "- **Laughter detection** *(later)*: an AudioSet tagger (e.g. PANNs CNN14) marks laughter ≥ 0.5 s; a line followed by laughter within 1 s is suggested as a punchline, and the caption gets a `[smiech]` sound tag."
- **Why:** makes an existing feature implementable. It's cheap on CPU (**unverified**: ~1 min per 13 min).
- **Priority:** later

**Sign-off:** approve with changes (P1–P4, P8 and P11 before phase 1 starts; the rest during phase 1)
