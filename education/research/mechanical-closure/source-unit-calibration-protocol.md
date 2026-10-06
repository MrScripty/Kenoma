# Source units and calibration identifiability: bounded audit protocol

Preserve frozen milestone **bc4f24a2ea72af3a0a4f1bf7b270ec9f3fe999bf** and its source, histories, failures, figures and qualification limits. This successor performs source research and exact dimensional/algebra checks. Production anatomy, book and Lean remain unchanged. No coupled kinetics, loading/release, fit, coefficient search or anatomical solve is authorized by this protocol.

## Evidence selection

Keep three sources of inputs distinct: measured fiber properties under a specified preparation/temperature/area protocol; fitted or assumed parameters from one pinned kinetic/elastic model; and whole-muscle geometry/load-sharing estimates. A source-population mean is not an individual observation or a hard specimen interval. The product of mean stress and mean area is not measured mean force. A live human fiber, elderly cadaver architecture and a 22°C permeabilized rat median model cannot silently become one calibrated specimen.

The original [PLOS pixel audit](original-plos-table-visual-audit.md) supplies preserved Eq14–22/Table2–3 pixels for DOI10.1371/journal.pcbi.1014748. The author's pinned implementation is **8c766dfb308051309193e7290ddd0bac3b726d11**, tree **a802ec6f7299d0745dfab1d5b715a3d9b7aa6f20**. It predates the final article. Source code is inspected read-only, not imported, executed or redistributed. Publisher coefficients, raw code coefficients, runtime/fitting variants and individual MAT files retain their separate provenance.

Fresh failed public-source access is preserved and stopped at the boundary. No credential, proxy, permission or network-policy change follows an error. The original parameter pixels already committed remain valid evidence when a temporary PDF is missing or a new request fails.

## Declared conditional coordinate and force map

For a selected code variant, let C=Fref·Fscale be its **unknown physical force multiplier** in N, ell=Lref/Gamma its **unknown physical length per internal coordinate** in m, and u=(LCE−Lorigin)/ell. Neither physical reference force nor length is assigned from an unlabelled source variable. The smooth PE fitting/soft branch and SE function have the mathematical forms below. The author’s PE runtime switches to a linear approximation at K(u−u0)>=10; this audit does not assert exact parity with that complete piecewise runtime. Abstract sigma/rho correspond conditionally to code kse0/kse, without asserting published coefficient parity. The audited forms are

```
PE_internal = kpe/K · log(1+exp(K(u−u0)))
SE_internal = sigma · (exp(rho·v)−1)
v = (LSE−LSE0)/ell
```

Thus PE force prefactor is C·kpe/K, smoothing width ell/K, asymptotic physical slope C·kpe/ell, and SE exponent per metre rho/ell. These transformations do not establish that published Table3 entries are those raw code coefficients. Publication Eq19's force-prefactor/stiffness label and inverse-xps conventions remain explicit alternatives until their normalization is identified.

A change from Gamma_old to Gamma_new preserving the SAME smooth PE force curve at fixed physical Lref requires kpe_new=kpe_old·Gamma_old/Gamma_new, K_new=K_old·Gamma_old/Gamma_new, and u0_new=u0_old·Gamma_new/Gamma_old. The SE coefficient sigma is unchanged and rho_new=rho_old·Gamma_old/Gamma_new for its corresponding re-expression. This is an elastic coordinate identity, not a claim that the source reproducer performs all those changes or that the entire kinetic model is invariant.

For the publication head map, gamma=2Ns·dps is a length, whereas Gamma=Lref/gamma is dimensionless. If and only if Lref=Ns·ls_ref, Gamma=ls_ref/(2dps). Parallel head count H determines Chead=H·kCB·dps; serial Ns adds link energy and length while transmitting the same force. Stress conversion needs a declared area/configuration. Unprojected PCSA=V/Lf,opt and projected force area FCSA=PCSA·cos(alpha) are separate conventions; apply the cosine once.

The frozen-head energy check uses a physical increment ΔL, delta=ΔL/(2Ns·dps), B=integral n dx, Q=integral (1+x)n dx and E0=integral .5(1+x)^2 n dx. Stored serial energy is 2Ns·H·kCB·dps²(E0+Q·delta+B·delta²/2). Its derivative is H·kCB·dps(Q+B·delta). This assumes held populations, uniform serial strain, full support and no boundary loss; it is not the derivative of a dynamically evolving activation law.

## Predeclared verification

After this protocol and the independent audit implementation are committed, execute the new **symbolic unit audit once**, preserving its protocol commit, source hash and raw result. Use exact SymPy identities and integer SI dimension exponents; no numerical ODE reference or machine-precision convergence comparison occurs.

- Verify the 12 declared coordinate, PE/SE derivative/re-expression, force-area/pennation and frozen-head energy/force identities exactly.
- Reject four deliberate dimensional misinterpretations: using Gamma as a physical gamma in a length ratio; treating Eq19's prefactor as N/m without a length factor; inserting a dimensionful inverse-length rho into an already dimensionless normalized exponent; and treating a force as stress without area.
- Retain two dimensionally valid but mechanically incorrect witnesses: multiplying transmitted force by serial count, and applying pennation cosine twice. Unit agreement alone cannot reject either mistake; the work/topology identities must distinguish them.
- Check the source-assumed head-scale conversion exactly: .5 pN/nm ×10 nm=5 pN, and the conditional source reference-coordinate ratio 2.6 µm/(2×10 nm)=130. These are model-scale illustrations, not measured human calibration or the specimen-specific SI scale of an individual fit.

Every symbolic equality must simplify to zero. Each intended dimensional misuse must raise the declared dimension error; failed checks stop and retain their partial receipt, exception and admitted check list. No retries or altered criteria follow a failure. Existing output must not be overwritten.

## Physical-example admission

Implement a numerical physical calibration example only if the original evidence supplies a coherent same-preparation record with force or stress units, area/configuration if required, passive/tare convention, reference denominator and geometry, and a compatible model/version/temperature. Unsupported fields remain missing. If those conditions fail, the deliverable is the supported-input/missing-data matrix and the conditional unit audit, with **no physical calibration selected**. No new SI or human default may be chosen merely to make the normalized circuit mechanically plausible.
