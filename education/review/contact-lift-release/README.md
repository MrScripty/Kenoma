# Completed contact lift/release review evidence

The committed `logs/` preserve the completed implementation's local execution and validation output. `logs.json` records commands, working directory, timestamps and exact log digests. These are captured pre-commit logs, not a claim that a remote workflow passed. Fresh exact-commit reruns are delivered separately.

The source-bound replay receipts are in `../../data/anatomical-arm-v1/audit/`: `contact-lift-release-recheck.json`, `contact-fine-release-recheck.json`, `contact-cold-start-recheck.json` and `arm-rejected-step-recheck.json`. Their execution inputs, saved material rules and operator snapshots are committed alongside them. Each verifier checks its recorded input/source hashes and freshly evaluates coordinates without optimizing. The completed primary run has 15 accepted steps; the optional finer comparison is explicitly interrupted after 22 of 27 requested steps.

## Limits retained for review

- Reduced Galerkin equilibrium and finite triangle/axial-line audits, not full nodal or continuous-motion convergence.
- Minimum sampled body determinant is 0.73754; local compression remains substantial.
- The interrupted finer-release comparison differs by up to 3.2884 degrees at matched times. No timestep convergence rate is established.
- The nonlinear work defect reaches 2.4340 J. It includes quasistatic relaxation and nonlinear sampling; it is not forced to vanish.
- Authored material scales, fixed tendon routing, omitted finite tendon radius, coplanar cases and source articulation gaps remain explicit.

From `education/`, replay with `node tools/verify-anatomical-contact-trajectory.mjs` and `node tools/verify-anatomical-release-prefix.mjs`. These can take several minutes on a CPU. See `../../README.md` for build prerequisites and browser/PDF checks. No force push, merge or Pages deployment is needed to review this work.
