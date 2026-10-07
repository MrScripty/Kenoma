# Frozen process-lifetime repair evidence

Local branch: `research/element247-shell-lifetime-repair-20261007`.
Predecessor: `178ef27e7687cc8278f689cab0d5c6aa2bd58b67`.
Repaired source: `732bc660b1a92411001de88e55b251f4823189e4`.
The evidence commit containing this README descends directly from the
source commit. Its exact ID is obtained with:

```sh
git log -1 --format=%H -- education/review/element247-shell-lifetime-20261007
```

The [protocol](../../research/element247-shell-lifetime-20261007.md) explains
the actual separate stdout-pipe failure and the narrow repair. The
[manifest](../../research/element247-shell-lifetime-20261007-inputs.json)
binds 1,111 unchanged inputs, eight current successor sources, and the
predecessor versions of five changed files. Earlier completed-shell,
weight-byte verification and arithmetic-order repairs remain unchanged.
The predecessor branch and all receipts are preserved.

## Passed controls

- [Preflight receipt](runtime-preflight.json):
  `PASS_ELEMENT247_SHELL_RUNTIME_PREFLIGHT_NO_MATERIAL_ASSEMBLY`.
- [JavaScript log](js-tests.log): 28 passed, zero failed.
- [Python log](python-tests.log): 31 passed, zero failed.
- 1,119 exact current source hashes, zero specimen constitutive calls,
  zero material assemblies, and no actual authorization or run directory.

The new process-lifetime test contains eight real synthetic Node-child
subcases. A Node child inherits the launcher process group but has a
separate PIPE or DEVNULL output stream. Launcher exit 7 and launcher
SIGKILL are each checked with both output modes. The remaining controls
cover exit 0 followed by missing-candidate refusal, unavailable observed
exit writes, unavailable refusal writes, and partial acceptance publication.

Each verifies actual launcher outcome, child startup and group identity,
no accepted completion, independent verifier refusal, and child termination.
The polling phase has no wall refusal, distinguishing these paths from
the retained inherited-stdout timeout control. All evidence is synthetic;
no specimen material law or assembly is evaluated.

The supervisor now stops the inherited group immediately on observed
nonzero launcher exit and again on every outer refusal after spawn.
Cleanup precedes best-effort refusal evidence. Missing groups are harmless;
other cleanup errors remain explicit refusals. Setup and directory/evidence
operations are inside that same refusal handler. The successful final
publication remains the last fallible acceptance operation.

## Preserved limits and pending work

Physical laws, parameters, fields, quadrature rules, positive weights,
independent totals, counters and all numerical/resource gates are unchanged.
The 180-second clock retains its precisely documented preauthorization-to-
prepublication scope. SIGKILL retention covers only already durable files;
current RAM and precise interrupted-shell counters are not guaranteed.

The old `UNRESOLVED_FIXED_PATCH_INTEGRATION`, all sixteen incident elements,
secondary elements 197/200/203/206/246/248, coupled A55/X55 chart/core change,
within-region cancellation, algebraically implied work gates and barycentric
moment qualification remain explicit. No integration, equilibrium, physical
deformation or anatomical completion is claimed.

Independent successor review and separately pinned material authorization
remain pending. Main, book, existing branches, PRs, deployment, protections
and credentials are unchanged. This successor is local only: no branch
push, PR, merge, publication or material invocation was performed.

Independent replay:

```sh
node --max-old-space-size=1024 education/tools/preflight-element247-shell-lifetime.mjs --output /tmp/kenoma-shell-lifetime-review-FRESH
```

The output path must be fresh. The JSON binds both log hashes. Receipt
SHA-256: `65c370e813e74aa90758f9792a99814648f9c0885fbfc58f1fda2df7062281ba`.
