# Cross-model capacity and calibration-state checkpoint

The lightweight local calculation reads the retained atlas reference volumes and pinned Arm26 XML directly. It computes **inferred area = atlas volume / Arm26 optimal fiber length**, then **nominal stress = Arm26 force target / inferred area** before continuum deformation. This combines two separate reference models; the area is not measured human PCSA or a measured area of the atlas subject.

| Head | Inferred area (approximately mm²) | Target / inferred area (approximately MPa) |
| --- | ---: | ---: |
| Brachialis FJ1486 | 758 | 1.302 |
| Short biceps FJ1512 | 481 | 0.905 |
| Long biceps FJ1478 | 700 | 0.892 |

All three retained Arm26 pennation parameters are exactly zero, so cosine projection leaves these model-target inferences unchanged. That does not establish zero anatomical pennation. Arm26 optimal fiber length also remains distinct from atlas belly length and measured fascicle length. The [pinned official model](https://github.com/opensim-org/opensim-models/blob/84b487c4e3245359a64381e01f01b9cf4772d457/Models/Arm26/arm26.osim) supplies model parameters, not same-subject calibration.

The parent separately forwarded the reviewer's source-volume-restoration estimates **1.104/0.777/0.757 MPa**. Those rounded values reduce the uncorrected inference by approximately 14–15%; this local tool computes that arithmetic but does not reconstruct the reviewer's restored volumes. The small correction alone does not account for fitted coefficients **3.59933/8.70839/20.37812 MPa**. The reference coefficient and a deformed Cauchy stress are different quantities, as set out in the [calibration outline](calibration-constraints-outline.md).

The [attributed preliminary review](calibration-review-preliminary.json) reports strongly redistributed short/long biceps stretches and low mean active force–length factors in frozen fixed-end fits. The [followup record](calibration-review-followup.json) preserves the parent's additional findings: frozen 256-point arithmetic gives mean factors approximately 0.085072/0.042353 and active Cauchy means approximately 0.47304/0.53470 MPa, while free residuals **1.6624/0.6742 N** still fail the original 0.0001 N gate. Those arithmetic observations are not a re-solved dense calibration. They were not independently recomputed in this author lane; the reviewer's final source-bound report remains pending.

For the accepted 32-point fits, the reviewer reports zero direct active distal-end generalized reaction because end segments lie above the authored active window, while whole-body axial virtual work attributes approximately 74.6/75.5% of total force to active stress. The active interior contribution transfers through passive fibers, authored sheets and bulk response to the end load. Keep the end-reaction and whole-body virtual-work conventions explicit; a zero direct end contribution cannot erase the active contribution. Complete partition definitions and signs remain the reviewer's responsibility in its final receipt.

The independently executed local inference is `audit/cross-model-capacity-inference.json`; its source hashes bind the retained volume diagnostic, Arm26 XML and calculation script. Raw execution is `review/dense-predictor-experiment/cross-model-capacity-execution.txt`. The forwarded restoration and stress-transfer results stay clearly attributed and preliminary. No coefficient, material/default, law, force target, solver tolerance, release equation or skin changes here. The **4.72138-degree / 7.40368-mm** dense trajectory discrepancy and loaded **J approximately 0.712** remain unresolved.
