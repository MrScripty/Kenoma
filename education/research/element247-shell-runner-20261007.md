# Frozen bounded element247 material runner: preparation only

This additive branch descends from independently accepted shell protocol and
evidence **`91478ffe8e4728d4589ede1c095c764a09cbfce2`**. Parent thread
`01a103c3-a2e6-7606-8c1e-06987ac710f1` accepted the immutable rules, all ten
binary hashes,13,482normalized shell moments,1,605physical-reference moments,
both exact whole-mesh saved-field guards and held-node preservation. It
authorized **runner implementation, runtime damage tests and a frozen
preflight**, and explicitly withheld material execution. No material assembly
or new source of physical laws is introduced during this preparation.

The [accepted protocol](element247-shell-protocol-20261007.md) and every
previous source/evidence identity remain unchanged. The old
`UNRESOLVED_FIXED_PATCH_INTEGRATION` remains the patch result. This source
adds only a runner, external launcher, counted shell/evidence helpers,
reusable verifier, tests and a preparation manifest. No accepted book,
existing branch, main, deployment, protection or credential is changed.
Only Node and Python standard-library facilities are needed; no dependency
installation or build-time download occurs.

## Fixed rules, physical inputs and reconstruction gates

The original C44/C55/R55/A55/X55 recipes and both saved valid fields are
unchanged. The runner checks exact source and normalized-rule hashes,
reference physical-weight byte identity, whole-mesh field certificates,
field/direction identities, held-node direction zeros, activation1 and the
original material record before calling the unchanged `stressComponents`
adapter. That adapter calls the original material law once per counted
callback and independently reconstructs its stress components; it does not
fit parameters or solve for a new field.

The planned reservation, entered callback and completed callback counts are
all exactly **62,438**, while the ceiling is62,500. The ceiling permits no
spare experiments. Every shell is a counted batch. Limits remain **180s**,
1024MiB old-space heap,2GiB Node process RSS and64MiB combined output.
Integration comparisons remain1e-5N and5.492029235357012e-7J. All thresholds
are bound in the source/preparation manifest before results.

Reconstruction gates are explicitly frozen at the inherited **1e-8N** for
force entries and **1e-9J** for energy. These are distinct from the integration
agreement gates. Every original shell checks its four components against
the **independently assembled actual-law total**. Each stage separately
reconstructs local element vectors/energies from the original shells, checks
the comparison-region aggregation against that reconstruction, and checks
the local element against its585-node global scatter. All nodes, including
held reactions and zeros outside247, are retained and checked. The final
stage also checks component/independent-total reconstruction. No total force
vector is fabricated by summing the four component vectors.

## Complete retention and refusal behavior

Each of107original recipe shells across the five rules is retained at both
fields: **214shell component-vector records and214physical-weight files**.
Every record includes all30local force entries for each of matrix, volume,
passiveFiber, activePotential and independently assembled total; energies,
directional derivatives, geometry intervals, point counts and sample-domain
minimum. Original shell identities stay present after depth22's inner
regions are grouped into the depth20core for the21-region comparisons.

All ten recipe/state element records contain local vectors, original shell
inventory, comparison-region vectors, complete585×3scatters, energies and
derivatives. Five complete normalized-point files match the reviewed binary
rules exactly; concatenated physical-weight files match the reviewed reference
weights exactly for both fields. Pair records retain signed shell/region
differences, per-entry absolute-sum force triangles, aggregate vectors,
signed/absolute-sum work differences and585-node difference scatters.

The Node process uses its uptime for wall checks before/after every callback,
at batches/shells, during output and after final writes. RSS is checked at
batch boundaries and at least every128callbacks. The external launcher
also observes child RSS and combined output with20ms polling and enforces
one180-second monotonic interval covering startup, the child process and
external evidence writes. These are observed process limits, not a changed
OS protection or environment configuration. Heap is fixed by the invocation.

Normal combined output is limited to62MiB, leaving2MiB for bounded emergency
evidence. Every external receipt is at most64KiB; a child failure receipt is
at most1MiB; a failed shell's partial/completed weights are at most64KiB.
If a callback, domain, count, time, RSS or output check fails, the current
completed vectors and available physical weights remain, earlier complete
shell files stay untouched, and a child incomplete receipt or external failed
exit/incomplete receipt records refusal. A completed shell whose normal
output write fails retains its complete weight file or an emergency weight
file and its vectors in the failure context. There is **no retry or overwrite**.

## Execution authorization and terminal completion chain

The one-shot authorization file
`research/element247-shell-execution-authorization-20261007.json` is
**deliberately absent**. Both public material entry points refuse before
creating a material invocation/output directory when it is absent. This
preparation manifest keeps `executionAuthorized:false` permanently.
Future authorization, if granted separately, must be a tracked clean record
with `authorized:true`, the parent thread identity, one invocation, exact
budget, reviewed `runnerSourceCommit` and exact runtime-preflight SHA-256.
The launcher and runner check the reviewed source hashes, test-log hashes,
tracked/unchanged files and ancestry. Adding a separate authorization record
does not silently change the frozen preparation source or its review scope.

The sole intended future public invocation, **not run here**, is:

```sh
cd education
python tools/launch-element247-shell.py --execute
```

It starts exactly
`node --max-old-space-size=1024 tools/run-element247-shell.mjs --execute`
once. A fresh `review/element247-shell-run-20261007/` holds external evidence,
while its fresh `material/` subdirectory holds numerical evidence. Reusing
either invocation directory is forbidden. A run identity and executed source
commit bind both processes. No credentials or persistent settings are used.

`completion-receipt.json` is **provisional**. After it is written, the child
must pass resource/count checks, write `terminal-completion.json` binding the
completion hash, pass checks again, and emit exactly one final stdout terminal
marker binding both file hashes and the post-terminal runtime counters. The
external launcher must then retain child exit0, the complete log hash and its
own successful final record, and pass post-write bounds. Any later failure
creates an external incomplete record and returns nonzero.

The reusable [verifier](../tools/verify-element247-shell.py) checks, in order:
failure/incomplete precedence; terminal/external completion evidence; source,
invocation and hash identity; exact62,438reserved/entered/completed counts;
fixed time/RSS/combined-output limits; complete source/output/shell inventories;
physical weights and original rules; unchanged arrays/material; shell and
element/global component reconstruction;21-region signed/absolute force/work
arithmetic and exact required pass/fail flags. It makes zero material calls
and writes no replacement evidence. A valid-looking provisional receipt can
never pass this verifier alone. An unresolved numerical outcome may verify
as a complete execution while remaining unresolved; an incomplete or failed
execution cannot do so.

## Runtime preflight and review limits

The preflight runs26JavaScript tests and19Python tests:45total. They combine
the accepted shell structural/damage tests and inherited runtime tests with
new actual shell-path synthetic assembly/scatter tests, independent affine
constant-stress P2 oracles, complete and damaged585-node retained-data
fixtures, failed/partial output preservation, real small synthetic process
exit/watchdog tests, missing/duplicate/nonfinal terminal evidence, altered
counters and late failure precedence. Fixture authorization records and
invented zero-force receipt counters exist only in isolated temporary test
directories. They are explicitly marked synthetic and never used as
specimen results. The specimen law is not called by the preflight. The
public material entry points are exercised only to verify the missing-
authorization refusal; no material invocation is created.

After freezing the source:

```sh
node --max-old-space-size=1024 education/tools/preflight-element247-shell-runtime.mjs
```

Independent replay can add `--output /tmp/kenoma-shell-runtime-review-FRESH`.
The [preflight receipt](../review/element247-shell-runtime-20261007/runtime-preflight.json)
and both test logs bind the exact runner source and all accepted inputs.
The final evidence commit and source identity will be recorded in the review
artifact README. This producing-agent preflight is not independent acceptance
of the runner or a material study.

The following interpretation limits are mandatory in any future report:

- **A55↔X55 changes both chart and core depth**; agreement/difference cannot
  be attributed to either factor alone.
- The21-region force triangles exclude cancellation **between** those
  regions, but cannot exclude within-shell, within-region or point-level
  cancellation, including cancellation among the grouped depth22core pieces.
- The work gates are consistency checks **algebraically implied** by the
  force triangles and the unchanged direction's L1norm. They are retained
  arithmetic checks, not additional independent accuracy evidence.
- The physical-reference moment gate is **barycentric degree2**. Because
  the reference map is P2, this covers first Cartesian coordinate moments,
  but not every quadratic Cartesian function, which may require barycentric
  degree4. The old accepted moment evidence is not expanded by this runner.
- Even every finite247comparison passing would establish only bounded
  fixed-field method agreement for247. Secondary197/200/203/206/246/248 and
  all16incident elements remain in the prior inventory; the residual
  7.659505061141658e-5N after diagnostic removal of247 remains unqualified.
  The236other elements, global integration, equilibrium, displacement
  resolution, continuum convergence and anatomy remain unqualified.

There is no material execution, physical-law alteration, anatomical
completion claim, book rebuild, main change, PR, merge or deployment here.
