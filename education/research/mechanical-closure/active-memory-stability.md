# Positive fast stiffness is not a long-time stability certificate

This parameter-free scalar thought experiment sharpens the [active-control recommendation](active-stability-controls-results.md). It introduces **no fitted coefficient or selected muscle law**. It is not a recreation of the frog transient experiments or an anatomical simulation. The original full-nodal negative witnesses and all force/geometry gates remain unchanged.

Consider a displacement perturbation x with positive modal mass M, nonnegative damping c, signed relaxed stiffness kr, an external end-separation stiffness ks, and a passive Maxwell branch q with nonnegative stiffness km and positive relaxation time τ:

`M xdd + c xd + (kr+ks)x + q = 0`

`τ qd + q = τ km xd`.

Stiffnesses have N/m units, c has N s/m, M has kg and τ has s. No numerical values for M, c, km, ks or τ are assigned. The fast incremental stiffness is kr+ks+km; the relaxed stiffness is kr+ks. The declared two-variable characteristic determinant is

`P(s)=Mτ s³+(M+cτ)s²+[c+τ(kr+ks+km)]s+(kr+ks)`.

If **kr+ks<0**, P(0)<0 and P(s)→+∞ for positive s. Continuity guarantees a positive real root regardless of the admissible passive memory or damping. Thus a positive fast stiffness alone cannot stabilize a negative relaxed scalar mode over long times. This is a falsifiable limitation on the model class, not an estimate of a human instability rate.

If **kr+ks>0** and c>0 or km>0, all cubic coefficients are positive and the Routh–Hurwitz margin is

`(M+cτ)[c+τ(kr+ks+km)]−Mτ(kr+ks)`

`=Mc+Mτkm+c²τ+cτ²(kr+ks+km)>0`.

The declared scalar linear system is then asymptotically stable. At kr+ks=0 a zero root remains. For positive total relaxed stiffness with c=km=0, the roots include a neutral oscillatory pair; they are not asymptotically stable. [The exact SymPy receipt](../../data/anatomical-arm-v1/review/active-stability-controls/memory-stability-symbolic.json) verifies the determinant, margin and undamped factorization. It is not a Lean theorem or nonlinear/full-continuum stability proof. The initial symbolic run failed because expanded and factored expressions were compared structurally; its [failure receipt](../../data/anatomical-arm-v1/review/active-stability-controls/memory-stability-first-failure-receipt.json) and log remain preserved. The correction compares algebraic identities and changes no equation or physical coefficient.

For the current descending homogeneous **global axial** mode, kr=−484.557192 N/m from the unchanged material derivative. A scalar end-separation spring needs ks>484.557192 N/m to make this model's relaxed total stiffness positive; no such coefficient is selected. The actual zero-cap interior witnesses do not change end separation, so their effective ks is zero for that apparatus. An end-only spring cannot cure those directions through this mechanism.

[Ford, Huxley and Simmons's original abstract](https://pubmed.ncbi.nlm.nih.gov/6973625/) supports separating rapid stiffness/recovery from steady tension, but supplies no Maxwell law or human parameters here. [Gordon, Huxley and Julian's original study](https://physoc.onlinelibrary.wiley.com/doi/abs/10.1113/jphysiol.1966.sp007909) supports retaining a descending isometric relation. **The inference here** is that matching those two observations requires a declared state/evolution model and tests of both limits; appending an arbitrary passive relaxation branch to the unchanged negative local relaxed law is not sufficient.

The next contractile/series-state candidate must therefore declare which relaxed force path and spatial/internal states differ from the present instantaneous local fL law. Validate fast, relaxed and coupled dynamic responses separately. Distributed architecture, activation-dependent passive behavior or active feedback are distinct hypotheses requiring original-source support, calibration and controlled tests. Do not claim that one of them stabilizes this arm without actually defining and verifying it. This calculation supplies a necessary control-class distinction, not a selected physiological repair.
