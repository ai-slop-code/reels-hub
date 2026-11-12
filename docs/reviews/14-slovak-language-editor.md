# Review packet 14: Slovak language editor

**Priority:** good to have (before captions go automatic in phase 3)
**Time needed:** ~1 h
**Decisions already made:** see [README](README.md#decisions-already-made-please-dont-reopen).

## Why you
Every reel is captioned in Slovak from Katarina's speech, and the Hub will auto-correct captions using a glossary. The rules need a language professional.

## Read
- [§8 Glossary and caption intelligence](../spec/REELS_HUB_SPEC.md#8-module-d-glossary-and-caption-intelligence)
- [`DESIGN_LANGUAGE.md`](../spec/DESIGN_LANGUAGE.md) §4 Captions
- Reference: Giro_00 captions (in `../reels/giro00-intro/review_notes.md`) and [`../reels/giro00-intro/instagram_caption.txt`](../reference/giro00/instagram_caption.txt)

## Questions
1. **Place names:** Slovak exonyms (Terst, Rím, Neapol) vs. Italian originals (Trieste, Roma, Napoli). Rule for captions, maps and post captions?
2. **Spoken vs. written:** Katarina speaks casually and in an eastern Slovak register at times. How faithful should captions be (filler words, dialect, grammar slips)?
3. **Numbers:** "po tridsiatke" in words, "24 dní" in digits. Is the rule in DESIGN_LANGUAGE §4 right?
4. **Foreign terms:** Giro, maglia rosa, Strade Bianche, rider names. Italics? Inflection (na Gire / na Giro)?
5. **Line breaks and punctuation:** our caption style hides end punctuation. Acceptable for questions?
6. **Glossary seed:** please list 30–50 cycling and Italy terms with correct Slovak spelling and inflection for the first project.
7. **Instagram caption:** review the Giro_00 caption for tone and correctness.

## Your input

*Reviewer: senior Slovak language editor (AI). Reviewed spec v0.5, DESIGN_LANGUAGE v1.1, Giro_00 review notes and Instagram caption. Packet was written for v0.4; all seven questions still apply to v0.5 unchanged.*

*Sources checked on 2026-11-12 (browsing available):*
- *ÚGKK SR, list of exonyms (last updated 2022-01-05). It says standardized exonyms (shown in bold in the list) are binding for the press and mass media, and it follows the UN recommendation to use fewer exonyms: <https://www.skgeodesy.sk/sk/ugkk/geodezia-kartografia/standardizacia-geografickeho-nazvoslovia/nazvy-geografickych-objektov-z-uzemia-mimo-sr/>*
- *Italian entries as cited on sk.wikipedia (Firenze → Florencia, Genova → Janov, Gorizia → Gorica, Milano → Miláno, Napoli → Neapol, Padova → Pádua, Roma → Rím, Torino → Turín, Trento → Trident, Trieste → Terst, Venezia → Benátky; river Po → Pád): <https://sk.wikipedia.org/wiki/Slovensk%C3%A9_exonym%C3%A1>. I could not open the ÚGKK PDF itself, so I couldn't confirm which of these are bold (binding) and which are historical. Rated **partly verified**.*
- *JÚĽŠ language advice service (prepositions with country names: v Slovinsku, do Slovinska): <https://jazykovaporadna.sme.sk/q/1960>*
- *Vocalized prepositions, e.g. vo Florencii (Quark, 2025): <https://www.quark.sk/vokalizacia-predloziek>*
- *Slovak sports-press usage: TASR/Pravda uses "Na Gire…", "víťazom 5. etapy Giro d'Italia" and "Janov – Lucca" (<https://www.pravda.sk/sportweb/cyklistika/clanok/709309-na-gire-sa-o-etape-rozhodlo-v-uniku-vitazom-thomas-ruzovy-dres-si-udrzal-pogacar>). Teraz.sk uses "víťaz 6 etáp na Gire" and "Okolo Lombardska". Sportnet uses "po Gire d'Italia". The 2027 Stage 2 route Ljubljana–Koper is from Delo (2026-11-03).*
- ***Unverified:** whether Monstera-Black has the glyphs „ “ ’; which end punctuation Edits' *Word Highlight Box V3* hides besides `?` and `.` (e.g. `!` and `…`); the license of the Hunspell `sk_SK` dictionary.*

### Summary
The caption design is sound, and the hand fixes in Giro_00 were correct. But the language layer of the spec (§8) is too thin to automate safely in phase 3. The biggest risk is the **correction memory**. As written, it would turn every future "takúto" into "toto" and would put uninflected forms into inflected positions (e.g. "v Trieste" would become "v Terst"). Slovak is a heavily inflected language, so glossary entries need their case forms, and corrections need context. Second, the spec doesn't say **how literal captions are**. I propose a "clean verbatim" rule: her words and word order, without fillers, with dialect kept as it was spoken. Under that rule, captions follow what she actually said, including "Trieste" vs. "Terst", while maps, titles and post captions follow the exonym policy. Third, number, line-break and punctuation rules need a few Slovak-specific additions. The main ones: an ordinal dot hidden at the end of a line turns "do 30." into "do 30", and yes/no questions lose their only marker. A 52-term glossary seed with inflection is in Q6. The Giro_00 Instagram caption is good. It needs one fix to the parallel structure, and I suggest one optional line.

### Answers

#### Q1. Place names: exonyms vs. Italian originals
The rule depends on the output, because captions transcribe speech and everything else is text we write ourselves:

| Output | Rule | Example |
|---|---|---|
| **Captions** (her speech) | Write the name **as she said it**. If she says "Trieste", the caption says "Trieste", and if she says "Terst", it says "Terst". Never swap one for the other: viewers hear the name and notice a mismatch, and it breaks "her own words". Only fix spelling and inflection. | "Štart je v Terste" / "v Trieste" (whichever she said) |
| **On-screen titles and map cards** (we write them) | Use the **Slovak exonym if it's in active use**, otherwise the Italian original, inflected in Slovak. | *Štart v Terste, cieľ v Ríme.* |
| **Map labels** (stand alone, not in a sentence) | Same list as titles, in the nominative. Country names in capitals as now (TALIANSKO, SLOVINSKO). | Terst, Rím, Benátky, Bolzano |
| **Instagram post caption** | Same as titles. **Hashtags** use the original or international form, lowercase, without diacritics, because that's how people search. | text "v Terste", hashtag `#trieste` |
| **Glossary hint for Whisper** | Both forms, so that whichever she says is transcribed correctly. | "Terst, Trieste, Rím, Zoncolan" |

**Which exonyms are "in active use":** start from the ÚGKK list, but use an exonym in titles only if current Slovak sports and travel media use it. Active (use these): Terst, Rím, Neapol, Miláno, Turín, Janov (TASR uses it), Benátky, Florencia, Ľubľana, Sicília, Sardínia, Toskánsko, Lombardsko, Benátsko, Piemont, Dolomity, Alpy, Apeniny, Jadranské more, Pád (river). Listed but dated in today's usage (use the Italian original): Padova (not Pádua), Trento (not Trident), Taranto (not Tarent), Gorizia (not Gorica). Every other town or climb keeps its Italian name: Bolzano, Bergamo, Siena, Asiago, Zoncolan, Stelvio. Never invent an exonym.

The spec currently says the opposite for captions: §8 "use Slovak exonym in captions" and R8 "uses glossary forms (Terst, Rím)". I record this as a risk in P3, not as a reversal of R8. It can be solved by making "Trieste" a glossary form too.

#### Q2. Spoken vs. written: how faithful
Use **clean verbatim** (*čistý doslovný prepis*), which is standard practice for same-language subtitles:
- **Keep:** her words, her word order, her humor, discourse particles that carry meaning ("no", "veď", "však", "hej", "nie?"), affectionate forms ("Ľuboško"), Bohemisms she really uses ("vlastne", "jasné"), her Italian words ("ciao", "andiamo", "maglia rosa"). These are never translated. The §8 translation rule should apply only to longer speech in another language, e.g. an Italian passer-by.
- **Drop:** hesitation sounds (eee, ehm, hmm), stutters, false starts, repeated words ("to to to"), and pure fillers ("akože", "proste", "teda") when they carry no meaning and the phrase is over 8 words. Dropping a filler from the **caption** doesn't change the cut, so R4 isn't affected.
- **Eastern Slovak:** Spell **pronunciation-only** differences the standard way. Stress, *ď/ť* softening and *dz* for *z* are invisible in writing anyway, so e.g. "ňe" → "nie". **Lexical** dialect words and particles that are part of her persona ("šak", "ta", "dze", "ľem", "bars") are **kept as said**. Add each one to the glossary as `keep_as_said`, so neither `fix_captions` nor the ASR correction memory "standardizes" it. Limit: if a dialect word would stop a western Slovak viewer in a muted reel and it's essential to the line, keep it anyway; never put a gloss in captions.
- **Grammar slips:** silently fix inflection and agreement endings (case, gender, number), e.g. "21 etapy" → "21 etáp". Never change a word, its meaning or the word order. **Factual** slips are never fixed in captions. They go into editors_notes.md as an open item, and the line is re-cut or dropped.
- **Crude words** are already excluded in the cut (DESIGN_LANGUAGE §10). If a mild one stays in, caption it as spoken. No asterisks.

#### Q3. Numbers
The DESIGN_LANGUAGE §4 rule is right in principle. It needs Slovak specifics and the edge cases. The exact YAML is in P5. In short:
- **Words:** idiomatic or approximate quantities and decades ("po tridsiatke", "pár dní", "tisíckrát", "v osemdesiatych rokoch"), and "jeden / jedna / jedno" used as a determiner ("každý deň jedna etapa").
- **Digits:** counts with a noun ("24 dní", "21 etáp", "3 krajiny"), exact ages ("má 28 rokov"), measurements, years and dates.
- **Ordinals:** digits plus a dot ("1. etapa", "8. mája"). When she says "prvá etapa", the caption may write "1. etapa"; it reads the same. **Never end a caption line with an ordinal**, because the style hides the dot at the end of a line (see Q5).
- **Slovak number format:** decimal comma ("3 418,9 km"); a non-breaking space as the thousands separator from 10 000 up (optional at 4 digits, so for consistency always use it: "3 419 km"); a space before units and the percent sign ("172 km", "8 %"), but a hyphen in adjectives ("8-percentné stúpanie"); the euro sign after the number ("25 €"); time "14:30"; ranges "od 8. do 30. mája" (Monstera has no en dash).
- Whisper normalizes number words to digits ("po 30"). That's a **formatting rule**, not a mishearing, so it belongs in the rule engine, not the correction memory.

#### Q4. Foreign terms
- **No italics anywhere.** Edits captions use a single Monstera-Black style, and Instagram captions have no italics. Unicode "fake italics" break search and screen readers. So foreign terms are written in plain upright text in their original spelling.
- **Case:** common nouns stay lowercase as in Italian (*maglia rosa*, *maglia azzurra*). Names keep their capitals (*Giro d'Italia*, *Strade Bianche*, *Cima Coppi*).
- **Giro:** the short form **declines** as a neuter noun like *mesto*: Giro, Gira, Giru, na Giro, na Gire, s Girom. "Na Gire" vs. "na Giro" is not either/or. Both are correct, with different meanings: **byť na Gire** (location, locative) and **ísť na Giro** (direction, accusative). The full name **Giro d'Italia stays indeclinable** in titles and post captions ("5. etapa Giro d'Italia", as TASR writes). Sportnet's "po Gire d'Italia" exists, but it's the less tidy option. Same for the others: *Tour de France* and *Strade Bianche* don't decline; *Vuelta* declines (na Vuelte).
- **Apostrophe:** "Giro d'Italia" with a straight `'` in captions and Edits titles (Monstera's `’` is unverified) and in post captions. Never in hashtags (`#giroditalia`).
- **Rider names:** original spelling with all diacritics (Pogačar, Roglič, Vingegaard). Men's surnames **decline** by Slovak rules: Pogačara, s Pogačarom; Ganna → Gannu, s Gannom; Ciccone → Cicconeho, s Cicconem; Pellizzari → Pellizzariho. For foreign women, caption what she says. In text we write, use the form without *-ová* (e.g. Elisa Longo Borghini), because Slovak practice varies and the original form avoids errors. That's my recommendation; ask Katarina how she says it.
- **Jersey names:** if she says "ružový dres", caption that. If she says "maglia rosa", caption that. Titles: say it in Slovak first ("ružový dres"), and use the Italian term once per reel at most for flavor.

#### Q5. Line breaks and punctuation
Hiding the final `.` is fine; it's the norm in short-form captions. Hiding `?` is fine **when the question is visible from its words**: a question word (prečo, kde, kedy, ako, koľko, kto, čo, ktorý, či) or a tag ("…, nie?", "…, však?", "…, hej?"). "Prečo je toto lízatko ružové" reads as a question without the `?`. It's **not** fine for yes/no questions in statement word order, which in Slovak differ only by intonation: "Ideme na Giro" (statement) vs. "Ideme na Giro?" (question). Muted, that question turns into a statement.

Rules (YAML in P6):
1. If a caption line ends in a question that has no question word or tag, the agent makes the `?` visible: move the line break so the `?` isn't at the end (if the style shows `?` mid-line, **unverified**), or put the line on a title card (titles keep their punctuation). Otherwise it notes the case in editors_notes.md.
2. Never end a line on an ordinal ("do 30." would read as "do 30"). Keep the ordinal with its noun ("30. mája").
3. Don't separate: a preposition from its noun, a number from its unit or noun ("24 | dní"), a first name from the surname, "Giro | d'Italia", "1. | etapa".
4. Don't end a line on a one-letter preposition or conjunction (v, k, s, z, o, u, a, i). This is the Slovak typographic convention (STN 01 6910).
5. Break at clause boundaries, i.e. before "že", "ktorý", "ale", "lebo", "keď", or after a comma.
6. Use a comma, never a dash (Monstera has no en dash). For speaker labels, keep the colon form "Ľuboš: Môže byť." For quotes inside captions or titles use „…“ (the glyphs are **unverified** in Monstera; if they're missing, avoid quotes).
7. Exclamation marks and ellipses: check once whether the style hides them (**unverified**). If it does, the same rule applies: the meaning must come from the words.

Side note: the pickup in Giro_00 `review_notes.md` closes with a straight `"`. The Slovak closing quote is `“`, i.e. „…“.

#### Q6. Glossary seed (52 terms)
These are ready to import as `sk-italy` and `sk-cycling`. The forms are nominative, genitive, locative with its usual preposition, and instrumental. `as_said` means: caption whatever form she used (exonym or original). Pronunciations are a Slovak-reader approximation, stressed syllable in capitals. Spellings are standard. The few points I'm less sure of are marked `verify`.

```yaml
# glossary: sk-italy
- { term: Taliansko,   type: country, forms: [Taliansko, Talianska, v Taliansku, Talianskom], adj: taliansky }
- { term: Slovinsko,   type: country, forms: [Slovinsko, Slovinska, v Slovinsku, Slovinskom], adj: slovinský, note: "do Slovinska / v Slovinsku (JÚĽŠ)" }
- { term: Terst,       original: Trieste,  type: city, forms: [Terst, Terstu, v Terste, Terstom], adj: terstský, captions: as_said }
- { term: Rím,         original: Roma,     type: city, forms: [Rím, Ríma, v Ríme, Rímom], adj: rímsky, captions: as_said }
- { term: Neapol,      original: Napoli,   type: city, forms: [Neapol, Neapola, v Neapole, Neapolom], adj: neapolský, captions: as_said }
- { term: Miláno,      original: Milano,   type: city, forms: [Miláno, Milána, v Miláne, Milánom], adj: milánsky, captions: as_said }
- { term: Turín,       original: Torino,   type: city, forms: [Turín, Turína, v Turíne, Turínom], adj: turínsky, captions: as_said }
- { term: Janov,       original: Genova,   type: city, forms: [Janov, Janova, v Janove, Janovom], adj: janovský, captions: as_said }
- { term: Benátky,     original: Venezia,  type: city, forms: [Benátky, Benátok, v Benátkach, Benátkami], adj: benátsky, note: "plural only" }
- { term: Florencia,   original: Firenze,  type: city, forms: [Florencia, Florencie, vo Florencii, Florenciou], adj: florentský, note: "vo before f" }
- { term: Ľubľana,     original: Ljubljana, type: city, forms: [Ľubľana, Ľubľany, v Ľubľane, Ľubľanou], note: "2027 Stage 2 start" }
- { term: Padova,      type: city, forms: [Padova, Padovy, v Padove, Padovou], note: "exonym Pádua is dated; don't use" }
- { term: Bolzano,     type: city, forms: [Bolzano, Bolzana, v Bolzane, Bolzanom] }
- { term: Siena,       type: city, forms: [Siena, Sieny, v Siene, Sienou] }
- { term: Sicília,     original: Sicilia,  type: region, forms: [Sicília, Sicílie, na Sicílii, Sicíliou], note: "island → na" }
- { term: Sardínia,    original: Sardegna, type: region, forms: [Sardínia, Sardínie, na Sardínii, Sardíniou] }
- { term: Toskánsko,   original: Toscana,  type: region, forms: [Toskánsko, Toskánska, v Toskánsku, Toskánskom] }
- { term: Lombardsko,  original: Lombardia, type: region, forms: [Lombardsko, Lombardska, v Lombardsku, Lombardskom], note: "race Il Lombardia = Okolo Lombardska" }
- { term: Benátsko,    original: Veneto,   type: region, forms: [Benátsko, Benátska, v Benátsku, Benátskom] }
- { term: Dolomity,    original: Dolomiti, type: range, forms: [Dolomity, Dolomitov, v Dolomitoch, Dolomitmi] }
- { term: Alpy,        original: Alpi,     type: range, forms: [Alpy, Álp, v Alpách, Alpami], note: "genitive Álp with á" }
- { term: Apeniny,     original: Appennini, type: range, forms: [Apeniny, Apenín, v Apeninách, Apeninami] }
- { term: Jadranské more, original: Mare Adriatico, type: sea, forms: [Jadranské more, Jadranského mora, pri Jadranskom mori, Jadranským morom], note: "colloquial: Jadran" }
- { term: Pád,         original: Po,       type: river, forms: [Pád, Pádu, pri Páde, Pádom], note: "Pádska nížina" }
- { term: Etna,        type: volcano, forms: [Etna, Etny, na Etne, Etnou] }
- { term: Zoncolan,    type: climb, forms: [Zoncolan, Zoncolanu, na Zoncolane, Zoncolanom], pron: "dzon-ko-LAN", note: "na Zoncolan (direction)" }
- { term: Stelvio,     original: Passo dello Stelvio, type: climb, forms: [Stelvio, Stelvia, na Stelviu, Stelviom], pron: "STEL-vio" }
- { term: Mortirolo,   type: climb, forms: [Mortirolo, Mortirola, na Mortirole, Mortirolom] }
- { term: Tre Cime di Lavaredo, type: climb, forms: indeclinable, pron: "tre ČI-me di la-va-RE-do" }

# glossary: sk-cycling
- { term: Giro,          type: race, forms: [Giro, Gira, na Gire, Girom], pron: "DŽI-ro", note: "byť na Gire / ísť na Giro; full name Giro d'Italia is indeclinable" }
- { term: Giro d'Italia, type: race, forms: indeclinable, note: "straight apostrophe; hashtag #giroditalia" }
- { term: Tour de France, type: race, forms: indeclinable, note: "short: na Tour" }
- { term: Vuelta,        type: race, forms: [Vuelta, Vuelty, na Vuelte, Vueltou] }
- { term: Strade Bianche, type: race, forms: indeclinable, pron: "STRA-de bi-AN-ke", note: "the roads themselves: šotolinové cesty" }
- { term: etapa,         type: term, forms: [etapa, etapy, v etape, etapou], note: "gen. pl. etáp: 21 etáp; 1. etapa" }
- { term: časovka,       type: term, forms: [časovka, časovky, v časovke, časovkou], note: "individuálna / tímová časovka" }
- { term: horská prémia, type: term, forms: [horská prémia, horskej prémie, na horskej prémii, horskou prémiou], note: "prémia 1. kategórie" }
- { term: ružový dres,   original: maglia rosa, type: jersey, forms: [ružový dres, ružového dresu, v ružovom drese, ružovým dresom], note: "maglia rosa: lowercase, indeclinable, pron. MA-ľa RÓ-za" }
- { term: modrý dres,    original: maglia azzurra, type: jersey, note: "vrchárska súťaž" }
- { term: cyklámenový dres, original: maglia ciclamino, type: jersey, note: "bodovacia súťaž" }
- { term: biely dres,    original: maglia bianca, type: jersey, note: "najlepší mladý jazdec" }
- { term: Cima Coppi,    type: term, forms: indeclinable, pron: "ČI-ma KOP-pi", note: "najvyšší bod Gira" }
- { term: pelotón,       type: term, forms: [pelotón, pelotónu, v pelotóne, pelotónom], note: "synonym: balík" }
- { term: únik,          type: term, forms: [únik, úniku, v úniku, únikom] }
- { term: celkové poradie, type: term, forms: [celkové poradie, celkového poradia, v celkovom poradí, celkovým poradím] }
- { term: deň voľna,     type: term, forms: [deň voľna, dňa voľna, počas dňa voľna, dňom voľna] }
- { term: šotolina,      original: sterrato, type: term, forms: [šotolina, šotoliny, na šotoline, šotolinou], note: "šotolinový úsek" }
- { term: Tadej Pogačar, type: rider, forms: [Pogačar, Pogačara, o Pogačarovi, s Pogačarom], pron: "po-GA-čar" }
- { term: Filippo Ganna, type: rider, forms: [Ganna, Gannu, o Gannovi, s Gannom], note: "declines like hrdina" }
- { term: Giulio Ciccone, type: rider, forms: [Ciccone, Cicconeho, o Cicconem, s Cicconem], pron: "či-KO-ne", note: "declines like Goethe" }
# her own words (never "corrected")
- { term: lízatko,       type: word, heard_as: [lyžičko], note: "Giro_00 hook" }
- { term: Ľuboško,       type: name, note: "vocative/affectionate; keep as said" }
```

For later: add `keep_as_said` entries for her eastern particles once Katarina confirms which ones she uses (needs Katarina). Add the Stage 2 town Koper only after checking its locative: "v Kopri" vs. "v Koperi" (`verify`).

#### Q7. Giro_00 Instagram caption
The tone is right: warm, first person plural, playful, the same voice as the reel. Spelling, diacritics, numeral agreement ("všetkých 21 etáp", "Gira 2027") and the spaced en dash are all correct. "naživo" and "popritom" are correctly written as one word, and "vám" is correctly lowercase for addressing the audience. Findings:
1. **Parallel structure (fix):** "trochu histórie, geografie a tipy, ako…" mixes the genitive after *trochu* with the accusative *tipy*. → "trochu histórie, trochu geografie a tipy, ako sa na Giro vybrať aj naživo."
2. **Optional: the hook doesn't land.** The question "Prečo je lízatko ružové?" is answered with May (the month), but the real point is pink = the Giro's color. Suggestion: "…a v máji je Giro d'Italia, ktorého farba je ružová. 🇮🇹🩷". Leave it if the vagueness is intended.
3. "Lebo máj je lásky čas" alludes to Mácha's *Máj* ("byl lásky čas"). It works as an allusion; keep it.
4. "Zajtra začíname 1. etapou." is correct. The video no longer says "Zajtra: 1. etapa" (removed in round 1), so the post caption is now the only place that makes the promise. That's fine.
5. Hashtags: lowercase and without diacritics, as they should be. `#trieste` with "Terst" in the text matches the Q1 rule. `#adventnykalendar` is fine.
6. Asking for comments is fine even though the Hub doesn't import them (R49). Comments are read on Instagram.

Corrected line 3, ready to paste:
> Tento december namiesto čokoládky v adventnom kalendári: každý deň jedna etapa Gira 2027. Za 24 dní vám predstavíme všetkých 21 etáp – trochu histórie, trochu geografie a tipy, ako sa na Giro vybrať aj naživo. Dolomity, Alpy, Apeniny alebo len more… a popritom spotení chlapi. 🚴‍♂️

### Proposals

#### P1. Correction memory must be context-bound
- **Type:** risk
- **Section:** §8
- **Proposal:** Every correction stores the heard **phrase** together with its neighboring words. It is auto-applied only when that exact phrase recurs. Single-word rules are auto-applied only if the heard word is **not a valid Slovak word** (not in the dictionary from P8) or the producer marks the rule `always`. Otherwise `fix_captions` only suggests the change. Number formatting ("po 30") moves to the style rules, out of the memory. Remove the "takúto → toto" example.
- **Suggested spec text:** Replace the §8 bullet "**Correction memory:** every manual caption fix is stored as (heard → correct, context) and auto-applied next time: `lyžičko → lízatko` · `takúto → toto` · `po 30 → po tridsiatke`." with:
  > - **Correction memory:** every manual caption fix is stored as `{heard_phrase, correct_phrase, scope}`, where the phrase includes at least one neighbouring word (e.g. `takúto lyžičko → toto lízatko`). `fix_captions` auto-applies a correction only when the whole phrase matches; a single-word correction is auto-applied only if the heard word is not a valid Slovak word (`lyžičko → lízatko`) or the producer set `scope: always`. Everything else is returned as a suggestion. Number formatting (`po 30 → po tridsiatke`) is a style rule (DESIGN_LANGUAGE §4), not a correction.
- **Why:** "takúto" is a common valid word. Replacing it everywhere corrupts captions silently, and nobody re-reads every word on a 50 s reel. One concrete false fix per reel is enough to break the "factual or caption corrections = 0" metric (§26).
- **Priority:** before phase 3

#### P2. Glossary terms carry their case forms
- **Type:** change
- **Section:** §8, §18 (`glossary_term`)
- **Proposal:** Each term stores its forms (nominative, genitive, locative with preposition, instrumental), a `captions` policy (`as_said` or `canonical`) and optional `heard_as` misspellings. `fix_captions` and `lint_script` match on **any form** and replace with the **same case** of the correct term. They never insert a nominative into an inflected slot. Also fix the §8 example, which isn't valid YAML.
- **Suggested spec text:** Replace the §8 glossary YAML block with:
  ```yaml
  - term: Terst
    original: Trieste
    type: city
    forms: [Terst, Terstu, v Terste, Terstom]   # nom, gen, loc, ins
    captions: as_said        # captions follow speech; titles, maps and post captions use the term
  - term: lízatko
    type: word
    heard_as: [lyžičko]
  - term: Zoncolan
    type: climb
    forms: [Zoncolan, Zoncolanu, na Zoncolane, Zoncolanom]
    pronunciation: "dzon-ko-LAN"
  ```
  and add after it: "Matching uses all forms; a replacement keeps the case of the matched form. Terms without `forms` are indeclinable."
- **Why:** Slovak declension. "v Trieste" → "v Terst" is ungrammatical, and the correct "v Terste" can only come from stored forms. This is cheaper than a morphological analyzer.
- **Priority:** before phase 3

#### P3. Caption fidelity: clean verbatim, names as spoken
- **Type:** risk
- **Section:** DESIGN_LANGUAGE §4, §8 (relates to R8)
- **Proposal:** Write down the clean-verbatim policy from Q2. Captions write place names in the form she said (exonym or original), since both are glossary forms. The exonym rule applies to titles, maps and post captions. Her Italian words are never translated, and her dialect words marked `keep_as_said` are never standardized.
- **Suggested spec text:** Add to the DESIGN_LANGUAGE §4 `captions:` YAML:
  ```yaml
    fidelity: clean_verbatim          # her words and word order; no fillers, stutters or false starts
    keep: [discourse_particles, dialect_words, her_italian_words, affectionate_forms]
    fix_silently: [spelling, diacritics, case_and_agreement_endings]
    never: [change_words, reorder, fix_facts_in_captions, translate_her_italian]
    place_names: as_said              # Trieste stays Trieste if she said it; titles/maps/post use exonyms (§7)
  ```
  and in spec §8, replace "**Translation:** speech in other languages is translated into concise Slovak, marked as translated in the data." with "**Translation:** longer speech by others in another language is translated into concise Slovak and marked as translated. Katarina's own Italian words and phrases are captioned as said, never translated."
- **Why:** R8 says captions use glossary forms (Terst, Rím). Read literally, an agent would caption a spoken "Trieste" as "Terst", and viewers hear one name and read another. That breaks principle 1 ("Katarina's own words") and the "words she actually said" rule (DESIGN_LANGUAGE §10). Making the spoken original a glossary form keeps R8 intact.
- **Priority:** before phase 3

#### P4. Exonym policy for titles, maps and post captions
- **Type:** addition
- **Section:** §8, DESIGN_LANGUAGE §7
- **Proposal:** Use an exonym only if it is in the ÚGKK list **and** in active media use; otherwise use the Italian original, inflected. Never invent exonyms. Hashtags use the original, lowercase, without diacritics.
- **Suggested spec text:** Add to §8 after the glossary block:
  > - **Place-name policy:** on-screen titles, map labels and post captions use the Slovak exonym when it is on the ÚGKK exonym list and in current use (Terst, Rím, Neapol, Miláno, Turín, Janov, Benátky, Florencia, Ľubľana, Sicília, Toskánsko, Dolomity, Alpy, Apeniny); otherwise the Italian original, inflected in Slovak (Bolzano → v Bolzane; Padova, not Pádua; Trento, not Trident). Never coin an exonym. Captions follow speech (DESIGN_LANGUAGE §4). Hashtags use the original form, lowercase, without diacritics (`#trieste`).

  and in DESIGN_LANGUAGE §7 change `labels_language: sk   # Terst, Rím, TALIANSKO, SLOVINSKO, Jadranské more` → `labels_language: sk   # exonyms per REELS_HUB_SPEC §8 place-name policy: Terst, Rím, TALIANSKO, SLOVINSKO, Jadranské more; otherwise Italian original (Bolzano)`
- **Why:** ÚGKK says its standardized exonyms are binding for the press, but it also recommends using fewer of them. Dated ones (Pádua, Trident) would look odd to a Slovak cycling audience, and TASR itself uses Janov while writing Italian names for small towns.
- **Priority:** before phase 3

#### P5. Number rules with Slovak formatting
- **Type:** change
- **Section:** DESIGN_LANGUAGE §4
- **Proposal:** Extend the `numbers` block as in Q3.
- **Suggested spec text:** Replace the `numbers:` block with:
  ```yaml
    numbers:
      words: [idiomatic_ages_and_decades, approximate_quantities, determiner_one]   # "po tridsiatke", "pár dní", "každý deň jedna etapa"
      digits: [counts_with_noun, exact_ages, measurements, years, dates]            # "24 dní", "21 etáp", "má 28 rokov", "172 km"
      ordinals: "digit + dot: 1. etapa, 8. mája; never at line end"
      decimal_separator: ","            # 3 418,9 km
      thousands_separator: nbsp         # 3 419 km (always, from 1 000)
      unit_spacing: "172 km, 8 %, 25 €; adjective: 8-percentné"
      time: "14:30"
      ranges: "od 8. do 30. mája"       # Monstera has no en dash
  ```
- **Why:** Whisper outputs English-style digits and separators. Without explicit rules, agents produce "3,418.9 km" or "8%", which is wrong in Slovak, and the ordinal-dot case quietly changes the meaning.
- **Priority:** before phase 3

#### P6. Line-break and question rules, checked by caption QA
- **Type:** addition
- **Section:** DESIGN_LANGUAGE §4, §8 (Caption QA)
- **Proposal:** Add the line-break rules from Q5 as data, and three cheap checks to caption QA.
- **Suggested spec text:** Add to the DESIGN_LANGUAGE §4 `captions:` YAML:
  ```yaml
    line_breaks:
      never_split: [preposition+noun, number+unit_or_noun, first+last_name, "Giro d'Italia", ordinal+noun]
      never_end_line_with: [single_letter_words, ordinal_number]   # v k s z o u a i; "30." loses its dot
      prefer_break_before: ["že", "ktorý", "ale", "lebo", "keď"]
    questions: >
      The style hides a line-final "?". A question without a question word (prečo, kde, kedy, ako,
      koľko, kto, čo, ktorý, či) or tag (nie?, však?, hej?) must not end a caption line; move the
      break or set it as a title, and note it in editors_notes.md.
    quotes: "„…“"
  ```
  and in spec §8, extend the **Caption QA** bullet with: "…inconsistent speaker labels, a one-letter word or an ordinal at line end, a number split from its noun, a yes/no question without a question word ending a line."
- **Why:** The muted pass is a brand principle ("Sound-off first"). A question that reads as a statement is the one Slovak-specific way the hidden `?` changes meaning. All three checks are simple token rules, with no model needed.
- **Priority:** before phase 3

#### P7. Foreign-term and inflection conventions
- **Type:** addition
- **Section:** DESIGN_LANGUAGE §4
- **Proposal:** Write down the Q4 rules so agents don't guess.
- **Suggested spec text:** Add under DESIGN_LANGUAGE §4 **Workflow**, as a new paragraph:
  > **Foreign terms.** No italics (captions, titles, post). Original spelling and diacritics (Pogačar, Roglič). Italian common nouns lowercase (maglia rosa). "Giro" declines like *mesto* (byť na Gire, ísť na Giro, víťaz Gira); "Giro d'Italia", "Tour de France" and "Strade Bianche" are indeclinable; "Vuelta" declines. Male rider surnames decline by Slovak rules (Pogačara, s Gannom, Cicconeho). Straight apostrophe in d'Italia; none in hashtags.
- **Why:** These are the most common points of uncertainty in Slovak cycling texts, and the press uses a mix (Sportnet "po Gire d'Italia", TASR "etapy Giro d'Italia"). One rule keeps the series consistent.
- **Priority:** before phase 3

#### P8. Dictionary-based diacritics and unknown-word check
- **Type:** addition
- **Section:** §8 (Caption QA), §21
- **Proposal:** Make "missing diacritics" in caption QA concrete. Flag any caption word that isn't in a Slovak Hunspell dictionary (`sk_SK`) or the project glossary, and suggest the diacritic variant if one exists ("lizatko" → "lízatko"). P1 uses the same check to decide whether a heard word is "not a valid Slovak word". This is not R2's deferred WER check; it doesn't compare against audio.
- **Suggested spec text:** In §8 change "**Caption QA:** missing diacritics," → "**Caption QA:** missing diacritics and unknown words (Hunspell `sk_SK` + project glossary as user dictionary; suggest the diacritic variant),"; in §21 add a row: `| Spelling | Hunspell sk_SK dictionary (license to confirm at build) | Diacritics check, P1 'valid word' test |`
- **Why:** Without a dictionary, "missing diacritics" can't be implemented, and P1's safety rule needs one anyway. It's a single small dependency. The license is **unverified**.
- **Priority:** before phase 3

#### P9. Seed the first glossary from this review
- **Type:** addition
- **Section:** §6.1, §8
- **Proposal:** Import the 52 terms from Q6 as the `sk-italy` and `sk-cycling` glossaries for the Giro project. Before Giro_01, add Katarina's dialect particles as `keep_as_said` (needs Katarina).
- **Suggested spec text:** Add to §8: "**Seed:** the Giro 2027 project starts with the `sk-italy` and `sk-cycling` glossaries from review packet 14 (Q6), 52 terms with case forms; Katarina's dialect words are added as `keep_as_said` before the first automatic caption run."
- **Why:** Phase 3's "done when" line tests `fix_captions` on "lyžičko" and "po 30" only. A seeded glossary makes the first real reels benefit from day one.
- **Priority:** before phase 3

**Sign-off:** approve with changes (P1–P3 before captions go automatic in phase 3; the rest can come with them)
