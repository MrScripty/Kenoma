# Standalone pressure-projection lab: browser review

Tested source: `0bda9b5226e1bae3c83bf8c8fa12b0c4d6a03e46` on `research/pressure-projection-lab`, based on frozen checker successor `1828dfbc1f8441137c962ae47a1db31bac376a76`. This directory adds review evidence only. The receipt records clean committed source binding and SHA-256 hashes for the page, guide, checker, and captures.

The Chromium 151.0.7922.173 check passed 5,625 actual browser model states against independent rational closed forms: 625 signed/zero half-step fields, three positive scales, and all three spaces. Additional checks exercise quarter-step presets and custom inputs through the real UI, verify displayed values, invalid-input rollback, Reset, keyboard refinement, common fixed-field comparison, print, no-JavaScript fallback, and desktop/mobile layouts. These are numerical implementation tests, not a floating-point refinement theorem or a new kernel proof.

- [Desktop: one shared value](desktop-coarse.png), [two group values](desktop-paired.png), and [full sample representation](desktop-full.png).
- [Mobile: 390 pixels](mobile-390.png) and [320 pixels](mobile-320.png). Both have no document overflow; controls work at each width.
- [Printed default reference](fixed-field-reference.pdf) and [source-bound check receipt](receipt.json).

The same default prescribed `g=(-3/4,1/4,-1/4,3/4)` and `K=8` appear in all three desktop captures. Full energy stays 8; condensed energy increases from 1/2 to 1 to 8; the independently computed residual gap decreases from 15/2 to 7 to 0. No state is re-equilibrated and no body is rendered.

The [proof guide](../pressure-projection-proof-guide.md) maps all 27 unchanged Lean statements and proposes an approximation interlude after weighted sampling/local volumetric penalties, before pressure-space resolution diagnostics and anatomical coupling. Main book, PR 8, SLS, serial and axisymmetric registrations remain unchanged. There is no site release or hosted qualification of this new browser lab.
