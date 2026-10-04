import test from 'node:test';
import assert from 'node:assert/strict';
import {makeMesh,materialMatrix,element,makeCase,applyStiffness,solveReference,solveCompliant,diagnose,continuumError,difference} from '../continuum.mjs';
const dot=(a,b)=>a.reduce((s,x,i)=>s+x*b[i],0);
const close=(a,b,tol=1e-10)=>assert.ok(Math.abs(a-b)<=tol,`${a} != ${b} within ${tol}`);
const maxAbs=a=>Math.max(...Array.from(a,Math.abs));

// Independent dense elimination: tiny systems only, no PCG recurrence.
function denseReference(p,h) {
  const free=Array.from(p.mass.keys()).filter(i=>!p.fixed[i]);
  const A=free.map(i=>free.map(j=>{
    let a=i===j?p.mass[i]/h**2:0;
    for(const e of p.elements) {const r=e.dofs.indexOf(i),c=e.dofs.indexOf(j);if(r>=0&&c>=0) a+=e.K[12*r+c];}
    return a;
  }));
  const b=free.map(i=>p.force[i]);
  for(let k=0;k<free.length;k++) {
    let pivot=k;for(let i=k+1;i<free.length;i++) if(Math.abs(A[i][k])>Math.abs(A[pivot][k])) pivot=i;
    [A[k],A[pivot]]=[A[pivot],A[k]];[b[k],b[pivot]]=[b[pivot],b[k]];
    for(let i=k+1;i<free.length;i++) {const r=A[i][k]/A[k][k];for(let j=k;j<free.length;j++) A[i][j]-=r*A[k][j];b[i]-=r*b[k];}
  }
  const x=new Float64Array(p.mass.length);
  for(let k=free.length-1;k>=0;k--) {let s=b[k];for(let j=k+1;j<free.length;j++) s-=A[k][j]*x[free[j]];x[free[k]]=s/A[k][k];}
  return x;
}

test('conforming tetrahedral volume, outward faces, exact total lumped mass',()=>{
  const p=makeCase({n:3}),volume=p.mesh.lengths.reduce((a,b)=>a*b,1);
  close(p.elements.reduce((s,e)=>s+e.V,0),volume,1e-18);
  close(p.mass.reduce((s,m,i)=>s+(i%3===0?m:0),0),1000*volume,1e-15);
  assert.equal(p.mesh.tets.length,6*3**3);assert.equal(p.mesh.surface.length,12*3**2);
  for(const f of p.mesh.surface) {const center=[0,1,2].map(d=>f.tri.reduce((s,i)=>s+p.mesh.nodes[i][d]/3,0));assert.ok(dot(f.normal,center.map((x,d)=>x-p.mesh.lengths[d]/2))>0);}
});

test('unit tetrahedron matches independently written tensor strain energy and gradients',()=>{
  const nodes=[[0,0,0],[1,0,0],[0,1,0],[0,0,1]],m=materialMatrix(120000,0.3),e=element(nodes,[0,1,2,3],m);
  close(e.V,1/6);assert.deepEqual(e.gradients,[[-1,-1,-1],[1,0,0],[0,1,0],[0,0,1]]);
  const H=[[.01,.003,-.002],[.004,-.005,.006],[.001,-.003,.008]],u=nodes.flatMap(X=>H.map(row=>dot(row,X)));
  const eps=H.map((row,i)=>row.map((x,j)=>(x+H[j][i])/2));
  const tr=eps.reduce((s,row,i)=>s+row[i],0),frobenius=eps.flat().reduce((s,x)=>s+x*x,0);
  const expected=e.V*(0.5*m.lambda*tr*tr+m.mu*frobenius);
  const Ku=u.map((_,i)=>u.reduce((s,x,j)=>s+e.K[12*i+j]*x,0));close(.5*dot(u,Ku),expected,1e-13);
  for(let i=0;i<12;i++) for(let j=0;j<12;j++) close(e.K[12*i+j],e.K[12*j+i],1e-10);
  const fd=1e-7,energy=v=>.5*v.reduce((s,x,i)=>s+x*v.reduce((t,y,j)=>t+e.K[12*i+j]*y,0),0);
  const plus=u.slice(),minus=u.slice();plus[4]+=fd;minus[4]-=fd;close((energy(plus)-energy(minus))/(2*fd),Ku[4],1e-6);
});

test('six infinitesimal rigid modes vanish; a finite rotation is outside this model',()=>{
  const p=makeCase({n:2});
  for(let axis=0;axis<3;axis++) {
    const translation=p.mesh.nodes.flatMap(()=>[0,1,2].map(d=>d===axis?.1:0));assert.ok(maxAbs(applyStiffness(p,translation))<1e-12);
    const rotation=p.mesh.nodes.flatMap(([x,y,z])=>axis===0?[0,-z,y]:axis===1?[z,0,-x]:[-y,x,0]);assert.ok(maxAbs(applyStiffness(p,rotation))<1e-12);
  }
  const theta=.8,u=p.mesh.nodes.flatMap(([x,y])=>[(Math.cos(theta)-1)*x-Math.sin(theta)*y,Math.sin(theta)*x+(Math.cos(theta)-1)*y,0]);
  assert.ok(diagnose(p,u).energyJ>0.01); // not objective under finite rotation
});

test('affine patch: displacement, constant stress, signed support and half-ramp work',()=>{
  for(const n of [1,2,3]) {
    const p=makeCase({n,kind:'affine'}),r=solveReference(p);assert.ok(r.converged);
    const exact=p.mesh.nodes.flatMap(p.exact);assert.ok(maxAbs(r.u.map((x,i)=>x-exact[i]))<1e-12);
    const d=diagnose(p,r.u),H=p.material.lambda+2*p.material.mu,area=p.mesh.lengths[1]*p.mesh.lengths[2];
    close(d.resultantReactionN[0],-H*p.strain*area,1e-10);
    close(d.energyJ,.5*H*p.strain**2*p.mesh.lengths.reduce((a,b)=>a*b,1),1e-13);
    close(.5*d.loadDotDisplacementJ,d.energyJ,1e-13);
    for(const s of d.stressPa) {close(s[0],H*p.strain,1e-6);close(s[3],0,1e-6);}
    assert.ok(maxAbs(d.balanceN)<1e-10);assert.ok(continuumError(p,r.u).relativeL2<1e-8);
  }
});

test('quadratic manufactured load is independent of FEM: divergence, surface resultants, refinement',()=>{
  const errors=[];
  for(const n of [2,4,8]) {
    const p=makeCase({n}),r=solveReference(p);assert.ok(r.converged);
    const H=p.material.lambda+2*p.material.mu,volume=p.mesh.lengths.reduce((a,b)=>a*b,1);
    close(p.body[0],-2*p.c*H,1e-12);
    const resultant=p.force.reduce((s,x,i)=>s+(i%3===0?x:0),0);close(resultant,0,1e-12);
    const d=diagnose(p,r.u);assert.ok(maxAbs(d.balanceN)<1e-9);
    const er=continuumError(p,r.u);errors.push(er);
    // Continuum RMS exact displacement: c L^2/sqrt(5). Independent integration.
    const expectedExactRms=p.c*p.mesh.lengths[0]**2/Math.sqrt(5);
    close(er.l2RmsM/er.relativeL2,expectedExactRms,1e-14);
    const exactEnergy=2*H*p.c**2*volume*p.mesh.lengths[0]**2/3;
    close(er.energyNormSqrtJ/er.relativeEnergy,Math.sqrt(2*exactEnergy),1e-12);
  }
  for(let i=1;i<errors.length;i++) {assert.ok(errors[i].relativeL2<errors[i-1].relativeL2/2);assert.ok(errors[i].relativeEnergy<errors[i-1].relativeEnergy*0.56);}
});

test('PCG implicit solve agrees with pivoted dense elimination; failed tolerance stays failed',()=>{
  const p=makeCase({n:1}),h=.001,r=solveReference(p,{h}),direct=denseReference(p,h);assert.ok(r.converged);
  assert.ok(maxAbs(r.u.map((x,i)=>x-direct[i]))<1e-13);
  const failed=solveReference(p,{h,maxIterations:1});assert.equal(failed.converged,false);assert.ok(failed.residualN>failed.targetN);
});

test('six compliant strain modes reproduce full element energy, including shear',()=>{
  const p=makeCase({n:2}),u=Float64Array.from(p.mass,(_,i)=>1e-4*Math.sin(i*1.234));
  const constraintEnergy=p.constraints.reduce((s,c)=>{const C=c.dofs.reduce((t,d,i)=>t+c.g[i]*u[d],0);return s+.5*c.stiffness*C*C;},0);
  close(constraintEnergy,diagnose(p,u).energyJ,1e-13);
});

test('XPBD finite iteration error decreases to the matched implicit solution; reset is deterministic',()=>{
  const p=makeCase({n:3}),h=.0005,r=solveReference(p,{h});
  let last=Infinity;
  for(const sweeps of [1,2,5,10,20,50]) {const fast=solveCompliant(p,{h,sweeps}),error=difference(p,fast.u,r.u,{h}).relativeObjectiveNorm;assert.ok(error<last);last=error;for(let i=0;i<p.fixed.length;i++) if(p.fixed[i]) close(fast.u[i],0,0);}
  assert.ok(last<1e-9);
  const a=solveCompliant(p,{h,sweeps:5}),b=solveCompliant(p,{h,sweeps:5});assert.deepEqual(a.u,b.u);assert.deepEqual(a.multipliers,b.multipliers);
  const reversed=solveCompliant(p,{h,sweeps:5,reverse:true});assert.ok(maxAbs(a.u.map((x,i)=>x-reversed.u[i]))>1e-8);
});

test('finite sweeps depend on timestep; convergence matches target at each step size',()=>{
  const p=makeCase({n:2}),errors=[];
  for(const h of [.0005,.001,.002]) {const r=solveReference(p,{h}),fast=solveCompliant(p,{h,sweeps:5}),converged=solveCompliant(p,{h,sweeps:1000});errors.push(difference(p,fast.u,r.u,{h}).relativeObjectiveNorm);assert.ok(difference(p,converged.u,r.u,{h}).relativeObjectiveNorm<1e-8);}
  assert.ok(errors[2]>errors[0]*5);
});

test('implicit force signs and backward-Euler work/dissipation balance for nonzero initial state',()=>{
  const p=makeCase({n:2}),h=.0007,u0=Float64Array.from(p.mass,(_,i)=>p.fixed[i]?0:1e-5*Math.sin(i)),v0=Float64Array.from(p.mass,(_,i)=>p.fixed[i]?0:.001*Math.cos(i));
  const r=solveReference(p,{h,u0,v0}),d=diagnose(p,r.u,{h,u0,v0}),old=diagnose(p,u0);
  const oldT=.5*v0.reduce((s,v,i)=>s+p.mass[i]*v*v,0),work=p.force.reduce((s,f,i)=>s+f*(r.u[i]-u0[i]),0);
  close(d.energyJ+d.kineticJ-old.energyJ-oldT-work+d.beDissipationJ,0,1e-13);
  assert.ok(maxAbs(d.balanceN)<1e-9);assert.ok(d.beDissipationJ>=0);
  const fast=solveCompliant(p,{h,u0,v0,sweeps:500});assert.ok(difference(p,fast.u,r.u,{h}).relativeObjectiveNorm<1e-8);
});

test('zero forces and invalid domains are explicit',()=>{
  const p=makeCase({n:1});p.force.fill(0);const r=solveReference(p);assert.ok(r.converged);close(maxAbs(r.u),0);assert.equal(r.iterations,0);
  for(const options of [{n:0},{n:13},{E:-1},{nu:.5},{rho:0},{kind:'spring'},{strain:.1}]) assert.throws(()=>makeCase(options),RangeError);
  assert.throws(()=>makeMesh(1,[0,1,1]),RangeError);
  assert.throws(()=>solveCompliant(p,{h:0}),RangeError);assert.throws(()=>solveCompliant(p,{sweeps:1.5}),RangeError);
  assert.throws(()=>solveReference(p,{u0:new Float64Array(24)}),RangeError);
  assert.throws(()=>applyStiffness(p,[NaN]),RangeError);
  assert.throws(()=>element([[0,0,0],[1,0,0],[0,1,0],[0,0,0]],[0,1,2,3],materialMatrix(1,.2)),RangeError);
});
