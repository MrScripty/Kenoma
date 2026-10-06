# Real-domain proof progress — not yet qualified

Base is the frozen cumulative checkpoint96f2e1d4afa2d2fec3d296c8283679a61e26d9be. PR7, workflow and cumulative branches are unchanged. A separate wording correction37733d4 is on origin/education/excitation-policy-doc.

The repository's documented official flow (`education/README.md`, `tools/build_property_mathlib.py`) fetched mathlib commit c44e0c8ee63ca166450922a373c7409c5d26b00b and the exact locked package revisions. ProofWidgets source assets were bootstrapped by the existing documented script. No pin or gate was weakened. Official two-job source compilation is still running; there has been no dependency denial. Live log: /tmp/kenoma-real-mathlib-dependency.log; exec session91814. Do not interpret successful acquisition as completed compilation.

MaterialResponseReal.lean proposes five genuinely real-volume/bulk/contact/work identities with explicit assumptions. MechanicsReal.lean proposes three real force/torque/power identities. All eight remain uncompiled, and no new checked cards or book claim counts are displayed. Existing valid Int and Real proof sources are unchanged. Constitutive real-power derivatives, Gaussian derivatives/root guarantees, activation bounds, full continuous energy balances, floating-point refinement and empirical validation remain separate unfinished obligations.

The fail-closed checker first reruns the existing pinned-real checker, then compiles both proposed files with warnings-as-errors, rejects admissions/custom axiom dependencies, and emits a receipt only if every claim passes. It is not yet integrated into the book/release registry.

After the running dependency flow succeeds, from /tmp/kenoma-real-claims/education run:

```bash
python3 tools/check_real_lesson_proofs.py
LEAN=/workspace/Kenoma/education/.tools/lean-4.19.0-linux/bin/lean python3 tools/build.py
```

Fix any actual compile error before marking these sources checked. If the official dependency process fails, preserve its full log and report the exact error; do not bypass acquisition restrictions or use stale receipts. Full book/PDF/browser/artifact qualification remains pending. Temporary .tools/node_modules symlinks point to the shared existing workspace dependencies; they are untracked setup, not source modifications.

An unattended follow-up is running in exec session59850 (`continue-qualification.sh`): it waits for the original official dependency process13569, requires its `SOURCE_BUILD_COMPLETE` marker, then runs the new proof checker and an independent full-book build. It preserves failures and never reports a pending result as passed. Outputs: /tmp/kenoma-real-proofs-qualification.log, /tmp/kenoma-real-full-book.log, and /tmp/kenoma-real-followup.log. Read actual exit/results and receipts before making any claim. The official dependency process remains exec session91814.

Next learner repair requested by independent closure: Lab3 must reproduce the chapter's 12-second comparison for every supported timestep. Its current 600-step cap stops h=.01 at6s (h=.005 at3s). After this proof milestone, use a separate successor with a duration-based bound (12s requires2400 steps at the smallest supported h), responsive batch execution/pause, explicit simulated-duration/step accounting, all-sample energy/error measurement, and actual browser reproduction. Do not remove the 12-second objective or relabel the old cap.
