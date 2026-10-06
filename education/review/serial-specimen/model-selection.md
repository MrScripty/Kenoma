# Existing coverage and the selected next model

The accepted book already demonstrates uneven axial strain from variable
reference area in `09a-properties.md`, including simultaneous extension and
compression in a reduced active fixed-end bar. That mechanism is not missing.
Its executable chart deliberately predicts no lateral stretch or current area.
The isochoric lesson prescribes uniform kinematics; the material lesson solves
one homogeneous block. Neither shows force-driven, unequal local 3D shapes and
their individual volume measurements for different reference areas.

The new lesson therefore uses **two separate homogeneous rectangular blocks**,
not a continuous tapered solid. Ideal bilateral traction-distributing end
fixtures transmit equal signed axial force while permitting tangential sliding.
A massless spacer has fixed length, while its end positions move with the blocks.
The square reference sections have areas A1 and A2=r*A1. Each block has reference
length 0.025 m by default. The connection visibly separates the blocks so different
lateral stretches do not imply an incompatible continuous material interface.

Each block uses an incompressible isotropic neo-Hookean energy. Volume preservation
is a material constraint, not a finite bulk penalty or a consequence of force
balance. For F=diag(lambda,b,b), the constraint and symmetric free sides give
b=1/sqrt(lambda). The full Cauchy stress is sigma=-p*I+mu*B; vanishing lateral
tractions give p=mu/lambda. This p is an incompressibility multiplier, not an
axial plate pressure. The resulting relations are

- W=mu/2*(lambda^2+2/lambda-3), in J/m³;
- nominal P=mu*(lambda-1/lambda^2), in Pa;
- force N=A0*P, shared by both blocks;
- axial Cauchy stress=lambda*P=N/currentArea;
- currentArea=A0/lambda, currentLength=L0*lambda, volume=A0*L0.

The positive-stretch force law is strictly increasing: dP/dlambda=mu*(1+2/lambda^3)>0.
Numerical bisection solves its positive root and exposes finite-cap residuals.
The actual 3D vertices generate the independent closed-triangle volume and the
measured area and length. Total-volume agreement alone is insufficient: a
counterfactual with local volume ratios 1.1 and 1-0.1/r has unchanged weighted
total volume but violates each block's constraint and free-side stress.

Bounds: mu=500–5000 Pa, A1=0.0003–0.001 m², r=0.5–4, signed N=-0.1–0.1 N,
reference block length 0.01–0.04 m, and 8–64 bisections. The fixed positive bracket
lambda=0.6–1.75 covers every bounded input: at the least A0*mu=0.075 N its endpoint
forces are -0.163333 N and +0.106760 N. Defaults retain the earlier authored shear
parameter 1500 Pa. No existing equations, calibration or acceptance limit changes.

The material framework is checked against the original author's
[A. F. Bower, Applied Mechanics of Solids, §§3.5.4–3.5.6](https://solidmechanics.org/Text/Chapter3_5/Chapter3_5.php).
The assembly, controls and worked quantities above are this lesson's derivation.
An independent model review confirmed the law and required bilateral fixtures,
moving spacer positions, and the pressure/axial-stress distinction before coding.

The exact real-number claims concern this homogeneous constitutive reduction.
They do not establish continuous-taper fields, JavaScript correctness, mesh-volume
measurement, unrestricted 3D stability or anatomical-capstone qualification.
SLS `0682249` and PR 8 remain frozen; this work is on a separate branch.
