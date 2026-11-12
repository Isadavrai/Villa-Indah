# Villa Indah review notes

This branch is a review draft. It must not be merged into `main` or deployed until the owner approves the missing details below. The existing `main` branch and GitHub Pages settings are unchanged. `robots=noindex` remains in the draft HTML.

## Items needed to finish the live enquiry path

1. Create a Formspree form in the owner's account, configure its notification destination and spam protection, and provide the form endpoint/ID. Set `villaConfig.formEndpoint` in `content.js` to the HTTPS endpoint. The form stays disabled without it. A local mocked success/failure test is not a delivery test; send a real test enquiry and verify it in the Formspree dashboard and notification inbox after the endpoint is configured.
2. Supply approved RU/EN/ES text explaining who receives the guest's contact details and why, plus the owner/service details needed for an accurate privacy notice. Add it beside the form before enabling real delivery.
3. Supply the exact Google Maps pin for the villa, not only the resort address. Set both `villaConfig.mapsEmbedUrl` (Google's official embed URL for that pin) and `villaConfig.mapsDirectionsUrl` (the same pin's directions URL). The map stays absent until both are set.
4. Confirm the photo-to-room mapping and approved room names in [PHOTO_GROUPING.md](PHOTO_GROUPING.md), including which bathrooms belong to which room and whether a guest WC photograph exists. The current gallery uses provisional location labels from the supplied photo descriptions.
5. If a direct WhatsApp option is wanted, provide the WhatsApp Business number in international format. Set `villaConfig.whatsapp`; the separate link is hidden until then.

The animation derivatives used by the page are in `assets/monkeys/new/`. A1 and A2 exist only as GIF in the supplied sources; A3–A5 and F1–F5 use animated WebP. The original owner uploads remain in the repository. Every animation starts only after the visitor clicks A1, except A1 itself. Reduced-motion visitors see matching still frames.

Screenshots from local browser review are in `review/`. They show this branch only, not the currently published `main` site.
