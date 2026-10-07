# Element247 runner preflight: no material assembly

Frozen runner source **`6e7ee1e078db42bf2ed010c3725ab670eb9ee60c`**, directly
descending from accepted protocol/evidence
`91478ffe8e4728d4589ede1c095c764a09cbfce2`.

The [runtime preflight receipt](runtime-preflight.json) passes **45tests**
(26JavaScript and19Python), binds **1,104source hashes**, and records
**zero specimen constitutive calls and zero material assembly invocations**.
Its SHA-256 is
**`707e91edfb36b482393729992c2aa75d3c6913122bdadfe3aca52a3824d49c1b`**.
[JavaScript log](js-tests.log) and [Python log](python-tests.log) retain the
synthetic fixture and damage-test evidence. The actual material authorization
record and material invocation/output directory remain absent.

The [source protocol](../../research/element247-shell-runner-20261007.md)
documents the runner, external launcher, complete retention schema,
terminal/external evidence chain and fixed interpretation limits. The
[manifest](../../research/element247-shell-runner-20261007-inputs.json)
preserves `executionAuthorized:false`. This is producing-agent verification;
it awaits independent runner/preflight review and does not authorize execution.

Passed runtime/evidence checks include:

- Distinct reservations, entered callbacks and completed callbacks; exactly
  62,438planned callbacks, no spare experiments below the62,500ceiling.
- Frozen180-second checks in the child and external launcher,2GiB observed
  child RSS, and64MiB combined external/material output with bounded emergency
  vectors/weights/receipts. Node invocation fixes old-space at1024MiB; the
  measured V8 total heap limit in this Node version is1,275,068,416bytes,
  which includes additional V8 spaces. The2GiB RSS guard covers the process.
- Complete original shell/vector/weight retention, independently assembled
  actual total, explicit shell-to-element and element-to-global reconstruction,
  and all585-node scatters including reactions. Reconstruction tolerances are
  frozen before results at1e-8N and1e-9J.
- Actual shell-path constant-stress P2 synthetic oracles, malformed totals,
  damaged held-node/outside-support scatters, missing shells and forged
  cancellation metrics even after refreshing fixture hashes.
- Partial and complete-shell output refusal retention, callback/time/RSS/
  storage failures, real small synthetic child exits and watchdog stops, and
  no retry/overwrite behavior.
- Terminal completion file, exactly one final stdout terminal marker,
  external exit0 and external final hashes. Missing, duplicate, provisional,
  failed or incomplete execution evidence refuses verification; late child
  or external incomplete evidence takes precedence over earlier valid hashes.

The complete zero-force fixtures are invented test records with copied
reviewed reference weights/arrays. Fixture authorization records and receipt
counters exist only in temporary isolated test roots; they are not specimen
results. No original material law or optimizer was evaluated in these tests.

Mandatory reporting limits remain: A55/X55 changes chart and core depth
together;21-region triangles permit within-region/within-shell cancellation;
work gates are algebraic consistency consequences of force triangles;
moment coverage is barycentric degree2, not every quadratic Cartesian
function. Resolving247 cannot qualify the prior16-element patch, its
secondary197/200/203/206/246/248 contributions, or the236other elements.
The old `UNRESOLVED_FIXED_PATCH_INTEGRATION` and all anatomical/equilibrium
qualification gaps remain.

Review replay, from a checkout without material authorization/output:

```sh
node --max-old-space-size=1024 education/tools/preflight-element247-shell-runtime.mjs --output /tmp/kenoma-shell-runtime-review-FRESH
```

All links are relative and portable. No book, main, previous branch, PR,
deployment, protection or credential was changed.
