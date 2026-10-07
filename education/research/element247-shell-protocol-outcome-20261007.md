# Element247 method protocol: structural gates pass, material study pending

The bounded whole-element method protocol and structural preflight are ready
for independent review. **No constitutive/material calls, new nodal fields,
optimizer attempts, nonlinear solves or refits were made.** No material
runner or material invocation is authorized by this work. The historical
`UNRESOLVED_FIXED_PATCH_INTEGRATION` result remains in force.

Ancestry is retained run/evidence
`74054f5c611c57c0b9ddb1fd77a9aaba20ee9c8b` → initial method source
`b5fdc631627e43a3a796de870a6e5790db90a406` → initial structural evidence
`a508ff1fb648eb75e6809d82e19438fd31ecef54` → wording source successor
**`b03085d86596306eca9d8c14bd51a781094e03b1`**. The wording successor clarifies
the percentage denominators; it changes no quadrature, criteria or law.
The source and evidence branches from earlier studies remain unchanged.

The [protocol](element247-shell-protocol-20261007.md) derives a complete
barycentric radial/triangular-face map with positive normalized Jacobian
6r²(1−a), geometric shells through depth20 and a depth22cross-check. Five
finite rules separate radial, angular and cross-chart/core sensitivity.
A later authorized run would require exactly62,438material callbacks over
the two identical frozen fields, within62,500maximum calls/180s/2GiB RSS/
64MiB output and1024MiB heap. Full component vectors and work must be
retained by original shell and scattered over all585nodes. Signed aggregate
and absolute shell-sum comparisons use the unchanged1e-5N and
5.492029235357012e-7J budgets, for every component and independently assembled
actual total. These are finite-rule agreement criteria, not certified error
bounds relative to an exact nonlinear integral.

The current source's [confirmation receipt](../review/element247-shell-protocol-20261007/confirmation-preflight.json),
SHA-256 **`9eedf9fc18c79b3c5582e65bb88b01b8d4e855d180187fe7770ae509e59aee8c`**,
passes1,076source hashes and eight damage/structural tests. Both saved-field
whole-mesh domain certificates pass. Every original shell's126normalized
monomials through degree5 agree with an independent exact rational oracle;
maximum relative error3.202122435216069e-15, below2e-11. Every shell's15
physical-reference moments through barycentric degree2 agree with the exact
curved-reference Bernstein polynomial; maximum error1.2160959534691902e-13,
below2e-10. Reference volume is2.310025031494046e-8m³ and all weights are
positive. The minimum terminal sample J is1.3116739650698844e-6, above the
unchanged1e-6guard. These structural facts do not qualify force accuracy.

All ten normalized-point/reference-weight files and the retained localization
are **byte-identical** between the original and confirmation preflight. Both
receipts and both test logs are retained; no old receipt was rewritten. The
[artifact inventory](../review/element247-shell-protocol-20261007/README.md)
describes binary schemas, hashes and portable relative links. Local links
were checked to resolve within the checkout. New numerical-analysis
references are original publisher sources:
[Duffy1982](https://epubs.siam.org/doi/10.1137/0719090) (metadata/abstract)
and [Mousavi–Sukumar2010](https://link.springer.com/content/pdf/10.1007/s00466-009-0424-1.pdf)
(open-access original full text). Their singular-kernel claims are not
applied to the saved finite positive-J specimen.

Producing-agent retained-data arithmetic reproduces the old terminal
U4→U5total peak0.14283916472766123N and confirms that subtracting247
diagnostically leaves **7.659505061141658e-5N**, still above1e-5N. All16
incident elements and all component differences remain retained. Secondary
197/200/203/206/246/248 cannot be dropped, and even a future247-only method
pass cannot qualify the patch. Other historical independent-review limits
and the lack of global qualification over236other elements remain.

Remaining work is independent protocol/evidence review and, only after a
separate authorization, a bounded material runner with runtime damage tests
and the fixed shell force/work comparisons. No equilibrium, displacement
resolution, continuum convergence or anatomical completion is claimed.
This branch contains additions and the clarification of its own new protocol
only; no accepted book, old branch, main, PR, deployment, protection or
credential was changed by this task.
