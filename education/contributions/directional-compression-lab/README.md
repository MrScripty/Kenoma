# Unequal transverse response of a constrained passive block

This standalone, unregistered addition starts at geometry adapter `da6842f146ea11bd1c0bfbfb3de409978a824f5c` without changing it. The existing progressive kinematics already permits unequal stretches, and the existing material lesson solves equal X/Z lateral stretches. The missing capability addressed here is **material-determined unequal transverse response under an independently fixed longitudinal length**. It is not another kinematic volume lesson or an anatomical solve.

The reference block is the unchanged teaching geometry, X=0.08 m, Y=0.06 m, Z=0.05 m. X stretch is prescribed in 0.8..1.2. Either Y or Z has prescribed stretch h in 0.5..1; the other transverse pair of faces is traction-free. X and the controlled transverse faces use bilateral displacement grips. They can push or pull; a negative displayed compression resultant requires a tensile attachment and cannot be supplied by compression-only contact. All fields are homogeneous diagonal. No shear, buckling, spatial bulging, muscle fibre direction, activation or anatomical ownership is modeled.

The energy is the exact diagonal extension of the existing isotropic teaching law:

`U = V0 [mu/2 (J^(-2/3) I1 - 3) + K/2 (J - 1)^2]`

`J = lx ly lz`, `I1 = lx^2 + ly^2 + lz^2`.

`Pi = mu J^(-2/3) (li - I1/(3 li)) + K (J - 1) J/li`.

At `[b,h,b]`, the implementation recovers the original `blockEnergy` and `blockStress` without altering them. Mu, K, h and iteration bounds are inherited. They are authored teaching parameters, not fitted muscle data. The new axial bound is authored. The uncalibrated status is saved in every export. K=0 retains the original law's degenerate dilation response; it is not a plausible muscle calibration.

Let c=lx*h and S=lx²+h². For the free transverse stretch b,

`Pfree = mu/3 c^(-2/3) [2 b^(1/3) - S b^(-5/3)] + K c (c b - 1)`.

Its derivative is `mu/9 c^(-2/3) [2 b^(-2/3) + 5 S b^(-8/3)] + K c²`, positive on the declared domain. The endpoint signs bracket the scalar root at b=0.1 and b=4. Bisection has an explicit cap and the inherited 1e-5 Pa residual criterion. Eight steps usually fail that criterion; this is displayed, never promoted to an equilibrium badge. Even a passing scalar equation does not establish unrestricted 3D stability or biology. Independent symbolic differentiation and high-precision reference roots check the numerical implementation; the Lean contracts below certify only their stated product algebra.

## Forces, areas and signs

`Nx=Px H0 D0` is signed tension-positive longitudinal force. `C=-Pload A0` is compression-positive resultant on **one** controlled transverse face. `q=C/Acurrent=-Pload lload/J` is current-area applied normal traction in Pa. Opposite faces have opposite vector reactions; their magnitudes are not added into C. `sigma_i=Pi li/J` is tension-positive Cauchy stress. Applied traction is not interstitial, vascular or a measured intramuscular pressure. Full-face contact geometry is not tendon CSA or PCSA. Mean solid stress, fluid pressure, perfusion, porosity, cell packing and transport remain absent.

Direction switches Y/Z, not a measured fibre axis. For this isotropic law the switched stretch/stress/energy fields are permutations; unequal reference dimensions make full-face resultant differ. Do not interpret that geometric difference as measured anisotropy or evidence for a universal compression penalty. The baseline end force uses h=1 at the same prescribed X stretch; its signed change is computed from the law, without a hardcoded reduction factor.

The parent compression audit motivates boundary/direction/load-area bookkeeping. Its animal/human studies do not calibrate these parameters. Protocol-incomplete evidence remains qualitative. A directional active-fibre challenge, partial footprints, unilateral contact, shear transfer, force-velocity, fluid mass balance/Darcy flux and sealed/drained transport are separate future mechanisms; none is implemented or implied here. No existing area/PCSA chapter is duplicated. No held anatomy campaign, capstone retuning or biological validation occurs.

## Exact narrow proof scope

`AreaLoadContracts.lean` imports Std only and remains unregistered. Its three complete statements quantify an arbitrary type and multiplication with explicit associativity/commutativity assumptions. They establish pressure-area-work association, cross-multiplied constant-pressure area scaling and transverse product permutation. They do not prove those assumptions for real multiplication, stress differentiation, root existence, browser arithmetic, constitutive validity or equilibrium. Fresh pinned Lean compilation and axiom reports are required; historical badges are insufficient.

## Local reproduction

Run `node --test model.test.mjs` from this contribution's checkout. It imports only five source-pinned teaching modules. Build with `node build.mjs --out ABSOLUTE_NEW_DIRECTORY --proof ABSOLUTE_FRESH_PROOF_RECEIPT`. The output keeps the original relative import layout, complete source/definitions, actual state export and portable downloads. Serve that output with a local HTTP server to run controls; no external request is required. Static equations, assumptions, default solved example and full Lean source remain readable with JavaScript disabled. A checksum inventory refuses damaged runtime files before model import. Actual desktop/mobile controls, invalid-input rollback, reset, export, damage cases and PDF typography must be checked separately from model algebra.

This addition needs no mathlib cache or ONNX download and changes no numerical acceptance limit.
