# Session prompt 03: review a finished phase (optional, owner-started)

You are reviewing phase **<n>** of **Reels Hub** in `/Users/S38RA/Personal/repos/reels-hub`. Don't build features in this session.

1. Read `AGENTS.md`, the phase section in `docs/BUILD_PLAN.md`, and the spec sections it cites (`docs/spec/REELS_HUB_SPEC.md`).
2. `git switch main && git pull --ff-only`, then run `make test` and `make test-container` (machine-safety rules in `AGENTS.md` apply).
3. Check the phase's **"done when"** line (spec §25) as far as the build machine allows, and each ticked item against its scope, spec refs and tests. List what you can't check here and the exact commands the owner should run on the run machine.
4. Check the product rules in `AGENTS.md` that touch this phase (approval, exclusions, captions, music, Instagram), and that `CHANGELOG.md` and the spec match what was built.
5. Report: what passes, gaps (each with spec ref and a suggested `fix/…` branch), spec ambiguities found, and a go / go-with-fixes / no-go recommendation for the next phase. If a fix is needed, add it as an unchecked item to `docs/BUILD_PLAN.md` on a `chore/phase-<n>-review` branch through a PR; don't fix code here.
