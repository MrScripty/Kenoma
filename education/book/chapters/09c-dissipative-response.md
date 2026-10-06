# Load, hold, release: storage and viscous loss {#dissipative-load-hold-release}

The [axial bar lesson](#measure-deformation-before-choosing-a-muscle-law) made area and elastic strain visible. Keep its passive force balance, area profiles and equilibrium modulus, then add one internal strain that takes time to change. The learning objective is to distinguish **creep under held force** from **stress relaxation under held extension**, and account for recoverable storage, signed external work and viscous loss throughout unloading.

The [bulk/shear compression lesson](#compression-bulk-shear-confinement) remains a separate finite-deformation model. This lesson follows the earlier small-strain axial bar: fixed material reference area $A(x)>0$, homogeneous axial coefficients, no body force, inertia, transverse equilibrium or active stress. Displacement and strain have tensile-positive signs. It uses a standard linear solid: an equilibrium spring in parallel with one Maxwell spring–dashpot branch. Roylance's [MIT teaching notes, §4.2](https://ocw.mit.edu/courses/3-11-mechanics-of-materials-fall-1999/d173f95347f59d59dd9b7387ab4303e7_MIT3_11F99_visco.pdf) present this arrangement and distinguish creep from relaxation. [COMSOL's constitutive theory](https://doc.comsol.com/6.3/doc/com.comsol.help.sme/sme_ug_theory.06.029.html) describes the same one-branch topology and viscosity/time-scale relation. These sources motivate the model; the coefficients below are authored demonstrations, not measurements of human tissue.

## One law for the image and the ledger

Let $\epsilon$ be total axial strain and $v$ the viscous strain in the dashpot. The Maxwell spring strain is $\epsilon-v$. With fixed $E_0>0$, $E_1\ge0$ and $\eta>0$,

$$\sigma=E_0\epsilon+E_1(\epsilon-v),\qquad \eta\dot v=E_1(\epsilon-v).$$

Here $E_0,E_1$ have units Pa and $\eta$ has units Pa s. This adds memory to the passive axial law. Setting $E_1=0$ recovers $\sigma=E_0\epsilon$ and the earlier bar's same midpoint strain, displacement and stored energy for identical geometry and load.

The stored energy density and viscous loss rate density are

$$\psi=\tfrac12E_0\epsilon^2+\tfrac12E_1(\epsilon-v)^2,\qquad d=\eta\dot v^2\ge0.$$

Differentiation and the Maxwell equation give the local balance

$$\sigma\dot\epsilon=\dot\psi+d.$$

For the whole bar, $U=\int_0^L A\psi\,dx$, $\dot D=\int_0^L A d\,dx$ and external power is $N\dot\delta$. Work $W=\int N\dot\delta\,dt$ is signed; unloading can return energy to the apparatus. $D$ is cumulative lost mechanical energy and cannot decrease. Starting from rest gives $W=U+D$, with the observed finite-precision residual displayed separately.

## Constant force balance and an internal state

With constant resultant $N$, $\sigma(x)=N/A(x)$. Uniform coefficients and an initially unstrained bar imply $\epsilon=c/A$ and $v=z/A$, where $c,z$ have units m². Define the geometric compliance factor $C_g=\int_0^L dx/A(x)$, with units 1/m. Then

$$\delta=C_gc,\qquad N=(E_0+E_1)c-E_1z,$$

$$U=\tfrac12C_g\{E_0c^2+E_1(c-z)^2\},\qquad \dot D=C_g\eta\dot z^2.$$

Under imposed force,

$$c=\frac{N+E_1z}{E_0+E_1},\qquad \dot z=\frac{E_1}{\eta(E_0+E_1)}(N-E_0z).$$

Holding force therefore permits increasing extension. Holding extension fixes $c$; then $\dot z=E_1(c-z)/\eta$ and force relaxes. For elapsed hold time $s$,

$$z(s)=c+(z_0-c)e^{-E_1s/\eta}.$$

The relaxation time is $\eta/E_1$ and the force-controlled creep time is $\eta(E_0+E_1)/(E_0E_1)$ when $E_1>0$. With the default equal moduli, these are 1 s and 2 s. Increasing viscosity delays response; it does not imply a monotone change in energy lost during every finite protocol.

The runtime integrates the scalar state exactly for each constant-extension interval and each linear force ramp. It separately integrates boundary work and squared viscous rate; loss is **not** filled in from the energy residual. Stable exponential differences avoid cancellation near $E_1=0$. Each step clips at protocol boundaries before changing the imposed condition. The bar uses explicit midpoint area quadrature. For a linear taper, the independent factor is $C_g=L\log(r)/(A_1(r-1))$ with limit $L/A_1$ at $r=1$; for two equal-length segments, $C_g=L(1+1/r)/(2A_1)$. The displayed refinement error compares midpoint extension to this exact profile integral.

## Run the same finite protocol

Default reference: $L=0.2$ m, $A_1=0.0003$ m², area ratio $r=2$, $E_0=E_1=100{,}000$ Pa, $\eta=100{,}000$ Pa s and 32 midpoint cells. Load ramps from 0 to 0.6 N over 1 s, holds for 2 s, unloads from the actual reaction to zero over 1 s, then recovers at zero force for 3 s. Switching to extension hold captures the extension reached at the end of loading. The unloading ramp begins at the relaxed reaction. Both switches preserve extension and internal state continuously.

![Default force-controlled load, hold, unload and recovery. Axial displacement is magnified tenfold; reference scale stays fixed.](assets/property-dissipative.svg)

{{dissipative:sls}}

{{dissipative-table}}

During force hold, compare the extension at 1 and 3 s. During extension hold, compare those forces instead. During the latter hold, boundary work stays constant while spring storage decreases and $D$ rises. At 4 s the applied force is zero, yet extension and stored energy remain positive. Recovery consumes that storage through viscous loss. At finite time 7 s a residual extension remains; the figure does not declare full recovery.

Try viscosity 20,000 and 500,000 Pa s, then change the ramp duration while retaining the same force target. Compare the same protocol boundary times and read $U$, $W$, $D$ and the residual separately. Set the Maxwell branch off: there is no viscous loss, force hold no longer creeps, and restoring zero force restores zero strain and storage. Reverse the taper or use two equal-length areas; the strain field and extension change through $A(x)$ while the same constitutive law remains in force.

The scene uses a fixed physical reference scale, explicitly magnifies axial displacement tenfold, and colors strain against a fixed ±5% scale. Thickness is schematic; there is no predicted lateral contraction. Changing a model or protocol parameter deliberately starts a new experiment and clears time, memory and energy history. Invalid edits retain the prior valid state. Reset restores the authored defaults. Step and Play advance physical time; Run completes the bounded protocol in small animation-frame batches. Export includes the initial row and every accepted observation.

Controls restrict positive geometry, equilibrium modulus at least 100,000 Pa, force at most 0.6 N and area ratio at least 0.5. The true narrow-end strain remains at most 4% in these tensile protocols, below the unchanged 5% small-strain warning used in the earlier axial lesson. The runtime rejects inconsistent constitutive state, imposed-force schedules, held extension or energy ledger rather than transferring an arbitrary state to new coefficients.

## What the real proofs establish

The eleven declarations below quantify real local constitutive variables. They check storage and loss signs, the storage derivative given path derivatives, power balance **assuming** the Maxwell equation, the zero-branch elastic limit, and the exact held-strain exponential's derivative, bounds and weak monotonicity. They do not prove the force-controlled bar reduction, midpoint quadrature, JavaScript arithmetic or exported discrete energy ledger. Independent numerical and actual-control checks cover those implementation obligations separately. No anatomical calibration, force–velocity muscle law or completed capstone follows from this example.

{{proof:dissipative-real-storage-sign}}
{{proof:dissipative-real-dissipation-sign}}
{{proof:dissipative-real-storage-derivative}}
{{proof:dissipative-real-power-balance}}
{{proof:dissipative-real-elastic-recovery}}
{{proof:dissipative-real-viscous-derivative}}
{{proof:dissipative-real-viscous-bounds}}
{{proof:dissipative-real-viscous-monotone}}
{{proof:dissipative-real-viscous-antitone}}
{{proof:dissipative-real-held-stress-bounds}}
{{proof:dissipative-real-held-stress-decay}}

Continue to [anatomical evidence](#anatomy-is-evidence) before deciding which properties a named tissue would need. The anatomical capstone and its calibration obligations remain separate.
