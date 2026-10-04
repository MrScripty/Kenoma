# A force has an application point {#a-force-has-an-application-point}

A force that passes through a pivot produces no moment about that pivot. The same force applied farther from the pivot can produce a larger moment. The laboratory introduces the moment of a force about a chosen origin; the definitions and axis convention are verified against Dourmashkin's rotational-dynamics notes, §17.1. [Rotational dynamics](#source-torque)

## A planar cross product

Let $\mathbf r=(r_x,r_y,0)$ point from the pivot to the application point, and $\mathbf F=(F_x,F_y,0)$ be the force on the lever. The component along z is:

$$
 \tau_z=(\mathbf r\times\mathbf F)_z=r_x F_y-r_y F_x.
$$

**Text equation:** torque around z equals x position times y force minus y position times x force. Positive torque is counterclockwise when viewed from positive z toward the origin.

In the schematic example a massless rigid lever of length $L$ supports a point load of mass $m$ at its tip. The angle $\theta$ is measured counterclockwise from the horizontal, not from a clinical elbow coordinate convention. Uniform gravity is $\mathbf F=(0,-mg,0)$, with **illustrative** $g=9.81$ m/s². Therefore:

$$
 \mathbf r=(L\cos\theta,L\sin\theta,0),\qquad \tau_z=-mgL\cos\theta.
$$

This is a posed lever. The slider prescribes its angle; no active muscle, torque controller, angular acceleration, or joint-contact force maintains the pose. A physical static hold would require an opposing moment supplied by some actuator and appropriate support forces.

{{demo:torque}}

## Worked values and the moment arm

At $m=5$ kg, $L=0.30$ m, and $\theta=0$°, gravity is 49.05 N downward and torque is -14.715 N m. At 90° the line of gravity passes through the pivot and the moment is zero within floating-point tolerance. At 120° the torque becomes positive because the load lies on the other side of the pivot's vertical line.

The perpendicular moment-arm magnitude is $d=|L\cos\theta|$. It is not generally the lever length. Its magnitude tells us how strongly gravity acts about this pivot, while the cross product retains direction.

**Try:** compare 0°, 60°, and 90°. Predict the torque ratio before moving the slider. At 60° the torque magnitude is half the horizontal value. Move from 89° to 91° and watch the sign change.

The exact worked arithmetic can be represented by 300 mm and -49050 mN. Multiplying those scales gives $10^{-6}$ N m per integer product unit. The following theorem checks the integer cross product; division by one million to obtain SI torque is an explicitly stated interpretation.

{{proof:torque-example}}

## Combining forces

Two forces at the same point contribute torques that add. We can either add their force vectors first or add the two moments. The identity is useful when assembling muscle and external-load contributions around a joint.

{{proof:torque-linearity}}

It is unsafe to add torques computed around different origins without transforming them. If the new origin is at $\mathbf o$ relative to the old one, the position becomes $\mathbf r-\mathbf o$, and:

$$
 (\mathbf r-\mathbf o)\times\mathbf F
 =\mathbf r\times\mathbf F-\mathbf o\times\mathbf F.
$$

{{proof:torque-origin}}

## Internal forces and couples

Equal and opposite forces can have zero resultant force and a nonzero resultant torque. Think of two forces acting along different parallel lines: they form a couple. Force cancellation alone is not enough to infer moment cancellation.

For a central pair between positions A and B, let the force at A be $k(\mathbf B-\mathbf A)$ and the force at B its negative. Their summed moment vanishes because both forces act along the joining line. The theorem checks this specifically for planar integer coordinates and integer k.

{{proof:central-pair}}

This assumption should be inspected before applying it to a tissue model. A model that exchanges angular momentum through distributed stress or explicit bending moments needs the corresponding moment balance, not a point-force argument with missing terms.

## Connecting torque to energy

The point load has gravitational potential $U=mgL\sin\theta$ relative to its horizontal position. Differentiating with respect to angle in **radians** gives $\tau_z=-dU/d\theta$. A finite-difference numerical test checks this relation for the implemented lever. It does not establish a floating-point theorem. This independent calculation is valuable because it can reveal a sign convention or degree/radian conversion error.
