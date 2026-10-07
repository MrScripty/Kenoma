# Shell launcher process-lifetime successor

This focused local successor descends from
`178ef27e7687cc8278f689cab0d5c6aa2bd58b67`, whose repaired runner source is
`ed212293a9b99c58a346fd09d338ce8db488749e`. Both predecessor commits,
branch and receipts remain unchanged. The parent independently verified
the completed-shell retention and arithmetic repairs, but identified a
remaining process-lifetime blocker. No specimen calls or material assembly
are authorized here.

## Failure and repair

The real material child has its own stdout pipe. If its Python launcher
dies, the supervisor can receive EOF on the launcher's pipe and finish
polling normally while the child remains live. The predecessor killed the
process group only when polling raised an exception. Its later refusal
on the observed nonzero launcher exit did not stop that surviving child.
The inherited-stdout watchdog test exercised a timeout, so it did not
cover this actual pipe topology.

The supervisor now shares one process-group stop operation across all
refusal paths after spawn. It stops the inherited group immediately when
it observes a nonzero launcher exit, even after ordinary polling completion.
An outer refusal handler also stops the group on selector/setup, output
directory, evidence-write, identity/hash, resource or acceptance-publication
failure. Cleanup precedes the best-effort failure receipt, so an unavailable
failure write cannot suppress termination. A missing group is harmless;
other cleanup errors remain explicit refusal evidence and never qualify.

The last successful acceptance publication still has no later fallible
operation. Earlier completed-shell retention and explicit binary64
arithmetic-order repairs are unchanged. The runner, public launcher and
verifier point to this successor's separate preflight, rather than relying
on the predecessor's receipt for changed sources.

## Focused controls

A real synthetic Node child waits while its Python launcher exits. The
child inherits the launcher's process group but uses a separate PIPE or
DEVNULL for output, allowing the supervisor's polling loop to finish without
waiting for the child. Eight subcases cover:

- Launcher exit 7 and launcher SIGKILL, each with PIPE and DEVNULL.
- Launcher exit 0 followed by missing completion-candidate refusal.
- Failure writing the observed-launcher receipt.
- Nonzero launcher exit with an unavailable failure receipt.
- Failure publishing the final acceptance after an otherwise valid synthetic
  child chain.

The controls verify the child started, its process-group identity, actual
launcher exit, absent published acceptance, verifier refusal and child
termination. They assert that the monitor did not report a wall timeout;
the inherited-stdout timeout control remains separately preserved. All
processes and evidence are synthetic, with zero specimen evaluation.

The preflight runs 59 tests: 28 JavaScript and 31 Python, with this new
test containing eight process-lifetime subcases. It binds 1,119 source
hashes, including unchanged predecessor sources and receipts, and verifies
the predecessor versions of five modified files.

```sh
node --max-old-space-size=1024 education/tools/preflight-element247-shell-lifetime.mjs
```

Independent replay uses `--output /tmp/kenoma-shell-lifetime-review-FRESH`.
The [receipt](../review/element247-shell-lifetime-20261007/runtime-preflight.json)
and [artifact README](../review/element247-shell-lifetime-20261007/README.md)
record the frozen source, logs and precise scope. This is producer
verification; independent successor review remains pending.

## Preserved scope

The planned/maximum material calls remain 62,438/62,500. The 180-second
interval, 1,024 MiB Node old-space, 2 GiB RSS, 64 MiB combined output and
emergency allowances are unchanged. Reconstruction stays 1e-8 N / 1e-9 J;
integration stays 1e-5 N / 5.492029235357012e-7 J. All physical laws,
parameters, frozen fields, quadrature recipes, positive reference weights,
independent totals and all 585-node scatters are unchanged.

Only already durable files are guaranteed on SIGKILL; current-shell RAM
and precise interrupted counters are not. The external interval begins
at public Python main entry before authorization/source checks and ends
at the last supervisor prepublication check; interpreter/module import
precedes it and atomic publication follows it.

A55/X55 still changes chart and core depth together. The 21-region
triangles allow within-region/shell cancellation; work gates follow
algebraically from force triangles. Reference moments cover barycentric
degree two, not every quadratic Cartesian function. The old
`UNRESOLVED_FIXED_PATCH_INTEGRATION`, all sixteen incident elements and
secondary elements 197/200/203/206/246/248 remain explicit. No integration,
equilibrium, physical deformation or anatomical completion is claimed.

No existing branch, main, book, PR, deployment, protection or credential
is changed. This successor and its preflight are local only; no push,
publication, PR, merge or actual material invocation is performed.
