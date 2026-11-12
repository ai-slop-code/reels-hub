# Review packet 12: motion designer

**Priority:** before phase 7 (graphics and motion)
**Time needed:** ~1.5 h
**Decisions already made:** see [README](README.md#decisions-already-made-please-dont-reopen). D7: HyperFrames accepted as the renderer.

## Why you
Motion graphics will be built outside Edits with HyperFrames (HTML/CSS/SVG → video) and reused across 24+ reels. They need a clear motion language that fits Katarina's calm-maps, loud-person style.

## Read
- [`DESIGN_LANGUAGE.md`](../spec/DESIGN_LANGUAGE.md): §1 brand core, §2 color, §3 typography, §5 layout, §7 maps, §8 motion
- [§10 Graphics generator and 10.1 HyperFrames](../spec/REELS_HUB_SPEC.md#10-module-f-graphics-generator)
- Reference: `../reels/giro00-intro/graphics/map_trieste_roma.png`, `map_trieste_border.png` and the Giro_00 draft

## Questions
1. **Motion language:** review the proposed tokens (ease-out, 0.3 s pops, 0.25 s text-in, 108 % push-in, one motion idea per graphic). What would you change?
2. **Template set:** `card_map_cities`, `map_travel`, `stage_route`, `stat_card`, `climb_profile`, `lower_third`. What's missing for a 21-stage series (e.g. rest days, time-trial distance, altitude)?
3. **Maps:** current style (navy sea, warm Italy, pink accents, Avenir labels). Keep, refine, or rethink for motion?
4. **Typography:** Monstera-Black for titles (no en dash) and Avenir Next on maps. Pair or unify? Licensing outside Edits is being checked by legal (packet 04).
5. **Overlay vs. full-frame:** where should graphics sit on top of footage (alpha MOV) vs. replace the shot?
6. **First test:** rebuild "Štart v Terste, cieľ v Ríme" with push-in and dot pops. What should we judge it on?

## Your input
<!-- Use the response format from the README. -->

**Sign-off:**
