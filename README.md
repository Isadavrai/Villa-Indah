# Private Villa Indah

A responsive, dependency-free website prototype in Russian, English and Spanish.

## Run locally

From `/workspace/Villa-Indah`:

```sh
python3 -m http.server 3000 --bind 0.0.0.0
```

Open the server in your local development browser. No dependency installation or build is required.

## Photographs

45 original JPEG photographs from the owner's archive are bundled in `assets/photos/`.
`manifest.json` maps the numbered files to their original names. Originals have not
been retouched or upscaled. The main sequence uses `38.jpg` (pool facing the facade)
and `14.jpg` (villa from the lower grounds), followed by bedroom `23.jpg` and living
room `26.jpg`. Separate galleries contain 38 villa and 7 resort photographs.
Gallery links open the original photograph in a new tab.

## Contact

Availability buttons open a dialog with a localized `mailto:` link to
`villaindah.valeriia@gmail.com`. It prepares an enquiry for dates and guest count
in the visitor's email client. Sending requires the visitor's action. This does
not provide a server-side booking, calendar, or email-delivery service.

## Current scope

- Three languages, with remembered language preference.
- Responsive layout and scroll animation respecting reduced-motion settings.
- Original villa and resort photographs and optional emoji monkey following pointer movements. The emoji is a prototype, not the requested realistic animated monkey; a suitable animated asset remains to be created.
- Accessible enquiry dialog opens the owner’s email address in the visitor’s email client.
- No prices, analytics, external fonts, or external dependencies.

## Before publication

Finish image enhancement, replace the emoji with the agreed realistic animation, and test on real mobile devices. A video tour is not yet produced. Verify current resort terms and all amenities before publishing. The villa has four bedrooms, capacity for eight guests, three bathrooms and a separate guest toilet. Hotel beach, infinity pool and cinema are shared facilities; food and drinks cost extra, and hotel beach cinema screenings are free according to the owner.
