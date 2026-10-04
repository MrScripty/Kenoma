// SI throughout. Deterministic pure functions; presentation owns time and camera.
export const G = 9.81; // illustrative uniform field, not a measured local value
export const DEFAULTS = Object.freeze({
  force: Object.freeze({mass: 2, force: 4, time: 0}),
  torque: Object.freeze({mass: 5, length: 0.3, angle: 0}),
  energy: Object.freeze({mass: 1, stiffness: 40, dt: 0.02, method: 'symplectic', x: 0.2, v: 0})
});
function positive(value, name) {
  if (!Number.isFinite(value) || value <= 0) throw new RangeError(`${name} must be positive and finite`);
}
export function forceState({mass, force, time}) {
  positive(mass, 'mass');
  if (![force,time].every(Number.isFinite) || time < 0) throw new RangeError('invalid force or time');
  const acceleration = force / mass;
  const velocity = acceleration * time;
  const position = 0.5 * acceleration * time ** 2;
  return {acceleration, velocity, position, work: force * position, kinetic: 0.5 * mass * velocity ** 2};
}
export function cross2(r, f) { return r[0]*f[1] - r[1]*f[0]; }
export function leverState({mass, length, angle}) {
  positive(mass, 'mass'); positive(length, 'length');
  if (!Number.isFinite(angle)) throw new RangeError('invalid angle');
  const theta = angle * Math.PI / 180;
  const r = [length * Math.cos(theta), length * Math.sin(theta)];
  const force = [0, -mass * G];
  return {r, force, torque: cross2(r, force), potential: mass * G * r[1], momentArm: Math.abs(r[0])};
}
export function springEnergy(state, p) {
  return 0.5 * p.mass * state.v ** 2 + 0.5 * p.stiffness * state.x ** 2;
}
export function springStep(state, p) {
  positive(p.mass, 'mass'); positive(p.stiffness, 'stiffness'); positive(p.dt, 'dt');
  if (![state.x,state.v].every(Number.isFinite)) throw new RangeError('invalid spring state');
  const a = -p.stiffness * state.x / p.mass;
  const h = p.dt;
  if (p.method === 'explicit') return {x: state.x + h * state.v, v: state.v + h * a};
  if (p.method === 'symplectic') {
    const v = state.v + h * a;
    return {x: state.x + h * v, v};
  }
  if (p.method === 'verlet') {
    const x = state.x + h * state.v + 0.5 * h*h * a;
    return {x, v: state.v + 0.5 * h * (a - p.stiffness*x/p.mass)};
  }
  throw new RangeError('unknown integration method');
}
export function exactSpring(time, p) {
  const w = Math.sqrt(p.stiffness / p.mass);
  return {x: p.x*Math.cos(w*time)+p.v/w*Math.sin(w*time), v: -p.x*w*Math.sin(w*time)+p.v*Math.cos(w*time)};
}
export function springTrace(p, count) {
  let state = {x:p.x, v:p.v};
  const trace = [{step:0,time:0,...state,energy:springEnergy(state,p)}];
  for (let step=1; step<=count; step++) {
    state = springStep(state,p);
    trace.push({step,time:step*p.dt,...state,energy:springEnergy(state,p)});
  }
  return trace;
}
