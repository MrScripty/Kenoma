# Lateral interface transfer — standalone contribution

An original passive discrete small-strain lab after architecture-force PR13 at `6a72e01b66e4d5724c8d6c74f98cf38a90b21e31`. Only this additive directory changes. Two localized interfaces connect guided axial macro-elements; this is not distributed tissue, actual human fibre geometry or anatomical calibration. Read `chapter.md` and `sources.json` for the exact contract and measured/computational distinctions.

All moduli, geometry, presets and ranges are illustrative engineering inputs. E is a reduced axial modulus. The model omits transverse/rotational DOFs and interface normal/moment physics. Zero interfaces are admitted; perfect ties occur only as a limit. The signed external forces are opposite even though the two end-pull scalars agree.

## Bounded reproduction

Run the checking/build CLI from this directory in a **Git source checkout**, with Python/SymPy/ReportLab/PyMuPDF/Playwright and pinned Lean/mathlib already available. No command installs them. The portable ZIP itself is a static site that can be extracted and served without Git; reproducing source checks/builds requires the source checkout, rather than running the CLI inside the extracted output bundle. Choose explicit, dedicated outside-checkout outputs; the guard protects every registered source worktree and rejects ancestor overlap, symlink and hardlink aliases. Set `KENOMA_LATERAL_OUTPUT_ROOT` to restrict output to an approved private root. In the author environment that root is `/workspace/Kenoma-output-routing-20261008/lateral-interface-transfer/`. Other installations use their own root. The checker alone admits a guarded nonempty directory for its warm-wrapper transcript; other writers require a fresh directory. This assumes no concurrent destination replacement and does not modify global output rules.

```sh
node --test model.test.mjs
python3 check_algebra.py --output /workspace/Kenoma-output-routing-20261008/lateral-interface-transfer/audit
python3 check_lean.py --mathlib PINNED_MATHLIB --lean-bin PINNED_LEAN_BIN --output /workspace/Kenoma-output-routing-20261008/lateral-interface-transfer/proofs
python3 build.py --output /workspace/Kenoma-output-routing-20261008/lateral-interface-transfer/site --audit RECEIPT --proof-receipt RECEIPT
python3 browser.py --site SITE --output /workspace/Kenoma-output-routing-20261008/lateral-interface-transfer/browser
python3 check_pdf.py --site SITE --output /workspace/Kenoma-output-routing-20261008/lateral-interface-transfer/print
python3 qualification_negatives.py --site SITE --audit RECEIPT --proof-receipt RECEIPT --output /workspace/Kenoma-output-routing-20261008/lateral-interface-transfer/qualification-negatives
```

`check_algebra.py` performs exactly 24 rational closed-form comparisons and six separate symbolic identity checks; no optimizer or trajectory. `check_lean.py` compiles only six new Real declarations against pristine pinned Lean 4.19.0/mathlib and never builds or downloads dependencies. A missing cache is a blocker, not permission to rebuild it. `build.py` requires an actual fresh proof receipt for checked status and produces a portable static site/PDF with full statements and exact Lean source. Source HTML remains explicit about unqualified proof status until bound by a build receipt. No-JavaScript default results are readable.

`browser.py` normally uses the browser already installed for Playwright. If that executable is unavailable, pass `--chromium /absolute/path/to/an/already/installed/chromium`; the receipt records the actual executable and browser version. The script never downloads a browser.

The six Real claims concern this discrete algebra, not certified differentiation, continuum equilibrium, floating-point execution or biology. No full-book/global test, anatomical solve, fitted coefficient, held campaign, dependency install, workflow dispatch, deployment or external upload belongs to this contribution. Existing proof/source/data/negative-evidence files are preserved. Independent source and appearance review and parent publication decisions remain separate gates.

`negative_controls.py` damages two actual private model copies and requires the rational audit to reject them. `guard_tests.py` checks source/ancestor overlap, symlink/hardlink aliases and receipt overwrite refusal. After a genuine portable build, `qualification_negatives.py` damages actual PDF copies (9 pt text, missing exact source, missing vector-diagram label) and a copied genuine kernel receipt (wrong source hash), and requires their corresponding gates to reject them. These do not alter the original sources or successful artifacts.

Source code and original prose use the repository's Apache-2.0 licence. Primary papers are cited, not copied as figures or redistributed datasets. Generated PDF/JPEG/ZIP/receipt outputs remain outside Git. Distribution screenshots use JPEG quality 85.
