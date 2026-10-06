# Independent dimensional bridge audit

**The symbolic force, length and series identities are consistent with the declared article convention and aligned one-dimensional topology. No equation defect was found.** This is a derivation review, not a kinetic experiment, source-code replay, human calibration or stability qualification.

Reviewed 2026-10-06: [contractile_dimensional_bridge.py](../../tools/contractile_dimensional_bridge.py), its existing [symbolic receipt](../../data/anatomical-arm-v1/review/dimensional-contractile-mapping/symbolic-bridge.json) and [dimensional mapping memo](dimensional-contractile-mapping.md). The receipt's source SHA-256 matches the inspected tool: `fb91c046c84de75bf6d0f65d3b92794f1cd6657b3f4a0e70fed504bd47a4e232`. The existing symbolic PASS was inspected; the tool and prior simulations were not rerun.

The source identities are the [original article's equations 3–4, 17–18 and 22](https://journals.plos.org/ploscompbiol/article/file?id=10.1371/journal.pcbi.1014748&type=printable), as retained in the [extracted-source evidence](source-rendering-evidence.md). They give centered strain x, force moment Q=∫(1+x)n dx, physical serial scale γ=2Ns dps, and normalized force Q/β. Their rendering and original Table 2/3 column alignment remain visually unverified.

The dimensional aggregation T=H kCB dps Q agrees with T=F0 Q/β only under the explicitly declared calibration constraint H kCB dps=F0/β. H counts parallel capacity at one transmitting section; serial count Ns does not multiply force. With Lref=Ns ℓs, Lref/γ=ℓs/(2dps), giving 130 for the stated 2.6 µm and 10 nm illustration. The frozen attached-population stiffness is F0 B/(βγ)=H kCB B/(2Ns), in N/m. This derivative assumes a translation without loss through an artificial strain boundary. It does not supply a relaxed force–length slope.

For a homogeneous aligned bundle, Acurrent=Aref J/λ yields σ=λP/J. The memo's corresponding tensors P=(T/Aref)t⊗a0 and σ=(T/Acurrent)t⊗t satisfy σ=PFᵀ/J. A changing area convention, pennation or nonuniform force path requires its own mapping; the scalar identity does not select one.

The series calculation follows by differentiating the massless balance TSE=TCE+TPE, with fixed conversion parameters and instantaneous local slopes Ks and Kp. If qkin denotes the held-CE reaction derivative of Q, then

\[
\dot Q=q_{\rm kin}+Bv_{\rm CE}/\gamma,\qquad
v_{\rm CE}=\frac{K_s v_{\rm total}-F_0q_{\rm kin}/\beta}
{K_s+K_p+F_0B/(\beta\gamma)}.
\]

Here **qkin must include the entire force moment's reaction derivative**, ∫(1+x)r(x)dx, where r is attachment minus detachment at fixed CE length. It is generally not just the attached-fraction rate ∫r dx. In a bin-mass implementation it is Σ(1+xi)ri. The source tool leaves qkin symbolic, so this is an implementation condition rather than a detected algebraic defect. With conservative transport on a finite strain domain, any prescribed boundary detachment changes the force moment and must be recorded in addition to the interior BvCE/γ term. Treating that boundary effect as kinetics requires an explicit definition.

The denominator must be nonzero. Physical assumptions Ks>0, Kp≥0, B≥0 and positive F0, β and γ make it positive. At qkin=0, the end stiffness is Ks(Kp+Kfast)/(Ks+Kp+Kfast), correctly the series combination of SE and the parallel PE/frozen-CB slope. This conditional fast tangent is not a proof of dynamic stability or of every continuum mode.

No human force capacity, area, head density, passive/series fit or overlap relation was selected. The [visual blocker](visual-parameter-column-audit.md) remains the explicit prerequisite for the next coupled release experiment. The separately corrected visual receipt distinguishes pinned commit `8c766dfb308051309193e7290ddd0bac3b726d11` from actual tree `a802ec6f7299d0745dfab1d5b715a3d9b7aa6f20`; both identities were independently checked through ordinary authorized GitHub reads. No frozen packet, source code, Git state or simulation output was changed in this audit.
