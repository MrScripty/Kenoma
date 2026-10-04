/** Kenoma bounded linear-tetrahedron lesson. Pure ES module; SI throughout.
 * No renderer, dependencies, active muscle, contact, or nonlinear material.
 * Arrays are node-major xyz. Strain order: xx,yy,zz,gamma_xy,gamma_yz,gamma_zx.
 * See README.md and chapter.md for API, assumptions, and signs.
 */
const dot = (a, b) => a.reduce((s, x, i) => s + x * b[i], 0);
const norm = a => Math.sqrt(dot(a, a));
const sub = (a, b) => a.map((x, i) => x - b[i]);
const cross = (a, b) => [a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0]];
const positive = (x, name) => { if (!Number.isFinite(x) || x <= 0) throw new RangeError(name); };
const integer = (x, lo, hi, name) => { if (!Number.isInteger(x) || x < lo || x > hi) throw new RangeError(name); };
const vector = (x, n, name) => { if (!x || x.length !== n || !Array.from(x).every(Number.isFinite)) throw new RangeError(name); };

export function materialMatrix(E, nu) {
  positive(E, 'E must be positive Pa');
  if (!Number.isFinite(nu) || nu <= -1 || nu >= 0.5) throw new RangeError('-1 < nu < 0.5');
  const mu = E/(2*(1+nu)), lambda = E*nu/((1+nu)*(1-2*nu));
  const D = Array.from({length:6}, () => new Float64Array(6));
  for (let i=0;i<3;i++) for (let j=0;j<3;j++) D[i][j] = lambda + (i===j ? 2*mu : 0);
  for (let i=3;i<6;i++) D[i][i]=mu;
  return {E, nu, lambda, mu, D};
}

/** Six conforming tetrahedra per brick, positive orientation, outward surface. */
export function makeMesh(n=3, lengths=[0.04,0.02,0.02]) {
  integer(n,1,12,'n must be an integer 1..12'); vector(lengths,3,'three lengths');
  lengths.forEach(x=>positive(x,'lengths in m'));
  const nodes=[], tets=[], id=(i,j,k)=>(i*(n+1)+j)*(n+1)+k;
  for(let i=0;i<=n;i++) for(let j=0;j<=n;j++) for(let k=0;k<=n;k++) nodes.push([i*lengths[0]/n,j*lengths[1]/n,k*lengths[2]/n]);
  const permutations=[[0,1,2],[0,2,1],[1,0,2],[1,2,0],[2,0,1],[2,1,0]];
  for(let i=0;i<n;i++) for(let j=0;j<n;j++) for(let k=0;k<n;k++) for(const p of permutations) {
    const a=[i,j,k], b=a.slice(); b[p[0]]++;
    const c=b.slice(); c[p[1]]++;
    const tet=[id(...a),id(...b),id(...c),id(i+1,j+1,k+1)];
    const [X0,X1,X2,X3]=tet.map(v=>nodes[v]);
    if(dot(sub(X1,X0),cross(sub(X2,X0),sub(X3,X0)))<0) [tet[1],tet[2]]=[tet[2],tet[1]];
    tets.push(tet);
  }
  const faces=new Map();
  for(const tet of tets) for(let opposite=0;opposite<4;opposite++) {
    const tri=tet.filter((_,i)=>i!==opposite), key=tri.slice().sort((a,b)=>a-b).join(',');
    if(faces.has(key)) { faces.get(key).count++; continue; }
    let N=cross(sub(nodes[tri[1]],nodes[tri[0]]),sub(nodes[tri[2]],nodes[tri[0]]));
    if(dot(N,sub(nodes[tet[opposite]],nodes[tri[0]]))>0) { [tri[1],tri[2]]=[tri[2],tri[1]]; N=N.map(x=>-x); }
    const twiceArea=norm(N);
    faces.set(key,{tri,normal:N.map(x=>x/twiceArea),area:twiceArea/2,count:1});
  }
  const surface=Array.from(faces.values()).filter(f=>f.count===1).map(({count,...f})=>f);
  return {n,lengths:lengths.slice(),nodes,tets,surface};
}

/** Constant strain element: K_e = V B^T D B, never six edge springs. */
export function element(nodes, tet, material) {
  const [X0,X1,X2,X3]=tet.map(i=>nodes[i]);
  const a=sub(X1,X0), b=sub(X2,X0), c=sub(X3,X0), det=dot(a,cross(b,c));
  if(!Number.isFinite(det) || det<=0) throw new RangeError('positive nondegenerate tetrahedron required');
  const g1=cross(b,c).map(x=>x/det),g2=cross(c,a).map(x=>x/det),g3=cross(a,b).map(x=>x/det);
  const gradients=[g1.map((x,i)=>-x-g2[i]-g3[i]),g1,g2,g3], V=det/6;
  const dofs=tet.flatMap(v=>[3*v,3*v+1,3*v+2]);
  const B=Array.from({length:6},()=>new Float64Array(12));
  gradients.forEach(([gx,gy,gz],i)=>{
    const j=3*i; B[0][j]=gx; B[1][j+1]=gy; B[2][j+2]=gz;
    B[3][j]=gy; B[3][j+1]=gx; B[4][j+1]=gz; B[4][j+2]=gy; B[5][j]=gz; B[5][j+2]=gx;
  });
  const K=new Float64Array(144);
  for(let i=0;i<12;i++) for(let j=0;j<12;j++) for(let r=0;r<6;r++) for(let s=0;s<6;s++) K[12*i+j]+=V*B[r][i]*material.D[r][s]*B[s][j];
  const a3=1/Math.sqrt(3),a2=1/Math.sqrt(2),a6=1/Math.sqrt(6);
  const modes=[[a3,a3,a3,0,0,0],[a2,-a2,0,0,0,0],[a6,a6,-2*a6,0,0,0],[0,0,0,1,0,0],[0,0,0,0,1,0],[0,0,0,0,0,1]];
  const eigenvalues=[3*material.lambda+2*material.mu,2*material.mu,2*material.mu,material.mu,material.mu,material.mu];
  const constraints=modes.map((q,i)=>({dofs,g:Float64Array.from({length:12},(_,j)=>q.reduce((s,x,r)=>s+x*B[r][j],0)),stiffness:V*eigenvalues[i]}));
  return {tet,dofs,gradients,V,B,K,constraints};
}

/** Two authored manufactured load cases. Same boundaries for both solvers.
 * quadratic: u*=(c x^2,0,0); affine: u*=(strain x,0,0).
 * x=0 clamped; every other face has exact traction sigma* n.
 */
export function makeCase({n=3,kind='quadratic',E=100000,nu=0.25,rho=1000,lengths=[0.04,0.02,0.02],strain=0.02}={}) {
  if(!['quadratic','affine'].includes(kind)) throw new RangeError('known case kind required');
  positive(rho,'rho in kg/m^3'); positive(strain,'positive strain');
  if(strain>0.05) throw new RangeError('lesson strain <= 0.05');
  const mesh=makeMesh(n,lengths), material=materialMatrix(E,nu), c=strain/(2*lengths[0]);
  const exact=X=>[kind==='quadratic'?c*X[0]**2:strain*X[0],0,0];
  const exactStrain=X=>[kind==='quadratic'?2*c*X[0]:strain,0,0,0,0,0];
  const body=[kind==='quadratic'?-2*c*(material.lambda+2*material.mu):0,0,0];
  const size=3*mesh.nodes.length, mass=new Float64Array(size),force=new Float64Array(size),fixed=new Uint8Array(size),diagonal=new Float64Array(size);
  mesh.nodes.forEach((X,i)=>{if(X[0]===0) fixed.fill(1,3*i,3*i+3);});
  const elements=mesh.tets.map(t=>element(mesh.nodes,t,material));
  for(const e of elements) for(let i=0;i<12;i++) {
    const d=e.dofs[i]; mass[d]+=rho*e.V/4; force[d]+=body[i%3]*e.V/4; diagonal[d]+=e.K[i*12+i];
  }
  // Three-point triangle rule integrates N_i times linearly varying traction exactly.
  const triRule=[[2/3,1/6,1/6],[1/6,2/3,1/6],[1/6,1/6,2/3]];
  for(const f of mesh.surface) {
    if(f.tri.every(i=>mesh.nodes[i][0]===0)) continue;
    for(const N of triRule) {
      const X=[0,1,2].map(d=>N.reduce((s,x,i)=>s+x*mesh.nodes[f.tri[i]][d],0));
      const stress=material.D.map(row=>dot(row,exactStrain(X)));
      const traction=[stress[0]*f.normal[0]+stress[3]*f.normal[1]+stress[5]*f.normal[2],stress[3]*f.normal[0]+stress[1]*f.normal[1]+stress[4]*f.normal[2],stress[5]*f.normal[0]+stress[4]*f.normal[1]+stress[2]*f.normal[2]];
      f.tri.forEach((v,i)=>traction.forEach((t,d)=>{force[3*v+d]+=f.area/3*N[i]*t;}));
    }
  }
  return {mesh,material,rho,kind,strain,c,body,mass,force,fixed,diagonal,elements,constraints:elements.flatMap(e=>e.constraints),exact,exactStrain};
}

export function applyStiffness(problem,u) {
  vector(u,problem.mass.length,'displacement vector');
  const out=new Float64Array(u.length);
  for(const e of problem.elements) for(let i=0;i<12;i++) {
    let s=0; for(let j=0;j<12;j++) s+=e.K[12*i+j]*u[e.dofs[j]];
    out[e.dofs[i]]+=s;
  }
  return out;
}

function stepData(p,h,u0,v0) {
  const size=p.mass.length;
  const initial=u0===undefined?new Float64Array(size):Float64Array.from(u0);
  const velocity=v0===undefined?new Float64Array(size):Float64Array.from(v0);
  vector(initial,size,'u0'); vector(velocity,size,'v0');
  const d=new Float64Array(size),rhs=Float64Array.from(p.force),inertial=new Float64Array(size);
  if(h!==null) {
    positive(h,'h in seconds');
    for(let i=0;i<size;i++) {d[i]=p.mass[i]/h**2;inertial[i]=initial[i]+h*velocity[i];rhs[i]+=d[i]*inertial[i];}
  } else if(u0!==undefined||v0!==undefined) throw new RangeError('initial state only for implicit step');
  for(let i=0;i<size;i++) if(p.fixed[i]&&(initial[i]!==0||velocity[i]!==0)) throw new RangeError('clamp state must be zero');
  return {d,rhs,inertial,initial};
}

/** Jacobi-preconditioned conjugate gradient on free DOFs. h=null is static;
 * h>0 is ONE backward-Euler step, lumped M, frozen dead loads.
 * Success requires a freshly recomputed ||A u-rhs||_2 <= max(atol,rtol||rhs_free||).
 */
export function solveReference(p,{h=null,u0,v0,rtol=1e-10,atol=1e-12,maxIterations=10000}={}) {
  positive(rtol,'rtol');positive(atol,'atol');integer(maxIterations,1,100000,'maxIterations');
  const {d,rhs}=stepData(p,h,u0,v0),size=rhs.length,mask=x=>{for(let i=0;i<size;i++) if(p.fixed[i]) x[i]=0;return x;};
  let stiffnessApplications=0;
  const A=u=>{stiffnessApplications++;const out=applyStiffness(p,u);for(let i=0;i<size;i++) out[i]+=d[i]*u[i];return mask(out);};
  const target=Math.max(atol,rtol*norm(mask(rhs.slice()))),u=new Float64Array(size);
  let r=mask(rhs.slice()),z=Float64Array.from(r,(x,i)=>p.fixed[i]?0:x/(p.diagonal[i]+d[i])),direction=z.slice(),rz=dot(r,z),iterations=0;
  let residualN=norm(r),converged=residualN<=target;
  while(!converged && iterations<maxIterations) {
    const Ad=A(direction),denominator=dot(direction,Ad);
    if(!(denominator>0)) throw new Error('CG breakdown: inspect rigid modes/material');
    const alpha=rz/denominator;
    for(let i=0;i<size;i++) {u[i]+=alpha*direction[i];r[i]-=alpha*Ad[i];}
    iterations++;
    if(norm(r)<=target) {
      const Au=A(u); r=mask(Float64Array.from(rhs,(x,i)=>x-Au[i]));
      residualN=norm(r);converged=residualN<=target;
      if(converged) break;
      // Restart after residual replacement; never accept only recursive residual.
      z=Float64Array.from(r,(x,i)=>p.fixed[i]?0:x/(p.diagonal[i]+d[i]));direction=z.slice();rz=dot(r,z);continue;
    }
    z=Float64Array.from(r,(x,i)=>p.fixed[i]?0:x/(p.diagonal[i]+d[i]));
    const next=dot(r,z),beta=next/rz;rz=next;
    for(let i=0;i<size;i++) direction[i]=z[i]+beta*direction[i];
  }
  const Au=A(u);residualN=norm(mask(Float64Array.from(rhs,(x,i)=>Au[i]-x)));converged=residualN<=target;
  return {method:'pcg',u,h,iterations,converged,residualN,targetN:target,stiffnessApplications,elementVisits:stiffnessApplications*p.elements.length};
}

/** Finite-sweep XPBD on six dimensionless strain modes per tetrahedron.
 * Exactly the SAME linear elastic energy and lumped-mass implicit target as PCG.
 * Fixed order, no warm start, multipliers reset per call; forward GS sweeps.
 * No claim that finite sweeps achieve timestep/iteration-independent accuracy.
 */
export function solveCompliant(p,{h=0.0005,u0,v0,sweeps=5,reverse=false}={}) {
  positive(h,'h');integer(sweeps,0,10000,'sweeps');
  const {rhs}=stepData(p,h,u0,v0),u=Float64Array.from(rhs,(x,i)=>p.fixed[i]?0:h*h*x/p.mass[i]);
  const multipliers=new Float64Array(p.constraints.length),inverseMass=Float64Array.from(p.mass,(m,i)=>p.fixed[i]?0:1/m);
  const order=Array.from({length:p.constraints.length},(_,i)=>i);if(reverse) order.reverse();
  const alpha=p.constraints.map(c=>1/(c.stiffness*h*h));
  const denominators=p.constraints.map((c,j)=>alpha[j]+c.dofs.reduce((s,d,i)=>s+inverseMass[d]*c.g[i]**2,0));
  for(let sweep=0;sweep<sweeps;sweep++) for(const j of order) {
    const c=p.constraints[j];let C=0;for(let i=0;i<12;i++) C+=c.g[i]*u[c.dofs[i]];
    const dlambda=(-C-alpha[j]*multipliers[j])/denominators[j];multipliers[j]+=dlambda;
    for(let i=0;i<12;i++) {const d=c.dofs[i];u[d]+=inverseMass[d]*c.g[i]*dlambda;}
  }
  return {method:'compliant-strain-gs',u,h,sweeps,multipliers,constraintVisits:sweeps*p.constraints.length};
}

/** Physical diagnostics for any displacement, including unconverged results.
 * reaction = K u + M/h^2 (u-u_n-h v_n) - f at FIXED nodes, force ON block.
 * At free nodes this same expression is the algebraic residual, not a reaction.
 */
export function diagnose(p,u,{h=null,u0,v0}={}) {
  const Ku=applyStiffness(p,u),{d,rhs,inertial,initial}=stepData(p,h,u0,v0);
  const residual=Float64Array.from(Ku,(x,i)=>x+d[i]*u[i]-rhs[i]),reactions=new Float64Array(u.length);
  let residualN2=0,rhsN2=0,maxDisplacementM=0,kineticJ=0,beDissipationJ=0;
  const resultantReactionN=[0,0,0],resultantExternalN=[0,0,0],resultantInertiaN=[0,0,0];
  for(let i=0;i<u.length;i++) {
    if(p.fixed[i]) {reactions[i]=residual[i];resultantReactionN[i%3]+=residual[i];}
    else {residualN2+=residual[i]**2;rhsN2+=rhs[i]**2;}
    resultantExternalN[i%3]+=p.force[i];resultantInertiaN[i%3]+=d[i]*(u[i]-inertial[i]);
    if(h!==null) kineticJ+=0.5*p.mass[i]*((u[i]-initial[i])/h)**2;
  }
  for(let i=0;i<p.mesh.nodes.length;i++) maxDisplacementM=Math.max(maxDisplacementM,Math.hypot(...u.slice(3*i,3*i+3)));
  const strain=p.elements.map(e=>{const ue=e.dofs.map(d=>u[d]);return e.B.map(row=>dot(row,ue));});
  const stressPa=strain.map(e=>p.material.D.map(row=>dot(row,e)));
  const maxStrain=Math.max(...strain.map(e=>Math.sqrt(e[0]**2+e[1]**2+e[2]**2+0.5*(e[3]**2+e[4]**2+e[5]**2))));
  const energyJ=0.5*dot(u,Ku),loadDotDisplacementJ=dot(p.force,u);
  if(h!==null) {
    const du=sub(Array.from(u),Array.from(initial)),Kdu=applyStiffness(p,du);
    const oldVelocity=v0===undefined?new Float64Array(u.length):v0;
    beDissipationJ=0.5*dot(du,Kdu);
    for(let i=0;i<u.length;i++) beDissipationJ+=0.5*p.mass[i]*((u[i]-initial[i])/h-oldVelocity[i])**2;
  }
  return {energyJ,kineticJ,beDissipationJ,loadDotDisplacementJ,maxDisplacementM,maxStrain,residualN:Math.sqrt(residualN2),relativeResidual:Math.sqrt(residualN2)/Math.max(Math.sqrt(rhsN2),Number.MIN_VALUE),reactions,resultantReactionN,resultantExternalN,resultantInertiaN,balanceN:resultantExternalN.map((x,i)=>x+resultantReactionN[i]-resultantInertiaN[i]),strain,stressPa};
}

/** Independent analytic continuum reference quadrature: 4^3 Duffy GL points,
 * exact for the quartic displacement-error square and quadratic strain-error
 * square in these polynomial cases. Reports displacement L2 and energy norm.
 * The quadratic reference is STATIC; do not compare it to an implicit step.
 */
export function continuumError(p,u) {
  vector(u,p.mass.length,'u');
  const points=[0.06943184420297371,0.33000947820757187,0.6699905217924281,0.9305681557970262],weights=[0.17392742256872692,0.32607257743127307,0.32607257743127307,0.17392742256872692];
  let displacement=0,reference=0,energy=0,referenceEnergy=0;
  for(const e of p.elements) {
    const ue=e.dofs.map(d=>u[d]),eps=e.B.map(row=>dot(row,ue));
    for(let i=0;i<4;i++) for(let j=0;j<4;j++) for(let k=0;k<4;k++) {
      const r=points[i],s=points[j],t=points[k],N=[(1-r)*(1-s)*(1-t),r,(1-r)*s,(1-r)*(1-s)*t];
      const X=[0,1,2].map(d=>N.reduce((sum,x,a)=>sum+x*p.mesh.nodes[e.tet[a]][d],0));
      const uh=[0,1,2].map(d=>N.reduce((sum,x,a)=>sum+x*ue[3*a+d],0)),exact=p.exact(X),diff=sub(uh,exact),de=sub(eps,p.exactStrain(X)),ee=p.exactStrain(X);
      const w=6*e.V*weights[i]*weights[j]*weights[k]*(1-r)**2*(1-s);
      displacement+=w*dot(diff,diff);reference+=w*dot(exact,exact);
      energy+=w*dot(de,p.material.D.map(row=>dot(row,de)));referenceEnergy+=w*dot(ee,p.material.D.map(row=>dot(row,ee)));
    }
  }
  return {l2RmsM:Math.sqrt(displacement/p.mesh.lengths.reduce((a,b)=>a*b,1)),relativeL2:Math.sqrt(displacement/reference),energyNormSqrtJ:Math.sqrt(energy),relativeEnergy:Math.sqrt(energy/referenceEnergy)};
}

export function difference(p,u,reference,{h=null}={}) {
  vector(u,p.mass.length,'u');vector(reference,u.length,'reference');
  const delta=Float64Array.from(u,(x,i)=>x-reference[i]),Kd=applyStiffness(p,delta),Kr=applyStiffness(p,reference);
  let error=dot(delta,Kd),scale=dot(reference,Kr),maxNodalM=0;
  if(h!==null) {positive(h,'h');for(let i=0;i<u.length;i++) {error+=p.mass[i]/h**2*delta[i]**2;scale+=p.mass[i]/h**2*reference[i]**2;}}
  for(let i=0;i<p.mesh.nodes.length;i++) maxNodalM=Math.max(maxNodalM,Math.hypot(...delta.slice(3*i,3*i+3)));
  return {relativeObjectiveNorm:Math.sqrt(Math.max(0,error)/Math.max(scale,Number.MIN_VALUE)),maxNodalM};
}
