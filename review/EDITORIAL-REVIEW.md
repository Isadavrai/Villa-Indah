# Review: editorial update and generated macaques

Not published. Branch: villa-editorial-monkey-troupe.

## Completed

- 15 separately generated resident animation loops (P01–P15), each with 6 distinct frames and its own motion. Animation payload about 795 KB total, plus static posters. Source and action manifest in assets/monkeys/generated/.
- P01 is the initial header macaque. Feeding uses an adjacent SVG banana with pointer/touch drag, or select-banana then activate-macaque with tap/keyboard. There is no separate framed banana control.
- One F1 follower appears immediately. P02–P15 join on object edges every 7 seconds. Maximum: 15 resident macaques including the header, plus one follower. Repeated header activation stops and resets.
- Residents load animations as they approach the viewport, keeping posters elsewhere. No additional resident assets load before activation. On coarse pointers/mobile the follower stays at a safe object edge. Reduced motion uses static posters.
- Story photographs now show two real villa/pool views (Private Swimming Pool/05 and /02). Gallery grouping is unchanged.
- Removed the two-column private/shared overview and the amenities strip as requested.
- Restaurant names, reception wording, additional-services note, bedroom/living descriptions and concise booking terms updated in RU/EN/ES.
- FAQ now has 10 practical questions with known facts and explicit pre-booking confirmation where property-specific rules were not provided. It does not duplicate the capacity figure or call the pool «приватный».

## Validation

- Mouse banana drag, actual emulated touch drag, two-tap alternative and keyboard activation verified.
- One immediate follower, first resident at 7 seconds, maximum 14 additional residents + header, no extra spawning, reset verified.
- All 15 WebP files decoded; each contains 6 unique frames. All posters exist. All 14 additional WebP clips loaded during viewport traversal; the header uses the 15th.
- Actual reduced-motion change switches active header/follower to posters. Starting with reduced motion leaves all 16 characters static and no pointer follower.
- RU/EN/ES at widths 375, 390, 768, 1024 and 1440: no horizontal overflow, 10 FAQ entries in every language, no missing translation keys.
- No JavaScript errors or failed same-origin requests in tested flows.

## Remaining blocker

The required analysis of 20–30 rental websites is not complete. External requests still return proxy 403. research/FAQ-RESEARCH.md lists 25 candidate services and the factual limits of the current FAQ. No claim is made that these sources or real guest questions have been analysed. Recheck access after the environment owner applies network settings, then complete the source matrix and refine the FAQ if needed.

Specific property terms remain unconfirmed: check-in/out, early/late access, housekeeping schedule, breakfast, child equipment, pets, smoking/events/visitors, payment/cancellation/refund terms and transfer price. The site asks guests to confirm them instead of inventing policies.
