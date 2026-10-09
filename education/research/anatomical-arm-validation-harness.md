# Bounded actual-arm execution harness

9 October 2026. New isolated source successor of
`e57847418a13da39db78cbfcdba070c285f3bfde`; this same immutable commit supplies
the actual physical operator. All existing physical modules, laws, solver,
subdivision helper, data and evidence retain their bytes. New files are only this
note, tools/arm-validation and synthetic tests. Author: MrScripty
<TheEnvironmentGuy@protonmail.com>. No numerical campaign, actual material or
atlas-configuration evaluation, download, browser recheck, public build, PR,
publication, deployment or protection/credential change occurs in this task.

## Exact execution set and limits

| Run | Action from an independently prepared copy of frozen rest | Solves max | Configuration entries | Wall ceiling |
|---|---|---:|---:|---:|
| A | Held rest, activation zero, Hessian=false; no optimizer | 0 | 1 | 60 s |
| B | Default actual step; effort=.04, h=.01 s, 120 iterations/rule | 1 | 512 | 240 s |
| C | Same inputs/options, subdivisionDepth=1 | 3 | 512 | 240 s |
| D | Two default .005 s steps; effort=.04, 120 iterations/rule | 2 | 512 | 240 s |

No continuation, sweep, refit, new interval search, retry or trajectory. Failed A,
resource/exception/replay inconsistency stops later jobs. Ordinary solver refusals
remain control outcomes. Aggregate: six attempts, 1,537 configuration entries,
780 s elapsed wall including supervisor/preflight/replay/disposal/publication.
Per-job worker setup, solve, replay and disposal are included; finalization is
charged to the last actual job. One second of each nominal job limit is reserved
for disposal; no accepted result may exceed the full ceilings.

Per job: owned RSS <=1,000,000,000 bytes, observed shared cgroup usage
<=16,000,000,000 bytes, output <=4,194,304 bytes, stdout/stderr <=262,144 bytes.
Aggregate output <=16,777,216 bytes and transcript <=1,048,576 bytes. Include
manifest/input/source text, result buffers/staging, logs, final/refusal receipts
and the exclusive external one-use claim. Reserve 65,536 output bytes and 1,024
transcript bytes for final/refusal reporting **within** the ceilings. No scientific
receipt is silently truncated; overflow means refusal.

The Linux watchdog uses PID/start identities and a process-local subreaper;
owned descendants are killed/reaped before another job or final acceptance.
Unexpected descendants refuse. RSS/cgroup are sampled every 10 ms; disposed
worker/supervisor RSS high-water marks and final resource observations are also
checked. Summed high-water marks are conservative. Shared memory.current is an
observed shared quantity, not task attribution or a continuous private allocation
quota. No cgroup limits/protections are changed. Unavailable monitors, excess
memory, incomplete disposal or deadline overrun prevent acceptance. Kernel kill
latency is recorded; it cannot be relabelled success.

## Exact accounting

A configuration entry is each invocation of the original private configuration
function used by anatomicalConfiguration/objectives: prior, repeated, Hessian,
rejected/partial, accepted, quadrature-event and independent replay evaluations.
Counters are inserted before work. No repeated coordinate/cache hit is free.
Every accepted leaf has four Hessian=false replays charged to its process ceiling.

Constitutive counters count actual entry calls, including partial failures:
56,448 muscleMaterial calls per full configuration (7*252*32), 633 tendonMaterial
calls (585 routed +48 internal branches), and <=56,448 materialTensor calls when
Hessian=true. tendonSegment's internal tendonMaterial call is counted once.
Analytic support arithmetic is not a separate constitutive call. HVP matrix
products are separately charged, not called material evaluations.

| Class | A | Each B/C/D | Aggregate maximum |
|---|---:|---:|---:|
| muscleMaterial | 56,448 | 28,901,376 | 86,760,576 |
| tendonMaterial | 633 | 324,096 | 972,921 |
| materialTensor | 0 | 28,901,376 | 86,704,128 |

HVP <=3,528,840/attempt, <=21,173,040 aggregate. The original nominal
7*(1+120*40)=33,607 objective entries/attempt is superseded by the tighter
configuration ceiling. Executed counters permit the last entry and deny the next
before work; denied entries are recorded separately. BudgetExceeded is not
RangeError. Its external latch survives subdivision catches and forbids all later
work/replay. B/default exceptions and both D halves are protected by an outer
transaction; first-half success cannot commit a failed interval.

Manifest preparation only reads/hashes immutable bytes. It embeds original
module/input text, original/transformed SHA-256, harness hashes, Git IDs, Node
version, fixed policy and the exact independent review. The in-memory synchronous
Node loader verifies both hashes before physical import and rejects foreign or
unlisted URLs. Exact-prefix/cardinality-checked insertion instruments internal
configuration/material/tensor/attempt/HVP call sites, including lexical calls.
Original physical files are never rewritten; physical expressions/gates are
unchanged. The private observer copies state/receipts only, never raw solve
closures or Hessians. Immediate leaf snapshots permit C's first half to be replayed.

## Inputs and gates

Immutable data commit: `0b83819ad3fdaed7405c6bbe617bc01640eef914`.
Paths relative to education/data/anatomical-arm-v1:

| Input | SHA-256 |
|---|---|
| generated/arm-reference.json | `1b80c1d3d9f2eb4370cd298f58f5e9c582625574f27072f6d3a1ea898ce4c036` |
| config/attachments-apparatus.json | `070fee738e73e127e334ee5cbe680cb622f100396ad0728eb9df6723c2232389` |
| config/apparatus-routing.json | `b8580e8158e17730b65b64d0fdbe0f1cbbafc76235b9a5f0c2b01020818cd93f` |
| audit/modal-fixed-end-results.json | `b0eeecdade262b682279d9ebeb7a8147a4525a992976a85afc0ce5e63270d8b4` |
| audit/arm-rest-results.json | `8dc23d896adce4b428f39cb172d76f3c74c828f49c2007c66155e45e8ea359c7` |
| audit/arm-rest-recheck.json (prior evidence only) | `3d1159de78088207320d3b19b17ffc83cb08a531781e26715c8167dd7efbecab` |

Exactly 460 frozen coordinates; q=.2841100888248933, omega/activation/effort/
time/step/work=0, mass=.5 kg, empty history/massEvents. No contactRule is stored:
use the unchanged prepared initial recipe. Exact original parameters/contact,
subdivided32 quadrature, 63 modes/head, fitted materials and geometry/routing.

Unchanged scientific gates: finite maximum reduced gradient <=1e-4 N (joint
excluded only for held rest), J>1e-6, original Newton/Armijo criteria, zero finite
transverse crossings, accepted routing and zero sampled bone/soft penetration.
Replay also checks sampled tendon penetration as the existing independent
trajectory verifier does. Its lineage tolerance is 1e-14 and residual/work/energy/
impulse/quadrature receipt tolerance is 1e-9. Additional exact coverage checks:
step+1, effort, unchanged mass/events, history prefix/tail, cumulative work and
contact-rule lineage. Each leaf replays prior(old rule/activation), old@final
rule, old@final activation and final@final rule. Include rigid gravity/stop/
inertia/damping in joint force; separate quadrature events and report nonzero
work defect. No nodal, continuum, physiological or anatomical qualification.

B/C whole successes must match scientific state/receipts exactly: control
compatibility, not recovery. Ordinary B refusal with two C leaves and exact D
reproduction/all gates supports that one reduced interval only. Completed half
refusals refute depth-one recovery there. Any cap/exception/mismatch/rest failure
is inconclusive. Historical refusals used predecessor operators; no known matched
failure is asserted and no new interval is searched when B passes.

## Observational status and authoritative acceptance

Rollback restores contact values, but rebuilt arrays/Maps/samples replace aliases.
Externally held old aliases may still contain provisional values. They are
UNTRUSTED_PROCESS_LOCAL_ALIASES_DISPOSED, never a committed state. Only detached
final state/contact recipe snapshots are eligible for acceptance; no model reference
crosses the worker boundary. The harness owns onIteration, copies scalar progress
only, and exposes no coordinates/arbitrary external callback.

Progress and earlier attempt/leaf receipts are PROVISIONAL_NOT_COMMITTED. Progress
has run/attempt/sequence labels and no accepted flag. Successful first halves and
workerStatus=PASS remain provisional; workers always output finalAcceptance=false.
Models are disposed before return; processes reaped before classification. Accounting
and receipt/hash maps are detached to prevent late bookkeeping alias changes.

The sole acceptance condition: supervisor exit zero **and** resource-receipt.json
COMPLETE_FINALIZED **and** matching manifest/file hashes **and** authoritative
acceptance for that run. Files observed while it runs, stale aliases, progress or
partial/missing commit cannot satisfy this. Failure/nonzero exit means no accepted
final snapshot. Reserved finalization refusals set every acceptance flag false.

Final directory inventory: manifest.json, rest-recheck.json, default.json,
adaptive-depth1.json, explicit-halves.json, comparison.json, resource-receipt.json,
transcript.log. The separately declared <approved-manifest>.executed exclusive
claim is hashed and charged to A. It prevents reuse/restart of the same approval.
No approval/claim is installed during preparation.

## Commands

Only synthetic/source checks are executed now:

```
node --test education/tests/anatomical-arm-substeps.test.mjs education/tests/anatomical-arm-validation.test.mjs
python3 -B education/tests/anatomical-arm-watchdog.test.py
```

After independent review, metadata-only preparation/preflight:

```
node education/tools/arm-validation/prepare.mjs REPOSITORY NEW_MANIFEST REVIEW_RECEIPT
python3 -B education/tools/arm-validation/watchdog.py --preflight --manifest NEW_MANIFEST
```

The deliverable supplies the exact manifest digest and private output path. Only
following explicit approval of that bound four-run set:

```
python3 -B education/tools/arm-validation/watchdog.py --execute --manifest APPROVED_MANIFEST --approved-manifest-sha256 EXACT_SHA256 --output NEW_PRIVATE_DIRECTORY
```

This command is not executed. All harness controls are implemented; after this
independent source review, only numerical-run approval remains. Runtime refusal
conditions are active guards, not future proposals or authority to weaken/restart.
