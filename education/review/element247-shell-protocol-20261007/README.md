# Whole-element247 structural evidence

Source **`b5fdc631627e43a3a796de870a6e5790db90a406`**, descending from
`74054f5c611c57c0b9ddb1fd77a9aaba20ee9c8b`.
The [protocol](../../research/element247-shell-protocol-20261007.md) is frozen
before this geometry-only preflight. **No material assembly is authorized or
executed.** The old result remains `UNRESOLVED_FIXED_PATCH_INTEGRATION`.

- [Structural receipt](structural-preflight.json): 1,076source hashes,
  eight passing tests, zero constitutive calls, both original valid-field
  certificates, actual reference volume and all per-shell moment evidence.
  SHA-256 `59869b3db8b7c0c912393c9c4d68a0883a19ea3ea7dc51a498355da5f22ed6cc`.
- [Test log](tests.log): coverage, Jacobian, exact moments and damage tests,
  including concealed shell cancellation. This is producer verification.
- [Retained-data localization](retained-patch-localization.json): every
  original16-element patch component difference for both states and all three
  required old pairs. Arithmetic only; no reevaluation or independent-review
  acceptance. Removing247 is diagnostic, never a permissible quadrature rule.
- `C44/C55/R55/A55/X55-normalized-points.f64le`: ordered little-endian Float64
  records of six values `(L0,L1,L2,L3,normalizedWeight,r)`. Original shell
  point ranges and comparison-shell grouping are in the structural receipt.
- Corresponding `*-reference-weights.f64le`: one positive physical reference
  weight in m³ per normalized-point record, using the original curved P2
  geometry. Receipt `pointArtifacts` binds byte counts and SHA-256 values.

Actual reference volume of247 is2.310025031494046e-8m³. The exact reference
Bernstein coefficient minimum is1.3860150188963699e-7, above1e-15. All126
normalized monomials through degree5 pass in **each original shell**, with
relative error at most3.202122435216069e-15, including the tiny core. All15
physical-reference monomials through degree2 pass against the independent
exact geometry polynomial on each shell, maximum relative error
1.2160959534691902e-13. The specified acceptance limits remain2e-11 and2e-10.
All generated reference weights are finite and strictly positive. The
smallest is4.0294866462394227e-35m³.

The deepest rule's nearest barycentric radius is1.1184233911196708e-8 and
its minimum terminal sample J is1.3116739650698844e-6, above the unchanged
1e-6guard. Sample minima supplement the exact whole-mesh saved-field
certificate; neither assesses material-force accuracy.

Terminal retained U4→U5 total discrepancy is0.14283916472766123N. Element247's
own peak local difference is0.1427997438257691N (approximately99.9724% of
that peak). The **whole-patch volume term** accounts for approximately99.17%
of the total peak;247's volume component accounts for approximately99.1450%
of the total peak. These percentages have different numerators. Subtracting
247 leaves **7.659505061141658e-5N**, above1e-5N. Elements206/203/246/197/200/248
have local total differences approximately7.66e-5/5.77e-5/4.58e-5/2.63e-5/
1.94e-5/1.29e-5N. They and all other incident elements remain in the retained
inventory and cannot receive a patch-qualification claim from this study.

The planned future sequence contains31,219points per field,62,438material
callbacks if separately authorized. Only method rules and geometry/retained-
vector arithmetic were executed here. A material runner, runtime damage
tests, finite force/work comparisons and independent review remain outstanding.
There is no equilibrium, continuum, anatomical or deployment qualification.

Replay using a fresh directory:

```sh
node education/tools/preflight-element247-shell.mjs --output /tmp/kenoma-shell-independent-FRESH
```

The original receipt stays unchanged. The replay checks the committed
protocol source hashes and writes its own source-commit identifier. All links
and binary files are portable within this checkout; no loopback service is
needed.
