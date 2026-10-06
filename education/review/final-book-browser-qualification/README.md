# Fresh browser qualification of the 53-card integrated build

The isolated checkout is `65b2cb56d495114973b47402532499a413cf302c`.
The complete static build was copied from the parent's stable final build at
`283e0adc51473e95a5cbff46b6a40c87fdd166c5`; the subsequent source revision
changes only the CI diagnostics directory. Every source input declared by
the actual build manifest matches this checkout. `build-binding.json` binds
the HTML, production app, manifest, and all six test files by SHA-256.

Commands, from `education`, each with its own log in this directory:

```sh
python3 tests/browser.py
python3 tests/mobile_startup.py
python3 tests/anatomical_inspection.py
python3 tests/coupled_inspection.py
python3 tests/anatomical_arm_inspection.py
python3 tests/worker_lifecycle.py
```

Task-owned earlier receipts and screenshot directories were removed from the
isolated copy before running. No 42-card browser receipt was reused or rebound.
Production source, equations, calibration, acceptance limits, and test assertions
were unchanged. The parent's coordinated Gaussian work assertion correction is
already part of this exact checkout.

The mobile-startup, anatomy-inspection, coupled-inspection, anatomical-arm,
and worker-lifecycle checks passed. The actual-arm test qualifies rest/control
behavior, including the 7.035136052391169e-5 N rest residual, preservation during
mass/release edits, exact reset, and cancellation of an in-flight solve. It
does not execute or qualify an anatomical lifting trajectory. The worker test
uses injected held-step/error events and synthetic unchanged-state replies
for its timer assertions; native initialization/reset is exercised.

Actual screenshots inspected: mobile anatomy source mesh in oblique view,
mobile coupled fixture after loading, and mobile anatomical-arm rest. Mobile
startup verifies real composited geometry and actual WebGL context loss/retry.
Viewport and touch emulation are not physical-phone evidence.

All six fresh receipt/screenshot sets were copied back to the parent's dist
only after verifying matching executable bytes and test files. The parent
owns the final artifact, package, review, and publication gates.

The whole-book run also passed: 53 actual proof cards, local links/assets,
real desktop/mobile WebGL controls, every embedded teaching-control case,
current state/release/export behavior, spoken summaries, atlas keyboard
controls, mobile overflow, and no-WebGL/no-JavaScript alternatives. See
`book/receipt.json` and `browser.log`. Its exact receipt and each new or
changed QA output were copied back after checking both builds' complete
executable maps and the exact browser test bytes again. `build-binding.json`
records the root handoff hashes. All six requested checks passed.

The final 53-card Lab7 active-shape-off screenshot was also inspected: actual
q=90° and activation a=.6 are retained with the shape ablation selected;
solver approximation and residual readouts remain explicit.
