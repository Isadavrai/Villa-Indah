# Villa Indah publishing notes

This revision is for PR review only; do not publish without owner confirmation. The integrations below still need confirmed inputs; the page does not present a fake booking success or an approximate map pin.

## Items needed to finish the live enquiry path

1. Create a Formspree form in the owner's account, configure its notification destination and spam protection, and provide the form endpoint/ID. Set `villaConfig.formEndpoint` in `content.js` to the HTTPS endpoint. The form stays disabled without it. A local mocked success/failure test is not a delivery test; send a real test enquiry and verify it in the Formspree dashboard and notification inbox after the endpoint is configured.
2. Supply approved RU/EN/ES text explaining who receives the guest's contact details and why, plus the owner/service details needed for an accurate privacy notice. Add it beside the form before enabling real delivery.
5. If a direct WhatsApp option is wanted, provide the WhatsApp Business number in international format. Set `villaConfig.whatsapp`; the separate link is hidden until then.

The animation derivatives used by the page are in `assets/monkeys/new/`. A1 and A2 exist only as GIF in the supplied sources; A3–A5 and F1–F5 use animated WebP. The original owner uploads remain in the repository. Every animation starts only after the visitor clicks A1, except A1 itself. Reduced-motion visitors see matching still frames.

Screenshots from local browser review are in `review/`.

The exact map coordinates are configured. Photo folders supply the confirmed gallery grouping. All three uploaded font archives contain the same multilingual Alumni Sans Pinstripe files. Additional monkeys arrive one at a time at seven-second intervals.
