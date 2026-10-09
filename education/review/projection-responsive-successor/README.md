# Responsive repair: same-executor checkpoint

This file preserves the historical access checkpoint. The subsequent completed rebuild and local qualification are recorded in [qualification/README.md](qualification/README.md), with exact source/tree, fresh artifact hashes, all local gates and the hosted/local distinction.

This is an isolated, local successor on `education/projection-responsive-successor-20261006` in `/workspace/Kenoma-mobile-successor`. Its source commit is **8f5bec15cf69643e3d6a9ab8f1164ef6ff452fd1**, directly parented by the preserved print-limits successor **e7d56450f6a806fa14b0a511bfcf6405d592fc27**. No remote push or new hosted qualification has been requested. The published 153-page edition, main, PR8, old branches, and deployment are unaffected.

## Cause and concrete repair

The sample table has six nowrap columns. At Q1 with DejaVu Sans, its intrinsic minimum width was 292.453125 px. The parent grid item's automatic minimum width expanded the panel to 328.453125 px, reaching x=345.453125 at a 320 px viewport. The existing table scroller therefore expanded rather than containing the table. This is a reproducible font/state-dependent grid sizing defect; it does not prove the hosted browser patch version caused the failure.

The HTML change adds `.details-grid>.panel{min-width:0}` and makes the existing table scroll region keyboard-focusable with an accessible name. With the fix, document width is 320 px, and the 250 px table region scrolls its 292 px content. There is no root overflow clipping, content removal, font reduction, or equation change. Both script bodies are byte-identical to e7d56450, as are all Lean sources and proof inventories.

The strict no-overflow assertion remains. The checker now saves element bounds, state, font, browser version, and a screenshot before asserting on a failing viewport. The workflow preserves these diagnostics with `if: always()`. An explicit actual-browser regression checks the frozen failing source and the responsive successor.

## Completed local evidence

- [Receipt](local-browser/receipt.json): PASS, source-bound to 8f5bec15; Chromium 151.0.7922.173; 42 combinations of widths 320/360/390/414/560/768/1280, spaces Q1/Q2/Q4, and native/DejaVu fonts. Strict document bounds and controls, independent rational oracle, actual preset/slider/custom-input/reset interactions, keyboard table scrolling, access to the last column, and visible interpretation paragraph passed. No JavaScript errors.
- [Frozen failure bounds](local-browser/viewport-failure-frozen-dejavu-320.json) and [screenshot](https://raw.githubusercontent.com/MrScripty/Kenoma/596df78f5cb652b4ac70917a82d8aa908b617056/education/review/projection-responsive-successor/local-browser/viewport-failure-frozen-dejavu-320.png) preserve the 345 px document on a 320 px viewport.
- [Fixed 320 px native screenshot](https://raw.githubusercontent.com/MrScripty/Kenoma/596df78f5cb652b4ac70917a82d8aa908b617056/education/review/projection-responsive-successor/local-browser/fixed-native-320.png) and [fixed DejaVu screenshot](https://raw.githubusercontent.com/MrScripty/Kenoma/596df78f5cb652b4ac70917a82d8aa908b617056/education/review/projection-responsive-successor/local-browser/fixed-dejavu-320.png) preserve the rendered successor.
- [Hosted failure extract](diagnosis/hosted-run-37489843475-extract.log) and [jobs](diagnosis/hosted-run-37489843475-jobs.json) preserve the failed run. Node 208, Python 55, build/Lean, and 103-statement/12-source actual-point print gates passed before the strict 320 px projection assertion failed, before PDF rendering. Original failed run 37484501133 and e7d56450 remain preserved.

## Access checkpoint and remaining work

The same `/workspace` executor is accessible after the reported disconnection. The completed local responsive test was inspected without restarting it. No test command was active at this checkpoint, and no environment was switched.

The exact CI Chrome/headless 151.0.7922.34 (Playwright 1.62.0, chromium v1234) is unavailable locally: official Playwright CDN downloads and the official Chrome-for-Testing storage URL received proxy HTTP 403. The standard and auto-approved escalated attempts are preserved in [download log](diagnosis/browser-install.log) and [escalated download log](diagnosis/browser-install-escalated.log). The escalation was approved; this is a download/network restriction, not an approval rejection. No proxy settings, credentials, or protections were changed.

This checkpoint does **not** claim CI-equivalent browser execution, a rebuilt successor book/PDF, a new portable bundle, or fresh full qualification. The ignored `education/dist` still contains the previous print-limits successor build and must not be presented as a build of 8f5bec15. The next build must bind the new HTML/checker source, rerender the portable projection PDF with its full Interpretation and limits paragraph, rerun the mandatory actual-point typography/full-source/diagram gates and relevant damage checks, and produce fresh portable MD/PDF/site artifacts before any new hosted qualification. The old qualified source and review artifacts remain immutable.
