# Ask which area and geometry a model can consume {#anatomical-geometry-contract-source}

A numerical model can consume geometry without that geometry being an equilibrium state. The frozen section inspector and geometry adapter make this distinction explicit. This release presents their source contract and retained evidence; **their builds, tests and anatomical interactive controls remain unrun under the anatomical execution hold**.

{{quantity-figure}}

## Keep five different quantities separate

| Quantity | Meaning in the authored source | Evidential boundary |
|:--|:--|:--|
| Insertion footprint | Retained bone source faces, sample weights and curved-triangle surface-area method | Does not supply measured tendon CSA or distinguish every deep/superficial tissue footprint |
| Belly-cap area | Authored boundary faces and existing weighted point samples | Does not identify a physiological cross-section or justify a force scale |
| Mapped material section | The same reference material slice transported by ten-node P2 interpolation | May curve away from its initial plane; tessellated surface area is not a planar current-space section |
| Tendon CSA | A specimen-, frame- and method-specific reference or current tendon section | Unavailable in this adapter |
| PCSA | A physiological architecture quantity requiring its stated convention and evidence | Unavailable in this adapter |

The original apparatus's authored 20% insertion/cap fractions, including its further 20% head-fan factor, are not newly measured tendon areas. The adapter exports no replacement A0. Population study pointers do not identify this atlas's landmarks, source faces or specimen-specific cross-sections.

## A partial connection for physical nodal positions

The declared adapter partitions seven repaired atlas-derived P2 bellies into six connected ring-band regions per body. It accepts complete unique `{elementId, nodesM}` body records in the existing apparatus position format. It observes geometry without importing or invoking the mechanics evaluator. Its intended outputs are regional signed material integrals, material-section dimensions, weighted cap points and retained route lengths.

The ten-node quadratic map has an affine parent Jacobian and cubic determinant. The source expands its determinant polynomial and integrates monomials using

$$\int_{tetrahedron}\xi^i\eta^j\zeta^k\,dV=i!j!k!/(i+j+k+3)!.$$

This is exact polynomial integration in real arithmetic, implemented in binary64. A positive **signed integral** does not prove pointwise orientation, absence of folds, enclosed volume, force stationarity or physical deformation. Current material-section area is a tessellation approximation and is not local $J$, PCSA or a slice perpendicular to the current fibres.

Existing weighted endpoint maps preserve source identities and original repair offsets. Only uniquely matched source samples acquire endpoint ownership; unresolved endpoints remain explicit source-indexed literals. Fixed guide points and literals do not supply sliding wraps, contact or a complete shared-aponeurosis degree-of-freedom map. Route geometry has historical provenance without a new clearance check.

## Read an adverse result before accepting a shape

Three saved calibration fields retain failed full free-node force gates: **64.067641, 52.058855 and 54.223684 N**, against the unchanged **0.0001 N** criterion. Four other bodies remain reference-only. The source-only adapter does not turn these historical failures into passing current states or measure new forces for supplied coordinates.

The inspector's 22 input bindings and adapter's 23 input bindings match the retained data locally. That read-only byte verification is separate from executing their geometry algorithms. Original reference data and notices remain unchanged. Source/test availability is not a successful model run, anatomical ownership review or biological validation.

## A source-reading exercise

Read [the inspector method](sources/contributions/anatomical-section-inspector/README.md), [the adapter contract](sources/contributions/anatomical-geometry-contract/README.md) and [its quantity definitions](sources/contributions/anatomical-geometry-contract/quantity-definitions.mjs). Identify which functions consume positions and which quantities they explicitly leave unavailable. Trace the complete-node and endpoint-ownership requirements. Explain why neither a positive regional integral nor a plausible image would resolve the retained force failures.

This exercise reads exact source; it does not offer a simulated or qualified anatomical lab. A future permitted run still requires independent ownership, boundary and architecture review, complete shared/tendon degrees of freedom, qualified integration and full force stationarity. Subject/protocol-matched geometry and volumetric material measurements remain unavailable. Anatomical execution and cap changes stay held.
