# Full-face load versus applied pressure

This standalone successor adds the missing inverse transverse loading control to the independently accepted passive unequal-transverse specimen at `15f8c30752859b5647b86d7b4a15b82a7615355d`. Its law, original parameters, geometry and scalar free-face criterion remain unchanged. It is not yet registered in the educational book.

Choose a fixed one-face compressive resultant C (N), or fixed applied current-area normal traction q (Pa). Fix longitudinal X stretch and solve selected transverse h in 0.5..1 while the other transverse stretch b solves Pfree=0 in 0.1..4. The inherited inner solve uses 64 bisections and its original 1e-5 Pa criterion. The outer solve uses 8, 32 or 64 bisections with criterion 1e-8 N for force or 1e-5 Pa for pressure. Both residuals must pass; iteration count alone is not evidence of equilibrium. The signed bracket update does not assume force increases or decreases with deformation. A target lacking endpoint bracketing is refused. Endpoint values are not a proof of the full attainable range, root uniqueness, buckling resistance or unrestricted 3D stability.

The same passive isotropic energy is used:

U = V0 [mu/2 (J^(-2/3) I1 - 3) + K/2 (J - 1)^2]

Pi = mu J^(-2/3) (li - I1/(3 li)) + K (J - 1) J/li

J = lx ly lz; I1 = lx² + ly² + lz²; sigma_i = Pi li/J.

C = -Pload A0; Acurrent = A0 lx b; q = C/Acurrent = -sigma_load.

Nx = Px H0 D0 is the signed longitudinal end resultant, tension positive. C and q are compression positive and concern one face; opposite resultants are not added. Reference-area compression C/A0 is also displayed. Solid stress and applied traction are not interstitial or vascular fluid pressure. This is a static snapshot with no transport, viscoelasticity or active fibres.

The breadth factor 0.5..2 multiplies the reference dimension along the free transverse axis. Each specimen still has full-face loading: this changes its reference volume and material amount, including its end area. It does not vary a localized contact patch on the same specimen. At fixed q, the homogeneous stretches and stresses are invariant under this breadth change; force and energy scale because reference area/volume change. At fixed total C, the area-dependent traction and solved deformation change. No force-capacity increase from bulging, PCSA surrogate, empirical compression penalty, calibration or force-direction rule is inserted. End stress and end reference area keep geometry and resultant distinct.

The model uses bilateral grips on X and the selected transverse axis, with zero traction on the remaining faces. Compression-only target loads are nonnegative; this is not an implementation of unilateral contact, friction or detachment. Fixed current pressure is a follower surface traction. We solve its force-balance equation directly: adding q times total volume to energy would also load the intended free faces and would describe a different problem.

The complete inherited Lean source and proof receipt are supplied. Its three checked identities are conditional algebra with explicit associativity/commutativity, not Real instantiation or a proof of this energy, derivatives, root algorithm or biological validity. No new Lean declaration or registered proof attempt is introduced. Separate ordinary book proof status remains 30 passed / 85 unrun.

Build the preview with `node build.mjs --out ABSOLUTE_NEW_DIRECTORY --proof ABSOLUTE_ACCEPTED_PASSIVE_RECEIPT`. It verifies inherited source hashes and genuine source/object/transcript bindings before copying runtime assets. Serve the output directory over local HTTP. All downloads use relative paths. Print conversion maps them to internal method/source destinations and separately supplies the JSON receipt. Source, claims, equations and diagram labels must retain actual PDF point sizes at least 10; a real 9pt source damage must be rejected.

This lab performs no anatomical material calls or outside236/fine-window integration. No registered proof attempt is introduced.
