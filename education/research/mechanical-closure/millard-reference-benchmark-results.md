# Bounded Millard reference benchmark: first executable cases

The [prospective protocol](millard-reference-benchmark-protocol.md) passes its source-kernel, activation, force-balance, matched-time and work checks while **retaining descending-limb instability**. This is an educational source-reproduction benchmark, not a full OpenSim simulation, human-biceps calibration, continuum coupling or arm stability result. The [constitutive/reference decision](constitutive-reference-decision.md) remains the physiological research boundary.

## Source and executable scope

Official OpenSim 4.5.2 resolves to commit **`5bc7d3308eda742690f485ec060bfe725a349fa6`**, tree `19ea9bb15e9c43a3f7506966ea6ac0ca14002df1`. Twelve unchanged source/license/notice files are hash-bound in the [upstream manifest](../../data/millard-reference-v1/upstream/manifest.json). Apache-2.0 licensing, source equations, units, numerical floors, finalization and initialization limits are documented in the protocol. The original [Millard et al. paper](https://nmbl.stanford.edu/publications/pdf/Millard2013.pdf) and [pinned implementation](https://github.com/opensim-org/opensim-core/tree/5bc7d3308eda742690f485ec060bfe725a349fa6) are distinct from our educational dimensional parameters.

The C++ harness extracts original curve-factory, control-point, activation-derivative and fiber-force function bodies. Its authored storage/Bernstein/root/RK4 shim does not instantiate the OpenSim runtime. Python independently translates the curve construction and uses SciPy BPoly, Brent root inversion, DOP853 and Radau. This comparison checks reproduction and independent numerical paths; it does not independently validate the upstream biological experiments.

Parameters are F0=100 N, optimal fiber length=.1 m, tendon slack length=.2 m and zero pennation, plus the audited source defaults. The damped finalizer sets the active FL floor to zero but retains minimum activation .01. Beta=.1 is a source default, not a new fitted stabilizer or measured tissue viscosity. Velocity inversion uses a predeclared bracket [−10,10] in normalized velocity; a missing bracket or invalid state raises instead of advancing. The observed held-case velocities range −.157852 to .047383, well inside the bracket. Source lower-length clamping and general slack/buckling transitions are not reproduced. All tested trajectories remain above the source lower-length bound.

## Numerical evidence

| Check | Observed result | Declared gate |
| --- | --- | --- |
| Original/native vs Python control points | 2.22045e−16 | <=2e−12 |
| Curve values / derivatives | 4.13558e−15 / 3.15248e−13 | <=2e−12 / 2e−8 |
| Active FL derivative finite difference | 2.08322e−9 | <=2e−8 |
| Original activation derivative / independent branch solution | 0 / 7.26869e−12 | <=2e−12 / 2e−8 |
| Maximum algebraic force residual | 2.33147e−13 N | <=1e−7 N |
| Native fine RK4 vs DOP853, matched activation/q | 1.38709e−10 | <=2e−6 |
| Native RK4 .0001/.00005 s refinement | 2.79495e−10 | <=2e−6 |
| DOP853 vs Radau | 1.40934e−10 | <=2e−6 |
| Independent static initialization | q=.9999999999999994; constructed residual 4.55885e−13 N | q error <2e−12; residual <=1e−7 N |
| Adaptive work balance | 2.82118e−10 J | <=1e−5 J |

All 14 declared/executable checks pass; five additional regression tests pass. Raw values and statuses are in [summary.json](../../data/millard-reference-v1/review/summary.json), with native/Python CSV histories, generated native source and execution logs in the same directory.

At held total length .3012157591 m, the supplied excitation pulse .05→.35→.05 produces separate activation, fiber-length and actual tendon-force histories. Force rises from 5 N to 34.8034 N; minimum q=.963784. At .30 s activation is still .070524 and force 7.30968 N. The run does not claim complete relaxation or a long-time equilibrium. Actual force was never prescribed in this case.

For the separate force-loaded fixture, a=1 and q=1.10 give external force 97.4420 N. Total normalized static slope is **−.959462425**, or **−959.462425 N/m** with the educational F0/lopt scale. The dynamic growth rate is **1.963344473 /s**, independently reproduced by a finite-difference rate **1.963344473 /s**. Initial ±1e−4 q perturbations grow in magnitude by **1.103204 / 1.103090** over .05 s. Tendon compliance follows the fixed external force while total length is free to move. This is a massless force-loaded experiment, not a target-force controller, held-length instability certificate or human-arm result.

Held-length passive storage changes by .002338478752 J. Integrated active mechanical input minus source damping dissipation is .002338479034 J. This bookkeeping excludes ATP/chemical closure and heat. External endpoint work is zero for the held-length case.

## Preserved failures and limits

The first C++ build encountered an ambiguous authored `clamp` shim versus std::clamp; its log is retained. The source function body was unchanged, and resolving the shim's member lookup fixed the build. The first Python reporting attempt could not serialize NumPy boolean statuses; that log is retained. Neither was a mechanical failure.

The **1 ms trapezoid work estimate failed** the unchanged 1e−5 J gate with error **4.38684e−5 J**. Its failed summary and complete log remain. Adaptive integration of the same dense trajectory, split at the already declared excitation transitions, gives the passing work result above. No equation, coefficient, ODE tolerance, step schedule or acceptance budget was relaxed. The current summary explicitly retains both coarse and adaptive work estimates.

The attempted q=.4 state is rejected before a derivative is returned and no continuation/time advance is performed. This local guard is not a claim of testing whole-arm rollback. General pennation, the upstream Newton initializer and velocity-sharing algorithm, minimum-length unilateral dynamics, slack transitions, target-force feedback and variable-mass mechanics remain outside this first deliverable. No original pressure, material or contact gates were modified. All preexisting tracked files, frozen evidence and book-release files are preserved.

## Reproduce and inspect

From the repository root, with existing NumPy/SciPy/Matplotlib and g++:

```sh
OPENBLAS_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1 python3 education/tools/millard_source_oracle.py --output education/data/millard-reference-v1/review
OPENBLAS_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1 python3 education/tools/millard_reference_benchmark.py
OPENBLAS_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s education/tools -p test_millard_reference_benchmark.py -v
OPENBLAS_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1 MPLCONFIGDIR=/tmp/kenoma-millard-mpl XDG_CACHE_HOME=/tmp/kenoma-millard-cache python3 education/tools/millard_reference_figure.py
```

The supplied [PNG](../../data/millard-reference-v1/review/reference-cases.png), [one-page PDF](../../data/millard-reference-v1/review/reference-cases.pdf) and PDF raster were visually inspected: titles, legends, axis units, descending perturbation signs, error metrics and scope footer are readable. No book figures were changed. Saved outputs are frozen review evidence; rerun in a separate checkout/output copy when preserving those exact bytes is required.

The next independently bounded extension would be a declared target-force feedback experiment or a reduced actuator plus external mass/inertia, with its own protocol and comparison. Neither requires pretending to have human reference-pose calibration. Continuum coupling and skin remain separate, unqualified work.
