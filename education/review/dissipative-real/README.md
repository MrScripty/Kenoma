# Local real standard-linear-solid proof checkpoint

The local model is an equilibrium spring `E0` parallel to a Maxwell branch
`(E1, eta)`, with total strain `eps` and viscous strain `v`:

```
sigma = E0*eps + E1*(eps-v)
eta*vdot = E1*(eps-v)
U = E0*eps^2/2 + E1*(eps-v)^2/2
Ddot = eta*vdot^2
```

Source checkpoint: `b262270f7d8fa0d725ba34d35ea319ee662dba0f`.
Source SHA256: `7368497bd84dcb8ab8e020270a4823d233424601b0225e546393114b7141c972`.
Claim-map SHA256: `c82b69418c7bb0ede1296b2a3c72b0904d47b23854c5db3c93f8986f93bad657`.

The fresh strict kernel run checked eleven declarations in
[`DissipativeBarReal.lean`](../../proofs/DissipativeBarReal.lean). They establish
storage and dissipation nonnegativity under their coefficient signs; the actual
storage time derivative given strain-path derivatives; exact local power balance
under the assumed Maxwell equation; zero-branch elastic recovery; and the exact
derivative, forward bounds, and weak monotonicity of the constant-strain
exponential. Held-strain stress bounds and decay require `v0 <= eps`.
[`dissipative-real-claims.json`](../../proofs/dissipative-real-claims.json) records
each theorem's explicit assumptions and limits, without hand-assigned statuses.

[`qualification.json`](qualification.json) records the actual fresh result,
source hashes, command, Lean version, and pristine pinned dependency identities.
[`lean-check.txt`](lean-check.txt) is the strict compiler transcript. All eleven
axiom reports contain only `propext`, `Classical.choice`, and `Quot.sound`.
The same run freshly checked the unchanged four real property declarations;
their receipt and transcript are included separately.

The run used Lean `4.19.0` and mathlib commit
`c44e0c8ee63ca166450922a373c7409c5d26b00b`, with manifest SHA256
`5c6421b650bc87a2427a892a39e5522dc44543ca4ac1bd6e9f08d536c044a752`.
All eight locked git packages matched their revisions and had pristine sources.
Existing compiled dependencies sufficed; no dependency source, lock, or build
configuration changed for this checkpoint.

With the repository's pinned tools provisioned, reproduce the fresh review run:

```
python3 education/review/dissipative-real/qualify.py
```

The review runner removes its previous success receipt first, runs the existing
fail-closed property checker, compiles this source with
`lake --no-cache env lean -DwarningAsError=true`, checks the axiom reports and
unchanged input hashes, and writes computed statuses only after success.
Integrating this family into the ordinary book checker and visible cards remains
the parent worker's responsibility.

These are real local constitutive and constant-strain hold proofs. They do not
prove JavaScript refinement, force-controlled creep, changing-load ramps,
whole-bar geometry/quadrature solutions, numerical time stepping, discrete
energy ledgers, calibration, biological validity, or browser rendering. The map
names `web/dissipative-bar.mjs` as the intended runtime source; runtime
implementation and qualification remain separate.
