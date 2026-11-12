# Villa Indah publishing notes

The owner requested publication of this version after reviewing the separate branch. The site is served from `main` on GitHub Pages. The integrations below still need confirmed inputs; the page does not present a fake booking success or an approximate map pin.

## Items needed to finish the live enquiry path

1. Create a Formspree form in the owner's account, configure its notification destination and spam protection, and provide the form endpoint/ID. Set `villaConfig.formEndpoint` in `content.js` to the HTTPS endpoint. The form stays disabled without it. A local mocked success/failure test is not a delivery test; send a real test enquiry and verify it in the Formspree dashboard and notification inbox after the endpoint is configured.
2. Supply approved RU/EN/ES text explaining who receives the guest's contact details and why, plus the owner/service details needed for an accurate privacy notice. Add it beside the form before enabling real delivery.
3. The owner supplied a Google Maps short link for the villa, now shown as a directions link. To embed an interactive map with the exact pin, supply Google's official embed URL for that same point and set `villaConfig.mapsEmbedUrl`. This environment could not resolve the short link because Google Maps returned a 403 through its network proxy, so no approximate pin is shown.
4. Confirm the photo-to-room mapping and approved room names in [PHOTO_GROUPING.md](PHOTO_GROUPING.md), including which bathrooms belong to which room and whether a guest WC photograph exists. The current gallery uses provisional location labels from the supplied photo descriptions.
5. If a direct WhatsApp option is wanted, provide the WhatsApp Business number in international format. Set `villaConfig.whatsapp`; the separate link is hidden until then.

The animation derivatives used by the page are in `assets/monkeys/new/`. A1 and A2 exist only as GIF in the supplied sources; A3–A5 and F1–F5 use animated WebP. The original owner uploads remain in the repository. Every animation starts only after the visitor clicks A1, except A1 itself. Reduced-motion visitors see matching still frames.

Screenshots from local browser review are in `review/`.
