# Local Euler defect: fresh kernel receipt

Ten real scalar declarations in [EulerConstraintDefect.lean](../../proofs/EulerConstraintDefect.lean)
compiled afresh with pinned Lean 4.19.0, warnings treated as errors, and the
existing pinned mathlib/dependency tree. The
[actual compiler transcript](../../data/euler-constraint-defect-proofs-v1/review/lean-check.log)
reports only propext, Classical.choice and Quot.sound for all ten declarations.
The [kernel receipt](../../data/euler-constraint-defect-proofs-v1/review/kernel-check.json)
binds exact statements, source/claims/checker/log hashes, compiler/lake binaries,
the mathlib lock and every Git dependency revision. No admission, custom axiom,
native_decide or unchecked execution is used.

Source freeze: `07a200674a1ee4911d4e7fdb4651eb221e79b5f2`,
tree `2d92d03826b4c142d35894f41613f45c091c5269`.

The [scope note](euler-constraint-defect-proofs.md) distinguishes the exact
arbitrary-function defect identity, supplied-slope symbolic normal cancellation,
conditional pointwise remainder bound and explicit quadratic example. No
derivative/C2 property of the actual tendon kernel is proved. The results do
not establish numerical convergence or accepted trajectory validity.

[Seven receipt-audit controls](../../data/euler-constraint-defect-proofs-v1/audit-tests.log)
pass. The [packet verification](../../data/euler-constraint-defect-proofs-v1/verification.log)
confirms all 2,090 baseline blobs remain byte-identical, source freeze and actual
compiler reports match, external committed diagnosis/proposal bindings hold, and
the held policy, numerical result and prior branch tips remain unchanged.
The first failed compile (unavailable optional tactic import) and successful
preliminary compile remain in the [attempt manifest](../../data/euler-constraint-defect-proofs-v1/attempts/manifest.json)
with their exact sources/logs. No dependency download or build was performed.

Commands, with OPENBLAS_NUM_THREADS=1 and PYTHONDONTWRITEBYTECODE=1:

```
python3 education/tools/check_euler_constraint_defect_proofs.py --tools /workspace/Kenoma/education/.tools --freeze-commit 07a200674a1ee4911d4e7fdb4651eb221e79b5f2
python3 education/tests/euler_constraint_defect_proof_audit.py
python3 education/tools/verify_euler_constraint_defect_packet.py
```

Zero ODE steps, new accepted states or book receipts were added. No book/main
change, numerical-policy execution, merge or production adoption follows from
the proof. Older external raw-review gaps and anatomical convergence limitations
remain unresolved. No new trajectory or render is produced in this proof lane.
