# Private Villa Indah

Static multilingual villa website: Russian, English and Spanish. No dependency
installation or build is needed.

## Run

From `/workspace/Villa-Indah`:

```sh
python3 -m http.server 3000 --bind 0.0.0.0
```

## Deployment

GitHub Pages serves the repository's `main` branch at `/ (root)`:
https://isadavrai.github.io/Villa-Indah/

The owner approved publishing the redesign on 8 November 2026. Relative asset
paths support the project base path. `.nojekyll` disables Jekyll processing.
The public draft retains `noindex,nofollow` until the final launch is approved.
CSS and script URLs are versioned to avoid reusing the previous interface's cache.

## Content and assets

- `index.html`: semantic page and Russian no-JavaScript fallback content.
- `content.js`: language dictionaries, `villaConfig` contact/video settings,
  confirmed amenity scope and image metadata.
- `app.js`: navigation, gallery, enquiry validation and optional animations.
- `style.css`: design tokens and responsive layout.
- `assets/photos/`: 45 original, unretouched owner photographs. `manifest.json`
  records source names, category, scope, focal point, alt text and image role.
  Mirror manifest edits in the `photos` array in `content.js`.
- `assets/jungle-background.png`: generated photorealistic rainforest artwork,
  used as the full hero background. It does not document the villa grounds.
- `assets/jungle-frame.png`: earlier generated framing asset retained for future
  adjustments; it is hidden in the current full-background design.

The main villa photos are `38.jpg` (pool facing the facade), `14.jpg` (view from
lower grounds), `23.jpg` (bedroom) and `26.jpg` (living room). Resort photographs
are labelled as shared facilities. The gallery supports categories, arrow keys,
Escape, focus restoration and touch swipes.

## Enquiries

Email: `villaindah.valeriia@gmail.com`. The enquiry opens the visitor's email app
with dates, adults, children and optional message. The visitor sends the message;
there is no server submission, live availability, payment or automatic booking.
A copy-email button is available when the mail application is not configured.

Date validation uses Asia/Makassar calendar days, check-out after check-in, at
least one adult and eight guests maximum including children. No prices appear.
`villaConfig.whatsapp` is empty and its button disabled until a confirmed number
is supplied. `villaConfig.video` is empty; the hero is a static rainforest image.
Only configure a real licensed villa video. Automatic playback respects reduced
motion and data saving. The optional monkey uses four generated photorealistic macaque poses in a transparent sprite sheet. Its first-screen switch enables pointer/touch following, direction changes and idle pauses. Reduced motion disables gait animation and smooth following. No interactions are blocked.

See `CONTENT_TODO.md` for remaining owner inputs. No analytics, external fonts,
server dependencies or fabricated legal policies are included.

`assets/monkey-run.png` is an AI-generated four-frame transparent animation sheet, not live animal footage. The monkey is opt-in and its state resets when the page reloads.
