# Session prompt 02: continue with the build plan

You are the developer agent for **Reels Hub** in `/Users/S38RA/Personal/repos/reels-hub`.

1. Read `AGENTS.md`, then `docs/BUILD_PLAN.md`. Check `git status` and `gh pr list` for unfinished work from an earlier session and finish that first.
2. Take the first unchecked item of the current phase and work through the items **in order**, one branch and one PR each, following the work loop in `AGENTS.md` (tests, tick the item, CHANGELOG line, PR, then merge only with `gh pr checks --watch --fail-fast && gh pr merge --squash --delete-branch`).
3. Keep going until the phase's ⛔ STOP line. Then stop and give the end-of-phase report (template in `AGENTS.md`), including exact commands for any "done when" check the owner must run on the run machine.
4. Stop earlier, and ask, whenever `AGENTS.md` → "When to stop and ask the owner" applies. Don't answer `Q#` items from the build plan yourself.

Owner notes for this session (optional; e.g. go-ahead for the next phase, answers to questions, inputs supplied):
-
