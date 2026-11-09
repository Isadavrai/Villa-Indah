# Villa Indah — Codex task: photoreal macaque animation system

## Goal
Replace the existing 2x2 PNG-sprite animation in `monkeys.js` with a coherent, production-ready state machine that plays five transparent animated WebP assets and drives movement on the website. Keep the existing monkey toggle, 30-second arrivals, max count, pointer-follow behavior, touch support, translations, accessibility, and reduced-motion behavior.

## Source-of-truth and limitations
Animation assets are essential for photorealism. JavaScript/CSS must NEVER pretend to synthesize new realistic anatomical poses from a still image. If WebP files are absent, retain the existing `assets/monkey-run.png` as a visible fallback and report missing source assets. Do not invent filenames as existing files.

Prepare to use these assets, supplied separately:
- `assets/monkeys/run.webp`: 3-second transparent in-place run, facing right, loop.
- `assets/monkeys/walk.webp`: 4-second transparent in-place walk, facing right, loop.
- `assets/monkeys/jump-land.webp`: ~1-second one-shot crouch -> jump -> land -> seated.
- `assets/monkeys/sit.webp`: 6-second transparent seated idle, loop.
- `assets/monkeys/look-scratch.webp`: 5-second one-shot seated look right -> camera -> scratch neck -> neutral seated.

The original assets are animated WebP, not CSS spritesheets. Use actual image decoding/browser playback; do NOT use background-position slicing or CSS `steps()` to fake their internal frames. Animated WebP placed in an <img> inherently loops according to its embedded loop metadata, and restarting or freezing it cannot be reliably controlled just by CSS `animation-iteration-count`. One-shots therefore require a controlled wrapper: show the animation asset, use a JS timeout for its known duration, then swap to the appropriate still/idle asset; the media itself should be encoded with one-shot metadata. If provided metadata conflicts, re-encode appropriately or document it. Avoid cache-busting URLs each loop.

## Behavior and finite-state transitions
Possible states: `idle` (sitting), `look` (look/scratch once), `walk`, `run`, `jump`, `land` (implicit last frame in jump animation).
- `run` when visual movement speed > 100 px/s, `walk` at 12..100 px/s.
- `sit` after visual movement speed < 8 px/s continuously for at least 1000 ms (hysteresis to avoid rapid state flips).
- While sitting, optionally trigger `look` at a random 9..20 second interval; on completion return to `sit`. Do not trigger in reduced-motion.
- `jump` when initiating a short scripted leap; at most once per monkey every 18 seconds, and not while another one-shot plays. Animate the site's wrapper position separately from the subject so the asset stays centered internally.
- Never swap animations every requestAnimationFrame: transition only when state changes. Preserve positioning and correct left-facing flipping of the entire image with CSS `scaleX(-1)`, not by reversing playback.
- Preserve a single immutable visual baseline per monkey: identical width, height, object-fit:contain, and center anchor across all states. Do not animate scale wildly; subtle natural bob can be optional but asset already carries body motion. Make sure each <img> remains entirely within the container with tail visible.

## Accessibility, loading and performance
- HTML `<img alt="" aria-hidden="true" decoding="async">` because visual monkeys are decorative.
- Lazy load nonessential animations after the opt-in toggle, ideally predecode before first use.
- Use CSS `pointer-events:none` on moving monkeys.
- When `prefers-reduced-motion: reduce`, no movement, no blinking/scratching loops and no frame animations: show a static still frame only. If a transparent still frame does not exist, export one from sit.webp into `assets/monkeys/sit-still.webp`.
- When document.hidden, pause time accounting and motion updates, cancel timers and resume safely.
- Ensure no layout thrashing; update positions through transforms; cap monkey count at 10 as currently implemented.
- Keep existing translation/localization, aria-pressed toggle, growth cadence, pointer and touch behavior.

## Code integration
1. Read `monkeys.js`, `style.css`, `index.html`, `app.js` before editing.
2. Change only relevant monkey assets, styles and behavior; keep unrelated landing-page sections intact.
3. Add a small reusable state controller in `monkeys.js` (or new `monkey-animations.js` module if architecture benefits), with explicit state/timing cleanup.
4. Change `.monkey-sprite` from background-position 2x2 PNG to an `<img class="monkey-animation">` or an equivalent layered image approach.
5. Switch images when state transitions. Implement timing for one-shots and time-based idling; keep pointer-follow movement outside the asset animation.
6. Add transparent static fallback (or PNG sprite) for missing files. Avoid 404s for assets not yet uploaded.
7. Verify no obvious artifacts in WebP alpha on black/white backgrounds. Color fringing from the generated media cannot be fixed by CSS alone; flag it for media cleanup.
8. Provide a table with animation -> filename -> duration -> loop mode -> trigger. Run available static checks and report what was actually tested.
9. Commit changes to a feature branch and open PR if needed; do not deploy/push to production without approval.

## Acceptance tests
- Toggle on/off works.
- 1 initial monkey and growth to 10 over time still works.
- Running / walking / sitting transitions do not flicker or restart every frame.
- Looking/scratching plays once, then returns to sitting.
- Jump landing plays once, ends in sitting (without a positional teleport).
- Position remains centered inside each square visual container; full tail visible at every state.
- Facing flips correctly.
- Touch, keyboard accessibility and reduced-motion work.
- No console errors or missing asset requests with fallbacks.
- Narrow mobile viewport does not crop characters.

## Important
The provided generated files so far are low source frame rate upscaled to 1024px, not native 24–30 fps. Interpolating may improve smoothness but cannot guarantee realistic anatomy. Keep source honesty in comments and don't claim original 24–30 fps if it does not exist.
