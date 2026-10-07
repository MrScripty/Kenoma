# Selective terminal outer-shell angular diagnostic

This separate local experiment descends from frozen single-run result
`4b83ec5dfebae73b08c3f964aa910f65e02458e0`. The accepted original protocol is
`91478ffe8e4728d4589ede1c095c764a09cbfce2`; the unchanged verified supervisor
source/evidence are `732bc660b1a92411001de88e55b251f4823189e4` /
`3846055c8d99b468b247fb225fb7a7945a71b9b5`. Original sources, authorization,
run and all evidence remain immutable inputs.

Parent thread `01a103c3-a2e6-7606-8c1e-06987ac710f1` authorizes exactly one
material invocation **only if an independent local reviewer accepts this
frozen preflight**. Otherwise execution stops with findings. The preparation
manifest remains executionAuthorized=false; a separate pinned conditional
authorization must be committed after independent acceptance.

## Fixed rule, field and identities

Only terminal46, element247, s1 and s2 are newly evaluated:

- s1: r in [0.5,1]; s2: r in [0.25,0.5].
- Existing Gauss5 nodes and weights in r, a and b; radial parts remain 1.
- Angular partitions increase from A55's 2 by 2 to 4 by 4, in both a and b.
- Chart face order stays [1,2,3]; shell/core depth stays 20.
- Each new shell contains 5 × 5 × 5 × 4 × 4 = 2,000 points.
- Exactly **4,000 new counted law callbacks**, with a 4,000 ceiling.

The remaining nineteen A55 regions s3 through s20 and core are reused:
500 points each, totaling **9,500 reused points**. Both their original JSON
vectors/energies and physical weight files are copied byte for byte. The
original normalized-point blocks are reused exactly. The constructed
whole-element inventory therefore has **13,500 points**, not 13,500 new
evaluations. Source hashes preserve every reused record's identity.

Terminal-position SHA-256:
`655eb058007d2432689257b0bbe84f9b054500587672b087b03dbecf0bdfc410`.
Saved-direction SHA-256:
`bb8bc986540e2e3e098969db2b34b3682f55602d868c9972e35b42464972cdab`.
All 585 nodes, including held nodes, remain present; held direction is zero.
The direction is used only for work comparisons, never applied to positions.
The unchanged reference geometry, fibres, material parameters, activation1,
matrix/volume/passive-fibre/active-potential laws and independently assembled
total are bound by the manifest's predecessor input hashes.

## Comparison and reconstruction

The required diagnostic compares retained A55 against new T24 over **only
s1 and s2**. Difference sign is A55 minus T24. It retains each shell's full
ten-node three-component vector, signed aggregate, component-wise absolute
shell triangle, all 585-node scatter and signed/absolute directional work
for every physical term and the independently assembled total.

Force aggregate and triangle must each be at most 1e-5 N. Work aggregate
and triangle must each be at most 5.492029235357012e-7 J. No gate changes.
The separate constructed whole-element record includes all21 regions,
absolute component energies and gradients, independently assembled total,
and the same comparisons. **Reused-tail difference is exactly zero by
construction**. It is reported separately and provides no additional
accuracy or qualification evidence.

Independent component-to-total and element-to-all585 reconstruction gates
remain 1e-8 N / 1e-9 J. Each changed shell is checked before output, with
completed-shell vector/weight retention on failure. Explicit binary64
reduction order matches the accepted JavaScript producer and Python verifier.
The old C55/A55 terminal total triangle **8.611662232570753e-5 N** remains
unchanged and unresolved, whatever this new comparison returns.

Completion result remains UNRESOLVED_ELEMENT247_SHELL_INTEGRATION. A separate
changedShellAssessment reports PASS_CHANGED_SHELL_AGREEMENT or
UNRESOLVED_CHANGED_SHELL_AGREEMENT. Both element247Qualification and
patchQualification stay false.

## Resource, execution and evidence gates

The unchanged verified supervisor observes the actual material-child and
launcher-worker exit, requires zero exits and no failure/incomplete marker,
and publishes the hash-bound acceptance last. Limits remain 180 seconds,
1,024 MiB Node old-space, 2 GiB RSS and 64 MiB combined raw output, with
the existing 2 MiB emergency reserve, 64 KiB external/weight allowance and
1 MiB child-failure receipt. Reserved, entered and completed counters must
all equal 4,000. No batch or callback can exceed the frozen count.

The wall interval begins at public Python main entry before authorization
and source checks; initial interpreter/module import precedes it. The last
resource check precedes acceptance publication. SIGKILL guarantees only
already durable files, not current-shell RAM or precise interrupted counts.

The executor's actual public-entry tool result will be copied verbatim into
a separate outcome artifact if available, including command/workdir and
initial/final tool results. It is explicit executor-return evidence rather
than a new cryptographically independent process observer. This artifact
does not modify the raw supervisor completion chain.

Preflight performs zero specimen calls. It checks 252 normalized degree5
moments and 30 physical-reference barycentric degree2 moments, positive
weights, new-point J>1e-6/reference Jacobian>1e-15 and the unchanged exact
whole-mesh terminal certificate. It freezes the prescribed 4,000 normalized
points and physical weights, reused-region identities and all source hashes.

The 22 synthetic/retained controls comprise six JavaScript tests, seven
Python numerical/damage tests and nine accepted supervisor controls. They
cover exact budget, retained construction, changed/whole separation,
nonzero JavaScript-to-Python comparisons, held-node damage, hidden tail
changes, reconstruction failure and emergency weight retention. Synthetic
callbacks are explicitly distinguished from specimen evaluations.

```sh
node --max-old-space-size=1024 education/tools/preflight-element247-two-shell.mjs
```

Independent replay uses `--output /tmp/kenoma-two-shell-pref-FRESH`. The
[preflight](../review/element247-two-shell-preflight-20261007/preflight.json)
must bind a frozen source commit. An independent PASS record and separately
committed authorization bind its receipt hash before any material invocation.
The sole future entry is:

```sh
PYTHONDONTWRITEBYTECODE=1 python education/tools/launch-element247-two-shell.py --execute
```

Existing run output refuses another invocation. No retry is permitted.

## Limits that remain

This tests outer-shell angular sensitivity at one saved terminal field.
It neither separates a versus b error nor checks control45 again. The prior
C55/R55 radial comparison was at baseline angular resolution; A55/X55
jointly changed chart and core depth. Neither establishes adequacy of this
new selective candidate. Region triangles allow within-region/shell
cancellation; work gates follow algebraically from force triangles;
reference moments cover barycentric degree two, not all quadratic Cartesian
functions. Passing this diagnostic cannot qualify element247, the full
patch, equilibrium, deformation, continuum accuracy or anatomy.

All sixteen incident elements and secondary197/200/203/206/246/248 remain
unresolved. There are no optimizer trials, refits, new fields, additional
rules or model assumptions. Main, book, previous branches, PRs, deployment,
protections and credentials stay unchanged. All work and evidence remain
local; no publication, push or merge is authorized.
