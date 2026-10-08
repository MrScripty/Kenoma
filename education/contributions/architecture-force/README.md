# Architecture to force research contribution

This additive, private-review contribution addresses the architecture-to-force bookkeeping gap after the nonuniform-volume lesson. It does not change the anatomical solver or publish a new capstone.

## Read and run

- Read `chapter.md` for the derivation, primary sources, and unresolved anatomical gates.
- Serve this folder with an ordinary local static HTTP server and open `index.html` for the analytic lab. There are no remote assets, dependencies, trackers, or network data requests.
- Run `node --test model.test.mjs` for the standalone scalar contracts.
- In the full Kenoma checkout, run `node --test repo-contract.test.mjs` to compare the lesson with `education/web/anatomical-material.mjs`. For a materialized pinned review, set `KENOMA_MATERIAL_MODULE` to the unchanged operator's absolute path.
- Run `python check_algebra.py` with SymPy available for seven symbolic identities. This is not a Lean check.
- `ArchitectureForce.lean` supplies six Real-domain contracts, including material-cut force invariance and area-weighted aggregation. All six compiled during private review under Lean 4.19.0 and mathlib commit `c44e0c8ee63ca166450922a373c7409c5d26b00b`, with warnings treated as errors. Run `python check_lean.py --mathlib PATH --lean-bin PATH --output REVIEW_DIRECTORY` for a fresh source-hashed receipt. The checker verifies dependency pins, pristine source and allowed kernel axioms before reporting success.

## Scope

All numerical examples are authored, including fibre counts, areas, nominal stresses, packing fraction and control ranges. Public papers are used to justify distinctions and required provenance, not to calibrate these examples. Static force balance is necessary but does not prove a compatible deformation or solve an anatomical continuum.

The current fitted 3.60–20.38 MPa model coefficients remain distinct from measured specific tension. Failed full-nodal stationarity and local-compression evidence remain untouched. No saved trajectory, mixed-volume numerical campaign, calibration refit, acquisition, deployment or external upload is part of this contribution.

## Integration boundary

The private overlay adds only this directory. It does not edit the 13 existing Lean sources, their 109 checked declarations (including the original 103), source anatomy references, book order, global build tooling or release status. The additional six checked contracts belong to this contribution only. Book registration remains pending independent review and integration. A future reviewed integration may insert this lesson between nonuniform kinematics and constitutive calibration, but must not increase formal proof counts from the SymPy result. No complete-book or hosted build is claimed.

## Private review status

Twelve Node tests pass, including direct comparison with the unchanged pinned repository material operator. Seven symbolic checks pass separately. Six Lean contracts pass the pinned kernel check. The original private-review browser attempt was blocked by the supported cloud browser's refusal of the local preview; that local attempt established no rendering or real-control pass.

Subsequently, the bounded hosted contribution checks in [run 37743673184](https://github.com/MrScripty/Kenoma/actions/runs/37743673184) passed at exact commit `143ac8863cd8a5be736e2c455cac9605c2e20a1f`. The repository test `education/tests/architecture_force_browser.py` passed real Chromium controls at 1280×1000 desktop and 393×852 mobile sizes plus the no-JavaScript fallback. The recorded agent visual review inspected all five JPEG quality-85 captures and passed the bounded analytic lab. The automated receipt's `pending human inspection` marker remains unchanged; owner release review, full-book integration and anatomical acceptance remain separate gates. Full-book build and deployment were skipped. This evidence applies to the named commit; later source heads require their own hosted qualification.

Source code and prose are the proposed Git changes. Browser capture receipts and generated outputs remain outside this directory. No PDF/PNG/simulation output is added to Git. This lesson has no distribution illustrations; if later illustrations are needed, follow the repository's JPEG quality-85 distribution rule.
