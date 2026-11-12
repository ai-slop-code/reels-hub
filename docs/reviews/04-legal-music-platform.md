# Review packet 04: legal (music, platform and API terms)

**Priority:** must review before implementation
**Time needed:** ~2 h
**Decisions already made:** D4 consent from Katarina and Ľuboš, local processing; D5 comments imported as available; D8 commercial music via Edits, no yt-dlp (see [README](README.md#decisions-already-made-please-dont-reopen)). Personal-data handling for the two hosts and comments is settled; this review focuses on **music and third-party terms**.

## Why you
The channel will publish daily with commercial music, automated analytics and third-party APIs. A wrong assumption here can get Reels muted, removed or the account restricted.

## Read
- [§15 Music](../spec/REELS_HUB_SPEC.md#15-module-k-music): especially 15.1, 15.2 and 15.6
- [§12.1 Analytics data sources](../spec/REELS_HUB_SPEC.md#12-module-h-performance-analytics)
- [§10.1 Motion graphics renderer](../spec/REELS_HUB_SPEC.md#10-module-f-graphics-generator) (HyperFrames, Apache 2.0)
- [§7 Facts and sources](../spec/REELS_HUB_SPEC.md#7-module-c-facts-and-sources)

## Questions
1. **Licensed music in Reels:** what exactly does the Edits / Instagram music license cover for this account? Creator vs. Business account, sponsored or branded Reels, collabs, regional restrictions.
2. **Signature track:** can we use the same commercial track ("Dolce Vita", Italian Atmosphere) across a 24-reel series and future seasons?
3. **Preview APIs:** do the Apple iTunes Search API and Deezer API terms allow downloading 30 s previews **for internal analysis** (tempo, vocals, loudness)? Any storage or caching limits?
4. **Premium catalogs:** what to check in Artlist, Musicbed or Epidemic Sound licenses (platforms, client vs. own channel, perpetual use of published reels, stems)?
5. **Cross-posting:** if a reel goes to YouTube Shorts or TikTok, what has to change (music, Natural Earth maps, fonts)?
6. **Meta developer app and Instagram Graph API:** any terms on how we store and analyze insights and comments in a local tool (D5 stands; just flag hard requirements)?
7. **Fonts and graphics:** Monstera-Black and IG fonts come from Edits. Can they be used in graphics rendered outside Edits (HyperFrames)? If not, which fonts should we license?
8. **Facts and quotes:** any limits on quoting the organizer's (RCS / Giro) pages, logos or official stage maps in reels?

## Expected output
A short list of **hard requirements** to build into the Hub (e.g. license fields, warnings, blocked actions) and things to check per reel.

## Your input

> Reviewer: AI acting as legal reviewer (music, platform and API terms). Reviewed 2026-11-12. Terms below were checked online on that date unless marked **unverified**. This is a design review for the build, not formal legal advice. For Season 2 or any paid deal, get a short written opinion from a Slovak or EU media lawyer.

### Summary
Overall the music policy is sound: Edits' licensed library first, no ripping, and license records per track. Three assumptions in the spec are wrong and would push agents to build features that break third-party terms.
1. **Preview analysis (§15.2 step 3, `analyze_preview`) is not allowed** by either named API. Apple's iTunes previews must be "streamed only, and not downloaded, saved, cached", and only used to promote the store item. Deezer forbids local or offline storage of audio and allows only non-commercial use.
2. **The channel needs a per-reel "commercial context" check.** Paid partnerships, gifted products, boosts and brand collabs take a reel outside Meta's personal-use music license.
3. **Graphics rendered outside Edits can't reuse Edits' fonts (Monstera) or macOS fonts (Avenir Next) in the Linux container.** They need separately licensed or OFL fonts.

The Hub needs a **license gate** next to the approval gate: a reel can't be approved for export, boosting or cross-posting unless the music, font and map records allow that destination. I also recommend producing a **clean master with no licensed music** for every reel, and dropping the rule that tells editors to trace the organizer's stage maps.

### Answers

#### Q1. What the Edits / Instagram music license covers
- **Basis.** The tracks in the Edits / Instagram audio library are licensed by Meta for use **only inside Meta products**, and for **personal, non-commercial use**. Meta's Music Guidelines say use "for commercial or non-personal purposes" is prohibited unless you hold the licenses yourself. That page wouldn't load from my tool on 2026-11-12. The wording is quoted consistently by [Soundstripe](https://www.soundstripe.com/blogs/royalty-free-music-for-instagram-ads) and [Third Chair](https://usethirdchair.com/blog/instagram-sound-library-rules-for-creators-and-brands), so I count it as verified second-hand. No license or file is passed to you. The music is added to the post through Meta's own deals. The Edits help page ["What audio can you use"](https://help.instagram.com/1718255785758961) says licensed audio "must be attributed or linked to the artist".
- **Creator vs. Business account.** Creator accounts get the broad library. Business accounts are restricted to the **Meta Sound Collection** (~14,000 royalty-free tracks) or a small commercial library ([Instagram Help: access to the licensed music library](https://help.instagram.com/402084904469945/)). **Keep the account as Creator.** Both Creator and Business are Professional accounts, so the Instagram API insights work for either.
- **Sponsored, branded and gifted reels.** Treat a reel as commercial when **any** of these is true: the paid partnership label is used, the brand paid, the brand gave free products or travel (Meta's branded-content policy counts any "exchange of value"), an affiliate link is in the caption, or the reel is made for a sponsor. For these reels, Instagram library music is not cleared. Use the Meta Sound Collection (its [terms](https://www.facebook.com/sound/collection/terms) allow "commercial or non-commercial purposes" on Meta products only) or a tier-2 track whose license covers branded or commercial use.
- **Boosting and ads.** Reels with licensed music **can't be boosted**. Instagram blocks it ("Reels that use copyrighted music can't be boosted as ads"; [Hootsuite](https://blog.hootsuite.com/why-cant-i-boost-my-reels/), referencing [Instagram Help 570215404599013](https://help.instagram.com/570215404599013)). If a reel might be boosted later, decide the music before posting, because you can't swap it afterwards.
- **Collabs.** A collab post shows on both accounts. If the co-author is a brand or Business account, or the collab is paid, treat the reel as branded (see above). Collabs with other creators that involve no exchange of value are fine with library music. **Unverified:** whether Instagram mutes library audio for the co-author when the co-author has a Business account. Test this before the first collab.
- **Regions.** Licenses are territorial. A track can be unavailable or muted for viewers in some countries, and Instagram shows a notice on the post. A track can also leave the library later, which mutes older reels retroactively. The Hub can't know this in advance. Record it after posting (the spec already does), and recheck at 24 h and 7 d.
- **Length limits (unverified, second-hand via [Thematic](https://hellothematic.com/music-rules-tiktok-instagram-youtube/)).** Edits drops licensed music from camera-roll exports with more than **60 s** of licensed audio, and from Instagram shares with more than **90 s** of the same song. Our reels are about 50 s, so this is fine. Put it in the playbook.

#### Q2. One signature track ("Dolce Vita") across 24 reels and future seasons
- **24 reels this season: yes, low risk.** Each post is covered separately by Meta's license, and I found no per-track usage cap. Same Creator account, organic posts and no sponsorship are the conditions.
- **Risks that grow over time:**
  1. Meta can remove the track from the library, and old reels then lose audio.
  2. The license is personal and non-commercial, so a sponsored episode can't use the signature, and you lose the "same sound every day" effect exactly when money arrives.
  3. The track can't follow the series to YouTube or TikTok.
  4. A track can't become the series' sound identity (a jingle or sound logo) on a license you don't hold. That's fine for recognition inside Instagram, but don't use it in trailers, ads or other platforms.
- **Recommendation:** use "Dolce Vita" for the December project. Before **Season 2**, or before the first sponsored episode, secure a **portable signature track**: tier 2 with stems, or tier 3 directly licensed for "all social platforms, organic + paid, worldwide, perpetual for content published during the term". "Italian Atmosphere" looks like a production-music or distributor artist. Check whether the same recording is sold through a production library (that's often cheap to license directly). **Unverified:** I didn't find who controls its rights.

#### Q3. Apple iTunes Search API and Deezer previews for internal analysis
**No, not as specified.** Checked 2026-11-12:
- **Apple** ([iTunes Search API, Legal](https://performance-partners.apple.com/search-api)): previews are "Promo Content" that may be used only "for the purposes of promoting the subject". They must sit next to a "Download on iTunes" badge, carry the attribution "provided courtesy of iTunes", be "**streamed only, and not downloaded, saved, cached, or synchronized with video**", and are "not used for independent entertainment value". Tempo, vocal and LUFS analysis is outside that purpose, and so is any storage. Rate limit is ~20 calls/min.
- **Deezer** ([developer guidelines](https://developers.deezer.com/guidelines), [terms of use](https://developers.deezer.com/termsofuse)): "Local Storage/Offline Storage of audio data is **strictly forbidden**". Use is "strictly limited for a non-commercial purpose", and content "shall not be associated, directly or indirectly with any trademark, brand name, or logo". Deezer also doesn't allow images to be cached ([FAQ](https://support.deezer.com/hc/en-gb/articles/360011538897-Deezer-FAQs-For-Developers)). Preview URLs are signed and expire after about 15 min ([cors.dev, observed](https://cors.dev/guides/deezer-api-cors)). Metadata (artist and track names) may be stored.
- **In-memory analysis without saving the file** still fails Apple's purpose test. For Deezer it's a grey area, and the channel's semi-commercial nature fails the non-commercial clause anyway. Don't build it.
- **What is allowed:**
  - **Metadata only** for tier-1 tracks: ISRC, duration and explicit flag from the iTunes or Deezer search JSON; BPM and key from GetSongBPM (its free API requires a visible backlink to getsongbpm.com, **unverified**, so check its current terms); MusicBrainz (core data CC0; tags and genres are in the supplementary CC BY-NC-SA set).
  - **Full audio analysis only on files we're licensed to download:** tier-2 downloads (Epidemic, Artlist, Musicbed), where downloading for editing is the licensed use and analysis is incidental to editing, and tier-3 masters.
  - **Producer's ears** for Edits tracks, which the spec already allows.
- **Also:** `check_mix` must not record or save Edits' licensed audio. Meter in memory, or use Edits' own metering, and store only numbers. Saving a copy of obfuscated audio, or working around the obfuscation, can count as circumventing a technical protection measure (EU InfoSoc Directive Art. 6, implemented in the Slovak Copyright Act 185/2015, §60).

#### Q4. What to check in premium catalog licenses (Artlist, Musicbed, Epidemic Sound)
Store these as fields per catalog and per track, not as free text:

| Check | Why it matters | What I found (2026-11-12) |
|---|---|---|
| **Plan tier: personal/creator vs. business/pro** | Creator plans usually exclude ads, paid partnerships and client work | Check on every plan change |
| **Licensee = channel owner** | If Ľuboš subscribes but posts to Katarina's account, it may count as "client" use | Licensee name and connected channels must include Katarina's IG (and later YT/TikTok) |
| **Channel safelisting** | Without it you get Content ID or Rights Manager claims | Epidemic: connect channels; "content published during an active subscription will stay cleared forever" ([Epidemic](https://www.epidemicsound.com/how-it-works/music-licensing/what-is-safelisting/)) |
| **Published vs. created during the term** | Epidemic ties coverage to the **publish** date, not the download date. A reel scheduled after cancellation isn't covered | Store `published_at` against `subscription_active_until` |
| **Perpetuity of published content** | Do old reels stay cleared after you cancel? | Epidemic: yes, for content published during the term. Artlist: advertises "lifetime coverage for downloaded tracks", but users report changed terms ([thread](https://www.reddit.com/r/VideoEditing/comments/1ok8emm/artlistio_scammed_us_with_their_forever_license/)), so **save the license PDF at download time**. Musicbed: **unverified** |
| **Platforms and paid use** | Organic only, or boosted/ads too? | Per plan |
| **Instagram "original audio"** | An uploaded tier-2 track shows as your "original audio" and others can reuse it. Some licenses forbid making the track available on its own | Rename the audio, check the catalog's guidance, and turn off audio reuse where Instagram allows it (**unverified** whether the setting exists for Reels in SK) |
| **Stems and edits** | Cutting under speech; some licenses forbid remixing or stand-alone loops | Stems: Epidemic has them for most tracks; Artlist and Musicbed for some |
| **Exclusivity and Content ID** | The same track may sit in Instagram's library under a different rights holder | Check before choosing a signature |
| **Proof** | Disputes | Store the license certificate or PDF, order ID and the date the terms were captured |

#### Q5. Cross-posting to YouTube Shorts or TikTok
- **Music:** tier-1 (Meta) music **must not** travel, because the license covers Meta products only. Make a **clean master** for every reel: the same timeline with the licensed music lane muted, dialogue and our own SFX only. Then add music per platform:
  - **YouTube Shorts:** add a track from the Shorts audio library in the YouTube app, or use tier 2 with YouTube safelisted. A Meta-licensed track left in the upload will be matched by Content ID and claimed, blocked or muted.
  - **TikTok:** add music in the app (Creator accounts get the general library; Business accounts only the Commercial Music Library), or use tier 2.
- **Natural Earth maps:** public domain, so they're fine everywhere. If OSM data is used for routes, the ODbL credit "© OpenStreetMap contributors" goes in the description on every platform.
- **Fonts and graphics rendered in Edits** (captions, titles in Monstera): Edits' App Store listing says "Export your videos in 4K with no watermark and share to any platform", so exported pixels can be shared. **Unverified:** Edits' terms on fonts specifically. HyperFrames graphics use fonts we license ourselves (Q7), so they travel as far as the font license allows (OFL: everywhere).
- **Edits' own assets** (stickers, effects, AI animation): treat them as Meta-only unless the terms say otherwise (**unverified**).
- **Platform text:** captions, hashtags and the `@`-tags differ per platform. The Hub should store a caption per platform.

#### Q6. Meta developer app and Instagram API: hard requirements
D5 stands. These come from the [Meta Platform Terms](https://developers.facebook.com/terms/dfc_platform_terms/) and the [Instagram Platform docs](https://developers.facebook.com/documentation/instagram-platform/overview), checked 2026-11-12:
1. **Official API only.** No scraping of instagram.com, the Instagram app's private API or the Edits insights dashboard. Meta's Terms of Use forbid automated collection without permission. Manual CSV or screenshot import of your own insights is fine.
2. **Access level.** Use the Instagram API with Instagram Login (`instagram_business_basic`, `instagram_business_manage_insights`, `instagram_business_manage_comments`). Keep the app in **Development mode / Standard Access**, with Katarina's account given an app role (tester or admin). Then no App Review is needed. You still accept the Platform Terms, and Meta can require an annual **Data Use Checkup**. Record who owns the developer account.
3. **Deletion (Platform Terms §3.d).** Delete Platform Data when it's no longer needed for a legitimate purpose, when Meta asks, when the user asks, or when you stop using the app. In practice: on each comment pull, **delete local copies of comments that were deleted or hidden on Instagram**, and provide a "purge all Instagram data" command. See P8 for the tension with D5.
4. **Service providers.** Comment text sent to Claude counts as sharing with a service provider. Use the Anthropic API under commercial terms (no training on inputs), not a consumer chat app. Never send comments to other services.
5. **No profiling of individuals.** Use comments for aggregate topics, questions and sentiment. Don't build per-commenter profiles or join commenters with outside data.
6. **Tokens.** Long-lived tokens last about 60 days. Refresh them automatically, keep them in Podman secrets (§22 already does), and alert 7 days before expiry.
7. **Store the API version with each number** (the spec already does), and respect rate limits (back off on HTTP 4/17/32/613).

#### Q7. Monstera-Black, Edits fonts and HyperFrames
- **No.** Fonts inside Edits are licensed to Meta for rendering inside the app. Pulling the font files out of the Edits app bundle (or a cache) to install them in HyperFrames or the container is unlicensed copying. The same applies to **Avenir Next** (DESIGN_LANGUAGE §3, map labels). It's an Apple system font licensed under the macOS license for use on the Mac. Copying it into the **Linux container** (§21 renders with resvg in the container) isn't covered. Rendering on the Mac with `qlmanage` as today is arguably fine (**unverified**).
- **What to use:**
  - **SIL OFL fonts.** They allow commercial use, embedding, rendering on a server or in a container, and every platform. Candidates close to Monstera-Black's heavy rounded-grotesk look, all with full Slovak (Ľ ľ Ĺ ĺ Ŕ ŕ ť ď ô ä) **and an en dash**: **Montserrat Black/ExtraBold**, **Rubik Black**, **Archivo Black**, **Inter Black**. For map labels in place of Avenir Next: **Figtree**, **Nunito Sans** or **Inter**.
  - **A commercial font with a desktop + server/app license**, if the brand needs a specific face. The EULA must explicitly allow use in video for social media and installation on a render server or container.
- **Consequence for design:** titles made in HyperFrames won't be Monstera. Either keep **all text in Edits** (the spec's current rule "text stays out of the PNG") and render only text-free motion, or switch titles to the OFL face. That decision belongs to the motion designer and host; the legal constraint is that the Hub records a font license per asset.

#### Q8. Quoting organizer (RCS / Giro) pages, logos and stage maps
- **Facts** (dates, km, start and finish towns, climbs) aren't protected by copyright. Say them freely and cite the source in the Hub.
- **Short text quotes** are fine as quotation for discussion (Slovak Copyright Act 185/2015 §37; Italian LdA art. 70). Keep them short, attributed and in service of our commentary. Don't reproduce the organizer's descriptions in full.
- **Stage maps, altimetry profiles, photos and videos** from giroditalia.it are copyrighted works. **Don't** show them in reels, screen-record the site, or "trace the official stage map" pixel by pixel (DESIGN_LANGUAGE §7 says to do this). Tracing copies the map's expression. **Instead:** rebuild the route from the facts (list of towns and climbs, km), drawn on Natural Earth and, for road-level detail, **OpenStreetMap** data (ODbL, credit required). If RCS publishes a GPX or KML, use it only if its terms allow reuse (**unverified**; I didn't find published terms). **Do** draw our own elevation profile from DEM data (e.g. Copernicus DEM, free with attribution), not from their profile image.
- **Trademarks and logos:** "Giro d'Italia", the logo, the Trofeo Senza Fine, the maglia rosa artwork and sponsor logos belong to RCS or partners. Using the **name** to describe the race is nominative use and fine. **Don't** use logos or official artwork. **Don't** call anything "official". Add "neoficiálny fanúšikovský projekt" (unofficial fan project) to the bio or caption once. This matters more because the account will show brands (the Chupa Chups lollipop is in the hook). Incidental product props are fine. Never imply sponsorship.
- **Broadcast footage:** race footage belongs to RCS and the broadcaster (Warner Bros. Discovery and others). Never use clips, even short ones, without a license. Block it in ingest (P7).
- **Automated re-checks of giroditalia.it** (§7.2 diff checks): fine at low frequency (≤ 1 request per page per day), honoring robots.txt. Store the extracted text and a hash, not full page copies or images.

### Proposals

#### P1. Remove preview downloads and analysis from iTunes and Deezer
- **Type:** change
- **Section:** §15.2 (step 3), §17.2 (`analyze_preview`), §21 (Music analysis, Music metadata), §27
- **Proposal:** Audio analysis runs only on audio the Hub is licensed to hold (tier-2 downloads, tier-3 masters, our own recordings). For tier-1 Edits tracks, use metadata APIs and the producer's ears only. iTunes and Deezer are used for metadata only; their preview URLs may be streamed to the producer in the UI, with attribution and a store link, but never downloaded, cached or analyzed.
- **Suggested spec text:** In §15.2 replace step 3 with:
  > 3. **Analysis (licensed audio only):** audio features (tempo, beat strength, LUFS, vocal presence via Demucs, speech-clash score, energy curve) are computed **only** from audio the Hub is licensed to hold: tier-2 catalog downloads, tier-3 masters, or our own recordings. For tier-1 (Edits) tracks the Hub uses **metadata only**: ISRC, duration and explicit flag (iTunes Search / Deezer JSON), BPM and key (GetSongBPM, with its required backlink in the UI), and genre and instrumental tags (MusicBrainz). iTunes and Deezer preview audio is **never downloaded, cached, stored or analyzed**. iTunes requires previews to be "streamed only, and not downloaded, saved, cached" and used only to promote the store item; Deezer forbids local storage of audio and commercial use. The UI may stream an iTunes preview to the producer only next to a store link with "Provided courtesy of iTunes".

  In §17.2 replace the `analyze_preview` line with:
  > - `analyze_track(track)` → bpm, vocals, loudness, speech-clash score, energy curve. **Refuses** unless `music_license.audio_analysis_allowed: true` (tier 2/3 or own audio); for tier 1 returns metadata only.

  In §21, Music metadata row: `Edits catalog, MusicBrainz, GetSongBPM, iTunes Search / Deezer previews` → `Edits catalog, MusicBrainz, GetSongBPM, iTunes Search / Deezer (metadata only; previews never stored or analyzed)`.
- **Why:** [Apple iTunes Search API, Legal](https://performance-partners.apple.com/search-api) and [Deezer guidelines](https://developers.deezer.com/guidelines) / [terms](https://developers.deezer.com/termsofuse), checked 2026-11-12. As written, the spec builds a terms violation into the core music pipeline.
- **Priority:** must-have before build (it changes tools and schema; phase 8 "can start early")

#### P2. License gate per destination, with a fuller license record
- **Type:** change
- **Section:** §15.6, §11.3, §17.2 (`export_allowed`), §18
- **Proposal:** Replace the `music_license` block with a richer record and add a **license gate**. `export_allowed`, and a new `destination_allowed`, check every music, font and map asset on the version against the destination (`instagram`, `instagram_boost`, `youtube`, `tiktok`) and the reel's commercial context (P3).
- **Suggested spec text:** Replace the YAML in §15.6 with:
  ```yaml
  music_license:
    track_id: music-dolce-vita
    tier: 1                                # 1 edits-licensed | 1b meta-sound-collection | 2 premium | 3 direct | 4 stock
    source: edits-licensed
    licensor: Meta (platform license)      # or catalog / label / publisher
    licensee: null                         # tier 2/3: legal name on the license; must own or have connected the posting account
    accounts_covered: ["@katarina"]        # channels safelisted / named in the license
    platforms_allowed: [instagram, facebook]
    paid_use_allowed: false                # boosts, ads
    branded_use_allowed: false             # paid partnership, gifted, affiliate
    regions_restricted: unknown            # filled from post notices at 24 h / 7 d
    audio_analysis_allowed: false          # true only for files we're licensed to hold (tier 2/3, own)
    stems_available: false
    term: platform                         # platform | subscription | perpetual | until:<date>
    covered_if_published_by: null          # subscription licenses: last day of the active term
    perpetual_for_published: null          # tier 2: published content stays cleared after the term
    evidence: []                           # license PDF/certificate path, order ID, terms URL + date captured
    checked_at: 2026-11-12
  ```
  Add to §11.3:
  > - **License gate:** approval for a destination (`instagram`, `instagram_boost`, `youtube`, `tiktok`) requires every music, font and map asset on the version to allow that destination and the reel's commercial context (§15.6). `export_allowed(version, destination)` returns the blocking asset and the reason. Tier-2 licenses also require `published_at ≤ covered_if_published_by`.
- **Why:** The current record can't express licensee, paid or branded use, publish-date coverage or evidence. Those are the fields that decide whether a post gets muted or claimed.
- **Priority:** must-have before build (schema)

#### P3. Commercial-context flags per reel that block Instagram library music
- **Type:** addition
- **Section:** §6.2 / §18 (`reel`), §15.6, §16.2 (Platform)
- **Proposal:** Every reel has a `commercial` block that the producer fills in at planning. Any `true` value blocks tier-1 licensed music and points the agent to tier 1b (Meta Sound Collection) or a tier-2 track with `branded_use_allowed`.
- **Suggested spec text:** Add to §15.6:
  ```yaml
  reel_commercial:
    paid_partnership: false      # brand paid, or paid partnership label used
    gifted_or_hosted: false      # free product, travel, tickets, accommodation (Meta treats as exchange of value)
    affiliate_links: false
    boost_planned: false         # licensed-music reels can't be boosted
    collab_with: []              # handles; brand or Business accounts count as branded
  ```
  > - If any field is true (or `collab_with` includes a brand), tier-1 Edits library music is **blocked**; use Meta Sound Collection (Meta-only, commercial OK) or tier 2 with `branded_use_allowed: true`. Decide before the edit: the music can't be swapped after posting in order to boost.
  > - The AI critique's Platform check confirms the flags were filled in and the paid partnership label is planned when required.
- **Why:** Meta's licensed library is personal and non-commercial, and boosting reels with licensed music is blocked ([Hootsuite](https://blog.hootsuite.com/why-cant-i-boost-my-reels/), [Instagram Help](https://help.instagram.com/570215404599013)). Gifted travel to the Giro is a realistic next step for this channel.
- **Priority:** must-have before build

#### P4. Clean master and per-platform deliverables
- **Type:** change
- **Section:** §15.6 (Cross-posting), §6.4 (Deliverables), §11.1
- **Proposal:** Every approved version produces an `ig_master` (with Edits music, posted from Edits or Instagram) and a `clean_master` (licensed-music lane muted). Cross-posting uses only the clean master plus a destination-specific track.
- **Suggested spec text:** Replace the §15.6 bullet "**Cross-posting** (YouTube Shorts, TikTok) needs tier 2 or 3 music, or a different track per platform." with:
  > - **Cross-posting:** every approved version has two renders: `ig_master` (with tier-1 music, for Instagram only) and `clean_master` (dialogue + own SFX, no tier-1 music). Other platforms get the `clean_master` with either tier-2/3 music whose license lists that platform, or music added inside that platform's app (YouTube Shorts audio library, TikTok library; TikTok Business accounts: Commercial Music Library only). A file containing tier-1 music is never uploaded outside Meta; the Hub blocks it via `export_allowed(version, destination)`.

  In §6.4 Deliverables add: `clean_master path; music per destination`.
- **Why:** Meta's license covers Meta products only ([Sound Collection terms](https://www.facebook.com/sound/collection/terms); same scope for the licensed library). Content ID will claim uploads elsewhere.
- **Priority:** before phase 4 (reviews and exports)

#### P5. Font licensing for graphics made outside Edits
- **Type:** change
- **Section:** §10.1, §9, §18 (`asset` type font), DESIGN_LANGUAGE §3
- **Proposal:** HyperFrames and container-rendered maps use only fonts the Hub holds a license for (preferably SIL OFL), recorded as assets. Edits fonts (Monstera) and macOS system fonts (Avenir Next) are never copied out of their apps or into the container.
- **Suggested spec text:** Add to §10.1 after "Engine":
  > - **Fonts:** compositions use only fonts registered as `font` assets with a license allowing video output, social platforms and installation in the container (default: SIL OFL, e.g. Montserrat, Rubik, Archivo Black, Inter, Figtree; must cover Slovak diacritics and the en dash). Fonts from Edits (Monstera) and macOS system fonts (Avenir Next) are **never** extracted, copied into the image or loaded by HyperFrames or resvg. Text set in Monstera stays in Edits.

  Add the asset fields: `font: { family, file_hash, license: OFL-1.1 | commercial, eula_ref, allows: [video, server, social] }`.
- **Why:** Fonts in an app are licensed for that app, and the macOS license covers Apple systems only. OFL removes the question entirely.
- **Priority:** before phase 7 (and before the container map renderer in phase 0 if it renders labels)

#### P6. No tracing of organizer maps; rebuild routes from open data
- **Type:** change
- **Section:** §10 (Guardrail), §10.1 (`stage_route`, `climb_profile`), DESIGN_LANGUAGE §7 (Rules)
- **Proposal:** Replace "trace the official stage map" with routes built from facts plus open data, and record the attribution.
- **Suggested spec text:** §10, replace "**Guardrail:** no precise route traces from non-official data." with:
  > - **Guardrail:** routes are drawn from the fact store (towns, climbs, km from primary sources) on open data: Natural Earth (public domain) and, for road-level detail, OpenStreetMap (ODbL; credit "© OpenStreetMap contributors" in the caption). Elevation profiles are computed from an open DEM (e.g. Copernicus DEM, with attribution). Organizer maps, profile images, photos, logos and race footage are **never** shown, traced or screen-recorded. An organizer GPX/KML is used only if its terms allow reuse (recorded in the asset's license). Precision claims ("exact route") are allowed only when the geometry comes from such a licensed official trace.

  DESIGN_LANGUAGE §7, Rules: "For a stage route, trace the official stage map from giroditalia.it." → "For a stage route, rebuild it from the official list of towns and climbs on OSM data (credit required). Never trace or show the organizer's map."
- **Why:** The maps and profiles are copyrighted works, and tracing them copies their expression. Facts and open data carry no such risk.
- **Priority:** before phase 7 (and before the first stage reel that needs a route)

#### P7. Blocked content types at ingest: broadcast footage and third-party media
- **Type:** addition
- **Section:** §5.1, §10, §22
- **Proposal:** Assets get `origin: own | licensed | open_data | third_party_unlicensed`. `third_party_unlicensed` (screen recordings of broadcasts, organizer images, downloaded social clips) can be stored for reference but is excluded from `search_moments` and refused by `export_allowed`.
- **Suggested spec text:** Add to §22:
  > - **Third-party media:** every clip and asset has `origin` (`own | licensed | open_data | third_party_unlicensed`). `third_party_unlicensed` items (race broadcast, organizer photos, maps, other creators' reels) are reference-only: hidden from agent search and moment suggestions, and any version containing them fails `export_allowed`.
- **Why:** The fastest way to get an account restricted is broadcast footage (RCS and broadcasters actively enforce). Agents searching "Zoncolan" will happily surface a screen recording if one is in the library.
- **Priority:** before phase 1

#### P8. Meta Platform Terms requirements for the importer (with a risk note on D5)
- **Type:** addition + risk
- **Section:** §12.1, §22, §27
- **Proposal:** Encode the hard requirements from Q6.
- **Suggested spec text:** Add to §12.1 after the API note:
  > **Platform terms (hard requirements):** official Instagram API with Instagram Login only; no scraping of instagram.com, the app's private API or the Edits insights dashboard. App stays in Development mode with Standard Access, with Katarina's account given an app role. On each comment pull, comments that were deleted or hidden on Instagram are deleted locally. `purge_instagram_data()` removes all Platform Data on request from Meta or the account owner, or when the app is retired. Comment text is sent only to the Claude API (commercial terms); no per-commenter profiles. Long-lived tokens are refreshed automatically, with an alert 7 days before expiry.
- **Risk (D5):** D5 ("no extra retention rules") stands. But the Meta Platform Terms §3.d deletion duties apply regardless: delete when no longer needed, on Meta's or the user's request, and when you stop operating. **Consequence if ignored:** Meta can restrict or revoke the developer app, which stops the analytics pull. That's a terms issue, not a privacy policy issue, so the deletion sync above is the minimum.
- **Why:** [Meta Platform Terms](https://developers.facebook.com/terms/dfc_platform_terms/) §3.d, checked 2026-11-12.
- **Priority:** before phase 5

#### P9. Never capture or persist Edits licensed audio
- **Type:** addition
- **Section:** §15.2 (step 7 mix check), §16.1, §22
- **Proposal:** `check_mix` and the critic's sound pass must work from metering numbers, not recorded licensed audio. A preview render that contains tier-1 music is used only for review on the Mac and is never uploaded to external AI services.
- **Suggested spec text:** Add to §22:
  > - **Licensed audio:** the Hub never records, decodes or stores tier-1 (Edits) music, and never attempts to bypass Edits' audio obfuscation. `check_mix` stores levels only (dB per section). Renders containing tier-1 music stay local; the AI critic receives transcripts and loudness curves, never the audio file.
- **Why:** This avoids TPM-circumvention exposure (EU InfoSoc Directive Art. 6; Slovak Copyright Act §60) and breach of Meta's terms. It also keeps the critic's existing design (§16.1 already sends transcript and loudness, not audio).
- **Priority:** before phase 8

#### P10. A durable signature track before Season 2
- **Type:** risk
- **Section:** §15.4 (Signature tracks), DESIGN_LANGUAGE §9
- **Proposal:** Keep "Dolce Vita" for December. Add a signature-track rule: a signature for more than one project must be tier 2 or 3, with `platforms_allowed` covering all planned platforms and `branded_use_allowed: true`. Monitor the tier-1 signature for library removal.
- **Suggested spec text:** Add to §15.4:
  > - A signature used across **more than one project or season** must be tier 2 or 3 with all planned platforms and branded use covered. Tier-1 signatures are allowed for a single project; the Hub re-checks availability weekly (`listMusicTracks` by asset ID) and flags removal, since removed tracks can mute already-posted reels.
- **Why:** The Meta license can't be extended, ported or used for sponsored episodes, and library deals change.
- **Priority:** before phase 8 (decision needed before Season 2)

#### P11. Disclosure flags: unofficial fan project, branded content, AI-generated media
- **Type:** addition
- **Section:** §16.2 (Platform), §6.4 (Rules), §22
- **Proposal:** Add a disclosure check to the critique and prompt rules:
  - (a) never use the words "oficiálny" / "official" or organizer logos;
  - (b) the paid partnership label when P3 flags are set;
  - (c) `ai_generated: true` on any asset made with generative AI (e.g. Edits' "AI animation", synthetic voice), which requires Meta's "AI info" label. This is also relevant under the EU AI Act Art. 50 transparency duties for deepfakes, in force from 2 Aug 2026 (**verify scope** for this use).
- **Suggested spec text:** §16.2 Platform row: "Runtime, Reels UI overlap, licensed-music restrictions, cover frame" → "Runtime, Reels UI overlap, licensed-music restrictions vs. destination and commercial flags, cover frame, disclosures (paid partnership label, AI label for generative assets, no 'official' or organizer logos)". Add to §6.4 Rules: "- Never synthesize Katarina's or Ľuboš's voice or face; pickups are recorded, not generated."
- **Why:** Meta's branded-content and AI-labelling policies, and RCS trademark rights. Cheap to check automatically and expensive to fix after posting.
- **Priority:** before phase 10 (the rules line in §6.4 before phase 9)

#### P12. Per-reel legal checklist (what the producer confirms before approval)
- **Type:** addition
- **Section:** §11.3
- **Proposal:** Add a short machine-checked checklist to the approval screen. Most items are filled from P2–P11. The producer confirms the rest.
- **Suggested spec text:** Add to §11.3:
  ```yaml
  legal_check:                      # shown on approval; blocking items auto-checked
    music_allowed_for_destination: auto   # P2 license gate
    commercial_flags_set: producer        # P3
    clean_master_rendered: auto           # P4, if cross-posting
    fonts_licensed: auto                  # P5
    no_organizer_media: auto              # P6/P7 origin check
    disclosures: producer                 # P11
    post_check_24h: auto                  # muted / region notice recorded on the reel
  ```
- **Why:** This turns the "Expected output" of this packet into one gate the Hub enforces.
- **Priority:** before phase 4

**Sign-off:** approve with changes (P1–P4 before build; the rest before their phases)
