# From a lever to an arm {#from-a-lever-to-an-arm}

The mechanics chapters establish a vocabulary and a testing pattern. The anatomy chapter integrates audited evidence, and Laboratory 4 supplies a force-driven schematic elbow, activation/release, and work accounting. Laboratory 5 adds series tendon storage and an affine-block contact reaction with a same-pose LBS comparison. The separate data chapter supplies actual static atlas surfaces, a recorded normalized trial and source model parameters. Anatomical registration, spatial skin/fascia mechanics and validation still need implementation before this becomes a calibrated arm. The five laboratories are a growing teaching progression, not its completion.

## Add anatomy with provenance

An anatomical dataset needs a source, version, specimen or subject description, coordinate system, segmentation conventions, units, and permission to redistribute each included file. A citation to a paper does not grant a licence to its meshes or scans. A reusable data record should distinguish measured values, fitted model parameters, and illustrative defaults.

Before adding bone meshes or medical images, verify the relevant dataset terms at the asset level. Store permitted source metadata and derived-file provenance, including hashes and any required attribution. Schematic geometry may teach a force path, but it must not be labelled an anatomical measurement. The data chapter demonstrates these records for its licensed atlas and research trial, without patient-specific calibration.

## Add muscles and tendons with a constitutive model

An active muscle develops tensile force according to a model of activation, fiber length, shortening or lengthening velocity, and passive stretch. A contracting muscle need not shorten: it can hold length or lengthen under load. Millard and colleagues explicitly separate excitation, activation dynamics, muscle force, and tendon equilibrium in their primary model-comparison paper. Their equilibrium, damped-equilibrium, and rigid-tendon variants have different accuracy and computational tradeoffs. [Millard et al., 2013, §§2-4](#source-muscle)

A tendon can stretch beyond slack length while transmitting force. Replacing it with an inextensible connection changes the model and must be labelled. The arm capstone will need a route from joint angle to musculotendon path length and moment arm, plus a force law and an activation state. A colored bulge driven directly by an animation slider does not supply those mechanics.

## Add surface and contact as separate mechanisms

Skin weights interpolate transforms. A surface mesh can move with its bones without representing forces, volume constraints, fascia attachments, or tissue contact. A continuum or particle model must introduce its own degrees of freedom, material law, boundary conditions, and solver. Matching one pose is insufficient to validate those choices.

Elbow compression requires an explicit collision/contact model and a definition of which tissues contact. Joint reaction force from a multibody model is a net load resultant; local cartilage pressure additionally needs geometry, contact area, and tissue mechanics. The book must keep those outputs distinct.

## Medical and CAD analysis versus visual approximation

| Intended question | Evidence required | A useful comparison |
|:--|:--|:--|
| How much load reaches a joint? | Anatomical paths, inertial parameters, forces, motion, sensitivity | Rigid-body inverse/forward dynamics with stated inputs |
| Where does tissue compress? | Geometry, material data, contacts, boundary conditions, convergence | Continuum analysis and independently measured deformation |
| Does a posed surface look plausible? | Mesh and pose comparison, artist-visible defects | Linear blend skinning, corrective shapes, reduced tissue models |
| Does a reduced model run faster? | Same workload, hardware, error metric, timing method | Accuracy-cost curves, not a universal speed ranking |

This table describes research requirements, not completed validations or algorithm rankings. CAD geometry alone does not establish a tissue material law. A faster game or film model can be a good choice for an image reference while remaining unsuitable for a medical load prediction.

## Capstone acceptance contract

The arm-and-dumbbell capstone will be introduced progressively, with matched states across mechanisms:

1. A rigid skeleton and external load establish coordinates, gravity, and torque balance.
2. Muscle paths and activation produce a controlled lift; release reduces excitation and reveals subsequent dynamics.
3. Tendon and passive-muscle stretch show compliance and stored energy.
4. Skin/fascia and soft tissue add visible deformation and defined attachment constraints.
5. Elbow contact reports gaps, penetration/residuals, reaction resultants, and any justified local pressure output separately.
6. A naive linear-blend-skinning surface runs at the same skeletal poses for comparison. It has no muscle-force or contact-pressure output.

For each stage, publish resettable inputs, numerical diagnostics, a static explanation, citations, and approximation labels. Compare ablations with the same task and pose/motion inputs. Do not claim the schematic first lever is a calibrated arm or that its gravity torque predicts compression.

## Publishing architecture

The canonical chapters are listed in `book/book.json` and assembled into one Markdown book. Small build directives insert laboratories, generated experiment results, and checked proof cards. `tools/build.py` emits the assembled Markdown and an HTML edition through Pandoc with native MathML. Local bundled JavaScript supplies interaction without a runtime CDN. `tools/render_pdf.py` prints the same HTML using static diagrams and print styles; controls and WebGL canvases are excluded from print.

Quarto is a reasonable later option for chapter navigation, cross-reference management, or a larger bibliography. This initial slice uses the available Pandoc and browser runtime to keep the reproducible path compact. There is no separate hand-maintained prose for PDF and web, and no hand-maintained proof success flag.

GitHub Actions checks proofs, runs equation tests, builds the book, and tests the browser before preparing an artifact. The foundation's exact-head workflow succeeded and was independently reviewed. A separate manually requested deployment job can publish an artifact after review. The workflow does not enable Pages, change repository settings, or publish this milestone automatically. This descendant's hosted build and any later deployment require their own verification.
