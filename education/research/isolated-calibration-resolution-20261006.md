# Frozen isolated calibration diagnostic

This research branch starts at merged main `596df78f5cb652b4ac70917a82d8aa908b617056`, tree `8fb39d42575dc5593869315e46e80a64e828d7e3`. It adds a bounded diagnostic only. It does not alter the accepted book, browser operator, release candidate, historical audit bytes, constitutive laws, anatomy, material constants, fitted forces or deployment.

## Frozen experiment contract

The input manifest binds the three original fully activated fixed-end calibration poses and their existing authored atlas-derived P2 meshes, fibres, embedded sheets, reference-model targets and fitted stress scales. Distal/proximal cap membership remains explicit. Coordinates and all physical parameters stay fixed; no optimizer, force rematching, continuation, contact or time stepping is run. Existing local anatomy is used without downloads.

At each frozen pose, independently assemble the body energy gradient at 32, 256 and 2,048 positive points per element using the existing equations. Add the unchanged nodal sheet gradient. Compare the original 45 free modal coordinates with all 1,485 free nodal components. A twice-orthogonalized Euclidean projection onto normalized modal directions separates retained and omitted force directions without relying on arbitrary modal scaling. Its squared-norm fraction is a declared discrete force metric; it is not displacement error, continuum convergence, mixed stability or an enriched equilibrium solve.

Matched affine and rigid-motion controls, finite differences of the actual compressed-state potential and full nodal energy, exact dyadic P2 orientation signs, source hash checks and damaged-input rejection address specific numerical explanations. Constitutive components are independently evaluated in Pa and assembled in N. Force components may cancel and their norms do not establish physical causation.

The unchanged physical stationarity gate is **0.0001 N**. The historical **52–64 N** residuals are full free nodal residuals at these isolated original calibration poses. The historical **0.0173852 N** finer-quadrature residual belongs to a different coupled dense state at 0.10 s; it is preserved as a separately labeled contrast, not an isolated-fixture result.

## Reproduction

Commit the manifest, diagnostic helpers, runner and tests before running the diagnostic. The runner requires tracked source files and refuses changed inputs or an existing completed result. It writes only to `review/isolated-calibration-resolution-20261006/`.

```sh
cd education
node --test tests/isolated_calibration_diagnostic.test.mjs \
  tests/anatomical_compression_quadrature.test.mjs \
  tests/anatomical_integration_refinement.test.mjs \
  tests/anatomical_bernstein_orientation.test.mjs \
  tests/anatomical-material.test.mjs tests/anatomical-element.test.mjs
node --max-old-space-size=6144 --expose-gc tools/run-isolated-calibration-diagnostic.mjs
```

Results will bind the qualified source commit and source hashes. Successful diagnostic execution must not be described as successful full nodal equilibrium. No physiological calibration, anatomical capstone completion, global injectivity, unrestricted stability or converged solution is claimed.
