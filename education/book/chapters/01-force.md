# Force changes motion {#force-changes-motion}

A force is not a displacement instruction. For constant mass in an inertial frame, the resultant external force determines acceleration. Doubling force doubles acceleration; doubling mass halves it. Newton's second law and the separation of action-reaction pairs are presented in Dourmashkin's original course notes, §§7.3-7.4. [Newton's laws](#source-force)

## Isolate the body before adding arrows

Consider a small object translated horizontally by an actuator. The schematic laboratory includes one constant horizontal net force. If we imagined gravity and a support, their vertical balance would be an additional assumption; this example simply solves the horizontal component. Do not mistake its missing contact solver for evidence that a support is physically correct.

For net force $F_x$, mass $m>0$, initial position $x_0=0$, and initial velocity $v_0=0$:

$$
 a_x=F_x/m,\qquad v_x(t)=a_x t,\qquad x(t)=\tfrac12 a_x t^2.
$$

**Text equation:** acceleration equals force divided by mass. Velocity equals acceleration times elapsed time. Position equals half acceleration times elapsed time squared, with both initial conditions zero.

This is an analytic solution, so the force laboratory does not accumulate time-integration error. JavaScript still evaluates floating-point arithmetic. We compare selected outputs with exact worked values using numerical tolerances; no theorem in this edition proves the JavaScript implementation.

{{demo:force}}

## Worked example

Set mass to 2 kg and force to 4 N. The acceleration is 2 m/s². At 1 s the position is 1 m and velocity 2 m/s. At 2 s the position is 4 m and velocity 4 m/s. A negative force produces negative position and velocity; the object accelerates along the negative x direction.

**Try:** keep force at 4 N, reset, and increase mass from 2 to 4 kg. At the same simulated time the position is half as large. Then set force to zero: position and velocity stay zero because the initial velocity is zero. A zero force would preserve a nonzero initial velocity in a different experiment.

## Equal and opposite forces belong to different bodies

If a tendon pulls a bone, the bone pulls back on the tendon. Those two forces cancel in a combined bone-plus-tendon system. They do not cancel on the isolated bone: only one member of that pair acts on it. This is why a diagram with every arrow drawn on a single object can be misleading.

For one scalar component, a pair $f$ and $-f$ sums to zero. That identity is enough to check bookkeeping once we have assumed an action-reaction pair. It does not prove that an actual biological interface follows our chosen constitutive law.

{{proof:force-pair}}

## Work offers a second calculation

A constant horizontal force does work $W=F_x\Delta x$. Starting from rest, the kinetic energy is $K=\tfrac12 m v_x^2$. Substituting the analytic solution gives $W=K$ in this ideal isolated horizontal model. For 4 N over 4 m, both are 16 J.

A negative force over a negative displacement also gives positive work. Force direction alone does not determine work's sign; the force-displacement relation does. The next chapter keeps track of the application point of that force, while the energy chapter studies what happens when we replace analytic solutions with time steps.

## Approximation boundary

This laboratory omits drag, friction, impacts, variable mass, deformation, actuator limits, and all anatomy. Its moving sphere is a marker for position, not a tissue particle whose radius or volume has medical meaning. Positions beyond the viewing window are reported numerically; the physical trajectory is not clamped to fit the image.
