# Static sliding-policy proposal receipt

The [held proposal](sliding-constraint-policy-proposal.md) distinguishes internal
trial-stage admissibility from accepted motion. Its primary option retains full
I integration and records internal predictor H defects, while retaining the
original constraint gate on candidate endpoints and accepted-polynomial
guard/GL8/grid/witness checks. This is explicitly a stage-policy change. No
revised policy has been implemented or executed, and the completed matrix is
still nine of twelve and unqualified.

Source/diagnosis freeze: `a901dd4e03f6c061521494eb135f8e07d3347b6b`,
tree `963af93d51610e89acfb33c433d65c275e051030`.
Baseline: `455641c0aa9b4a9ad4b68e50fc1b6f5746180226`,
tree `8dfc931e72a58730ac61b8ea34a80a0abe2bb4bf`.

| Evidence | Result |
| --- | --- |
| [Archived-state calculation](../../data/sliding-constraint-policy-proposal-v1/diagnosis.log) | Three bitwise Euler matches; zero new ODE steps or accepted states |
| [Raw curvature receipt](../../data/sliding-constraint-policy-proposal-v1/predictor-curvature-diagnosis.json) | Maximum measured-minus-curvature remainder 1.70771874213e−15 |
| [Original gate controls](../../data/sliding-constraint-policy-proposal-v1/unchanged-gate-tests.log) | All fourteen pass without modifying source or tests |
| [Custody and diagnostic checks](../../data/sliding-constraint-policy-proposal-v1/verification.log) | All 2,131 baseline blobs byte-identical; six negative controls rejected |
| [Verification metadata](../../data/sliding-constraint-policy-proposal-v1/verification.json) | Input/source bindings, exact rollback, held scope and older review gaps |
| [PNG figure](../../data/sliding-constraint-policy-proposal-v1/archived-predictor-defects.png) / [SVG](../../data/sliding-constraint-policy-proposal-v1/archived-predictor-defects.svg) | 1,800×990 PNG visually inspected; archived unaccepted predictors only |

Commands used, with OPENBLAS_NUM_THREADS=1 and PYTHONDONTWRITEBYTECODE=1:

```
python3 education/tools/diagnose_sliding_predictor_curvature.py
python3 education/tests/first_sliding_segment.py
python3 education/tools/render_sliding_predictor_diagnosis.py
python3 education/tools/verify_sliding_policy_proposal.py
```

The render additionally used MPLCONFIGDIR=/tmp/kenoma-first-slide-mpl and
XDG_CACHE_HOME=/tmp/kenoma-first-slide-cache. The diagnostic uses analytic BPoly
curvature and static quadrature on old failed states; these are not ODE steps.
No equation or anatomy assumption changed. Existing book and Lean claims are
untouched. The fresh independent first-sliding raw ACK does not close either
older combined or historical activation external raw-review gap.

The bounded next step is independent review of the proposed numerical auxiliary
field and role table, followed by explicit authorization and a separately frozen
execution branch. Endpoint/dense-curve success is unknown. No revised-policy
execution is authorized by this receipt, and no book adoption, merge, publication,
download retry or anatomical-envelope qualification follows from it.
