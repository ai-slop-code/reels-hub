# Review packet 08: data analyst / statistician

**Priority:** before phases 5–6 (analytics, learning)
**Time needed:** ~1.5 h
**Decisions already made:** see [README](README.md#decisions-already-made-please-dont-reopen).

## Why you
The Hub will turn performance of a few dozen reels into "findings" that change how future reels are made. With small samples and a growing account, it's easy to learn the wrong lesson.

## Read
- [§12 Performance analytics](../spec/REELS_HUB_SPEC.md#12-module-h-performance-analytics): 12.2 features, 12.3 derived metrics, 12.5 analysis approach
- [§13 Learning loop and experiments](../spec/REELS_HUB_SPEC.md#13-module-i-learning-loop-and-experiments)
- [§16.4 Critique calibration](../spec/REELS_HUB_SPEC.md#16-module-l-ai-critique)
- [§18 Data model](../spec/REELS_HUB_SPEC.md#18-data-model): metric_snapshot, retention_point, features

## Questions
1. **Normalization:** comparing each reel to the account's trailing 30-day median. Good enough with fast follower growth, or should we model reach growth explicitly?
2. **Snapshots:** metrics pulled at 1 h / 24 h / 72 h / 7 d / 28 d. Which window should decisions use?
3. **Feature impact:** with ~24 reels per project and ~20 features per reel, what method is honest (simple comparisons with intervals, Bayesian partial pooling, nothing at all until N > X)?
4. **Experiments:** "one change per reel" in a daily series where topics also change. How do we separate the effect of the change from the stage topic (mountain vs. sprint stage)?
5. **Retention curves:** often imported manually from screenshots. How do we store and compare curves of different lengths?
6. **Critique calibration:** how should we score "predicted drop points vs. actual"?
7. **Findings:** what evidence level should be required before a finding changes the design language?

## Your input
<!-- Use the response format from the README. -->

**Sign-off:**
