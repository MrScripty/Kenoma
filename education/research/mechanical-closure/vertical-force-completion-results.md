# Completion and mode-label successor: independent review handoff

The successor rejects the reviewer's truncated-replay false full qualification and corrects force-target labels in bypass modes. The original `765ce8c4e9c969a81bb0c4261484ad59c5c0c906` packet, checker, HTML, raw histories, failed cases and all 148 bindings remain byte-identical, as do all 1707 files tracked at that commit. This branch adds separate checker/UI/test files and a separate evidence directory. No physics, gains, tolerances, event mechanics or antiwindup continuation changed.

Branch `education/force-qualification-completion`. Tested source `359182410f0ca964ab218798ecb41eafbf702dcd`, tree `eef1e79285134c4e4e378f277f37d6fcb0b8eb17`. The final evidence commit binds this source snapshot and all deliverables.

## Exact checker repair

[Completion-aware checker](../../tools/audit_vertical_force_completion.py) requires coarse RK4, fine RK4, DOP853 and Radau. Every required method must have a failure report with no failure, a finite accepted time at the declared protocol endpoint, and a finite strictly increasing history from zero whose last row agrees with that accepted time. Initial conditions/protocol must agree across methods. Each fine/other comparison must contain every declared 1 ms grid timestamp from zero through the endpoint, plus the endpoint itself, and pass the original state/force/event budgets. The 1e−9 s metadata precision follows the original round(t,9) matcher; no ODE or physical/event tolerance changes.

Declared endpoints come from the unchanged protocol implementation: .30 s, or .15 s for descending comparisons. There is **no declared earlier terminal event**. Armed brake crossings are intermediate phase changes and cannot replace the final endpoint. A future early terminal criterion would require its own explicit protocol and consistent verification across required methods.

`compare().passed` now means full comparison qualification. `prefix_passed` is separate, requires every grid timestamp through the common accepted horizon and the original numerical gates, and compares only saved events within that common interval. `qualify()` requires all four methods and returns `full`, `prefix-only`, or `unqualified`. The audit additionally rechecks original force/work/momentum gates and accepted-state retention before assigning case qualification. Its aggregate `passed` means the reported full/prefix checks pass; `full_trajectory` and `full_presets` are the explicit completion claims.

The original numerical results remain ten full trajectories and two prefixes (`high`, `mass-1`). This recheck evaluates all 48 unchanged raw histories and binds their hashes plus `cases.json`, the checker, original mechanics source, protocol and source curves. Original mode/stability evidence remains preserved.

## Negative controls

[Raw controls](../../data/vertical-force-completion-v1/review/completion-negative-controls.json) and [test log](../../data/vertical-force-completion-v1/review/completion-test-run.log) contain nine passing unit tests and fifteen control records. The actual frozen old checker falsely accepts baseline DOP853 truncated to .009 s; the old primary-only full flag is also true. The new comparison rejects full qualification and identifies the valid common prefix. The truncated input is saved separately.

Additional controls reject a failure in each of the four methods, a missing endpoint row in each method, missing accepted-time metadata, a missing required method, changed initial conditions and a sparse three-point common history (another old false acceptance). A pulse history stopped after its genuine brake crossing cannot claim full completion. Positive controls retain the ten completed cases and two stopped prefixes. Raw old failures are demonstrated, not overwritten or retrospectively relabeled.

## Exact presentation repair

[Mode metadata wrapper](../../web/vertical-force-mode-aware.js) delegates all integration and physical calculations to the unchanged original model. It changes presentation metadata only: target/capacity applicability, floor-drive/fixed-activation mode, inactive raw PI/error signals and inactive saturation labels. The separate [HTML template](../../web/vertical-force-completion.template.html) displays bypassed targets, explicit floor drive, and PI-only target curves. Capacity warnings and PI saturation labels apply only when the controller is active. Subtitle and accessible force-chart labels follow the same rule. A selected fixed fixture bypasses the target; its companion PI uses that target and reports a stopped companion if applicable.

Four [model checks](../../data/vertical-force-completion-v1/review/mode-model-check.json) establish exact equality of all eleven state/diagnostic values between release 0 N and 150 N, and between fixed-activation wrapper/base trajectories. Dormant raw PI clipping cannot produce a saturation claim; active PI retains those semantics.

Five [real browser checks](../../data/vertical-force-completion-v1/review/mode-browser-check.json) exercise custom release 150 N versus 0 N, release's earlier actual PI stage, fixed activation 0/150 N with no target line/capacity/saturation claim, active PI capacity warnings and 360px rendering. No JavaScript errors occurred. Desktop release/fixed and mobile PNGs are saved.

Open the [self-contained successor browser](../../data/vertical-force-completion-v1/review/vertical-force-lab.html). It requires no network. [Completion recheck](../../data/vertical-force-completion-v1/review/completion-validation.json), [execution commands](../../data/vertical-force-completion-v1/review/execution.json), [preservation receipt](../../data/vertical-force-completion-v1/review/preservation-check.json) and the new packet manifest bind the exact sources, inputs, raw logs and renders. This is a review successor, not a book/site release. High/mass-1 continuation and whole-arm convergence remain unqualified; neither is extended by this repair.
