# Shell retention and fail-closed completion successor

This repair descends from frozen runner/evidence
**`33fa964ff8d11e96a28f82a0d59c6d2e262b6a93`**, whose runner source is
`6e7ee1e078db42bf2ed010c3725ab670eb9ee60c`. The predecessor branch, source and
all receipts remain unchanged. Its independently identified execution
blockers are repaired here; its passing 45-test receipt did not establish
correctness of the uncovered failure cases. Parent thread
`01a103c3-a2e6-7606-8c1e-06987ac710f1` authorized only a minimal successor,
focused failure controls and frozen review evidence. **Specimen material
execution remains zero and unauthorized.**

## Completed shell and weight retention

The completed shell's vectors/energies/count are now snapshotted immediately
after the unchanged counted assembler returns, before derivative, scatter,
component reconstruction or output operations. All those completed-shell
operations share one protected catch. A reconstruction failure therefore
retains the complete physical weights through the existing 64 KiB emergency
weight allowance and the vectors through the existing 1 MiB failure receipt.

An existing normal weight filename is reused only if it is a regular file
whose exact byte count and SHA-256 match the completed in-memory weights.
A truncated file or a same-length damaged file remains untouched as failure
evidence while a separate full emergency weight file is written and verified.
The failure context records the retained filename and whether its bytes
were actually verified complete. If emergency retention itself cannot be
written, that is explicit and persisted-weight completeness is false; the
computed shell data and hash remain in the failure context when writable.
No write failure is converted into a successful stage or retried material
callback. Physical calculations and source weight enumeration are unchanged.

Focused synthetic controls cover component reconstruction failure before
normal output, truncated normal writes, same-length corruption, preserved
complete normal weights, and unavailable emergency weight writes. They
verify actual bytes, vectors and counters, not merely filename existence.

## Actual launcher outcome and acceptance publication

The external launcher worker now writes only a provisional
`external-final.pending.json`. A separate supervisor waits for that launcher's
**actual process exit**, records it in `launcher-exit.pending.json`, and
requires exit 0 with no supervisor refusal or existing incomplete evidence.
The material child still has its own recorded exit, terminal file and final
stdout hash chain. Both material-child and launcher outcomes are required.

The supervisor fsyncs its launcher log and a staged enriched acceptance
receipt, validates the candidate/source/run identity and hashes, and checks
wall/output bounds before publication. It then atomically renames the
external candidate and publishes `launcher-exit.json` **last**. No checks,
writes or logging follow successful publication; the public entry point
exits directly. Failure before the last publication leaves the required
launcher acceptance absent, even if an external-final file has already
been published. A failed launcher exit remains independently observed, so
failure-marker write errors cannot turn it into completion.

The reusable verifier requires the published observed-launcher record,
its zero exit, source/run/budget identity, launcher-log hash and external-
final hash. It rejects pending-only files, nonzero observed exits, failed
or incomplete supervision, and missing acceptance even when every earlier
material/child hash is otherwise valid. Pending failures take precedence.
Real small synthetic processes exercise worker exit 0, nonzero launcher
exit, late checks with unwritable failure receipts, and partial acceptance
publication with an unwritable refusal record. No material law is called.

For watchdog termination, the supervisor kills the worker's process group;
the material child inherits that group. The group is killed even when the
launcher has already exited, so the child cannot remain orphaned and
continue material work after the supervising watchdog stops it. A process
that is forcibly terminated cannot run its in-process failure catch. The
retention guarantee is therefore deliberately narrower: **only files
already durably written before SIGKILL are retained**. No current-shell
RAM vectors/weights/counters are promised on SIGKILL. The precise actual
count within an interrupted shell may be unknown; that run cannot qualify.
The SIGKILL control verifies an earlier fsynced synthetic shell file survives
while current in-memory data is not claimed to have been saved. This
qualification supersedes the predecessor's overbroad full-preservation
wording; no new checkpoint or extra specimen evaluation is introduced.

## RSS, arithmetic order and timing

A live-child RSS read now fails closed on missing, unreadable or malformed
resident-memory information. Zero is returned only for a positively observed
zombie/exited address space, not as a substitute for unavailable live RSS.
The same 2 GiB process bound and sampling cadence remain.

The Python verifier's float reductions are pinned to the producer's explicit
IEEE binary64 order. Stored shell/stage directional work sums three
coordinates and then nodes, matching JavaScript's nested reductions.
Comparison work sums flat node/component order, matching the comparison
helper's sequential `+=`. Component force/energy reconstruction and
direction L1 norm also use explicit sequential `+=`. Python's builtin
floating `sum` is avoided because Python 3.12 can use a different algorithm.
All existing arithmetic/reconstruction tolerances and force/work gates
remain unchanged. A nonzero cancellation-heavy fixture is emitted by the
actual JavaScript comparison helper and independently read by Python; it
contains 2^54-scale opposing components, finite nonzero 585-node scatters and
nonzero finite comparison differences. It is invented test evidence and
does not purport to be specimen data.

The authoritative 180-second external interval starts at public Python
`main` entry **before authorization, source and preflight checks**, and is
shared with the worker and supervisor. It includes those checks, subsequent
process startup, material child execution, launcher exit and the final
supervisor prepublication resource check. Initial Python interpreter/module
import occurs before `main` entry and is not included. The final atomic
publication follows the last check; no later fallible resource check can
leave a valid acceptance chain after returning failure. This is the precise
recorded scope, not a claim about arbitrary OS shutdown latency.

## Frozen gates and independent review

The planned/material ceiling remains 62,438/62,500 callbacks, with separate
reserved/entered/completed counters; 180 s, 1024 MiB Node old-space, 2 GiB RSS and
64 MiB combined output. The 2 MiB emergency reserve and 64 KiB external/weight
and 1 MiB child-failure record limits remain. Reconstruction stays 1e-8 N/
1e-9 J; integration stays 1e-5 N/5.492029235357012e-7 J; domain guards stay
J>1e-6 and reference Jacobian>1e-15. Both original fields, all material
parameters/activation, recipes, reference geometry, independent totals,
original shells and all 585-node scatters are unchanged.

The repair manifest binds unchanged predecessor files, frozen predecessor
versions of the seven modified files, and current successor source hashes.
New runner/launcher/verifier references point to this successor's separate
preflight. The predecessor runtime receipt is preserved and cannot authorize
the repaired source. The one-shot material authorization record remains
absent, and both material entry points still refuse before creating output.

The successor preflight runs **58 tests**: 28 JavaScript and 30 Python. After the
source commit is frozen:

```sh
node --max-old-space-size=1024 education/tools/preflight-element247-shell-retention.mjs
```

Independent replay can use `--output /tmp/kenoma-shell-retention-review-FRESH`.
The [successor receipt](../review/element247-shell-retention-20261007/runtime-preflight.json)
and both logs bind the exact source and outcomes. The
[review artifact README](../review/element247-shell-retention-20261007/README.md)
records the source/evidence commits and receipt hash. This is producer
verification; independent successor review and separate material execution
authorization remain pending.

All prior limits remain: A55/X55 changes chart and core depth together;
21-region triangles permit within-region/shell cancellation; work gates
follow algebraically from force triangles; reference moment coverage is
barycentric degree 2, not every quadratic Cartesian function. The old
`UNRESOLVED_FIXED_PATCH_INTEGRATION`, secondary 197/200/203/206/246/248 and
all 16 incident elements remain explicit. There is no global integration,
equilibrium, displacement-resolution, continuum or anatomical completion
claim. Main, book, old branches, PRs, deployment, protections and credentials
are untouched; no new dependency or build-time download is used.
