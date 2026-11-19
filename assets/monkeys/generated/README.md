# Villa Indah generated macaques

15 separate animated WebP files, P01–P15, created for this task with image generation. Each uses six distinct generated poses; these are short frame-based loops, not captured wildlife footage. P01 is the header macaque; P02–P15 appear on object edges after feeding. The existing F1 animation remains the single pointer follower.

Actions, frame counts, durations and source-image hashes are recorded in manifest.json. Each clip has a static PNG poster for reduced motion and offscreen placeholders. Offscreen residents display a poster; their WebP loads when approaching the viewport. No animation library, remote SDK or third-party requests are used.

Production: three 6-column, 5-row photorealistic sprite sheets; alpha cleanup and removal of detached fragments from neighbouring cells; consistent per-row crop and scale; 192×192 WebP encoding. The originals remain in /workspace/generated_images. Animation production script is included as build-troupe.py and requires Pillow.
