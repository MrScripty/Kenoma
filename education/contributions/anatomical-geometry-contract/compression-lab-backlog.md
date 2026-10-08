# Compression and coarse-grained mechanics backlog

Research design only, 8 October 2026. This summarizes the supplied evidence scopes; it does not certify a new primary-source retrieval, a completed laboratory or a human calibration. The existing book already distinguishes measured fibre area, PCSA, volume and reference/current stress area. Keep those lessons and the accepted SLS lesson; do not add another generic bulging chapter. This contribution remains unregistered.

## Consequences for this geometry contract

The observer exports signed regional volume, approximate transported material-section area, width/depth, source attachment maps and kinematic route lengths. It does not compute local J, current fibre direction, measured pennation, perpendicular fibre-normal area, force, pressure, packing or fluid state. Near-unity average volume cannot bound local J. Atlas guides are approximations, and the inherited failed nodal force checks remain prerequisite failures. Geometry plausibility cannot validate the underlying fixture.

For an initially straight local material prism, projected area normal to its current fibre has the kinematic ratio J/lambda_f. This requires a declared material prism, deformation gradient and fibre direction; it is not the contract's arbitrary anatomical material slice. Acute deformation does not add fibres. Contractile fraction is not automatically one minus porosity. Reference force capacity must not increase merely because current section area grows; avoid repeated pennation/packing corrections.

Keep applied contact traction, solid mean Cauchy stress, incompressibility multiplier, interstitial pressure and vascular pressure separate, with explicit signs. A finite elastic bulk penalty is not fluid mass balance or measured fluid pressure. SLS relaxation does not uniquely identify drainage. The active potential can contribute mean stress; its volumetric term alone is not fluid pressure. Current fV=1 is not velocity validation. This adapter neither evaluates nor changes these inherited laws.

## Proposed sequence and implementation gates

| Proposed lab | Actual mechanism required before claiming implementation | Saved observables and checks |
| --- | --- | --- |
| Kinematic area bookkeeping, reusing existing lessons | Anisotropic transverse stretches, axial stretch, shear and declared material/fibre frames | J, lambda_f, fibre-normal projected area, anatomical slice, orientation; fixed material count; geometry only |
| Passive directional compression | Explicit energy and equilibrium solve; axial/transverse load, free/confined sides and contact footprint | Reaction, energy, local J, separate width/thickness; no inferred cell spacing or measured stiffness |
| Coarse lateral transfer | Declared effective shear connection and distributed side/end attachments; attach/detach one path | End/side resultants and power balance; no universal lateral-transfer percentage |
| Axial activation and rate response | Independently qualified activation, force-length/velocity, tendon compliance and reference/current area conventions | Timing and axial reaction; no external compression; fV=1 cannot pass a velocity check |
| Active transverse-load challenge | Fixed overall length plus sweeps of initial length, activation, pennation, top/side direction and footprint; paired constant-load/variable-area and constant-pressure/variable-area controls | Contact resultant/area, tendon reaction, local strain/J, transverse work and pennation; do not program a required positive or negative force change |
| Optional sealed/drained load-hold-release | Interstitial mass balance, Darcy flux, explicit drainage faces and solid/fluid constitutive assumptions, sizes and ramp times | Outflow, volume, fluid pressure and separate dissipation; sealed elastic and drained long-hold limits; no universal drainage time |
| Anatomical transfer | Only independently qualified mechanisms, adequate displacement/pressure spaces, full nodal stationarity, integration/timestep sensitivity, reviewed attachment/contact maps | Designated model/biological calibration targets and limitations; shape/global volume are insufficient |

For every implemented lab save reference geometry, loading history, contact/drainage boundary, measurement definitions, SI units and calibration status. A text description does not establish that its physics runs. No laboratory in this backlog is implemented by the geometry observer. This document implements no experiments or anatomical campaigns.

## Source-specific evidence and retrieval gates

The summarized evidence gives these distinctions. They are comparison-design evidence, not parameters installed in this contract:

- [Takaza 2014](https://pubmed.ncbi.nlm.nih.gov/25222870/): passive porcine transverse loading changes fibre-section shape; use unequal transverse stretches. Abstract-only preparation/count/fixation details remain incomplete; perimysial explanation is a hypothesis. Keep qualitative.
- [Siebert 2016](https://pubmed.ncbi.nlm.nih.gov/26976226/): in-situ active rat gastrocnemius distinguishes contact pressure from total transverse load. Pair pressure/load/area controls. Timing, drainage, length normalization and uncertainty details remain incomplete; reported reductions are not transferable coefficients.
- [Stutzig 2019](https://doi.org/10.1016/j.jbiomech.2019.01.011) and [Ryan 2019](https://pubmed.ncbi.nlm.nih.gov/30792071/): human stimulation/indenter studies associate architecture with longitudinal/joint output. Loading-device masses are not pressures; joint force is not isolated fibre force. Cohort overlap and full posture/protocol/drainage require recovery. Keep qualitative.
- [Sleboda and Roberts 2020](https://pmc.ncbi.nlm.nih.gov/articles/PMC6983394/): isolated bullfrog cuff compression has length-dependent force changes of both signs. Total activated force includes passive contribution. External cuff pressure does not measure internal pressure or prescribe drainage; do not impose a universal force-reduction rule or human coefficient.
- [Wheatley 2017](https://pmc.ncbi.nlm.nih.gov/articles/PMC5580854/): passive rabbit bulk-permeation experiment and separate FEBio comparison. Hydraulic permeability is m4/(N s); simulated stress is not measured stress. Recover complete drainage/boundary/constitutive specification before reproduction. Not a living-human constant.
- [Wang 2020](https://pmc.ncbi.nlm.nih.gov/articles/PMC7167341/): passive bovine long-hold indentation infers endomysial intrinsic permeability in m2 and phase forces through a model. Initial compaction exclusion, restricted drainage and scale differ from bulk rabbit tests. Do not pool the estimates or claim directly measured phase pressure.
- [Ramaswamy 2011](https://pmc.ncbi.nlm.nih.gov/articles/PMC3060596/): mouse/rat side-yoke experiments demonstrate lateral paths with changed attachment boundaries and internal length redistribution. They do not supply a universal lateral-force fraction.
- [Kirby 2007](https://pmc.ncbi.nlm.nih.gov/articles/PMC2277182/): human forearm vascular response to compression/release is not interstitial drainage, fibre swelling or pressure inferred from J. Perfusion requires a separate vascular subsystem and is unnecessary for minimal mechanical labs.
- [Ryan 2020](https://www.frontiersin.org/journals/physiology/articles/10.3389/fphys.2020.538522/full): simulated nearly incompressible fibre-reinforced blocks provide a directional/length/pennation design reference. Keep its energy, stress and reference configuration together. No tendon/aponeurosis, fluid transport, independent Kenoma validation or transferable bulk modulus follows.

Use intrinsic permeability kappa=mu_fluid k_hydraulic only with an explicitly declared viscosity and matching units. Species, tissue scale, access paths, drainage lengths and constitutive inference prevent pooling. Near-incompressibility may describe short observations with limited drainage; it does not imply a universal time constant.

Indexed original text was available during preparation, but some PMC pages/standalone figures encountered browser checks; figure images were not visually inspected. Protocol-incomplete evidence stays qualitative. Recover complete original boundary, time, preparation and uncertainty definitions before any numerical reproduction. Preserve source-specific licenses before redistributing figures or data. The cited studies do not establish Kenoma-specific coefficients, individual-fibre dynamics or anatomical validation.
