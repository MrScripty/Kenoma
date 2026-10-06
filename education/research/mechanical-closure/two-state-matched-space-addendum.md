# Matched-time bin refinement: a separate limit

This read-only successor analyzes the saved matrix-exponential trajectories, with no new solve, gate or change to the [144-case experiment](two-state-benchmark-results.md). The predeclared spatial gate tested **equilibrium force**, while the timestep gate referenced each finite strain grid's exact generator. Neither alone establishes continuous-space transient accuracy.

At each domain/shift, subtract that grid's own equilibrium force and divide by `abs(delta) N/beta`. Compare the incremental response at identical times on dx=.04/.02/.01. Capacity cancels by linearity, so the normalized comparison applies to both declared pCa inputs. Signed difference arrays, exact input hashes and code hash are preserved in [matched-space-diagnostic.json](../../data/anatomical-arm-v1/review/two-state-kinetics/matched-space-diagnostic.json).

| Shift sign | Max .04→.02 difference | Max .02→.01 difference | Halving ratio |
|---|---:|---:|---:|
| Positive, both amplitudes/extents | .001599135813 | .000771895249 | .482695242 |
| Negative, both amplitudes/extents | .001368160641 | .000714167648 | .521991078 |

These are errors **between discretizations**, not independently measured continuum errors. They show approximately first-order transient refinement, despite the approximately second-order equilibrium force result. A linear center-mass split introduces an extra second moment `B abs(delta)(dx-abs(delta))` on an unbounded grid. Strain-dependent detachment then responds to this numerical broadening. This numerical inference explains why a conserved first moment at the immediate step does not make the later force history exact.

No continuum transient reference, extrapolated true trajectory or new acceptance threshold is selected after observing these values. The result supports the declared kinetic/transport operator qualification and narrows its accuracy claim. A subsequent continuous characteristic/reference calculation or more accurate conservative transport needs its own predeclared experiment before source histories are replayed. No arm timestep, anatomical mesh, physical-stability or physiological claim follows from these normalized pairwise differences.
