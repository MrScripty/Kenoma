# One bounded whole-element247 material diagnostic

Result: **`UNRESOLVED_ELEMENT247_SHELL_INTEGRATION`**. The prescribed
five-rule, two-field invocation completed once. The frozen retained-evidence
verifier passed, but terminal46 C55/A55 fails the unchanged volume and
total-force gates. No retry or additional material experiment was performed.

Local branch: `research/element247-shell-material-run-20261007`.
Exact ancestry and authority:

- Accepted protocol/evidence: `91478ffe8e4728d4589ede1c095c764a09cbfce2`.
- Accepted runner source: `732bc660b1a92411001de88e55b251f4823189e4`.
- Independently reviewed runner evidence: `3846055c8d99b468b247fb225fb7a7945a71b9b5`.
- Frozen authorization and actually executed HEAD:
  `07aafe8b1c1ef27d212434232f4546feb27449ac`.
- The result commit containing this README descends directly from that
  authorization commit. Its ID is obtained with
  `git log -1 --format=%H -- education/review/element247-shell-run-outcome-20261007`.

The [one-shot authorization](../../research/element247-shell-execution-authorization-20261007.json)
binds the exact accepted commits, source hashes, laws, fields, rules,
budgets and gates. Authorization SHA-256:
`2a05485e9d1d68d7151cf72935746a98b9e9e17e9f01ae56bed74eb2bf3648d6`.
Accepted runtime-preflight SHA-256:
`65c370e813e74aa90758f9792a99814648f9c0885fbfc58f1fda2df7062281ba`.

The invocation was:

```sh
PYTHONDONTWRITEBYTECODE=1 python education/tools/launch-element247-shell.py --execute
```

The public entry, supervised launcher worker and material child each exited
0. Run ID: `8845e700070c42838c6bf68ea008d30c`. Existing output now prevents
another invocation. The authorization is consumed; do not remove the run
directory or invoke the launcher again.

## Physical comparisons

Each comparison checks matrix, volume, passive fiber, active potential and
independently assembled total over all original shells, the 21 comparison
regions, local nodes and all 585 scattered nodes, including held nodes.
The force gate is 1e-5 N; the directional-work gate is
5.492029235357012e-7 J. Both signed aggregate and region-triangle bounds
must pass. Below are the total term's triangle bounds; pass status requires
every component and total to pass.

| Field | Required pair | Total force triangle (N) | Total work triangle (J) | All terms |
| --- | --- | ---: | ---: | --- |
| control45 | C55/R55 | 5.613474430341103e-11 | 3.640461940141889e-15 | Pass |
| control45 | C55/A55 | 1.2825659369687512e-8 | 3.8914378188831894e-13 | Pass |
| control45 | A55/X55 | 1.4748685038020776e-10 | 4.29966524549141e-15 | Pass |
| terminal46 | C55/R55 | 1.3061503815079538e-7 | 8.808037628219098e-12 | Pass |
| terminal46 | C55/A55 | **8.611662232570753e-5** | 5.702594362077475e-9 | **Fail: volume, total force** |
| terminal46 | A55/X55 | 2.3009154424176776e-6 | 1.3700766754406926e-10 | Pass |

The failed C55/A55 volume signed aggregate and triangle are both
8.581686034488093e-5 N; total is 8.611662232570753e-5 N, approximately
8.612 times the force gate. The total peak is global node575, component1,
a free node. Matrix, passive fiber and active potential pass this pair.
All required work bounds pass. These are finite-rule agreement results,
not an independent continuum-error bound.

The informational C44/C55 pair passes for control45. It fails terminal46
volume and total force, with total aggregate/triangle
0.001984225063769406 N and work triangle 1.3572923512260846e-7 J; that
informational failure does not change the prescribed required-pair result.

## Completion and resources

Reserved, entered and completed callback counts are each exactly **62,438**,
equal to the frozen plan and below the 62,500 ceiling. Ten rule/field stages
completed; no batch remains active. There were zero new fields, optimizer
trials, refits or nonlinear solves. All source laws, parameters, activation,
reference weights and frozen state/direction arrays remain unchanged.

The observed launcher exit occurred at 9,443.92012499884 ms from the
preauthorization main-entry clock. External peak material-child RSS was
325,885,952 bytes, below 2 GiB. Node old-space remained configured at
1,024 MiB. Final raw combined output is 5,057,671 bytes across 455 files,
below 64 MiB. No incomplete/failure receipt exists. The final acceptance
was published through the verified supervisor.

All reconstruction gates passed: 1e-8 N / 1e-9 J. Across stage receipts,
the maximum component force difference is 7.105427357601002e-14 N,
component energy difference is 5.551115123125783e-17 J, shell-to-element
force difference is 7.105427357601002e-15 N and element-to-global difference
is zero. Constitutive stress-component reconstruction error is zero.

## Retained evidence

- [Complete comparison vectors](../element247-shell-run-20261007/material/shell-vector-comparisons.json).
- [Material completion](../element247-shell-run-20261007/material/completion-receipt.json).
- [Terminal completion](../element247-shell-run-20261007/material/terminal-completion.json).
- [External exit](../element247-shell-run-20261007/external-exit.json).
- [External final](../element247-shell-run-20261007/external-final.json).
- [Observed launcher acceptance](../element247-shell-run-20261007/launcher-exit.json).
- [Execution log](../element247-shell-run-20261007/execute.log).
- [Producer retained-evidence verification](verification.json).
- [Summary, all comparison metrics, energies, reconstruction and raw-file hashes](result-summary.json).

The verifier checked 446 inventoried numerical outputs and 1,123 source
hashes, with **zero additional material calls**. This is producer
verification; independent review of the actual diagnostic remains pending.
All original shell files, physical weights, normalized rules, local and
585-node gradients, component energies and directional derivatives are
retained without changing the raw run files.

## Remaining scope

The old `UNRESOLVED_FIXED_PATCH_INTEGRATION` result remains. All sixteen
incident elements and secondary elements 197/200/203/206/246/248 remain
unresolved, regardless of element247's method comparisons. A55/X55 changes
chart and core depth together; 21-region triangles allow within-region and
within-shell cancellation; work gates follow algebraically from force
triangles; reference moments cover barycentric degree two, not every
quadratic Cartesian function. SIGKILL retention remains limited to already
durable files. There is no equilibrium, deformation, displacement-resolution,
global integration, continuum or anatomical completion claim.

Main, book, existing branches, PRs, deployment, protections and credentials
are unchanged. The authorization, raw run and outcomes are local only; no
public write, push, PR or merge was performed.
