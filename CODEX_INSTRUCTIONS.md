# Villa-Indah: macaque animation assets

Place files from `assets/monkeys/` into the same path in repo `Isadavrai/Villa-Indah` (branch `main`).

## Codex task

In this repository, integrate the supplied animated WebP files in `assets/monkeys/` into the existing monkey behavior. The site currently has `monkeys.js` and `assets/monkey-run.png` (a sprite sheet). Replace the sprite-sheet visual layer with an `<img>`-based renderer or CSS background-image loading WebP. Preserve the current monkey toggle, 30-second arrival cadence, pointer following, monkey count, accessibility, reduced-motion treatment, mobile behavior and existing navigation. Do not remove old PNG until the new implementation is verified.

Behavior mapping:
- run.webp: running while moving fast, LOOP.
- walk.webp: slower movement, LOOP.
- jump-land.webp: optional arrival transition, PLAY ONCE; sit image after finishing.
- sit.webp: idle on invisible ledge, LOOP.
- look-scratch.webp: occasional seated idle gesture, PLAY ONCE, then sit.webp.

Important: image animation restart needs reassigning `src` or replacing `<img>` when changing state; avoid doing that on every animation-frame tick. Flip image horizontally on direction change without moving its parent. Respect prefers-reduced-motion by showing a static frame/asset with no animated movement. Sprite remains fully contained in its square box with object-fit:contain. Verify no backgrounds, clipping or visible light halos on both dark and light backgrounds.

QA: Generated assets contain relatively few unique frames and may show matte/contour artifacts; do not represent them as 24–30 unique FPS or perfectly clean. Optimize filesize if useful without sacrificing transparency.
