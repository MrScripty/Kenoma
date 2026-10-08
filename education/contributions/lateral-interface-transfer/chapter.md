# Give a lateral force a compatible load path

Local fibre stress contributes to end force through a declared mechanical load path. This standalone lab joins two passive axial macro-elements through compliant interfaces and computes equilibrium displacements, interface shear forces and end reactions. All geometry and material constants are authored engineering inputs. They are not actual human fibre dimensions, measured endomysium, recruitment or tendon calibration.

## Why this follows architecture to force

The accepted architecture-force lesson sums parallel forces and balances prescribed lateral exchange forces. It explicitly leaves interface mechanics unspecified. Here an interface force follows from relative displacement and recoverable energy. This is a new compatible **discrete** load path, rather than another packing, PCSA or stress-area conversion identity.

The preserved `research/progressive-muscle-labs.md` sequences a small-strain axial bar, effective aggregation, rate/history lessons and anatomical prerequisites. `research/measured-fibre-property-map.md` identifies missing ECM/shear load paths while keeping measured, fitted, reference-model and authored quantities distinct. This additive fixture develops that load-path prerequisite after PR13; it neither changes those briefs nor replaces their measured-data or anatomical acceptance gates.

Street's original 1983 experiment studied **single myofibres from frog semitendinosus**, partly covered by a retained surrounding-tissue splint containing cut fibres, blood vessels and connective tissue. Its abstract reports recorded lateral transmission of active and resting tension to the pinned splint. This is measured motivation for specifying a load path, not a human-biceps interface modulus or a bundle/whole-muscle calibration. Only the original abstract was verified; no quantitative parameter was extracted. [Street (1983), DOI 10.1002/jcp.1041140314](https://pubmed.ncbi.nlm.nih.gov/6601109/).

Zhang and Gao studied lateral transmission using a **computational** 2D fibre/endomysium model. Its original abstract motivates examining shear transfer and fibre endings; it is not measured material data, and this fixture does not reproduce its geometry, equations or results. Full PMC access was blocked during this review. [Zhang and Gao (2012), DOI 10.1016/j.jbiomech.2012.04.026](https://pubmed.ncbi.nlm.nih.gov/22682257/).

## Two guided elements, two localized interfaces

Let the upper element's left axial displacement be 0 and its right displacement be u. The lower element's left displacement is v and its right displacement is the prescribed delta. The left interface joins 0 to v; the right joins u to delta. Their relative slips are v and delta-u.

The drawing is a schematic displacement graph. **Two localized macro-links are an authored discretization, not distributed endomysium or measured fibre architecture.** Only axial endpoint degrees of freedom remain. Ideal guides constrain transverse motion; transverse strain, rotations, interface normal stress and moment mechanics are omitted. Therefore E is a **reduced axial modulus** for this element, not a claim about a fully constrained 3D Young-modulus experiment.

For axial element i and interface j, define

    Ki = Ei Ai / Li       [N/m]
    Cj = Gj As,j / hj     [N/m]

E and G have units Pa; A and As are reference areas in m²; L and h are positive reference length/thickness in m. The imposed constitutive laws are bilateral passive linear laws: axial force Ki times extension, and along-element interface force Cj times relative slip. They permit signed tension/compression and signed shear mathematically; the teaching controls use nonnegative displacement. The axial law uses reduced strain extension/L. The interface law uses engineering shear strain slip/h, traction G slip/h, and energy C slip²/2. Small reversible strains and the ideal guides are assumptions. Slender-element buckling and an unrestricted 3D stress field are not represented. The original-author elasticity text explains these modulus/energy conventions; the discrete reduction is original Kenoma work. [Bower, §§3.2.6–3.2.7](https://solidmechanics.org/Text/Chapter3_2/Chapter3_2.php).

## One passive energy and explicit equilibrium

At a fixed imposed delta,

    U(u,v;delta) = K1 u²/2 + K2(delta-v)²/2
                  + CL v²/2 + CR(delta-u)²/2       [J]

This is passive recoverable storage. It contains no activation device, viscosity, plasticity, damage, perfusion or fluid-transport law. It is distinct from the anatomical active solve potential.

The algebraic stationarity equations are

    K1 u = CR(delta-u),      K2(delta-v) = CL v.

For K1,K2>0 and CL,CR>=0, their denominators are positive, including zero interfaces. The closed-form solution is

    u* = CR delta/(K1+CR),   v* = K2 delta/(K2+CL).

No iterative solve is needed. Completion of squares gives a finite-dimensional minimum:

    U - Keff delta²/2 = (K1+CR)(u-u*)²/2 + (K2+CL)(v-v*)²/2,
    Keff = K1 CR/(K1+CR) + K2 CL/(K2+CL).

This identity proves that the stated **discrete quadratic energy** has a unique minimum. It does not prove differentiation, continuum equilibrium, tissue architecture or nonlinear anatomical stationarity. The separate symbolic audit differentiates this polynomial energy as an independent check; that evidence is not a Lean kernel proof.

## Follow forces through both interfaces

The upper axial force is F1=K1u; the lower is F2=K2(delta-v). The left exchange scalar is qL=CLv; the right is qR=CR(delta-u). At equilibrium F1=qR and F2=qL. End-pull scalars are

    Tleft = F1+qL,   Tright = F2+qR = Tleft = Keff delta.

They describe the same axial end-force value; the **external forces on the fixture** have opposite signs: left -Tleft and right +Tright. Guide reactions in omitted directions are not reported as a solved 3D resultant. The lab reports each residual separately and the sum of the two signed external forces.

Finite interfaces give 0<=Keff<K1+K2. With both interfaces zero, u*=0, v*=delta, U=0 and end force is zero: the lower element translates with its prescribed endpoint rather than providing a connected load path. A zero G is a deliberate disconnected-interface model, with positive geometry; it is not a physiological claim of absent ECM. A perfect tie is only the limit as interface stiffness increases without bound; no finite slider value is labeled a tie.

Increasing CR changes stiffness by

    Keff(CR')-Keff(CR) = K1²(CR'-CR)/[(K1+CR')(K1+CR)].

Thus Keff is monotone in interface stiffness. At fixed **nonnegative** delta, the end force also increases or stays unchanged. For negative delta, that signed-force conclusion reverses. An end-force change here follows the declared interface law and imposed displacement, not new fibres, a geometric bulge multiplier or a universal muscle-strength claim.

## Predict, change one property and inspect the result

The authored geometry is A1=A2=As,L=As,R=1 mm²; L1=L2=10 mm; hL=hR=0.2 mm. These macro-element dimensions deliberately have no single-fibre anatomical interpretation. The equal preset uses E1=E2=1 MPa; the unequal preset uses E1=0.5 MPa, E2=2 MPa. The controls use delta=0–2 µm and GL,GR=0–80 kPa. These are educational ranges, not biological or clinical limits. They bound axial strain by 0.0002 and interface engineering shear strain by 0.01 within the declared linear model.

At delta=1 µm and GL=GR=20 kPa, the equal preset has K1=K2=CL=CR=100 N/m. It gives u*=v*=0.5 µm, F1=F2=qL=qR=0.05 mN, signed external forces -0.1 and +0.1 mN, Keff=100 N/m and U=50 pJ.

Predict what happens when only the right interface modulus is reduced to zero. The upper branch loses its end-force path, while the lower/left path remains. Then set both interfaces to zero and explain the moving free endpoint. Restore defaults, choose unequal axial moduli, and compare individual forces rather than averaging moduli or angles. The drawing amplifies displacement by a stated factor; its stroke width conveys no material area or force magnitude.

This differs from the serial specimen's incompressible nonlinear axial law and the SLS lesson's rate-dependent relaxation. This lab has no finite-strain area update, time, hold/release trajectory or dissipative state. It provides interface compatibility and passive storage in a guided finite network. It cannot identify real ECM G from a fibre diameter, muscle-level force or a matching end-force value alone.

## Six proposed Real contracts and separate checks

`LateralInterfaceTransfer.lean` contains exactly six declarations in its own namespace. The portable lab and PDF include every complete statement and the exact source. Before a fresh source-hashed pinned kernel receipt, their status is **unqualified**. Symbolic simplification, unit tests and this prose do not supply kernel status.

The standalone audit checks six symbolic identities and exactly 24 closed-form states against independent rational reciprocal-compliance branch forces. Unit tests check SI conversion, positive geometry, zero links, quadratic energy completion and invalid inputs. Browser checks must exercise actual controls at 1200, 390 and 320 pixels, reset, rejection rollback, state export and no-JavaScript reading. Two damaged models must fail the independent audit. Actual PDF text and vector diagram labels must be at least 10 pt, with internal source/statement links and no local-file or localhost annotations.

These checks qualify only the stated contribution at its bound source. They do not qualify the 115-declaration integrated book, published site, calibration, full nodal displacement/pressure space, contact, anatomical tissue equilibrium or capstone. No existing operator, threshold, trajectory, source ledger or data asset changes here.
