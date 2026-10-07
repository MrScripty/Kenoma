# Bounded saved-state collapse diagnostic

This separate branch starts from frozen refused-run evidence `713d74645a32fc24c02b71a7879d90dabd93441c`. Preserve the old result, all fractions and geometry/force gates. No optimizer, extra line fractions, fitting, parameter changes, new nodal fields, anatomical qualification, publication/deployment or book adoption are authorized. The diagnostic evaluates only exact saved **valid** fields and distinguishes those evaluations from solver advancement.

The previous own-run verification reproduced170 trial and55 additional material-gate certificates. The parent review did **not independently replay the full50.6 MB raw result or those55 additional gates**. Keep that coverage limit explicit. This diagnostic produces new source-bound evidence for independent review; it is not an upgrade of the prior review scope.

## Frozen material and force decomposition

Read the actual existing law in `web/anatomical-material.mjs`, reference assembly and isolated runner. Decompose its first Piola stress/energy into isochoric matrix, finite-bulk volume, tension-only passive fibre and fixed-activation active-potential contributions. Use the exact existing material call and verify the component stress sum against it. Do not replace full fibre stretch `lambda=|F f0|` by an isochoric stretch. All material parameters remain the old values.

Verify units: F,J,lambda,b,width and activation are dimensionless; energy density/first Piola stress are Pa, reference weights m³, reference shape gradients1/m, nodal/generalized energy gradients N, coordinate increments m and virtual work J. Component quantities are energy **gradients**; physical internal nodal forces have the opposite sign. Fixed caps supply reactions but do not add an external energy term. Confirm the isolated objective contains no external load/gravity/inertia/contact or tendon potential, and its checked sheet fixture has zero branches/strips.

Bind the authored config and historical fit/Arm26 source. The1 MPa bulk and0.001 MPa matrix constants are authored assumptions; sigma0=3.599330734 MPa is a historical restricted45-mode,32-point fixed-end fit to the Arm26 BRA target987.26 N. The achieved987.274411719 N and fitted stress scale are numerical model records, not measured physiology or a newly enforced load.

## Declared evaluation scope and limits

Material/force assembly is bounded to three exact saved states: control45(iteration1), first valid46(iteration1), and last valid46(iteration13). Certify each stored field against the unchanged whole-element `J>binary64(1e-6)` gate before diagnostic material calls. Reassemble the original2048-point body without solving and reproduce recorded component energies and full-free gradients. Save component nodal gradients, projected45/added-direction gradients, full-free norms/cap reactions and component sums. Report outside46-space residuals separately from projected residuals.

For the same control and last-valid fields, refine the **16 source elements incident to free vertex92**:

`195,196,197,198,199,200,202,203,206,237,240,243,244,246,247,248`.

Stage4 uses16,384 positive points per incident element. Stage5 raises only element247 to131,072 points, retaining the other15 at16,384. Every element outside the incident patch stays at the original2048 rule. Report component energies, component directional derivatives along the recorded terminal scaled Newton increment and full nodal gradients at the unchanged fields. Compare patch and whole-body contributions, and retain the exact original physical gates for interpretation. A hybrid assembly is a diagnostic, not a new equilibrium or global quadrature-convergence claim.

Also grade only element247/corner0 from its original depth3 cell partition to corner depths6,10,14,18 at control and last-valid. All other original subcells remain unchanged. The deepest rule has2468 points. This tests whether sampling nearer the collapsing corner changes its integrated contributions, with no state changes. The geometric quadrature identity and degree2 moments are tested; accuracy of the nonlinear material integral is an empirical diagnostic question, not assumed from those moments.

Pointwise profiles at the actual corner, the nearest original2048 point, and three inward edges at distances2^-1 through2^-18 record J, full fibre stretch, F, reference position/weight, component densities/first Piola norms and fixed-direction/recorded-terminal-direction density derivatives. The three previously implicated elements247/250/251 receive corner profiles at all three saved states. Corners have zero integration weight in the original rule; pointwise material calls here are diagnostics and are not injected into the old integral.

For all16 saved trace fields, compile exact spatial determinant coefficients and reference/current coefficient ratios. Positive reference coefficients express J as a convex combination of those ratios. Their minimum is a rigorous lower bound; when attained at a pure-corner coefficient it proves the actual whole-domain minimum and its location. Record exact inward barycentric derivatives at the critical corners to characterize the local collapse geometry without generating a limiting or invalid field.

Stop if a saved field cannot certify the unchanged guard, replay/component checks fail, a diagnostic material call throws, or the budget is exceeded. The resource ceiling is **3,000,000 material-point evaluations** across field assemblies/probes. No rejected-state material evaluation is allowed. The chosen recipes require approximately2.845 million calls. Preserve partial diagnostic evidence if it fails; do not silently enlarge the bound or add another field.

## Source and validation sequence

The manifest binds the full prior source/input inventory, refused raw/compact results and parameter provenance. Freeze new source, protocol and tests first, then run the diagnostic once. Five helper tests verify stress/energy derivatives, full/tension-only fibre behavior, hydrostatic isochoric separation, positive quadrature weights/moments and equivalence of depth3 geometry to the old rule. Synthetic tensor tests are local law/unit checks, not new nodal specimen fields or optimizer steps.

```sh
node --test education/tests/isolated_collapse_components.test.mjs
node --max-old-space-size=6144 education/tools/run-isolated-collapse-diagnostic.mjs
```

Create no research/model correction until the pointwise and integrated evidence identifies what can be attributed to active/passive terms, local geometry, restricted space and sampled integration. Pointwise resistance, aggregate energy reduction and quadrature coverage are different observations. Any proposed correction must be a separately reviewed research protocol with unchanged historical evidence; smaller line fractions are not assumed to solve this failure.
