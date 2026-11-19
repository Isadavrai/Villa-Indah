# Villa Indah integrations — review and owner checks

## Public configuration

- Production: https://villa-indah.com/
- Host: GitHub Pages. Existing CNAME retained as `villa-indah.com`; Cloudflare DNS and Pages publishing mode unchanged.
- Formspree endpoint: https://formspree.io/f/mrpqlvrd
- GA4: G-D7TEB0RWS6
- Telegram: https://t.me/VillaIndahV

No private API key, bot token or visitor submission is stored in the repository.

## Form

Existing fields and Bali calendar validation remain. Optional phone, adult/data consent, dates and a maximum of 8 guests are checked before POST. `_gotcha` is the honeypot. A synchronous in-flight guard stops repeated submissions; the button and aria-busy reflect sending. The request uses FormData, POST and Accept: application/json. Errors preserve fields; only a positive HTTP response with no explicit provider rejection produces success/reset and `generate_lead`. A 30-second timeout reports that submission could not be confirmed; it does not claim the server never received it.

Browser validation is not a substitute for provider-side validation. Check available Formspree validation, spam protection and allowed-origin settings in the account. The guard prevents simultaneous duplicate UI requests; it does not provide a server-side idempotency guarantee for manual retries after an ambiguous network failure.

## Analytics and privacy

- Basic Consent Mode: no gtag script or GA requests before explicit analytics permission. Ads storage/user data/personalisation remain denied.
- Map and analytics permissions are independent fields in `indah-privacy-v2`. A previous v1 map preference survives; it never grants analytics automatically. Necessary language preference remains separate.
- One tag URL, no GTM container, config send_page_view:false, one explicit page_view per page load. Language changes and re-grant in the same page do not produce another page_view.
- Events: click_telegram, booking_form_start (once on first input interaction per page), generate_lead (positive submission only), click_email. No retroactive replay of interactions before consent.
- The site sends only constant/sanitised event parameters: production root URL, fixed title and an allowed language. No form values, email address, phone, message, raw query, hash or referrer URL are passed by this code.
- No Google Signals or ad personalisation. GA cookies use the `indah` prefix to distinguish them from unrelated cookies.
- Revocation sets the GA disable flag, denies consent, drops pending events and clears accessible owned analytics cookies. Already-sent/in-flight requests cannot be retracted. The loaded tag may remain in memory; collection stays disabled until another explicit grant.
- Consent withdrawal in another same-origin tab is applied. If browser storage is blocked, choices work for the current page.
- Policy settings remain keyboard-accessible through the native dialog; analytics refusal does not disable the form, email or Telegram.

### Required GA4 account check before release

In the web stream settings, review **Enhanced Measurement**. Disable automatic page/history, outbound-click and form-interaction measurement when validating this explicit event-only setup. These account-controlled features cannot be confirmed or changed from the current environment. Do not enable automatic collection of user-provided data. Otherwise Google-managed automatic events may exist in addition to the explicit events tested here.

## CSP

Formspree is allowed only in connect-src. Native form-action remains 'none', because the site uses AJAX and should not leak a native GET submission if JavaScript is unavailable. Script sources add only www.googletagmanager.com. Measurement sources are www.google-analytics.com and region1.google-analytics.com in connect-src/img-src. Existing Google Maps frame hosts are retained. No wildcard or unsafe-eval was added.

## Checks actually performed

`node tests/integrations.cjs` (Playwright already installed in this environment; use PLAYWRIGHT_MODULE/CHROMIUM_PATH/BASE_URL to point to another local setup).

The test suite uses isolated mocked Formspree responses, a mock at the official Google tag URL, a mock collection endpoint and a mock map document. It sends no real enquiries or measurements. It verifies:

- No map/tag/analytics requests before permission; separate map permission; migration of legacy map preferences.
- One tag and page_view; validation, honeypot, double-submit guard, loading state, success/reset, HTTP error, network error and explicit provider rejection.
- Correct lead timing, first input event once, Telegram/email events and absence of form/query/hash PII in the tested payloads.
- Revocation, owned-cookie removal, no replay on re-grant, cross-tab withdrawal and sending with analytics refused.
- 53 photos in 10 tabs, lightbox keyboard navigation, RU/EN/ES, menus and no horizontal overflow at 375/390/768/1024/1440 px.
- Banana interaction, 15 residents including header, one follower and reset.
- Bali date boundary, CNAME, canonical/OG domain, sitemap and source CSP.
- No page JavaScript or CSP errors in those flows. Mocked cross-origin requests passed browser CSP/CORS checks; actual service CORS remains unverified.

## Live attempts and unverified work

The authorised TEST submission attempt to Formspree was blocked before connecting to the origin: proxy CONNECT 403, HTTP 000. No successful submission/delivery is claimed. Read-only requests to the production domain, Google tag URL and Telegram URL also returned proxy 403.

Not verified here: real Formspree acceptance/account entry, actual email delivery, real Google tag internals/collection/Realtime/DebugView, actual Telegram account availability, production HTTPS/certificate/redirects or live service CSP/CORS. Account access is not available. These are manual owner checks, not passed tests.

## Owner verification steps

1. **Formspree**: open the form `mrpqlvrd`, confirm destination email, notifications, account activation and any origin rules for `https://villa-indah.com`. Submit one clearly marked TEST enquiry after deployment, then check both the Submissions entry and recipient mailbox. Check spam folders if needed. Do not treat HTTP 200 alone as proof of email delivery.
2. **GA4**: review Enhanced Measurement as above and choose retention settings. In a clean browser session, reject analytics and verify no googletagmanager/GA collection requests. Accept analytics and check one page_view. Enter the form once, click Telegram/email, submit a valid TEST enquiry and verify the four explicit event names. Invalid/server-error submissions must not emit generate_lead. Withdraw analytics and verify no further collection, while the form and Telegram still work.
3. In GA4 Admin → Events/Key events, mark `generate_lead` as a key event when available. Do not create a second derived event that duplicates the site event. Confirm the actual GA4 ID and production stream URL.
4. **Telegram**: open the button on desktop and phone and confirm the destination is @VillaIndahV. No bot or automatic dates/message generation is implemented.
5. **Domain**: check https://villa-indah.com and any intended www redirect, certificate and Pages Enforce HTTPS. Verify canonical/OG and https://villa-indah.com/robots.txt and /sitemap.xml. DNS was not changed by this work.
6. **Privacy**: approve operator details, enquiry/correspondence and GA retention settings, recipient access and deletion procedures. No legal compliance certification or invented retention period is provided.

Do not merge or publish until the owner reviews the change and the required live/account checks are resolved or explicitly accepted for the release.
