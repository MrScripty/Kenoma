# Dense trajectory and bulk-compression qualification

Author lane starts at `08f5f3b7fd4b987d3f049c13fdf4338bfaa2928e`, tree `c8743d6b61236bcfeb2ef13a8172df9b1ae123b8`. Historical accepted and failed receipts are retained. The original browser operator, constitutive law, fitted stress scales and gates are unchanged.

## Localize before changing a constitutive assumption

`tools/anatomical-compression-localization.mjs` queries all 256 positive points and four corners of every original P2 element at the separately accepted dense same-old-state comparison. It records the twelve smallest sampled determinants per head, complete deformation gradients, reference/current positions, fibre stretches, stress decomposition and six longitudinal reference-volume bins. `audit/anatomical-compression-localization.json` binds its inputs and implementation by SHA-256.

The smallest corner determinant, **0.71263118**, occurs in short biceps **FJ1512**, element 212, corner 3, at the distal belly plane (longitudinal fraction 1). Its fibre stretch is **0.768758**. In this head, **1.60194%** of total reference volume has sampled J below 0.9 in the distal sixth; **0.113398%** is in the proximal sixth; none is sampled in the four middle bins. The distal sixth's mean J is **1.013694**: compression and dilation coexist even within that bin. Neither global nor regional mean volume proves local incompressibility.

For the unchanged law, let `s = tr(P Fᵀ/J)/3` denote mean Cauchy stress, positive in tension. Direct differentiation gives

\[
s_{\rm matrix}=0,\qquad
s_{\rm volume}=K\log(J)/J,\qquad
s_{\rm active}=a\sigma_0 f(\lambda)\lambda/(3J),\qquad
s_{\rm passive\ fibre}=\frac{k_f}{b}\operatorname{expm1}(b\max(\lambda-1,0))\lambda/(3J).
\]

The diagnostic checks the split against the actual material's Cauchy tensor. A separate test checks `dW(exp(t)F)/dt = 3Js` by an energy directional difference. At the worst corner, the volume contribution is **−475.409 kPa**, active contribution **+71.051 kPa**, passive-fibre contribution zero, and total mean stress **−404.358 kPa**. The isochoric matrix's trace error is below **2.33 × 10⁻¹⁰ Pa** over the short head. These are constitutive diagnostics, not measured pressure or a local hydrostatic equilibrium assertion. The active trace cannot alone explain the worst compression; endpoint transfer, authored geometry and the restricted displacement space also need investigation.

The present active potential uses **full stretch** `λ=|F f₀|`. It therefore contributes positive mean stress under isotropic dilation. This is a concrete modeling distinction to examine before a new constitutive law is selected. [Blemker, Pinsky and Delp (2005), equations 1–3 and 9, Table 2](https://nmbl.stanford.edu/publications/pdf/Blemker2005.pdf) separate dilatational and deviatoric invariants and use a logarithmic volume penalty; their muscle bulk parameter is 10 MPa. Their architecture and parameters do not validate this authored 1 MPa fixture. [Ryan et al. (2020), discussion](https://www.frontiersin.org/journals/physiology/articles/10.3389/fphys.2020.538522/full) use 1 MPa in a different formulation and explicitly identify uncertainty in volumetric constitutive behavior. Neither study licenses choosing a bulk value merely to hide local determinant loss.

Original anatomy remains the retained licensed [BodyParts3D source meshes](../data/elbow-v1/sources/bodyparts3d/) and the separately documented [Arm26 parameters](../data/elbow-v1/sources/arm26.osim). Endpoint maps, remeshed bellies, fibres and stress matches are authored/model-derived; they are not measurements of the owner's arm.

```sh
cd education
node tools/anatomical-compression-localization.mjs
node --test tests/anatomical_compression_localization.test.mjs
```

No material equation or exact Lean statement is changed by this diagnostic. It does not establish full nodal equilibrium or give a determinant bound between samples. Skin remains absent.

## Trajectory experiment contract

`tools/anatomical-dense-trajectory.mjs` solves a dense held state and then the original 0.5 kg loading/release schedule with 256-point body integration. Each increment uses only this run's accepted old coordinates, velocity, activation and time. Original 32-point target poses are nonlinear starting guesses. Contact rules refine between solves; each Newton objective remains fixed. A rejected increment preserves the old state and restores its contact rule. The runner refuses to overwrite existing evidence.

The half-step experiment splits **every** original loading and release interval, preserving matched event times. Both runs retain the original 240-iteration ceiling, 1e-4 N force gate, material parameters and finite geometry checks. `tools/verify-anatomical-dense-trajectory.mjs` uses no optimizer: it independently assembles full P2 body gradients at every accepted pose, projects them, checks the total implicit residual and all finite surface/path/sample gates, and replays temporal lineage, impulse and work bookkeeping. A preserved failed increment is also replayed and must fail a gate.

```sh
node --max-old-space-size=8192 tools/anatomical-dense-trajectory.mjs
node --max-old-space-size=8192 tools/anatomical-dense-trajectory.mjs --time-factor 2 \
  --output data/anatomical-arm-v1/audit/anatomical-dense-fine-trajectory.json
node --max-old-space-size=8192 tools/verify-anatomical-dense-trajectory.mjs
```

Execution logs are under `data/anatomical-arm-v1/review/dense-qualification/`. Trajectory conclusions require completed execution and fresh replay; a running receipt is not an accepted trajectory.
