# Scalar Filippov proof receipt

The [fourteen exact real scalar declarations](../../proofs/FilippovConvexWeight.lean)
passed a fresh **Lean 4.19.0** compilation with warnings treated as errors.
Source freeze: `5f907466a13ed42a4f30d9525ecc2f2af09aca0d`, tree
`58ddf9c871690955fa96894987a4680aeee08c65`. The
[kernel receipt](../../data/filippov-convex-weight-proofs-v1/review/kernel-check.json)
SHA-256 is `e560df73f6adc2643b858930683556073537aeda0217f63c65bbfebc98deb609`.
Proof-source SHA-256 is
`8cafcaf2fd8e1d4a6102739ceb04a09989d8807172e95bd6e78879d397613814`.

The exact assumptions and [source mapping](filippov-convex-weight-proofs.md)
identify θ as the integrating-field coefficient. Under `νon>0>νoff`,
`−νoff/(νon−νoff)` lies strictly between zero and one, makes the mixed
scalar normal zero, and is its unique real zero-normal weight. The generic
zero-normal and uniqueness statements require an explicit nonzero denominator.
For `νon=η(d+k)` and `νoff=ηd`, with η and k nonzero, this is exactly
`−d/k`, and its convex combination of scalar I rates k and 0 is `−d`.
There is no sign-convention mismatch or change to the approved physical law.

Every final dependency report contains only `propext`, `Classical.choice` and
`Quot.sound`. There are no custom axioms or admissions in the accepted source.
The [real compiler log](../../data/filippov-convex-weight-proofs-v1/review/lean-check.log),
[command log](../../data/filippov-convex-weight-proofs-v1/frozen-check-command.log),
[seven passing audit controls](../../data/filippov-convex-weight-proofs-v1/audit-tests.log)
and [packet verification](../../data/filippov-convex-weight-proofs-v1/packet-verification.log)
are source-bound. The checker verifies the pinned clean mathlib commit,
dependency manifest and all eight transitive Git package revisions before
invoking the real compiler. Compiler/lake binary hashes, exact theorem
statements and original equation-source hashes are in the receipt.

Three failed compiler attempts and the successful preliminary compile are
retained with exact source/log hashes in the
[attempt manifest](../../data/filippov-convex-weight-proofs-v1/attempts/manifest.json).
The failed runs never issued checked receipts; Lean's `sorryAx` error-recovery
output in the missing-tactic run is preserved as a failure. No warning or linter
was disabled. A separate
[metadata failure](../../data/filippov-convex-weight-proofs-v1/attempts/preservation-metadata-failure.json)
records the absent local main ref; rerun preservation checks use the verified
`origin/main` ref without changing it.

All **2,066 baseline blobs** from c1c7ba3 remain byte-identical. The held first
sliding branch is still `b692d372bfcec354dfef377dc2245c3176c3e5cb`; the separate
activation-proof branch is still `4da4eccc9af3b10f05be1bbd8966084f098dc6dc`.
No book proof registry, manuscript, physical/numerical source or published
candidate changes. The [preservation receipt](../../data/filippov-convex-weight-proofs-v1/baseline-preservation.json)
and replayable [verifier](../../tools/verify_filippov_convex_weight_packet.py)
support these checks. This branch was created from c1c7ba3 and contains no
b692d372 or activation-proof changes.

This proves scalar real algebra only. It supplies **no ODE existence, solution
uniqueness, numerical event accuracy, residence, exit or stability theorem**.
Zero sliding steps and zero trajectory states were added. Sliding execution
remains held under the parent's independent protocol review. No main merge,
book adoption or deployment follows from this receipt.
