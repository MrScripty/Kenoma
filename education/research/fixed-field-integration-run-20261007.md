# Runtime enforcement and one authorized fixed-field integration invocation

Base `da435ea4595b4f1cb23ab1a0815f21574288d41a`; preserve its reviewed [protocol](fixed-field-integration-protocol-20261007.md), recipes, states, direction, criteria and structural receipt. Parent thread `01a103c3-a2e6-7606-8c1e-06987ac710f1` authorized implementing the missing runner and **one** assembly invocation, conditional on frozen source and passing runtime preflight. This document records that authorization; it does not alter the earlier protocol's historical `executionAuthorized:false` manifest.

The new run manifest binds all89 prior source/protocol/evidence identities and the new runtime files. The runner accepts only `--execute`, no user-selected recipes, states, thresholds or budgets. It requires a source-bound successful runtime receipt, tracked clean source and a new output directory. Existing invocation evidence is never overwritten. No retry, new field/probe, extra mode, optimizer, material change, bulk increase or refit is permitted.

## Enforcement beyond reservations

Reservations, actual constitutive callback entries, and successfully returned callbacks are separate counters. Every point calls the unchanged `stressComponents` adapter once, whose first operation is the unchanged `muscleMaterial` call. Callback entry increments actual count before invocation; a throwing callback remains counted. Only the declared **8,847,360** actual calls are permitted. The9-million ceiling never authorizes spare calls.

The900-second clock covers Node process uptime, including loading, hashing, geometry preparation and output. Check elapsed time before and after every callback, before/after batches, after evidence writes and after final completion write. A single synchronous callback cannot be preempted from within itself: if it returns after the deadline, the post-call check refuses the run and records the actual overrun. No successful completion can override a wall refusal. RSS is sampled before/after batches and every128 actual calls, with an8GiB ceiling; peak observed RSS and cadence are recorded. This is sampled RSS enforcement, not a guarantee about an unobserved instantaneous allocation peak. Node's6,144MiB heap ceiling is required by the launch command and checked in runtime preflight.

Storage is measured from actual files during batches and after writes. Normal outputs may consume at most255MiB, retaining1MiB within the unchanged256MiB ceiling for an incomplete receipt. Writes use exclusive creation and fsync. Completed element-local vectors and weights are retained immediately; a failure also retains available partial weights, their hash, partial vectors/energies, completed-point count and source/runtime context. If a partial weight write itself is refused, its hash/count/recipe remain in the emergency receipt with the write error; prior files remain intact. Storage refusal does not trigger another material call or a smaller rule.

On any callback/domain/hash/count/time/RSS/storage failure, `incomplete-receipt.json` is authoritative and overrides any provisional completion file. The run propagates the failure without retry. A complete invocation with failed fixed criteria reports `UNRESOLVED_FIXED_PATCH_INTEGRATION`. A pass means only bounded fixed PATCH agreement; the236 unchanged elements and global integration, equilibrium, displacement/tangent and anatomy remain unqualified. Preserve the older full-raw/55-certificate independent review limit.

## Structural/runtime preflight and launch sequence

Small fixtures exercise the same assembly/scatter and resource path without evaluating the specimen's constitutive law. Test actual versus reserved counts, exhausted planned allowance, callback exceptions, time before/during/after the final batch, RSS during/final batch, storage growth/refusal, retained partial evidence and unchanged files. A constant-stress affine P2 oracle checks assembly and scatter independently of the numerical model; floating arithmetic is compared within1e-14 for that fixture.

Freeze source, then:

```sh
node --max-old-space-size=6144 education/tools/preflight-fixed-field-runtime.mjs
```

Record and publish source commit, runtime-preflight hash and its passing tests **before** the assembly. Only then use the already authorized single invocation:

```sh
node --max-old-space-size=6144 education/tools/run-fixed-field-integration.mjs --execute
```

No assembly invocation occurred merely by adding these files or running the fixture tests. The expensive invocation may proceed only if the frozen runtime preflight succeeds; a failed preflight is reported without an assembly attempt.
