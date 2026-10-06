# First sliding protocol: static preparation receipt

This is a proposal for parent review, with **zero sliding steps, zero new incoming
ODE steps and zero accepted state/time advances**. Source freeze is
`03cc50f21d0a863da316f386bf3730669229fcdb`, tree
`c36cbcede60c44861658c1a1a27ce6a01f3bf6fb`. The [protocol](first-sliding-segment-protocol.md)
proposes twelve independent mass-1 continuations to absolute .263 s under the
already approved Filippov convention. It supplies no sliding execution source.
The scoped combined-incoming ACK is not execution authorization.

The [raw read-only receipt](../../data/first-sliding-segment-protocol-v1/preflight/entry-custody.json)
binds all twelve original c1c7ba3 input files and actual incoming polynomials.
Fresh localization from each original bracket achieved the proposed width 1e−12 s
and |H|1e−13 targets within the unchanged 32-bisection budget. The candidates
remain unaccepted and no state projection is performed. This reduces finite
handoff contamination on those stored polynomials; it does not independently
solve or qualify a new incoming trajectory.

| Static diagnostic | Result |
| --- | --- |
| Resolved candidate roots | 12/12 |
| Bisections | 25–29, original budget 32 |
| Maximum root bracket width | 7.450706718259426e−13 s |
| Root-time span across cells | 8.158385744749808e−9 s |
| Coarse H residual span | 1.2864871980211579e−9 |
| Refined H residual span | 2.2200991045551177e−14 |
| Maximum absolute I handoff discrepancy | 1.5171891520893155e−14 |
| Bitwise reduced-I preservation | 0/12; finite discrepancy disclosed |
| Prospective strict sign/entry checks | 12/12 pass; all unaccepted |
| Original baseline blobs unchanged | 2,066/2,066 |
| Unit tests | 13 pass |

The [derived scalar summary](../../data/first-sliding-segment-protocol-v1/preflight/diagnostic-summary.json)
records signed delta-I and delta-raw separately for every cell. Four physical and
six ledger coordinates are retained; the reduced I coordinate is reconstructed,
so its finite change must not be reported as exact continuity. The full native
handoff proposes retaining incoming I exactly, with its small finite H residual.
Parent review must explicitly resolve that disclosed numerical handoff before
execution; no offset state or reset is silently added.

Static GL8 incoming-prefix errors against all six cumulative ledger coordinates
are at most [1.75565e−11, 7.93524e−12, 6.57269e−12, 2.88358e−11,
1.03604e−11] J and 3.57829e−11 N*s. Original gates remain five 1e−5 J
component checks and 1e−7 N*s impulse. This is a prospective prefix check, not
accepted quadrature. Future reviewed execution must certify the prefix,
preserve historical ledgers, and check cumulative and entry-to-endpoint work,
impulse, constraint, tangency, normals, all 66 matched absolute-time comparisons
and all four post-entry absolute witnesses without relaxing gates.

[Tests](../../data/first-sliding-segment-protocol-v1/preflight/tests-v3.log),
[static execution log](../../data/first-sliding-segment-protocol-v1/preflight/static-entry.log),
[execution metadata](../../data/first-sliding-segment-protocol-v1/preflight/execution.json)
and [baseline preservation receipt](../../data/first-sliding-segment-protocol-v1/preflight/preservation.json)
are retained. Two report serialization failures are also preserved separately,
with their prior protocol freezes; fixes only encode NumPy scalar report values.
No tolerance, root budget, law, incoming polynomial or historical result changed.

The primary source semantics remain the reviewed single-surface construction in
[Dieci–Lopez](https://epubs.siam.org/doi/10.1137/080724599) and solution distinction in
[Cortés](https://arxiv.org/pdf/0901.3583), as applied in the
[existing local derivation](antiwindup-continuation-analysis.md). No new physical
assumption or constitutive change is introduced in this preparation.

Both raw review gaps remain explicit: the new combined result's full external
raw replay was unavailable after canceled transfer, and historical activation
raw replay remains incomplete. There is no retry or reroute. Guard sampling is
not a hidden-root exclusion theorem. No fourth-order, full incoming, sliding,
whole-arm or anatomical qualification, new trajectory render, book release,
main change or skin addition follows from this receipt. Prior trajectory renders
and failed evidence remain byte-identical. Any sign loss, additional guard or
undeclared exit must stop before acceptance under the proposed protocol.

The next authorized action is parent review of the frozen protocol and handoff;
a separate explicit authorization and frozen execution source packet are required
before sliding can run.
