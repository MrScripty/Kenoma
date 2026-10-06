# Actual integrated book browser qualification

This isolated checkout starts from `5a8e84081dbe579705535daffebdd2f98121f63c`.
Its `dist` was copied from the actual 42-card integrated build produced at
`11b5dbd47ddb5364eae594bf1aae18050add5c65`. All production controls match
the build's source hashes. Two subsequent inspector-tool refinements differ;
`build-binding.json` records those differences explicitly. This is not final
source release qualification or physical-phone evidence.

Commands, from this checkout's `education` directory:

```sh
python3 tests/browser.py > review/integrated-browser-qualification/browser.log 2>&1
python3 tests/mobile_startup.py > review/integrated-browser-qualification/mobile.log 2>&1
python3 review/integrated-browser-qualification/run_integrated_controls.py > review/integrated-browser-qualification/controls.log 2>&1
python3 review/integrated-browser-qualification/probe_series.py > review/integrated-browser-qualification/series-probe.log 2>&1
```

The unchanged whole-book browser test failed at `tests/browser.py:106`, which
still expects Lab5 active work above 8.59 J. The actual compliant Gaussian
force-length fixture gives 5.919902142568573 J at q=90°, a=0.5985127486940003,
t=0.30000000000000016 s. Its actual downloaded trace identifies
`series-force-length-affine-tissue-v2`, matching the integrated test's model
assertion. An initial report about an outdated model assertion referred to
the original workspace checkout and was corrected after checking this isolated
source. The work-threshold failure was reported to the parent for correction.
The later contact-off 13.891 mm and bulk-zero 0.45384 checks remain valid.

The unchanged mobile-startup test passed using Chromium 151.0.7922.173 with
Pixel 7 touch emulation and default headless launch. It checks actual drawn
geometry in all seven labs and the atlas, stable Start hit targets without
downloads, actual WebGL context loss and retry, injected draw failure and
retry, and unavailable-WebGL numerical controls. See `mobile/receipt.json`,
`mobile.log`, and the fresh screenshots in `mobile/`.

The integrated controls run uses the unchanged `teaching_controls_browser.check`
against the actual full book and bundle, with an executable-byte identity gate.
Its first evidence runner attempt used Playwright's implicit one-page context;
the intentional second-page fallback check rejected that harness setup.
`controls-runner-failure.json` and `.log` preserve the failed attempt. The runner
now uses an explicit context as the repository browser tests do. Final status
is recorded only after all checks finish in `controls/receipt.json`.

Screenshots actually inspected: mobile spatial drawn mesh, mobile series
numerical-only fallback, Lab3 Verlet h=.005 completed 2400/2400 steps at 12 s
with 2401 samples, and Lab5 held current-force/work fixture. No uninspected
render, hosted deployment, or final extra-proof-family rebuild is claimed.

The parent corrected only `tests/browser.py` in integration commit `79cf93e`.
That exact file was copied into this isolated checkout for a rerun against
unchanged executable bytes. Its SHA-256 is
`ba1c7c813d0507c1560443dee2cf8bac53266f1e4bdd2040d720f312ec3c81fe`.
The original failure is preserved in `browser-original-failure.log`; the rerun
log is `browser-corrected.log`. The revised checks retain the current work
fixture and independently verify activation, Gaussian force, and energy balance.

The integrated controls rerun passed every case against the actual 42-card
book with no JavaScript errors and unchanged executable bytes. The receipt is
`controls/receipt.json`; all 15 energy traces contain every fixed-step sample
and terminate exactly at 12 simulated seconds. Actual Lab7 active-shape-off
screenshot was inspected: q=90° and a=.6 remain selected, the rendered shape
changes, and the finite-iteration approximation is labelled explicitly.

The corrected unchanged-build whole-book browser rerun passed all checks,
including 42 proof cards, internal links/local resources, real desktop/mobile
viewport WebGL, all integrators, full embedded teaching-control regressions,
state/trace/release and reset, explicit spoken summaries without frame
announcements, actual atlas views, keyboard controls, and no-WebGL/no-JavaScript
alternatives. See `book/receipt.json` and `browser-corrected.log`.
