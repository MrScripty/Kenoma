import test from 'node:test';
import assert from 'node:assert/strict';
import {solveTwoBone} from '../rig.js';
const dist=(a,b)=>Math.hypot(...a.map((v,i)=>v-b[i]));
const close=(a,b)=>assert.ok(Math.abs(a-b)<1e-7,`${a} != ${b}`);
const base={root:[0,0,0],joint:[1,0,0],end:[1,1,0],pole:[0,0,1]};
test('reachable solve respects lengths, target and pole',()=>{
 const solved=solveTwoBone({...base,target:[1,0,0]});
 close(dist(base.root,solved.joint),1);close(dist(solved.joint,solved.end),1);
 assert.deepEqual(solved.end,[1,0,0]);assert.ok(solved.joint[2]>0);assert.equal(solved.status,'reachable');
});
test('singular and unreachable targets are bounded deterministic and finite',()=>{
 for(const target of [[0,0,0],[100,0,0],[0,2,0],[0,-2,0],[1e-15,0,0]])for(const pole of [[0,0,0],[0,1,0],[0,-1,0]]){
  const input={...base,target,pole},s=solveTwoBone(input);
  assert.deepEqual(s,solveTwoBone(input));assert.ok([...s.joint,...s.end].every(Number.isFinite));
  close(dist(base.root,s.joint),1);close(dist(s.joint,s.end),1);
 }
});
test('unequal lengths clamp inner and outer radii',()=>{
 const input={...base,end:[1,2,0]};
 const near=solveTwoBone({...input,target:[0,0,0]});
 close(dist(near.end,input.root),1);close(dist(near.end,near.joint),2);assert.equal(near.status,'clamped-near');
 const far=solveTwoBone({...input,target:[10,0,0]});close(dist(far.end,input.root),3);assert.equal(far.status,'clamped-far');
});
test('continuous regular-pole trajectory preserves lengths in 3000 solves',()=>{
 for(let i=0;i<3000;i++){
  const t=i*.019,s=solveTwoBone({...base,target:[Math.sin(t)*3,Math.cos(t*.7),Math.sin(t*.3)],pole:[.2,.3,2]});
  close(dist(base.root,s.joint),1);close(dist(s.joint,s.end),1);
 }
});
test('invalid and zero-length inputs rejected without mutation',()=>{
 const input={...base,target:[1,0,0]};const before=structuredClone(input);
 solveTwoBone(input);assert.deepEqual(input,before);
 for(const target of [[NaN,0,0],[Infinity,0,0],[0,0],[1e20,0,0]])assert.throws(()=>solveTwoBone({...input,target}));
 assert.throws(()=>solveTwoBone({...input,joint:[0,0,0]}));
});
test('sparse coordinates are rejected for every solver input',()=>{
 for(const name of ['root','joint','end','target','pole']){
  for(const sparse of [new Array(3),[0,,0]])assert.throws(()=>solveTwoBone({...base,target:[1,0,0],[name]:sparse}),/finite coordinates/);
 }
});
