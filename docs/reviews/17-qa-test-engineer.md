# Review packet 17: QA / test engineer

**Priority:** good to have (before phase 0; the test setup gates every merge)
**Time needed:** ~1.5 h
**Decisions already made:** D10 every feature on its own branch, merged to `main` only when finished and the **full** suite passes; D2 AI builds the Hub (see [README](README.md#decisions-already-made-please-dont-reopen)).

## Why you
An AI agent will build every feature, and the test suite is the gate for every merge. The tests have to catch real regressions, including in AI-generated outputs that vary from run to run.

## Read
- [§24 Development workflow](../spec/REELS_HUB_SPEC.md#24-development-workflow): 24.2 tests, 24.3 definition of done
- [§23.6 Image, updates and backups](../spec/REELS_HUB_SPEC.md#23-deployment-podman) (container smoke test)
- [§6.4 Reel prompt](../spec/REELS_HUB_SPEC.md#6-module-b-projects-reels-and-the-reel-prompt) (golden tests), [§16 Critique](../spec/REELS_HUB_SPEC.md#16-module-l-ai-critique)

## Questions
1. **Test layers:** is the table in §24.2 complete? What's missing (e.g. performance, migration rollback, MCP backwards compatibility)?
2. **Fixtures:** small Sony + DJI clips with known transcript, sync offset and moments. How many, and how to keep them in the repo (Git LFS)?
3. **Variable outputs:** prompt generator and critique use models. How to test them (snapshots of inputs, rubric checks, tolerances, recorded responses)?
4. **External services:** mocking Instagram, Edits MCP, music previews, HyperFrames renders.
5. **Speed:** the full suite runs before every merge. Target duration, and what runs only in a slower nightly suite?
6. **Agent-built code:** extra checks to catch common AI coding mistakes (unused code, skipped tests, weakened assertions)?

## Your input
<!-- Use the response format from the README. -->

**Sign-off:**
