# Frozen e19 dependency build failure and separate successor

The frozen delivery remains e19b9bf40226352e9e94bcae801ab97c208cd31a, with tested source 3cd3c5fbf2b061058e1dc5d2305408951dd4b5ee. Its PDF, Markdown, bundle and local proof/book evidence are preserved. This successor changes dependency preparation and diagnostics only; the finite-bulk curriculum work is on a separate branch.

[Run 37369315504](https://github.com/MrScripty/Kenoma/actions/runs/37369315504), build job 111962195246, failed at 20:36:19 UTC on 2026-10-05. “Compile pinned real-proof dependencies from source” failed at `ProofWidgets.Compat`; book/proof compilation and deployment were skipped. The wrapper hid the module stderr in a runner-local file, and no failure artifact preserved it. Thus the remote log alone identifies the failing dependency, not its nested stderr. The complete fetched run log and job/step summaries are retained beside this report.

A disposable cold reproduction used the exact locked mathlib configuration, Lean 4.19.0, a pristine ProofWidgets checkout at c4919189477c3221e6a204008998b0d724f49904, and the existing pinned remaining dependencies. The same `lake --no-cache build ProofWidgets.Compat` failed in `proofwidgets/widgetJsAll` with:

```text
ProofWidgets not up-to-date. Please run `lake exe cache get` to fetch the latest ProofWidgets. If this does not work, report your issue on the Lean Zulip.
```

Mathlib's unchanged lakefile sets `errorOnBuild` for ProofWidgets. The upstream library requires JS assets even for this module target. The previously qualified local workspace had these assets; a cold no-cache dependency build does not. This is a reproduced cause consistent with the exact CI failure, rather than a recovered verbatim nested CI message.

The successor first runs the upstream pinned package's standalone `lake --reconfigure --no-cache build widgetJsAll`. It verifies its Git revision, pristine source and unchanged npm dependency lock, then re-elaborates the original mathlib configuration to restore its guard. A fresh guarded `ProofWidgets.Compat` build passes. No upstream source, proof statement, dependency pin, proof assertion, numerical tolerance or artifact gate changes. No binary release cache is used. Writable task-local npm cache fixes the separate executor's read-only default cache; that executor-specific failure is not asserted as the CI cause.

Raw negative and positive probes, the helper's cold asset receipt, a fresh four-real-claim kernel check against the frozen book source, and a bounded-tail check are retained. Failure output is limited to 40 lines/8000 characters; complete dependency logs are uploaded with `if: always()`. A build error still returns failure. The corrected remote run and downstream book/physics checks remain required before Pages publication; local cold repair is not a remote workflow pass or a deployment.
