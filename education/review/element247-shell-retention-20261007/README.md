# Frozen shell-retention successor evidence

This is preparation and synthetic failure verification only. No specimen
material law, material assembly, nodal update, optimizer trial, refit or
nonlinear solve was run. Separate independent review and explicit pinned
one-shot material authorization remain pending.

Branch: `research/element247-shell-retention-repair-20261007`.
Exact source ancestry:

1. Accepted whole-element protocol/evidence:
   `91478ffe8e4728d4589ede1c095c764a09cbfce2`.
2. Frozen predecessor runner source:
   `6e7ee1e078db42bf2ed010c3725ab670eb9ee60c`.
3. Frozen predecessor runtime evidence and repair base:
   `33fa964ff8d11e96a28f82a0d59c6d2e262b6a93`.
4. This repaired source:
   `ed212293a9b99c58a346fd09d338ce8db488749e`.
5. The evidence commit containing this README and the three files below
   descends directly from that source commit. Its exact ID is obtained with
   `git log -1 --format=%H -- education/review/element247-shell-retention-20261007`.

The [source protocol](../../research/element247-shell-retention-20261007.md)
defines the repair and precise guarantee boundaries. The
[input manifest](../../research/element247-shell-retention-20261007-inputs.json)
binds 1,101 unchanged inputs, the predecessor versions of seven modified
files, and eleven current successor source files. Physical laws, material
parameters, saved fields, original shells, positive reference weights,
quadrature recipes, independent totals and all 585-node scatters are unchanged.
Predecessor branches and receipts are preserved.

## Receipt and checks

- [Runtime preflight](runtime-preflight.json):
  `PASS_ELEMENT247_SHELL_RUNTIME_PREFLIGHT_NO_MATERIAL_ASSEMBLY`.
- [JavaScript log](js-tests.log): 28 passing tests, zero failures.
- [Python log](python-tests.log): 30 passing tests, zero failures.
- 1,112 exact current source hashes; zero specimen constitutive calls and
  zero material assembly invocations. Authorization and actual run output
  remain absent.

The receipt contains the SHA-256 of both logs. Receipt SHA-256:
`d1137e513545d8121a155b87403d16550f4d39b743fab2143087c42057a84b56`.

Focused controls cover completed-shell reconstruction failure; truncated
and same-length corrupted weight files; verified emergency bytes;
unavailable emergency writes; late launcher failure with unavailable
failure receipts; actual nonzero launcher exit despite otherwise valid
child evidence; pending-only or partially published acceptance; forced
termination; unavailable live RSS; preauthorization time consumption;
and nonzero cancellation-heavy JavaScript-to-Python verification with
explicit sequential binary64 arithmetic. A real process control also
checks that a watchdog kills an inherited child after its launcher has
already exited.

Acceptance requires the independently observed launcher exit and publishes
its hash-bound receipt last, after final wall/output checks. There is no
fallible check or logging operation after successful publication. The
180-second interval starts at public Python main entry before authorization
and source checks, includes worker startup/execution/exit, and ends at the
last supervisor prepublication check. Initial interpreter/module import
precedes main entry; the atomic publication follows the last check.

SIGKILL preserves only already durable files. Current-shell RAM vectors,
weights and precise interrupted counters are not guaranteed; killed or
incomplete runs cannot qualify. These controls are invented evidence and
do not establish specimen integration accuracy.

## Remaining limits

Reconstruction gates remain 1e-8 N / 1e-9 J. Integration gates remain
1e-5 N / 5.492029235357012e-7 J. The 62,438 planned / 62,500 maximum
callbacks, 180 seconds, 1,024 MiB Node old-space, 2 GiB RSS, 64 MiB combined
output and emergency allowances remain unchanged.

A55/X55 changes chart and core depth together. The 21-region triangles
allow within-region and within-shell cancellation; the work gates follow
algebraically from those force triangles. Reference moment coverage is
barycentric degree two, not every quadratic Cartesian function.

The old `UNRESOLVED_FIXED_PATCH_INTEGRATION` result, all sixteen incident
elements and secondary elements 197/200/203/206/246/248 remain explicit.
This successor establishes no global integration, equilibrium, physical
deformation, displacement-resolution, continuum or anatomical completion.
No book source, main, existing branch, PR, deployment, protection or
credential was changed.

Independent replay from the frozen source or its evidence descendant:

```sh
node --max-old-space-size=1024 education/tools/preflight-element247-shell-retention.mjs --output /tmp/kenoma-shell-retention-review-FRESH
```

The output path must not already exist. The replay refuses source changes
and refuses any actual material authorization or material-run directory.
