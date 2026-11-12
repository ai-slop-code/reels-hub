---
name: reels-hub-branch-workflow
description: "Reels Hub development rule — every change on its own branch, merge to main only when finished and all tests pass"
metadata:
  node_type: memory
  type: feedback
  originSessionId: 31e669fe-99b9-4a02-8a11-54dd37c24ecb
  modified: 2026-11-12T08:08:57.911Z
---

When building the **Reels Hub** app (repo `reels-hub`), every change or feature must be built on its own branch (`feature/…`, `fix/…`, `chore/…`) from latest `main`. Merge back to `main` only when the feature is finished and the **full** test suite passes; rebase on main and re-run tests before merging; delete the branch after. Never commit directly to main.

**Why:** the user stated this as a standing instruction for the tool (2026-11-12); main must always stay releasable.

**How to apply:** at the start of any Reels Hub coding task, branch first; run the full suite before merging; put the same rule in the repo's CLAUDE.md. See [[reels-hub-project]].
