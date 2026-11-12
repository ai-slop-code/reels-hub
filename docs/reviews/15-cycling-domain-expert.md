# Review packet 15: cycling journalist / domain expert

**Priority:** good to have (before the Giro project's stage reels)
**Time needed:** ~1 h
**Decisions already made:** see [README](README.md#decisions-already-made-please-dont-reopen).

## Why you
Each reel states race facts, history and spectator tips. The Hub's fact store decides what counts as verified; it needs someone who knows the sport and its sources.

## Read
- [§7 Facts and sources](../spec/REELS_HUB_SPEC.md#7-module-c-facts-and-sources)
- [§6.3 New reel: gathered intelligence](../spec/REELS_HUB_SPEC.md#6-module-b-projects-reels-and-the-reel-prompt)
- Reference: Stage table and sources in `../reels/giro00-intro/review_notes.md`; the Stage 1 Slovenia question (announcement says it crosses briefly into Slovenia, route page doesn't say where)

## Questions
1. **Source tiers:** organizer (giroditalia.it), Giro archive, transport operators and local authorities as primary; press as secondary. Agree? Other primary sources (e.g. regional race committees, UCI)?
2. **Stage 1:** where does the route cross into Slovenia, and when will the official stage map show it?
3. **Story angles:** for 21 stages, what makes a good one-minute story per stage (history, climbs, towns, riders, food, travel)? Any stage you'd prioritize?
4. **Pronunciation:** town and climb names Katarina will say. Who can check pronunciations?
5. **Spectator advice:** best sources for race-day access, road closures and public transport for each region?
6. **Change tracking:** routes and distances change. How often should facts be re-checked before each reel?

## Your input

> Reviewer: AI acting as a senior cycling journalist / domain expert. Reviewed spec v0.5. Web sources checked on **2026-11-12**; links below. `giroditalia.it` returned **HTTP 403** to my automated fetches (route page and news article), so organizer wording is quoted from search-engine snippets of those pages and from press that reproduced them. Anything I could not confirm is marked **unverified**.

### Summary
The fact store is the right idea and the Stage 1 case proves it, but the v0.5 model is too coarse for a December preview of a May race. Three things matter most. (1) **Silence is not a conflict.** The organizer clearly says Stage 1 enters Slovenia; what is open is *where* and *how much*, so the Hub should split "does it cross" (verified) from "where/how long" (conflicting). I found the likely answer below: the stage reportedly passes **Lipica (km 94.2)** on the Karst and goes back into Slovenia over the **Hrvatini** climb (km 134) above Muggia, so it is two incursions, not one. (2) **Facts need a volatility class.** History doesn't change, route details change until the road book comes out, and spectator access isn't official until months after December. Re-check timing should follow the class, plus a check within 48 h of posting. (3) **There is a dated risk:** Slovenia's hosting agreement is due **3 December 2026**, the same day the Stage 2 reel would post. Smaller fixes: rank sources within "primary", let press-only facts be said only with attribution, add stress and source fields to glossary pronunciations, and store climbs and per-place country in the stage table so the map generator can draw the border crossing.

### Answers

#### Q1. Source tiers
I mostly agree, with four refinements.

1. **Rank documents within "primary".** The organizer publishes several documents that don't say the same thing, and the more specific one should win:
   `road book (Garibaldi) / stage timetable > official stage profile & planimetry > route page technical info > press release prose > organizer social posts`.
   Stage 1 is the example. The route page's technical text doesn't mention Slovenia, the EN press release says "crossing briefly", the IT press release says "uno sconfinamento in Slovenia", and the organizer's own post says "From Trieste to Slovenia and back to Italy". The **profile image** is probably the most specific primary source (Slovenian press quote km points that look read off it), but I couldn't open it (403).
2. **Other primary sources, each only for its own domain:**
   | Source | Primary for | Not primary for |
   |---|---|---|
   | RCS Sport / giroditalia.it (organizer) | route, km, climbs, GPM categories, dates, stage stats in the press kit | spectator access, transport |
   | Host authorities: Regione FVG, Comune di Trieste, Slovenian Ministry of Economy, Tourism and Sport (MGTŠ), host municipalities (Ljubljana, Koper) | whether and how they host; later, road-closure ordinances | route details |
   | National federations (FCI, KZS Slovenia, SZC Slovakia) | hosting statements, national team facts | route |
   | UCI | calendar status (WorldTour), registered teams, rules (e.g. time cuts, jersey rules) | route, history |
   | Transport operators (Trenitalia, Trenord, Trieste Trasporti, ATAC, SŽ, Arriva SI, DARS/promet.si) and police (Polizia Stradale, Prefettura) | services, closures, detours | race facts |
3. **Archive tier:** the organizer's own press-kit statistics count as primary. For older history, the organizer's albo d'oro and Giro archive count as archive. Independent statistics sites (ProCyclingStats, Cycling Archives / dewielersite, Mémoire du cyclisme) are good **secondary** cross-checks. **La Gazzetta dello Sport** belongs to the organizer's group (RCS). Treat it as secondary: it's close to the source but it's still press.
4. **Add a "lead" tier: never cite, only use to find the primary source.** This covers Wikipedia, aggregators (Pollar), tour sellers (Mummu Cycling) and fan sites. Evidence from today's check: Pollar wrote that the race "crosses into Slovenia for the second stage" and left out Stage 1. Press also disagrees with the organizer on numbers. RTV SLO's table gives Stage 7 as 19.9 km and Stage 15 as 37.9 km, while the organizer and Cyclingnews give 19.6 and 37.3. The Zum Zeri climb is 8.7 km per Domestique and 8.4 km per RTV. The count of summit finishes is 7 or 8 depending on whether the uphill ITT counts. The spec's rule that only primary counts as `verified` is correct. Keep it.

Also: a press-only fact that is plausible and useful, like "past Lipica", should be **sayable with attribution** ("podľa slovinských médií…") rather than banned. See P2.

#### Q2. Stage 1: where it crosses into Slovenia, and when the official map will show it
**What I found (checked 2026-11-12):**

| Point | Claim | Source | Tier |
|---|---|---|---|
| Stage enters Slovenia | "crossing briefly into Slovenia" (EN); "uno sconfinamento in Slovenia" (IT) | [Organizer EN](https://www.giroditalia.it/en/news/from-trieste-to-rome-giro-ditalia-2027-route-unveiled/), [Organizer IT](https://www.giroditalia.it/news/da-trieste-a-roma-presentato-il-percorso-del-giro-ditalia-2027/) (snippets; page 403) | primary |
| Route page silent on Slovenia for Stage 1 | "Undulating opening stage… ~2,400 m… start and finish in Trieste, which hosted the 2014 Grand Finale" | [Route page](https://www.giroditalia.it/en/the-route/) (snippet) | primary |
| Route sequence | flat start past **Redipuglia** → Karst → **Rupinpiccolo / Repnič** (Italian Karst) → **Lipica** at **km 94.2** → finale climbs **Hrvatini**, **Prebeneg**, **Cattinara–Sella di Longera** (crest 13.3 km from the line) | [Siol.net, 4 Nov 2026](https://siol.net/sportal/kolesarstvo/sloviti-giro-prinasa-nekaj-cesar-slovenija-se-ni-dozivela-prvo-povsem-slovensko-etapo-705455) | secondary |
| Two incursions | "Trasa jih bo dvakrat popeljala na slovensko stran meje" (the route takes them across to the Slovenian side twice) | Siol (above); [Mummu Cycling stage page](https://mummucycling.com/events/2027-giro/stages/stage-1-trieste-to-trieste) ("crosses into Slovenia twice over the Karst") | secondary / lead |
| Climb km | Hrvatini 151 m at km 134.0; Prebeneg 246 m at km 142.6; Cattinara–Sella di Longera 283 m at km 158.7; finish km 172 | Mummu (above) | lead (must confirm on the official profile) |
| Lipica named by the federation | KZS president Andraž Vehovar: the first stage goes "mimo Lipice" (past Lipica) | [Delo, 3 Nov 2026](http://www.delo.si/sport/kolesarstvo/slovenski-navijaci-cakajo-na-odgovor-pogacarja-in-roglica) | secondary (quoting a federation) |
| Extent disputed | RTV SLO: "v dobršni meri v Sloveniji… celotni Kras od zahoda do vzhoda" (to a large extent in Slovenia, across the whole Karst west to east); Cicloweb: "buona parte… in territorio sloveno"; SpazioCiclismo: "lungo sconfinamento"; organizer EN: "briefly" | [RTV SLO](https://www.rtvslo.si/sport/kolesarstvo/dirka-po-italiji/prva-etapa-gira-2027-po-celotnem-krasu-druga-etapa-od-ljubljane-do-kopra/798880), [Cicloweb](https://www.cicloweb.it/news/278694104582/giro-ditalia-2027-percorso-tutte-le-tappe-e-altimetrie), [SpazioCiclismo](https://cyclingpro.net/spaziociclismo/percorsi/percorso-giro-ditalia-2027-tappe-ufficiale) | secondary vs primary → **conflicting** |
| A stage-1 map exists | RTV SLO published an RCS Sport map of the stage ("Zemljevid uvodne etape…", credit RCS Sport) | RTV SLO (above) | secondary (reproduces an organizer map) |

**My reading:** the race leaves Trieste westwards towards Redipuglia, climbs onto the Karst, crosses into Slovenia on the Karst and passes Lipica around km 94, then comes back into Italy. In the finale it crosses into Slovenia a **second time** at **Hrvatini** (Crevatini). That is a Slovenian village above Muggia, in Ankaran municipality; the location is my own geographic knowledge, so check it on a map. From there it goes back into Italy for Prebeneg/Prebenico (San Dorligo della Valle / Dolina) and Cattinara above Trieste. **The exact border crossings** (e.g. Basovizza/Bazovica–Lipica, Fernetti/Fernetiči, or the Muggia/Škofije roads) **are not published anywhere I found.** Don't state them.

**What can be said on 2 December (Stage 1 reel):**
- Safe now (verified, organizer): "Štart aj cieľ v Terste, a cestou odbočí do Slovinska."
- Safe with attribution (secondary): "Podľa slovinských médií pôjde okolo Lipice, domova lipicanov."
- Only if the producer confirms the official profile shows Lipica and Hrvatini: "dvakrát do Slovinska". Until then, *don't* say "dvakrát" or "krátko" (briefly); the sources conflict on both.

**When the official map will show it:** the route page currently shows profiles and technical text, no stage maps. A reader asked on 5 Nov "Where do we find maps of the individual stage routes? The Giro site only gives profiles", and cyclingstage replied they will publish GPX files "in the coming weeks" ([cyclingstage](https://www.cyclingstage.com/giro-2027-route/italy-route-2027/)). Historically the organizer adds stage planimetries and timetables in spring, and the road book (Garibaldi) appears shortly before the race. Both timings are **unverified for 2027**. **Practical consequence:** no official stage map before the December series ends. Act now: (a) open the official Stage 1 **profile** on giroditalia.it in a normal browser. Profiles usually label places and km, so if it shows "Lipica" and "Hrvatini/Crevatini", the crossing becomes `verified` with the profile as source. (b) Note that a third-party GPX (cyclingstage) is a *lead*, not a source.

**Extra risk found:** Siol reports that Slovenia's Ministry of Economy, Tourism and Sport (MGTŠ) has only signed a letter of intent, and the **final agreement is targeted for 3 December 2026**: "odločitev o izvedbi slovenske etape pa bo… sprejeta po koncu pogajanj" (the decision on holding the Slovenian stage will be taken after the negotiations end). That date falls between the Stage 1 reel (Day 2, 2 Dec) and the Stage 2 reel (Day 3, 3 Dec). See P5.

#### Q3. Story angles for 21 stages
**What makes a one-minute stage story:** one question, one answer, one place. A good stage reel has **one surprising fact** (verified), **one place you can picture** (town, climb, food), and **one reason to watch the stage in May**. History works when it's a person and a moment ("Pantani, 1994, Mortirolo"), not a list. Climb numbers (length, %) work as one on-screen card, not as speech. Rider predictions don't work in December (start lists are unknown; see P6).

Suggested angle per stage. Data is from the organizer release and route page, Domestique, Bikeitalia and RTV SLO as linked. Anything marked † is from secondary press only and must be verified before stating.

| Stage | Angle (one-minute story) | Hook fact |
|---|---|---|
| 1 Trieste–Trieste | Two countries in one day; Lipizzaner horses at Lipica† | Trieste's Grande Partenza returns after 1981 (Knudsen won a 6.6 km prologue in Piazza Unità) — organizer |
| 2 Ljubljana–Koper | **First ever stage entirely in Slovenia**; Postojna Cave† on the way; Markovec kicker | 4th Giro stage start in Slovenia (1971, 1994, 2001) — organizer |
| 3 Cervignano–Possagno | Possagno = Canova's birthplace (Gipsoteca)† | Back to Italy; uphill finish |
| 4 Argenta–Misano | Finish on a MotoGP track (Misano "Marco Simoncelli") | Start of a "three racetracks" mini-thread (4, 11, 15) |
| 5 Filottrano–Sassotetto | **Tribute to Michele Scarponi**, 10 years after his death (Filottrano, 22 Apr 2017) | First summit finish, 13.1 km at 7.4 %† |
| 6 Alba Adriatica–Lanciano | Abruzzo coast to hills; food (arrosticini†) | Rising finish |
| 7 Sulmona–Campo di Giove | Uphill time trial; Sulmona's confetti† (sugared almonds) | First Giro ITT in Abruzzo (Pollar)† |
| 8 Trasacco–Napoli | Naples: 6th consecutive finish, 48th overall — organizer | Pizza, obviously |
| 9 Itri–Monte Livata | Subiaco, monasteries of St Benedict† (organizer's "spiritual routes" theme) | Summit finish |
| 10 Palombara Sabina–Norcia | Norcia: rebuilt after the 2016 earthquake†; norcineria | 218 km, no flat road† |
| 11 Gualdo Tadino–Scarperia | **Longest stage, 220 km**; Mugello circuit finish | Racetrack #2 |
| 12 Montecatini–Zeri | "Tappa Bartali" (organizer); first time on Passo dei Due Santi | Gino Bartali story (Righteous Among the Nations)† |
| 13 Borgo Val di Taro–Reggio Emilia | Parmigiano country; easy sprint day | Food story |
| 14 Cantù–Piani di Bobbio | Madonna del Ghisallo, the cyclists' chapel† | 4,900 m climbing† |
| 15 Monza–Milano ITT | From the F1 circuit to central Milan; Milan's 91st finish (organizer) | Racetrack #3 |
| 16 Sondrio–Aprica | **Queen stage**: Mortirolo twice + Gavia (Cima Coppi, 2,618 m); Pantani 1994 | Gavia 1988 snow stage†; Gavia returns after it was cut in 2019† |
| 17 Chiari–Vo' | Colli Euganei, Petrarch's Arquà†; quiet day before the mountains | Two short climbs in the final 25 km† |
| 18 Rovereto–Madonna di Campiglio | Campiglio 1999, Pantani's exclusion (handle with care) | 5 categorised climbs† |
| 19 Rovereto–Sacile | Sacile, "Garden of the Serenissima"†; transition day | Last sprinter chance before Rome† |
| 20 Pordenone–Zoncolan | **The decisive climb**: 10.1 km at 11.9 % from Ovaro†; 8th finish there (Simoni ×2, Basso, Antón, Rogers, Froome, Fortunato — Bikeitalia†) | Pordenone, Italian Capital of Culture 2027 (RTV)† |
| 21 Roma–Roma | 5th consecutive Rome finale (organizer); ~9 km circuit × 8 | Monuments circuit |

**Priorities.** If time is short, give the best footage and most care to **Stage 1** (two countries, the open question from Giro_00), **Stage 2** (historic first fully Slovenian stage, closest to Slovak viewers), **Stage 16** (queen stage, Pantani), **Stage 20** (Zoncolan) and **Stage 5** (Scarponi; tone matters).

**Slovak angle (unverified):** Peter Sagan won a Giro stage (2020) and the points jersey (2021). Check this in the organizer archive before stating; it's the natural local hook for a sprint stage. Current Slovak riders' 2027 Giro plans are unknown in December; don't state them.

**Days 23–24 (open slots):** Day 23 "how to watch in person": the closest stages to Slovakia are Stages 1–2 in Trieste and Slovenia and Stage 20 Zoncolan in Friuli. Day 24 (Christmas Eve): a recap with the "promise" of May. Rest days fall on **17 and 24 May**, which matters for continuity lines like "next day".

#### Q4. Pronunciation: names and who can check them
**Who checks:**
- Italian names: **DiPI online** (Canepari's *Dizionario di pronuncia italiana*) and **RAI DOP** (*Dizionario di ortografia e pronunzia*, dizionario.rai.it). Forvo native recordings are a lead only.
- Slovene names (Lipica, Hrvatini, Markovec, Koper, Postojna): **Fran.si** (ZRC SAZU dictionaries, with accent marks); a Slovenian speaker for confirmation.
- **Slovak exonyms and declension** (Terst, Rím, Ľubľana, Neapol, Miláno; "v Terste", "na Zoncolane"): the official Slovak exonym list from **ÚGKK SR's Názvoslovná komisia** and **JÚĽŠ SAV** (Jazykovedný ústav Ľ. Štúra) dictionaries and language advice. This overlaps with packet 14 (Slovak language editor).
- Human check: one Italian-speaking cyclist or commentator for the climbs. In practice, a Slovak TV cycling commentator knows the broadcast-standard pronunciations (**unverified** availability).

**Names Katarina is likely to say, with stress (CAPS).** These are from my knowledge; **verify each in DiPI or RAI DOP before use**, because Italian stress is not predictable from spelling.
Trieste (tri-ES-te; Slovak *Terst*), Redipuglia (re-di-PU-lya), Lipica (LI-pi-tsa; It. *Lipizza*), Hrvatini (hr-va-TI-ni; It. *Crevatini*), Cattinara (kat-ti-NA-ra), Ljubljana (Slovak *Ľubľana*), Koper (KO-per; It. *Capodistria*), Markovec (MAR-ko-vets), Cervignano (cher-vi-NYA-no), Possagno (pos-SA-nyo), Argenta (ar-JEN-ta), Misano (mi-ZA-no), Filottrano (fi-lot-TRA-no), Sassotetto (sas-so-TET-to), Lanciano (lan-CHA-no), Sulmona (sul-MO-na), Trasacco (tra-ZAK-ko), Itri (I-tri), Subiaco (su-BYA-ko), Norcia (NOR-cha), Gualdo Tadino (GWAL-do ta-DI-no), Scarperia (skar-pe-RI-a), Zeri (DZE-ri), Cantù (kan-TU), Piani di Bobbio (PYA-ni di BOB-byo), Sondrio (SON-dryo), **Aprica (A-pri-ka, stress on the first syllable)**, Mortirolo (mor-ti-RO-lo), **Gavia (GA-vya)**, Chiari (KYA-ri), Vo' (VO), Rovereto (ro-ve-RE-to), **Sacile (SA-chi-le)**, Pordenone (por-de-NO-ne), Zoncolan (dzon-ko-LAN; Friulian, final stress), Ovaro (O-va-ro).
Traps: *Aprica*, *Sacile*, *Gavia* and *Itri* are stressed on the first syllable, which a Slovak speaker wouldn't guess. Italian *z* in Zoncolan and Zeri is voiced (dz). "Cima Coppi" is CHI-ma KOP-pi.

#### Q5. Spectator advice: best sources per region
**The rule first:** in December, **nothing about closures, timings or access is official.** Closure ordinances, the race timetable (*cronotabella*) and transport plans come out in the weeks before the race. So spectator advice in December reels must be framed as typical: "cesty sa zvyčajne zatvárajú niekoľko hodín pred príchodom pretekárov" (roads usually close a few hours before the riders arrive). It should carry the "race-day access unconfirmed" flag that §7.2 already has. Advice can be **verified** only from these sources once they publish:

| Need | Source (authority) |
|---|---|
| Timings, route km by km | Organizer road book / *cronotabella* on giroditalia.it |
| Road closures (Italy) | Ordinances of the host **Comune** and **Prefettura**; ANAS for state roads; Polizia Stradale press releases |
| Road closures (Slovenia) | **promet.si** (national traffic info, DARS), host municipalities (Koper, Ljubljana, Sežana for the Karst†) |
| Public transport FVG / Trieste | Trenitalia FVG, **Trieste Trasporti** (city buses), TPL FVG |
| Slovenia | **Slovenske železnice**, Arriva Slovenija, LPP (Ljubljana buses) |
| Lombardy (Stages 14–16) | Trenord, ATM Milano (Stage 15) |
| Rome (Stage 21) | ATAC / Roma Mobilità |
| Naples (Stage 8) | EAV, ANM |
| Mountain finishes (Zoncolan, Gavia, Mortirolo) | Host Comune / Regione notices on climb closures (often closed to cars from the evening before or early morning; **unverified for 2027**) |
| Border | Italy and Slovenia have had **temporary internal Schengen border checks** in recent years; 2027 status **unverified**. Tell viewers to carry ID on Stages 1–2 |

#### Q6. Change tracking: how often to re-check
Re-check by **volatility class**, not one global interval:

| Class | Examples | Re-check | Can be `verified` in Dec? |
|---|---|---|---|
| `history` | 1981 Knudsen prologue; 2014 finale; Pantani 1994 | once, at entry | yes |
| `route` | start/finish, km, climbs, GPM km, places passed | at prompt build, and again **≤ 48 h before posting**; default `review_by` = 14 days | yes, from organizer docs |
| `pending` | Slovenian hosting deal (3 Dec 2026); Naples finish location "still to be confirmed" (Domestique†); a stage-route GPX release | on the named date | no until resolved |
| `access` | closures, transport, viewing spots | after official ordinances only | no (always flagged) |
| `forecast` | rider participation, favourites | never a fact | no (see P6) |

Two more practical points:
- **The automated "diff check against the source page" in §7.2 will fail for the organizer.** giroditalia.it returned HTTP 403 to my fetches today. Keep a manual path: a "Re-checked" button that sets `checked` to today, with an optional pasted quote (`says`). See P4.
- Known change points before May: the Slovenian deal (3 Dec 2026), planimetries/GPX (spring, unverified), road book (just before the race), and weather changes during the race (the Gavia was cut in 2019; snow on the Gavia and Mortirolo can change Stage 16 on the day). A reel made in December can't track the last two, which is why stage reels should use **"plánovaná trasa"** (planned route) language.

### Proposals

#### P1. Split the Stage 1 fact: "silence is not a conflict"
- **Type:** change
- **Section:** §7.1, §7.2, §25 (phase 3 "done when")
- **Proposal:** a source that doesn't mention something doesn't contradict it. Store "crosses into Slovenia" as verified and "where / how much" as a separate conflicting fact. Update the §7.1 example with today's findings. Keep the phase-3 acceptance check by pointing it at the extent fact.
- **Suggested spec text:**
  §7.1, replace the YAML block with:
  ```yaml
  fact:
    id: fact_giro27_s1_slovenia
    stage: 1
    class: route                 # history | route | pending | access | forecast (§7.2)
    claim: "Stage 1 (Trieste–Trieste, 8 May 2027) enters Slovenia."
    claim_sk: "Prvá etapa (Terst – Terst) odbočí do Slovinska."
    status: verified
    sources:
      - url: https://www.giroditalia.it/en/news/from-trieste-to-rome-giro-ditalia-2027-route-unveiled/
        kind: primary
        doc: press_release
        says: "crossing briefly into Slovenia"
        checked: 2026-11-12
      - url: https://www.giroditalia.it/news/da-trieste-a-roma-presentato-il-percorso-del-giro-ditalia-2027/
        kind: primary
        doc: press_release
        says: "uno sconfinamento in Slovenia"
        checked: 2026-11-12
    used_in: [giro00]
    review_by: 2026-11-30
  ---
  fact:
    id: fact_giro27_s1_slovenia_extent
    stage: 1
    class: route
    claim: "Stage 1 crosses into Slovenia twice: on the Karst past Lipica (km 94.2) and at the Hrvatini climb (km 134)."
    status: conflicting          # organizer says "briefly"; Slovenian press says "a large part"; route page silent
    sources:
      - url: https://www.giroditalia.it/en/the-route/
        kind: primary
        doc: route_page
        says: "Stage 1 technical info: no mention of Slovenia"
        checked: 2026-11-12
      - url: https://siol.net/sportal/kolesarstvo/sloviti-giro-prinasa-nekaj-cesar-slovenija-se-ni-dozivela-prvo-povsem-slovensko-etapo-705455
        kind: secondary
        says: "dvakrat na slovensko stran meje … Lipica po 94,2 km … Hrvatini, Prebeneg, Cattinara–Sella di Longera"
        checked: 2026-11-12
      - url: https://www.rtvslo.si/sport/kolesarstvo/dirka-po-italiji/prva-etapa-gira-2027-po-celotnem-krasu-druga-etapa-od-ljubljane-do-kopra/798880
        kind: secondary
        says: "v dobršni meri v Sloveniji … celotni Kras od zahoda do vzhoda"
        checked: 2026-11-12
    next_step: "Open the official Stage 1 profile; if it labels Lipica and Hrvatini/Crevatini, add it as a primary source (doc: profile) and set verified."
    review_by: 2026-11-30
  ```
  §7.2, add a bullet after "Conflict detection":
  > - **Silence is not a conflict.** A source that doesn't mention a claim never makes it `conflicting`. Conflict needs two sources that say different things about the same detail. Split broad claims ("enters Slovenia") from details ("where, how long, how many times") so the broad claim can be `verified` while the detail is still open.

  §25 phase 3 "Done when": `Stage 1 Slovenia shows as conflicting` → `Stage 1 "enters Slovenia" shows as verified and "where/how long" as conflicting`.
- **Why:** Giro_00 treated the organizer's own clear statement as unconfirmed only because another page was silent. As specified, the store would block a true, sourced line in the Stage 1 reel (2 Dec). The real disagreement is about extent ("briefly" vs "a large part", once vs twice), and that is what must stay unsaid.
- **Priority:** must-have before build (the dress rehearsal on 27 Nov uses the Stage 1 reel)

#### P2. Rank sources within tiers; add "lead" tier and attributed use
- **Type:** change
- **Section:** §7.2 (Source tiers), §6.4 (Facts you may state)
- **Proposal:** add a document rank within primary sources, a domain for each primary source, a "lead" kind that is never cited, and a third way to use a fact: *attributed* (secondary only, said with "according to…").
- **Suggested spec text:** §7.2, replace the "Source tiers" bullet with:
  > - **Source tiers:** `primary` > `archive` > `secondary` > `lead`.
  >   - **Primary** counts only for its own domain: organizer (route, km, climbs, dates, press-kit stats); host authorities and national federations (hosting, later closures); UCI (calendar, teams, rules); transport operators and police (services, closures). Within the organizer, more specific beats more general: `road_book > profile/planimetry > route_page > press_release > social`.
  >   - **Archive:** organizer albo d'oro and Giro archive.
  >   - **Secondary:** press and statistics sites (incl. La Gazzetta dello Sport, which belongs to the organizer's group).
  >   - **Lead:** Wikipedia, aggregators, tour sellers, fan sites, third-party GPX. Use only to find a primary source; never cite.
  > - **Status vs. use:** `verified` (primary agrees) may be stated as fact. A claim backed only by secondary sources with no primary contradiction may be said **with attribution** ("podľa slovinských médií…"), and editors_notes.md lists it as attributed. Everything else is not said.

  §6.4 template, under "### Facts you may state", add a line:
  > `Attributed only (say "according to {source}"): {secondary-only facts with IDs}`
- **Why:** today's check found press contradicting the organizer on km (Stage 7 19.6 vs 19.9; Stage 15 37.3 vs 37.9) and an aggregator that dropped Stage 1's Slovenian leg. At the same time, the best Stage 1 detail (Lipica) is so far press-only. Without an attributed level, the agent can either over-claim or lose the story.
- **Priority:** before phase 3

#### P3. Volatility class drives re-check timing; check within 48 h of posting
- **Type:** addition
- **Section:** §7.2 (Re-check reminders), §18 (`fact`)
- **Proposal:** add a `class` field to facts with a default `review_by` per class, plus one rule: route facts in a reel must have been checked within 48 h of its planned posting date.
- **Suggested spec text:** §7.2, replace the "Re-check reminders" bullet with:
  > - **Re-check by class** (`class` on each fact):
  >   ```yaml
  >   fact_classes:
  >     history:  { review_by: null }          # checked once
  >     route:    { review_by_days: 14, recheck_before_post_h: 48 }
  >     pending:  { review_by: "{event date}" } # e.g. 2026-12-03 Slovenian hosting deal
  >     access:   { stateable: false }          # closures/transport: flagged "race-day access unconfirmed" until official ordinances
  >     forecast: { stateable: false }          # rider participation, favourites
  >   ```
  >   The reel page and Today (§20) show a warning when a reel's facts are past `review_by`, or when a `route` fact used in the reel wasn't checked within 48 h of its planned posting date. The warning never blocks approval (§2 principle 10).

  §18, `fact` row: `claim, status, review_by` → `claim, claim_sk, stage, class, status, review_by, next_step`.
- **Why:** history never needs re-checking, but route details can change until the road book, and spectator access can't be verified in December at all. One global interval would either nag about fixed history or miss route changes. A 48-hour pre-post check fits the daily cadence and the "2 reels in buffer" rule: the buffer reel gets a quick re-check on its day.
- **Priority:** before phase 3

#### P4. Risk: the organizer's site blocks automated checks
- **Type:** risk
- **Section:** §7.2 (diff check), §21 (fact re-check jobs)
- **Proposal:** don't count on the automated diff check for giroditalia.it. Add a manual re-check that takes a few seconds per fact.
- **Suggested spec text:** §7.2, append to the re-check bullet:
  > Automated page checks are best-effort: some sources (giroditalia.it returned HTTP 403 on 2026-11-12) block non-browser requests. Each fact has a **Re-checked** button that sets `checked` to today and accepts an optional pasted quote (`says`). A failed automated check shows "couldn't check, please check manually" and never changes `status`.
- **Why:** both organizer URLs in the §7.1 example returned 403 to my fetches today. A diff job that fails silently, or marks facts `outdated` because of a fetch error, would be worse than no job.
- **Priority:** before phase 3

#### P5. Risk: Slovenian hosting deal is due on the day the Stage 2 reel posts
- **Type:** risk
- **Section:** §7.1 (example data), §6.3 (open items carried over)
- **Proposal:** seed the `giro2027` fact domain with a `pending` fact for the hosting agreement, and an open item on the Stage 1 and Stage 2 reels. Stage 2 copy should say "plánovaná" (planned) until the deal is announced.
- **Suggested spec text:** §7.1, append to the example:
  ```yaml
  fact:
    id: fact_giro27_slo_agreement
    class: pending
    claim: "Slovenia and RCS Sport sign the final hosting agreement for the Slovenian stage(s)."
    status: unverified
    sources:
      - url: https://siol.net/sportal/kolesarstvo/sloviti-giro-prinasa-nekaj-cesar-slovenija-se-ni-dozivela-prvo-povsem-slovensko-etapo-705455
        kind: secondary
        says: "Končni dogovor želijo skleniti do 3. decembra 2026 … odločitev o izvedbi slovenske etape … po koncu pogajanj"
        checked: 2026-11-12
    review_by: 2026-12-03
  ```
- **Why:** the series plan posts Stage 1 on 2 Dec and Stage 2 on 3 Dec. If the deal slips or changes the route, a reel saying "the first fully Slovenian stage in history" without "planned" would need a correction. That's one of only four success metrics (§26).
- **Priority:** must-have before build (the date falls in the first week of the series)

#### P6. Preview tense; no forecasts as facts
- **Type:** addition
- **Section:** §6.4 (Rules)
- **Proposal:** one prompt rule: December reels describe a planned race. Rider participation, favourites and outcomes are never stated as fact.
- **Suggested spec text:** §6.4 template, "## Rules (always)", add:
  > - This is a preview of a race months away: describe the route as planned ("plánovaná trasa", "pôjdu cez…"). Never state rider participation, favourites or outcomes as fact; at most quote a named person's stated intention with attribution.
- **Why:** December press is full of "will Pogačar ride?" (RTV, Delo, Bikeitalia). Pogačar has said he prefers the Vuelta, and his post-crash status is unclear. That's tempting hook material that would date badly or turn out false by May.
- **Priority:** before phase 9

#### P7. Glossary pronunciation: stress, respelling, source, checker
- **Type:** change
- **Section:** §8 (Glossary)
- **Proposal:** a glossary entry needs a Slovak-reader respelling with the stressed syllable marked, the native name, the source it was checked against, and who confirmed it.
- **Suggested spec text:** §8, replace the YAML example with:
  ```yaml
  - term: "Terst"; original: "Trieste"; type: city; note: "use Slovak exonym in captions"
  - term: "Rím"; original: "Roma"; type: city
  - term: "Zoncolan"; type: climb; say_sk: "dzon-ko-LAN"; stress: 3; source: "DiPI / RAI DOP"; checked_by: null
  - term: "Aprica"; type: town; say_sk: "A-pri-ka"; stress: 1; source: "DiPI / RAI DOP"; checked_by: null
  - term: "Lipica"; original_it: "Lipizza"; type: place; country: SI; say_sk: "LI-pi-ca"; source: "Fran.si"; checked_by: null
  ```
  and add a bullet:
  > - **Pronunciation sources:** Italian: DiPI online or RAI DOP; Slovene: Fran.si; Slovak exonyms and declension: ÚGKK SR exonym list and JÚĽŠ SAV. Forvo is a lead only. An entry with `checked_by: null` shows in the reel prompt as "pronunciation unchecked".
- **Why:** Italian stress isn't predictable from spelling (Àprica, Sàcile, Gàvia), and Katarina says these names on camera, where they can't be fixed with a caption. The stage list has about 40 such names.
- **Priority:** before phase 3

#### P8. Stage table: climbs and places with country
- **Type:** addition
- **Section:** §7.2 (Stage reference data), §10 (`stage_route`)
- **Proposal:** the stage table should hold the facts the map generator needs: climbs (name, km from start, summit altitude, length, average gradient, category) and places passed (name, km, **country**). That lets `stage_route` show the border crossing and keeps map labels tied to fact IDs.
- **Suggested spec text:** §7.2, replace the "Stage reference data" bullet with:
  > - **Stage reference data:** a versioned table per stage (date, start, finish, km, type, elevation gain, rest days) plus:
  >   ```yaml
  >   climbs: [{ name: "Cattinara–Sella di Longera", km: 158.7, summit_m: 283, length_km: null, avg_pct: null, category: null, fact: fact_… }]
  >   places: [{ name: "Lipica", km: 94.2, country: SI, fact: fact_… }]
  >   ```
  >   Each row points to a fact; `stage_route` (§10) only draws places and climbs whose fact is `verified` or `attributed`, and draws a border tick where `country` changes.
- **Why:** R47 requires maps rebuilt from facts instead of organizer maps. The most interesting Stage 1 visual (two countries in one day) needs per-place country data, which isn't in the current model.
- **Priority:** before phase 7

**Sign-off:** approve with changes (P1 and P5 before build; P2–P4, P7 before phase 3; P6 before phase 9; P8 before phase 7)
