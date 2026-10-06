# Additive interpretation correction: the frozen negative witness is weak-discrete

**The −9477.446195 N/m relaxed witness in frozen commit `f2504e871b9ee4b536e94405612efa2436d39b45` establishes a negative direction of the finite-P1 weak discrete model. It does not, by itself, establish a defective long-time continuum constitutive law or human muscle instability.** This correction supersedes the broader physical-law interpretation in the [earlier results](matched-force-contractile-state-results.md) and the associated protocol conclusion. It preserves those documents, every numerical receipt, old gates, tests and renders byte-for-byte. Pair the frozen result/figure with this correction when presenting its interpretation.

## Different volume operators

The [research mixed protocol](full-p2-p1-protocol.md) and [research implementation](../../tools/full_p2_p1.py) explicitly eliminate finite P1 pressure, producing

```
Evolume,weak = (K/2) b^T M^-1 b
             = (K/2) ||ΠP1 log J||²_L2(V0).
```

The [production material contract](../../web/anatomical-material.mjs) instead defines pointwise volume storage `K/2 (log J)^2` and its pointwise stress `K log J F^-T`, giving

```
Evolume,pointwise = (K/2) ||log J||²_L2(V0).
```

The projection is the reference-volume L2 projection with the SAME research quadrature, basis and mass matrix. These operators agree in energy and first variation at an exact affine patch, because its constant log J is represented by P1. Their tangents on general P2 perturbations differ. At that affine patch the missing pointwise term is

```
delta²(Epointwise-Eweak)[v,v] = K ||(I-ΠP1) delta log J[v]||² >= 0.
```

A small pointwise pressure mismatch at the unperturbed state does not bound this missing directional tangent. Here the archived witness has nonzero pointwise volume change, with directional log-J RMS 16.859294142625853/m. Exact held caps, accurate gradients and passing original weak-discrete tests establish properties of the declared discrete problem; they do not change its volume operator into the pointwise contract.

## Checked scalar diagnostic, not a new Hessian

The read-only audit reconstructs `delta log J = tr(F^-1 delta F)` on the SAME frozen accepted coordinates and unit Euclidean nodal witness, then independently projects it through `M^-1`. No equilibrium, Hessian, spectrum or state/time update is computed.

| Quantity | N/m |
|---|---:|
| Archived weak-discrete witness | −9477.446195040056 |
| Pointwise volume Gram `K integral (delta log J)^2` | +15917.20474330439 |
| P1-represented volume Gram | +22.70469677101402 |
| Positive projection complement | +15894.50004653338 |
| Archived witness plus complement, algebraically | +6417.05385149332 |

The direct complement integral agrees with full-minus-represented volume Gram under the fixed 1e-8 N/m diagnostic gate. Reconstructed RMS and represented response agree with the frozen receipts. The audit binds all seven input/source files to frozen f250, with exclusive new output under `review/matched-force-volume-interpretation/`.

**The +6417.054 N/m value is only an algebraic diagnostic.** The actual archived state is slightly non-affine, with pointwise log-J projection mismatch RMS approximately 6.48e-8. For a fixed reference projection Q=I−Π, the full Hessian difference at a general state also contains `K <Q log J, Q delta² log J[v,v]>`. A pointwise operator changes the force field and prestress as well. This audit does not recompute those terms, demonstrate stationarity for the changed operator, or inspect all directions. Even an exact positive value in this one direction would not prove a positive full spectrum, dynamical stability, continuum convergence or physiological validity.

## Corrected conclusion and hold

The original active axial force–length contribution remains −11844.433632 N/m within the weak-discrete decomposition, and carried contractile density still supplies the independently checked fast material-point response at matched initial force. The density's relaxed state returns to the original stress map; the frozen weak-discrete operator therefore retains its negative direction. Those numerical statements remain supported.

The broader conclusion that this particular block witness proves an inadequate long-time physical law is withdrawn. Underrepresented volumetric tangent is a material alternative explanation that the pressure-space/operator comparison must resolve before further constitutive interpretation or changes. The earlier fixed-transverse material-point and powered energy ledgers remain bounded educational results, rather than whole-tissue or human validation. Earlier strict pointwise volume-preserving witnesses, if used, require their own correctly scoped analysis; this correction supplies no new conclusion about them.

**Hold further constitutive changes while the separate pressure-space comparison is selected.** No pressure-space experiment is duplicated here; no production, book, Lean or protected file changes occur. Bulk/compression credibility and the self-consistent dense loaded-arm trajectory remain unqualified. There is no anatomical or clinical stability claim and no skin work.

Evidence: [read-only checker](../../tools/check_matched_force_volume_interpretation.py), [scalar diagnostic receipt](../../data/anatomical-arm-v1/review/matched-force-volume-interpretation/volume-complement-diagnostic.json), raw execution log/timing and preservation audit in that same new directory. This correction follows directly from the repository's two declared mathematical volume operators; it introduces no new anatomical/mechanical coefficient or external physiological premise.
