# Frozen implementation geometry review — initial

Reviewed source: ce5df8ae5266e481496d2fb05b386a2d52f7a949, `/tmp/Kenoma-fine-window-runner`. Repository files were read only. Zero specimen/material-law calls and no repository edits.

PASS for actual maps, topology, degree5 moments and physical weights/geometry. Independently reconstructed all34880 exact microtetrahedron vertices, determinant numerators/denominators, enumeration indices and orientations across I0/I1 and all4 corners. The frozen source's up-then-down face triangle order and triangle-then-radial interval order are explicit and deterministic. Actual4360000 normalized point coordinates match independently reconstructed values exactly; relative weight discrepancy≤3.59e-16. All21168 actual degree5 moment checks pass, maximum relative error4.26e-16.

Actual physical arrays pass independent P2 Jacobian and rational polynomial checks on all7 sensitive elements, both fields:4410 degree2 moments (maximum relative error7.01e-14),15260000 geometric determinant ratio checks, and unchanged physical weight `normalizedWeight*det(referenceJacobian)/6` agrees with independent computation to4.91e-15 relative. Minimum actual terminal J=1.3430852676931198e-6>unchanged1e-6 guard. Integer determinant implementation avoids tiny-core subtraction loss; degree5 Duffy exactness covers degree3 physical Jacobian times degree2 moment.

No geometry/scientific blocker found. Historical exact point/weight alias assertions in the source are correct: H4 outer20 share P4/F44;247 C4 outer20 share X44; all material values still retain element/field identity. Array/alias hashes must be closed against the eventual completed preflight receipt before final structural acceptance. Initial reports explicitly mark that receipt pending.

One resource-proof issue was reported: `maximalNumericShape` substitutes -Number.MAX_VALUE, whose JSON encoding is24 characters, but `JSON.stringify(-0.0000010000000000000002)` is25. Actual file caps may remain amply sufficient, but the current claimed worst-numeric fixture is not a true worst-case bound. Use a justified universal finite-number encoding bound and unchanged caps; this requires no physical-gate change.

Scope: geometric implementation only. Completion, streaming resources, authorization/terminal failure receipts and full serialization need source-bound structural acceptance. Outside236 elements remain unqualified; no nonlinear integration agreement or anatomical/equilibrium conclusion follows.
