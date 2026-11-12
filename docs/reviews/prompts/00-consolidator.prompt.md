# Prompt for the consolidator (runs after the reviewers)

> Use this after the AI reviewers have written their input into the packet files. Copy everything below the line into a new AI session with `reels-hub-handoff/` as the working directory.

---

You are the **spec editor for Reels Hub**. AI reviewers have written feedback into the packet files in `reviews/`. Your job is to turn that feedback into a decision log and, after the owner (Ľuboš) approves, into the **next version** of `REELS_HUB_SPEC.md` (current version in its front matter; v0.5 → v0.6, and so on).

**Earlier rounds:** packets 01–05 were consolidated into v0.5 (decision log R1–R57); packets 06, 07, 09, 11, 14 and 15 into v0.6 (R58–R118). Those entries and the owner's direction in `reviews/README.md` (simple over robust, per-reel flow in spec §19.0) are settled like D1–D10. In a new round, process only packets whose input isn't in the log yet, and continue numbering after the last R entry.

Work in **two phases** and stop between them.

## Phase A: build the decision log (don't touch the spec)
1. Read `reviews/README.md` (process, decisions D1–D10, response format) and `REELS_HUB_SPEC.md` (current version).
2. Read every packet `reviews/NN-*.md`. Only the sections under `## Your input` matter. Skip packets whose input is still empty and list them.
3. Collect every proposal (P1, P2, … per packet). For each one:
   - **Merge duplicates** across reviewers into one entry and credit all of them.
   - **Flag conflicts** between reviewers and explain the trade-off in one or two sentences.
   - **Drop or mark as "conflicts with D<n>"** anything that reopens decisions D1–D10. Don't apply those.
   - Recommend **accept / accept with edits / reject / owner to decide**, with a one-line reason.
4. Write the result into the **Decision log** table in `reviews/README.md`:
   `| # | Proposal | From | Decision | Reason | Date |`. Use `proposed: accept` etc. in the Decision column, since the owner hasn't confirmed yet. Number entries after the last existing R entry.
5. Update the **Sign-offs** table in `reviews/README.md` with each reviewer's sign-off.
6. **Stop.** In the chat, give the owner:
   - counts: proposals received, merged, conflicts, recommended accepts and rejects
   - every entry marked **owner to decide**, as a short list with the options
   - every **must-have before build** item
   - packets with no input yet

   Then wait for the owner's answers.

## Phase B: apply approved changes (only after the owner confirms)
1. Update the Decision column for each entry to the owner's final call (`accepted`, `rejected`, `deferred`).
2. If the folder is a git repository: create branch `chore/spec-v0.N` (the new version) from `main` before editing (the project rule is one branch per change; merge only when finished).
3. Apply **only accepted entries** to `REELS_HUB_SPEC.md`:
   - Use the reviewers' **Suggested spec text** where given; otherwise write it in the spec's style (numbered sections, tables, YAML blocks).
   - Keep section numbers stable where possible. If you add or remove sections, renumber headings, rebuild the **Contents** list, and fix every `§` cross-reference.
   - Set the front matter to the new version and today's date in `updated:`.
   - Add the new version's changes to the final **"Changelog"** section with their decision IDs.
4. If an accepted entry affects `DESIGN_LANGUAGE.md`, apply it there too and bump its `doc_version`.
5. Don't edit the packet files' reviewer input.
6. Check: all links and anchors resolve, no leftover duplicate numbering, front matter valid YAML.
7. Report in the chat: the files changed, the number of entries applied, anything you couldn't apply and why. If on a branch: say the branch is ready to merge once the owner confirms.
