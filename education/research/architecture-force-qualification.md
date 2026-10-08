# Bounded architecture-force contribution qualification

The `architecture-force-contribution` job in `education.yml` runs only for draft
pull requests. It checks out the explicit PR head SHA with read-only permissions
and no retained Git credentials. It does not change the existing full-book or
Pages job conditions. Keep the contribution PR in draft: marking it ready still
starts the repository's separate, broad full-book gate.

The original thirteen files under `contributions/architecture-force/` are the
reviewed additive lesson, not book registration. The job names their two Node
test files explicitly because the existing default `npm test` glob excludes
this directory. Its twelve Node contracts include the actual checked-out
`web/anatomical-material.mjs`. Seven SymPy identities remain supplementary
symbolic evidence, separate from the six Lean Real contracts.

## Dependency and source boundary

The job reuses the repository's pinned action commits, Node 22, Python 3.12,
Python requirements and hash-verified official Lean 4.19.0 installer. It verifies
the pinned mathlib revision and manifest *before* cloning the manifest's exact
package revisions. It verifies pristine package sources before and after
fetching only the official cache closures of `Mathlib/Data/Real/Basic.lean`,
`Mathlib/Tactic/FieldSimp.lean`, and `Mathlib/Tactic/Ring.lean`. Mathlib's official
cache tool may also retrieve its pinned ProofWidgets release assets. Nothing
invokes a full mathlib target, book build, PDF render, anatomical solve, campaign,
calibration, proof registry update, or deployment.

This bounded official-binary-cache route is explicitly different from the
full-book all-dependencies-from-source qualification. The contribution's own
`check_lean.py` then rechecks all pins/pristine sources and freshly compiles its
six declarations with warnings as errors and the existing kernel-axiom policy.

`source.json` records the exact checked-out commit, Git tree, Actions run/workflow
identifiers and SHA-256 hashes of the thirteen contribution files plus the
workflow, qualification tools, browser test, pinned requirements/installer/lock,
and unchanged material operator. All inputs must be tracked and pristine.
`qualification.json` is written only after checking source identity again and
binding Node, symbolic, Lean, browser and JPEG capture receipts. Generated files
and dependency checkouts are refused inside the repository and live under
`runner.temp`. Failure diagnostics upload using `always()`; their mere presence
does not mean qualification passed. Only a successful job with a matching head
and complete `qualification.json` establishes the bounded automated result.

## Real-control and visual boundary

The portable browser test derives its static source root from its own location
and uses the Chromium installed by pinned Playwright. It tests 1280×1000 and
393×852 viewports, independent keyboard Home/End changes for every range,
ArrowRight stepping, the force–length checkbox in both directions, all readout
rows, repeated reset, local anchor targets and exact HTTP response bytes, browser/HTTP errors,
horizontal overflow and a no-JavaScript fallback. It serves only this static
contribution and rejects external requests. Five full-page JPEG quality-85
captures cover both layouts in default and changed states plus no-JavaScript.

Automated success is not visual acceptance. Inspect all captures for readable
text, layout, clipping, spacing and meaningful control state before claiming
visual acceptance. The receipt deliberately retains `pending human inspection`
until that separate decision. No anatomical rendering acceptance is implied.

## Reproduction after reviewing the workflow delta

Use a clean committed checkout. Set `RECEIPTS`, `LEAN_ROOT` and `MATHLIB` to fresh
absolute paths outside it, and `EXPECTED_HEAD` to its exact commit. Run the
commands in the named workflow job in order. The browser command is:

```
cd education
python3 tests/architecture_force_browser.py --output /absolute/external/browser
```

A source-only preparation may run the twelve Node tests, seven symbolic checks,
Python syntax/receipt tests, and dependency verification against an existing
pinned checkout without fetching or compiling anything. Such a preparation is
not a hosted run, fresh Lean compilation, browser-control pass or visual review.
No dispatch, merge, ready-for-review transition or Pages publication is implied.
