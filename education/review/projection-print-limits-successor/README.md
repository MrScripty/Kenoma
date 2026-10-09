# Projection PDF limits correction

Renderer/regression source: `789c079963374b57e5213e02772114b00e60346f`.
Frozen predecessor: `9c4ab8b23adf56c84bcabdcab28cfe8ea59ff99f`.
Successor branch: `education/projection-print-limits-successor-20261006`.

The old portable projection PDF (`68777646f3a24518972b32dd7f459584bdc856ff52f8169b8e306d2520e44542`) printed the “Interpretation and limits” summary but omitted its complete paragraph because the source `<details>` element was closed. Present glyphs were 10.5 pt, so the prior size, label and link gates did not detect missing content. The main book already retained its limits.

`tests/projection_integration.py` now opens the existing footer details element only in the review-render DOM, before `page.pdf`. The accepted standalone HTML, mechanics, mathematical assumptions, proofs and screen interaction remain unchanged. `tools/check_projection_print_limits.py` extracts the complete authored paragraph from that same source and requires its complete normalized text at actual ≥10 pt, with in-page glyph bounds. `tests/artifacts.py` makes the semantic paragraph gate mandatory alongside the existing projection binding gate. The renderer/checker hashes are bound to the immutable source commit in the new receipt.

The [corrected four-page PDF](https://raw.githubusercontent.com/MrScripty/Kenoma/596df78f5cb652b4ac70917a82d8aa908b617056/education/review/projection-print-limits-successor/artifacts/fixed-field-reference.pdf) is SHA-256 `22bc6672b42fe723cbdc429dcf9315fd450a9a9231d3d01285f610809286a617`. All **416 normalized paragraph glyphs**, its heading and all **33 diagram labels** pass at **10.5 pt**. Page 4 was visually reviewed; [capture](https://raw.githubusercontent.com/MrScripty/Kenoma/596df78f5cb652b4ac70917a82d8aa908b617056/education/review/projection-print-limits-successor/corrected-last-page.png) and [qualification](qualification.json) preserve the exact measurements and hashes. Its full paragraph includes positive-J justified sampling, exact projector, positive constant K, coefficient-uniqueness/injective-evaluation conditions and the no-equilibrium/Hessian/continuum/anatomy/floating-point-refinement limits. HTTPS and internal PDF links remain portable.

Passed affected checks:

- The committed regression rejects the frozen heading-only PDF despite its visible heading and ≥10 pt present glyphs.
- A self-consistently rehashed heading-only artifact passes the legacy glyph/label/link/binding checks, but the new full-paragraph gate rejects it. [Negative evidence](rehashed-omission-negative.json).
- Fresh projection integration passes 5,625 independent rational browser cases, actual desktop/mobile and in-book refinement/Reset controls, and the complete-paragraph gate.
- Existing projection artifact bindings, all seven existing damaged-copy controls, and full artifact qualification pass with the additional mandatory paragraph check.
- The original 208-page book typography still passes all 103 full statements, twelve complete sources and 176 diagram labels at minimum 10.377959 pt.
- The complete portable archive passes file hashes, CRC and link/resource validation. The [archive receipt](portable-bundle.json) records `/workspace/kenoma-print-limits-successor-portable.zip`, 1,222 files, 88,763,907 bytes, SHA-256 `be7387d0fe61d415fa0581a368d5de5a80ee865b0deabefed4d6a83493dafd6f`.

This is a narrowly derived projection review. The original main HTML/Markdown/PDF, build manifest, mechanics and proof/kernel receipts are retained byte for byte; their historical book source stays `061359eaaee4345c9a41186ee4e5f70b26cb2a8f`. The regenerated projection receipt separately records renderer source `789c079…`. No historical main-book receipt was relabeled as a newly compiled build. [Unchanged identities](unchanged-inputs.json) and affected-check logs are preserved. No fresh full Node/Python/kernel suite is claimed, and no local affected gate remains failing.

Original exact-head [CI run 37484501133](https://github.com/MrScripty/Kenoma/actions/runs/37484501133) is visible and was queried read-only: setup/install steps succeeded, and dependency compilation was still in progress at the recorded [snapshot](original-ci-snapshot.json). Its results are preserved, with no rerun or cancellation. The distinct successor branch avoids its concurrency group. No hosted success is claimed before completion; previous “no run reported yet” statements describe only the earlier lookup.

The frozen `9c4ab8b` ref/artifacts, main, PR8 and deployment path are unchanged. No PR, deployment, publication, cancellation, environment-protection or credential change is performed. Source and evidence commits use repo-local `MrScripty <TheEnvironmentGuy@protonmail.com>`.
