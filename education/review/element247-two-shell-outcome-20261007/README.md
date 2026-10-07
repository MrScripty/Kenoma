# Incomplete one-shot two-shell diagnostic

**Execution result: INCOMPLETE_TWO_SHELL_DIAGNOSTIC.** Exactly one invocation
completed all 4,000 material callbacks, then failed before constructed-stage
output or terminal completion. No retry, source repair or additional material
experiment was performed. All partial/failure evidence is preserved.

My new assembler serialized the two completed records with `id` rather than
the `shell` field required by the constructor. Its complete-region inventory
assertion failed. The synthetic assembly tests did not connect those new
records to the constructor; the retained-record construction tests used the
older correct schema. The accepted independent preflight also missed this
handoff. This is a producer defect, not a physical-law or resource refusal.

## Exact frozen identities

- Preserved original result: `4b83ec5dfebae73b08c3f964aa910f65e02458e0`.
- Selective source: `7580cfccbe028329ff774971ea06a6cdbda6431b`.
- Selective preflight evidence: `10a49d0f51aac6c6be08059b7a8265d5768f0255`.
- Independent PASS and authorization/actually executed HEAD:
  `97da4bdea7d0be11fc18222221b8b551b53a8e3b`.
- The local failure-evidence commit containing this README descends directly
  from that executed HEAD. Obtain its exact ID with
  `git log -1 --format=%H -- education/review/element247-two-shell-outcome-20261007`.

Branch: `research/element247-two-shell-diagnostic-20261007`, local only.
The [protocol](../../research/element247-two-shell-20261007.md),
[preflight](../element247-two-shell-preflight-20261007/preflight.json),
[independent gate](../element247-two-shell-preflight-20261007/independent-review.json)
and [conditional one-shot authorization](../../research/element247-two-shell-authorization-20261007.json)
remain unchanged. Authorization SHA-256:
`b1e6e7f8852845982b264fa2be9d6b396c9583de097d73ddba6b1037cb7033c5`.

## Actual invocation, counts and exits

```sh
PYTHONDONTWRITEBYTECODE=1 python education/tools/launch-element247-two-shell.py --execute
```

Run ID: `ec5d414a349c4ae19695345fbea28071`.
Reserved, entered and completed callbacks are each exactly **4,000**;
planned and maximum are both 4,000, with no active batch. Both new shells
completed 2,000 callbacks each. All nineteen A55 tails were copied byte
for byte with zero additional calls.

Child exit **1**, observed launcher-worker exit **1**, public-entry executor
exit **1**. [Verbatim executor tool returns](executor-public-entry-exit.json)
retain the initial exec session and final exit result rather than just a
summary assertion. They remain producer-retained executor evidence, not a
cryptographically independent process-observer chain.

The observed worker exit was at 1,541.0219889963628 ms. External peak child
RSS was 151,576,576 bytes. Final raw output totals 1,529,071 bytes across
57 files. No resource ceiling was exceeded. The nonzero child caused
external/supervisor refusal. The raw [material incomplete receipt](../element247-two-shell-run-20261007/material/incomplete-receipt.json),
[external exit](../element247-two-shell-run-20261007/external-exit.json),
[external incomplete receipt](../element247-two-shell-run-20261007/external-incomplete.json),
[observed worker exit](../element247-two-shell-run-20261007/launcher-exit.pending.json)
and [supervisor refusal](../element247-two-shell-run-20261007/supervisor-incomplete.json)
take precedence. No completion/terminal/accepted-final file exists.

## Offline comparisons from retained complete vectors

The two complete changed-shell JSON records, 32,000 reference-weight bytes,
4,000 normalized points, nineteen copied tail records/weights and complete
13,500-point constructed rule/weight inventories survive. Per-shell
component reconstruction errors are below the unchanged 1e-8 N / 1e-9 J
gates. All 1,598 source hashes and 49 inventoried numerical output hashes
match; the outcome summary additionally inventories all 57 raw files.

The [offline analysis source](retained-vector-analysis.mjs) explicitly sets
`shell=id` **only on in-memory copies** of the two retained records. It
performs ordinary retained-vector sums and comparisons with no quadrature
generation or constitutive calls. It changes neither raw files nor frozen
producer code and does not reconstruct an execution completion receipt.
The [offline comparison artifact](offline-comparisons.json) reports changed
shells separately from constructed whole-element values. The producing
[Python arithmetic/refusal check](producer-verification.json) verifies those
values and confirms EXTERNAL_INCOMPLETE_TAKES_PRECEDENCE.

Difference sign is retained A55 minus refined T24, s1/s2 only:

| Term | Force triangle (N) | Work triangle (J) | Offline finite-rule gate |
| --- | ---: | ---: | --- |
| Matrix | 1.2510401233294284e-9 | 7.861719520368571e-14 | Pass |
| Volume | 3.4381602409538914e-7 | 2.0462431405183263e-11 | Pass |
| Passive fiber | 4.731770530952417e-13 | 1.3784035354247793e-17 | Pass |
| Active potential | 0 | 0 | Pass |
| Independently assembled total | 3.4506699020386833e-7 | 2.0541062897544185e-11 | Pass |

Force and work gates remain 1e-5 N / 5.492029235357012e-7 J. These offline
comparisons do **not** make the run complete or accepted. Whole-element
values are an offline construction; the nineteen reused tails agree by
construction and provide no new qualification evidence.

## Remaining blockers and preserved scope

The producer's record-schema handoff requires a separately reviewed repair
and a test connecting actual synthetic producer records to the constructor
before any future execution could be considered. The consumed authorization
does not permit another run. Nothing has been repaired or rerun here.

The original C55/A55 8.611662232570753e-5 N failure is unchanged. Element247,
the full sixteen-element patch and secondary197/200/203/206/246/248 remain
unresolved. Radial evidence at the earlier angular level and the coupled
chart/core comparison do not establish this candidate's accuracy. There
is no equilibrium, deformation, continuum or anatomical qualification.
Main, book, existing branches, PRs, deployment, protections and credentials
are untouched. No push, publication or merge occurred.

The [failure summary](failure-summary.json) binds raw hashes, counts, exits,
offline values and scope. The [independent post-failure review](independent-partial-review.json) passes
seven read-only checks with zero new material calls. It verifies partial
evidence and offline arithmetic while refusing terminal acceptance and
explicitly acknowledging the earlier handoff-review miss. Its exact SHA-256
is `0c639675672ba9e56874d6e750272ca9b5683c32829eb8d36a3b600cbc8d4da4`.
