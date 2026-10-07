# Independent P2 physical-geometry design review

PASS_INDEPENDENT_PHYSICAL_GEOMETRY_DESIGN. The separate script reads only immutable JSON from the schedule worktree and independent mathematical geometry definitions. It imports no repository module and invokes no material law/specimen evaluator.

The script independently derives ten-node P2 shape gradients, reference and both fixed-field Jacobian matrices, positive physical weights `normalizedWeight*det(referenceJacobian)/6`, and the exact degree3 reference determinant polynomial from binary64 input coordinates interpreted as dyadic fractions. Physical moments use exact rational degree≤5 shell integrals with actual corner exponent permutation. They are not delegated to the repository oracle.

Both I0 and I1, all seven sensitive elements, all21 regions and both frozen fields passed. Across4410 physical degree2 moment checks, maximum relative error was6.663555575575021e-14, below the existing2e-10 structural tolerance. All15,260,000 geometry-only field-point checks passed the unchanged J>1e-6 guard. Minimum sampled J: control45 .5607113786709221; terminal46 1.3430852676931198e-6. Minimum reference Jacobian1.3860150188955186e-7, minimum physical weight1.611794658495245e-34.

Counts refer to geometric determinant checks, not material callbacks. Specimen calls=0 and material-law invocations=0. Actual production arrays/source identities, full streaming/resource checks and receipt lifecycles still require source-bound implementation review. These checks do not establish stress integration agreement, equilibrium, anatomy or outside236-element qualification.

Artifacts: `check_physical_geometry.py`, `physical-geometry-design-review.json`, `physical-geometry-design-review.log`. The script reuses geometry function definitions from `check_geometry.py` without rerunning or replacing its preserved design report. Both independent designs are geometry-only.
