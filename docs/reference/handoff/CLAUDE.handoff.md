# Reels Hub: standing instructions

Read `HANDOFF.md` first for context, folder map and status.

## Git workflow (mandatory)
- Never commit directly to `main`.
- Every change or feature gets its own branch from the latest `main`: `feature/…`, `fix/…` or `chore/…`.
- Merge back to `main` only when the feature is finished **and the full test suite passes**. Rebase on `main` and re-run the tests before merging; delete the branch afterwards.

## Documents
- `REELS_HUB_SPEC.md` is the source of truth for what to build. Change it only through the review process in `reviews/README.md` or when the owner asks.
- Decisions D1–D10 and the owner's decisions R1–R123 in `reviews/README.md` are settled. Don't reopen them (`deferred` entries may come back when their phase starts).
- Reviewers write only into their own packet file in `reviews/`.
- Simple over robust: one user, one machine. Build the simplest thing that supports the per-reel flow (spec §19.0).

## Reels
- All speech is captioned in natural Slovak with correct diacritics. Use only words Katarina actually said, and never splice her words into sentences she didn't say. Proposed lines go under "Suggested pickups (not recorded)" in the reel's `editors_notes.md`, never into captions or on screen.
- Every reel gets an `editors_notes.md` (template: spec §11.4). Start it when the edit starts and complete it before asking for approval: footage, moments, captions, facts with sources, graphics, music and license, fonts, design-language practices and deviations, Edits quirks, legal checklist, open items.
- Follow `DESIGN_LANGUAGE.md` for colors, type, captions, layout, maps and sound.
- Music: commercial / artist-grade tracks through Edits' licensed library. Generic royalty-free stock only as a last resort. Never download songs from YouTube (no yt-dlp) and never download or analyze iTunes/Deezer previews. You can't listen to licensed tracks; shortlist up to 3 with metadata and let the owner choose.
- Check race facts against the organizer's current pages and record sources.
- Never render, export or publish a reel until the owner explicitly approves that exact version.
- AI critique runs only when the owner asks for it, after a video exists (spec §16.5).

## Edits app
- Its sandbox can't read `~/Personal`; media must be under `~/Movies` (Reels Hub: `~/Movies/ReelsHub`).
- Known API quirks: spec §14.
