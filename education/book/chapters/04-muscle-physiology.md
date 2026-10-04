# Muscle pulls through a changing path

A muscle is not merely a red spring. An actuator model needs an input, internal state, force law, geometry and a clear statement of what it omits. Begin with a line of action because it makes loading understandable. Add a three-dimensional continuum only when the question requires internal deformation, local stress, broad attachments or contact.

The benchmark paper by [Millard, Uchida, Seth and Delp](https://pmc.ncbi.nlm.nih.gov/articles/PMC3705831/) compares equilibrium, damped-equilibrium and rigid-tendon models against numerical and biological tests. Its measured speedups belong to its hardware, integrators, tolerances and test actuators. They are not transferable frame-rate promises for an arm demo. Its central practical lesson here is to make tendon assumptions and numerical singularities explicit.

## 1 Excitation is not instantaneous force

Let u ∈ [0,1] be neural excitation and a ∈ [0,1] be activation. A deliberately simple teaching model is

$$\dot a=(u-a)/\tau.$$

For constant u and τ during a step, use the exact update

$$a_{n+1}=u+(a_n-u)e^{-h/\tau}.$$

This avoids the overshoot that a large explicit-Euler step can produce. Separate rise and fall constants can be added, with the switch rule specified. This first-order filter is an illustrative activation model; its time constants must be fitted or sourced before making quantitative physiological claims.

**Reader exercise.** Pulse u while plotting u, a and force. Keep length fixed first. Then move the endpoints without changing u to show that activation alone does not determine force.

## 2 A Hill-type actuator is a collection of functions

Define fiber length l_f, optimal fiber length l_opt, fiber velocity v_f = l̇_f and maximum isometric force F₀. Adopt positive v_f for lengthening. One model family has

$$F_f=F_0\left[a\,f_l(l_f/l_{opt})\,f_v(v_f/v_{scale})
+f_{pe}(l_f/l_{opt})+\beta(v_f/v_{scale})\right].$$

Here f_l is the active force-length curve, f_v the active force-velocity curve, f_pe passive force-length response and β a dimensionless damping coefficient under this normalization. Choose v_scale explicitly, often from optimal length times a maximum-shortening-rate parameter. A model that omits force-velocity effects must not claim to predict the load dependence of shortening speed.

For a toy first lesson, f_l can be a smooth bell curve and f_pe a tension-only polynomial. Label those curves as authored teaching functions. A Gaussian width is a design parameter, not a measured human constant. Later replace the toy law with a specified, tested musculotendon formulation and its published parameter conventions.

Concentric contraction means active shortening; eccentric contraction means active lengthening; isometric means fixed length of the specified quantity. Fixed joint angle does not necessarily imply fixed fiber length when a compliant tendon stretches. A motion label must say whether it refers to whole musculotendon length or fiber length.

## 3 Tendon and pennation add internal state

For a simple pennated actuator,

$$l_{MT}=l_T+l_f\cos\alpha,\qquad F_T=F_f\cos\alpha.$$

The equal-force relation assumes the massless equilibrium idealization of this model. A dynamic tendon or muscle-mass model requires its own momentum equations.

A tendon force law normally depends on normalized tendon length or strain and is tensile. A teaching spring can use F_T = k_T max(0,l_T−l_slack), while a research model should use a specified nonlinear curve, transition smoothing and fitted slack length. A tendon should not become a compressive strut just because its length falls below slack length.

If pennation is modeled using constant thickness h_f,

$$h_f=l_f\sin\alpha,\qquad
l_f\cos\alpha=\sqrt{l_f^2-h_f^2}.$$

Therefore

$$\dot l_{MT}=\dot l_T+\dot l_f/\cos\alpha.$$

The last term is not generally l̇_f cos α because α also changes. The model becomes poorly conditioned as cos α approaches zero; use a physiologically justified domain and explicit failure reporting.

A rigid-tendon approximation removes tendon stretch from the state. It can be useful, but it changes fiber operating lengths, velocities and stored elastic energy. It is a model simplification, not just a faster integrator. Do not switch tendon assumptions silently when moving from offline calculations to an interactive preview.

::: {.keep-together}
**Original equilibrium pseudocode**

```text
muscle_step(path_length, path_speed, excitation, old_state, h):
    advance activation with the specified activation dynamics
    establish admissible fiber-length and pennation bounds
    initialize tendon and fiber state consistently at the starting pose
    evaluate tendon tension from tendon length
    solve the chosen fiber/tendon equilibrium equation
        with safeguarded root finding and the model's velocity convention
    reject or reduce h on loss of admissibility or failed convergence
    return tendon tension, fiber state, stored energy, work and residual
```
:::

This is a solver contract, not an interchangeable formula for every Hill model. For a damped equilibrium formulation one may solve for fiber velocity and integrate fiber length. A fully implicit formulation may solve the next fiber length and velocity together. State which unknown is being solved and report the normalized force residual.

## 4 The signed moment arm comes from virtual work

For musculotendon length l_MT(**q**), positive tension F_T resists increasing length. Virtual work gives

$$\delta W=-F_T\,\delta l_{MT}
=-F_T\sum_j\frac{\partial l_{MT}}{\partial q_j}\delta q_j.$$

::: {.keep-together}
Thus

$$Q_j=-F_T\frac{\partial l_{MT}}{\partial q_j}
=r_jF_T,\qquad r_j=-\frac{\partial l_{MT}}{\partial q_j}.$$
:::

For a rotational q_j, r_j has units of metres. For a translational coordinate, the corresponding derivative has a different interpretation. For coupled coordinates, derivatives must follow the permitted motion, not move one geometrically dependent coordinate independently.

A line segment from an origin point to an insertion point is enough for the first example. Intermediate via points and wrapping surfaces avoid impossible paths through bones, but they introduce branches and possible changes in contact topology. A discontinuous path produces discontinuous moment arms. Plot l(q) and its derivative over the complete supported range before trusting the force curve.

**Reader exercise.** Move a synthetic insertion point farther from the elbow. Predict how tension changes for the same moment. Then compare a straight path with a wrapped path. Verify the analytic or automatic-differentiation moment arm against centred finite differences of path length.

## 5 One net moment does not identify individual muscle forces

If several muscles cross the hinge,

$$\tau_{net}=\sum_i r_iF_i+\tau_{passive}.$$

One measured net moment usually leaves multiple unknown tensions. A flexor and extensor can both increase their forces while leaving the net moment unchanged. An optimization criterion or motor-control assumption can select one solution, but that assumption is additional information, not a measurement.

The reference environment [OpenSim](https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1006223) supports musculoskeletal model construction and analyses. It is appropriate for independent comparisons when geometry, parameters, excitations, conventions and solver tolerances are matched. Agreement with another program is verification evidence; it is not automatically validation against a person.

## 6 A line actuator does not determine muscle shape

A line model supplies tension and length. It does not uniquely determine bulging, fascicle curvature, local strain, intermuscular pressure or skin sliding. An ellipsoid whose radius increases as its length decreases illustrates an approximate volume constraint, but that geometry is an authored visualization.

For a cylindrical illustration with volume V = πr²l, constant volume implies

$$r(l)=r_0\sqrt{l_0/l}.$$

Show this as a first intuition for lateral expansion, then show why a real muscle with nonuniform architecture cannot be inferred from that formula alone. [Blemker, Pinsky and Delp](https://pubmed.ncbi.nlm.nih.gov/15713285/) used a three-dimensional biceps model and compared local strains with measurements during low-load elbow flexion; their result motivates spatially varying fiber architecture instead of uniform shortening everywhere.

Three-dimensional active tissue can be coupled in either of two educational modes:

- **One-way visualization:** a line actuator drives joint mechanics; an explicitly approximate volume-preserving shape follows activation and length. No tissue reaction is claimed to affect the lift.
- **Mechanical tissue model:** active stress or active strain in a continuum produces tissue forces, contact and bone reactions. Its contribution is included exactly once in the coupled equations.

Adding a line-muscle torque and a second continuum actuator representing the same muscle can count active work twice. The model must declare which component supplies the mechanical action.

## 7 What would make the model credible

Check force-length and force-velocity curves separately before attempting a curl. Test a slack tendon, an isometric activation transient, passive stretch, constant-velocity shortening, constant-velocity lengthening and a return cycle. Check energy accounting for the passive parts and report active work separately. Vary time step and tolerances without retuning material parameters.

For biological validation, match the intended task and available independent observations: external torque, kinematics, fascicle/tendon behavior or deformation fields, with measurement uncertainty. Electromyography can inform activation timing, but it is not a direct tendon-force measurement. Reserve independent trials from calibration. A visually recognizable biceps contraction is an instructional success; it does not establish the accuracy of its predicted internal force.

Laboratories 4–5 implement the declared simplified line and series laws rather than all functions in the general Hill formulation above. Laboratory 7 adds a solved spatial preferred-shortening model, membrane and sampled bone contact under one-way coupling. The line remains the hinge force owner. This lets the reader separate excitation, actual active/passive force, tendon storage and shape, while preserving the stated force–velocity, pennation and architecture omissions.
