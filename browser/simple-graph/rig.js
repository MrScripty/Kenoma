/** Pure deterministic kinematics. Coordinates are character-local metres. */
export const LIMBS = Object.freeze({
  rightArm: Object.freeze([4, 5, 6]), leftArm: Object.freeze([7, 8, 9]),
  rightLeg: Object.freeze([10, 11, 12]), leftLeg: Object.freeze([13, 14, 15]),
});
const sub = (a,b) => a.map((v,i) => v-b[i]);
const add = (a,b) => a.map((v,i) => v+b[i]);
const mul = (a,s) => a.map(v => v*s);
const dot = (a,b) => a.reduce((s,v,i) => s+v*b[i],0);
const norm = a => Math.hypot(...a);
export function vector(value, name='vector') {
  if (!Array.isArray(value) || value.length !== 3 || !Array.from(value).every(v => Number.isFinite(v) && Math.abs(v) <= 1e6)) {
    throw new Error(`${name} must contain three finite coordinates within ±1000000`);
  }
  return [...value];
}
/** Pole specifies a point toward which the middle joint bends. At a singular
 * pole, prefer the original joint plane, then a deterministic perpendicular.
 * Targets outside the annulus are clamped; target retains the requested point.
 */
export function solveTwoBone({root,joint,end,target,pole}) {
  [root,joint,end,target,pole] = [root,joint,end,target,pole].map((v,i)=>vector(v,['root','joint','end','target','pole'][i]));
  const a=norm(sub(joint,root)), b=norm(sub(end,joint));
  if(a<1e-8 || b<1e-8) throw new Error('Both limb segments must have nonzero length');
  const delta=sub(target,root), requested=norm(delta);
  const original=sub(end,root);
  const direction=requested>1e-10 ? mul(delta,1/requested) : norm(original)>1e-10 ? mul(original,1/norm(original)) : mul(sub(joint,root),1/a);
  // A tiny positive radius resolves equal-length fully folded chains without 0/0.
  const minimum=Math.max(Math.abs(a-b),1e-9*Math.max(a,b));
  const distance=Math.max(minimum,Math.min(a+b,requested));
  let bend=sub(sub(pole,root),mul(direction,dot(sub(pole,root),direction)));
  if(norm(bend)<1e-9) bend=sub(sub(joint,root),mul(direction,dot(sub(joint,root),direction)));
  if(norm(bend)<1e-9) {
    const axis=[0,0,0]; axis[direction.map(Math.abs).indexOf(Math.min(...direction.map(Math.abs)))]=1;
    bend=sub(axis,mul(direction,dot(axis,direction)));
  }
  bend=mul(bend,1/norm(bend));
  const along=(distance+(a-b)*(a+b)/distance)/2;
  const height=Math.sqrt(Math.max(0,a*a-along*along));
  return {joint:add(root,add(mul(direction,along),mul(bend,height))),end:add(root,mul(direction,distance)),target,
    status: requested>a+b ? 'clamped-far' : requested<minimum ? 'clamped-near' : 'reachable'};
}
