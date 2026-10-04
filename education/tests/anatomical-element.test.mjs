import test from 'node:test';import assert from 'node:assert/strict';
import {quadraticShape,midpointNodes,QUADRATURE,prepareQuadraticElement,evaluateQuadraticElement} from '../web/anatomical-element.mjs';
const close=(x,y,abs=1e-10)=>assert(Math.abs(x-y)<=abs,`${x} != ${y}`),corners=[[0,0,0],[.03,0,0],[0,.02,0],[0,0,.025]],X=midpointNodes(corners);
test('Positive quadratic quadrature and shape reproduce partition, reference volume and polynomial moments',()=>{
 for(const points of Object.values(QUADRATURE)){
  close(points.reduce((sum,p)=>sum+p.weight,0),1);
  for(const p of points){assert(p.weight>0&&p.L.every(l=>l>0));close(p.L.reduce((sum,l)=>sum+l,0),1);const s=quadraticShape(p.L);close(s.N.reduce((sum,n)=>sum+n,0),1);for(let d=0;d<3;d++)close(s.gradient.reduce((sum,g)=>sum+g[d],0),0);}
  for(let i=0;i<4;i++){close(points.reduce((sum,p)=>sum+p.weight*p.L[i],0),.25);close(points.reduce((sum,p)=>sum+p.weight*p.L[i]**2,0),.1);}
 }
 for(const quadrature of Object.keys(QUADRATURE))close(prepareQuadraticElement(X,{quadrature}).referenceVolumeM3,.03*.02*.025/6,1e-18);
});
test('Quadratic element gradients match independent differences including displaced midside nodes',()=>{
 const current=X.map((v,i)=>v.map((x,d)=>x+(i===6&&d===1?.0003:0))),element=prepareQuadraticElement(X,{quadrature:'subdivided32'}),r=evaluateQuadraticElement(element,current,.5),h=1e-8;
 for(let i=0;i<10;i++)for(let d=0;d<3;d++){
  const plus=current.map(x=>x.slice()),minus=current.map(x=>x.slice());plus[i][d]+=h;minus[i][d]-=h;const finite=(evaluateQuadraticElement(element,plus,.5).solvePotentialJ-evaluateQuadraticElement(element,minus,.5).solvePotentialJ)/(2*h);
  assert(Math.abs(finite-r.gradient[i][d])<1e-5+1e-5*Math.abs(finite));
 }
 for(let d=0;d<3;d++)close(r.gradient.reduce((sum,g)=>sum+g[d],0),0,1e-10);
});
test('Isoparametric reference midside geometry has exactly zero passive rest stress',()=>{
 const reference=X.map(x=>x.slice());reference[4][1]+=.0005;const e=prepareQuadraticElement(reference,{quadrature:'subdivided32'}),r=evaluateQuadraticElement(e,reference,0);
 close(r.passiveStoredJ,0,1e-12);r.gradient.flat().forEach(g=>close(g,0,1e-9));
});
test('Finite rotation produces no passive force and rejected orientation is explicit',()=>{
 const q=.7,c=Math.cos(q),s=Math.sin(q),rot=X.map(([x,y,z])=>[c*x-s*y,s*x+c*y,z]),e=prepareQuadraticElement(X),r=evaluateQuadraticElement(e,rot,0);close(r.passiveStoredJ,0,1e-12);r.gradient.flat().forEach(g=>close(g,0,1e-9));
 assert.throws(()=>prepareQuadraticElement(midpointNodes([corners[0],corners[2],corners[1],corners[3]])));
 assert.throws(()=>evaluateQuadraticElement(e,X.map(([x,y,z])=>[-x,y,z]),.5));
});
