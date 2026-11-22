# Monkey, FAQ and phone update

- Banana aligned immediately beside the arrow, above the gesture hand; drag and keyboard feeding preserved.
- 20 resident monkeys including the header, plus one follower. Five additional existing A1–A5 animations reused. Asymmetric perches extend through gallery, FAQ, enquiry, map and footer; all residents appear immediately after feeding.
- Follower keeps moving toward the last cursor position, then freezes position and animation on arrival. Touch and reduced-motion layouts remain anchored.
- Removed requested FAQ entries and House Rules group; 11 questions remain in RU/EN/ES.
- Native calling-code selector with flags and 92 countries. National and international input accepted; Formspree receives the combined international number.

Validation: integration regression and targeted Chromium tests passed, including 15 viewport/language combinations, gallery rerender, drag feeding, immediate full troupe, follower arrival/idle/resume, FAQ removal, and mocked form submission. Service delivery was not retested live. Screenshots: feeding-gesture-mobile.png and phone-country-mobile.png.
