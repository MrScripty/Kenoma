# Measured fiber force and area calibration: primary-source review

**The selected rat preparation still lacks a verified same-specimen absolute force/area calibration chain.** Original acquisition text establishes that the authors report stress in kPa. That is stronger evidence for the publication's quantity than a plotting-axis label, but it does not establish the units of a particular saved `Fmax` MAT array. A separately accessible original human single-fiber study supplies a bounded metrology example, not a replacement human constant.

This new lane follows parent frozen context `bc4f24a2`. Facts and access levels are preserved in [measured-fiber-facts.json](measured-fiber-facts.json). No simulation, coefficient adoption, author code execution, old-file edit, Git mutation or PLOS source re-download occurred. Publisher S1/S2 inventory remains parent-owned and was not duplicated.

## Selected rat experiment: directly verified quantity and missing metrology

[Horslen et al. (2023), original acquisition article](https://journals.biologists.com/jeb/article/226/18/jeb245456/329515/History-dependent-muscle-resistance-to-stretch), Materials and Methods and the Statistical analyses text introducing Eq4, directly reports **kPa** for onset stress. The preparation is eleven permeabilized soleus fibers from two female rats at **22°C**, with Aurora 403 transduction and 1 kHz acquisition. Methods describe isometric activation relative to pCa 4.5, but supply no diameter/CSA measurement or sensor-to-newton calibration. Conditioning-transient subtraction isolates the test response; it does not establish passive subtraction. These are the particular inspected locations, not a claim about every file in the advertised dataset.

The earlier [pinned processing audit](../../../../research/mechanical-closure/source-code-initialization-audit.md) records division by 1000 and recording gain, followed by pCa/reference normalization. The source plotting label and publication stress terminology agree in *intent*. Independent recovery of the physical meaning of stored `Fmax` still requires upstream channel metadata: a divisor/gain operation alone cannot distinguish voltage, force, stress or a preprocessed channel. Ratios erase that distinction. An older source's area convention does not supply this experiment's individual area.

There are three distinct evidence levels:

| Quantity | Current evidence | Admitted use |
|---|---|---|
| Publication onset stress | Original acquisition HTML explicitly says kPa | Interpret the paper's reported stress unit |
| Stored `Fmax` values | Earlier MAT inspection and pinned processing; no attached unit/calibration manifest | Preserve numbers without assigning N, microN or kPa |
| Same-specimen force and area | Not recovered in this lane | No absolute physical calibration yet |

The physical chain would be `raw channel → calibrated force → declared reference-area stress → normalized reference force`. Each arrow needs the same specimen identifier, measurement configuration and tare/passive convention. Instrument model identity is useful provenance, but is not the instrument's calibration certificate or area measurement.

## Original antecedent rat studies: preliminary evidence stays separate

The acquisition article cites [Campbell (2006), Tension recovery after shortening/restretch](https://doi.org/10.1529/biophysj.105.067504) and [Campbell–Moss (2002), History-dependent mechanical properties](https://doi.org/10.1016/S0006-3495(02)75454-4). Original indexed text indicates circular-profile area estimation in both. The 2006 snippet reports area **6550±3940 um²** and pCa 4.5 P0 **79±29 kN/m²**, with geometry measured at pCa9.0. These are **snippet-only discovery facts**, not an admitted calibration: full Methods and temperature remain unverified here, and these are older specimens. Multiplying their marginal means cannot reconstruct any individual's paired force.

Access remained bounded: PMC presented a browser challenge; the original Cell PDF read returned an internal error; ordinary Europe PMC article reads were inaccessible. No challenge was solved or bypassed. The original 2002 PubMed abstract is readable, but an abstract and an indexed area sentence do not substitute for inspected metrology. Those sources therefore supply a concrete follow-up locator, not source coefficients to insert into the current rat or human model.

## Separate bounded human example: explicit metrology, no selected default

[Krivickas et al. (2011), original Methods and Table 1](https://physoc.onlinelibrary.wiley.com/doi/full/10.1113/expphysiol.2010.055269) describes chemically skinned **human vastus lateralis** fibers at **15°C**, approximately 1.5 mm segments, sarcomere length 2.75–2.85 um and pCa 4.5 activation. Width is imaged; depth is obtained from focus displacement; elliptical CSA is estimated in solution. Po is peak minus resting tension. A **20% swelling correction** is adopted for specific force, not individually measured. Original HTML/PDF text is readable; no pixel-inspection claim is made.

| Table 1 cohort mean | Po (microN) | CSA (um²) | Corrected specific force (N/cm²) |
|---|---:|---:|---:|
| Type I | 532 | 5012 | 15.5 |
| Type IIa | 549 | 4349 | 17.9 |

These rows are population summaries, not paired individual measurements. No individual force/area row was recovered. They qualify a **measurement-convention example only**; they are not current-human defaults.

For an actually paired row under that explicitly declared geometry, the independent unit check would be

\[
A_{\mathrm{ellipse}}=\pi w d/4,\qquad
T_{\mathrm{active}}=T_{\mathrm{peak}}-T_{\mathrm{resting}},\qquad
\sigma_{\mathrm{active}}=T_{\mathrm{active}}/A_{\mathrm{ellipse}}.
\]

Micronewtons convert to `1e−6 N`; square micrometers to `1e−12 m²`; `1 N/cm² = 10 kPa`. These identities are available without choosing a specimen. They do not license dividing a cohort-mean force by a cohort-mean area and calling that an individual measured specific tension. The mean of ratios is generally different from the ratio of means, and a swelling correction adds a further convention. A reference-area stress is also distinct from a current-area Cauchy stress when geometry changes.

## Measured, geometrically estimated, assumed and fitted quantities

The [frozen calibration reconciliation](../../../../research/mechanical-closure/calibration-source-reconciliation.md) and [dimensional bridge](../../../../research/mechanical-closure/dimensional-contractile-mapping.md) retain the earlier inspected original [PLOS 2026 Methods](https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1014748) classification without repeating the parent-owned source download:

| Category | Quantity | Consequence |
|---|---|---|
| Experimentally recorded | Force/stress trace and reference microscopy geometry under the acquisition protocol | Need raw units and specimen pairing before SI use |
| Geometrically estimated | Serial sarcomere count from fiber length/sarcomere length; section area under an explicit profile convention | Neither is a directly counted parallel myosin-head capacity |
| Assumed in the selected molecular model | Stroke 10 nm, head stiffness 0.5 pN/nm, paper beta 0.5 | Not independently measured on these eleven fibers |
| Fitted or source-fixed by declared model family | Kinetic functions, activation parameters and PE/SE terms | Preserve fitting/held/fixed status and family, not a generic biological constant |
| Unrecovered | Parallel head capacity/density, same-specimen force/area chain and passive denominator convention | No head-density or human stress calibration follows |

`paper_beta` denotes the article's force-normalization coefficient; pinned code `beta_attachment` names an attachment-rate field. They are not interchangeable calibration measurements. A good force/area record could establish an empirical force scale without resolving every microscopic parameter individually; it cannot by itself demonstrate that the assumed head stiffness, stroke or attachment fraction was measured. Conversely, fitting kinetics to normalized traces does not recover the erased absolute force scale or area.

## Concrete next candidate and rejection conditions

The closest candidate is a **one-fiber measurement ledger**, not another dynamic run. For the selected rat source, it needs one existing waveform's specimen identifier paired with raw-channel units, sensor calibration/gain/tare, force/reference denominator definition, diameter or width/depth measurements and their configuration, reference fiber/sarcomere lengths, bath temperature and preparation. Parent-owned S1/S2 inspection can establish whether those fields exist. If only normalized trajectories and marginal geometry summaries are present, the SI gate remains open; an older Campbell cohort cannot fill it.

The human 2011 protocol is a separate bounded candidate once an actual individual paired row is available. Its pCa, temperature, swelling and area conventions must stay attached. Until that row is recovered, the mean table is descriptive evidence rather than a numerically executable individual calibration benchmark.

Reject an attempted calibration if it (a) infers stored-channel units solely from `Fmax`/axis names, (b) combines force and area from different fibers or cohort means, (c) silently changes passive subtraction/reference area, (d) treats a skinning correction or beta as a measured specimen quantity, (e) inserts serial count as a parallel force multiplier, or (f) transfers 15°C/22°C kinetics or these cohorts into a current human arm default. These are source-linkage and dimensional rejection conditions; no new numerical model gate or tuned SI input was introduced.
