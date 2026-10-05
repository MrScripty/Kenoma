# Dense integration comparison and review evidence

The unchanged 32-point lift/release remains source-bound to the original implementation. Matplotlib 3.10.8 was added in `84cb8f4e331d668fbb2b89308b3f30870f9d2233` to fix the hosted book build. Its hosted run is https://github.com/MrScripty/Kenoma/actions/runs/37301624228; inspect that run's actual conclusion rather than inferring hosted success from these local logs.

The new experiment re-equilibrates the 0.07–0.10 s increment with 256-point body integration. It retains the exact original old state and all material, displacement, Newton and contact parameters. Fifteen Newton iterations across two frozen contact rules pass the original 0.0001 N force gate and finite geometry gates. Independent full P2 body assembly gives total incremental residual 0.0000900553 N; body gradient/energy assembly differences are at most 6.45e-12 N / 1.43e-14 J. The angle difference is 0.001299 degrees and the maximum reduced-coordinate difference is 0.12457 mm.

Compression remains explicit: minimum sampled/corner J are 0.725476/0.712631, and a near-unit global volume ratio does not prove local incompressibility. This single increment starts from a 32-point old state; it is not a self-consistent dense trajectory, quadrature/nodal convergence proof or timestep accuracy bound. Re-equilibrated bulk sensitivity remains open. The original finer release is an interrupted 22-step prefix with a 3.2884-degree matched-time difference. Finite radius, coplanar contact and continuous-motion certification remain open.

`dense-logs/` contains the raw nonlinear solve, independent replay, derivative tests, 102-test JavaScript suite, 16-test Python suite, build/PDF, browser/mobile, anatomical viewer, artifact and setup output captured before this commit. `dense-logs/logs.json` records command, exit status and raw-log digest. The execution receipt additionally binds the actual physics/tools inputs by SHA-256; the no-optimizer replay binds that receipt and its verifier. Post-commit clean-checkout logs and deliverable hashes are provided separately with the published review archive, so generated artifacts can identify the exact tested commit.

From `education/`, reproduce the focused checks with:

```sh
node --test tests/anatomical_dense_quadrature.test.mjs
node --max-old-space-size=8192 tools/verify-anatomical-dense-step.mjs
# Re-run the nonlinear comparison only when needed:
node --max-old-space-size=8192 tools/anatomical-dense-step.mjs
```

No acceptance gate or conditional formal claim is weakened. The 25 existing Lean declarations are rechecked by the book build; they do not certify floating-point integration or anatomy.
