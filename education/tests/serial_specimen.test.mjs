import test from 'node:test';
import assert from 'node:assert/strict';
import {SERIAL_DEFAULTS,validateSerialParameters,nominalStress,energyDensity,solveStretch,serialSpecimen,globalVolumeOnlyCandidate} from '../web/serial-specimen.mjs';
import {boundaryMeasurements,BOX_FACES} from '../web/continuum-properties.mjs';

function close(actual,expected,{abs=2e-12,rel=2e-10}={}){
 assert.ok(Number.isFinite(actual)&&Number.isFinite(expected));
 assert.ok(Math.abs(actual-expected)<=abs+rel*Math.abs(expected),`${actual} differs from independent reference ${expected}`);
}
// Newton solves the polynomial force equation, independently of the runtime
// stress helper, force residual and bracketed bisection.
function cubicRoot(area,mu,force){
 const t=force/(area*mu);let x=Math.max(1,t+1);
 for(let n=0;n<40;n++){
  const f=x*x*x-t*x*x-1,d=3*x*x-2*t*x,next=x-f/d;
  assert.ok(next>0&&Number.isFinite(next));
  if(next===x)break;x=next;
 }
 assert.ok(Math.abs(x*x*x-t*x*x-1)<1e-13);
 return x;
}
const sub=(a,b)=>a.map((x,i)=>x-b[i]);
const dot=(a,b)=>a.reduce((s,x,i)=>s+x*b[i],0);
const cross=(a,b)=>[a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]];
const norm=a=>Math.hypot(...a);
function cornerMap(reference){
 assert.equal(reference.length,8);
 const lows=[0,1,2].map(j=>Math.min(...reference.map(v=>v[j]))),highs=[0,1,2].map(j=>Math.max(...reference.map(v=>v[j])));
 const map=new Map(reference.map((v,i)=>[v.map((x,j)=>Math.abs(x-lows[j])<Math.abs(x-highs[j])?0:1).join(''),i]));
 assert.equal(map.size,8);return map;
}
// Six tetrahedra fill the affine hexahedron. Absolute scalar triple products
// use local differences, independent of the production boundary-face sum.
function tetraVolume(reference,current){
 const ids=cornerMap(reference),tets=[['000','100','110','111'],['000','110','010','111'],['000','010','011','111'],['000','011','001','111'],['000','001','101','111'],['000','101','100','111']];
 return tets.reduce((total,keys)=>{const [a,b,c,d]=keys.map(key=>current[ids.get(key)]);return total+Math.abs(dot(sub(b,a),cross(sub(c,a),sub(d,a))))/6;},0);
}
function meshEdges(cell){
 const ids=cornerMap(cell.referenceVertices),origin=cell.currentVertices[ids.get('000')];
 return ['100','010','001'].map(key=>sub(cell.currentVertices[ids.get(key)],origin));
}
function verifyCell(p,cell){
 const lambda=cubicRoot(cell.referenceAreaM2,p.mu,p.force),edges=meshEdges(cell);
 close(cell.stretch,lambda);close(cell.lateralStretch,1/Math.sqrt(lambda));
 close(cell.currentLengthM,norm(edges[0]));
 close(cell.currentAreaM2,norm(cross(edges[1],edges[2])));
 close(cell.currentAreaM2,cell.referenceAreaM2/lambda);
 close(cell.currentLengthM,cell.referenceLengthM*lambda);
 close(cell.referenceVolumeM3,tetraVolume(cell.referenceVertices,cell.referenceVertices));
 close(cell.currentBoundaryVolumeM3,tetraVolume(cell.referenceVertices,cell.currentVertices));
 close(cell.currentBoundaryVolumeM3,cell.referenceAreaM2*cell.referenceLengthM);
 close(cell.volumeRatio,1);close(cell.J,1);
 const pMultiplier=p.mu/lambda,axialCauchy=p.mu*lambda*lambda-pMultiplier;
 close(cell.incompressibilityMultiplierPa,pMultiplier);close(cell.lateralStressPa,p.mu*cell.lateralStretch**2-pMultiplier,{abs:2e-10,rel:2e-10});
 close(cell.cauchyStressPa,axialCauchy,{abs:2e-9,rel:2e-10});
 close(cell.cauchyStressPa,cell.resultantN/cell.currentAreaM2,{abs:2e-9,rel:2e-10});
 close(cell.nominalStressPa,cell.resultantN/cell.referenceAreaM2,{abs:2e-9,rel:2e-10});
 assert.ok(Math.abs(cell.resultantN-p.force)<=1e-10);
 close(cell.forceResidualN,cell.resultantN-p.force);
 const f=cell.F.flat();assert.equal(f.length,9);
 const expected=[lambda,0,0,0,cell.lateralStretch,0,0,0,cell.lateralStretch];f.forEach((x,i)=>close(x,expected[i]));
 const fullEnergy=cell.referenceVolumeM3*p.mu/2*(f.reduce((sum,x)=>sum+x*x,0)-3);
 close(cell.energyJ,fullEnergy);
}

test('default force-driven meshes match an independent cubic root, tetra volumes and full free-side stress',()=>{
 const p={...SERIAL_DEFAULTS},s=serialSpecimen(p);
 assert.equal(s.cells.length,2);assert.equal(s.converged,true);
 s.cells.forEach(cell=>verifyCell(p,cell));
 close(s.referenceVolumeM3,s.cells.reduce((sum,c)=>sum+c.referenceVolumeM3,0));
 close(s.currentBoundaryVolumeM3,s.cells.reduce((sum,c)=>sum+tetraVolume(c.referenceVertices,c.currentVertices),0));
 close(s.totalEnergyJ,s.cells.reduce((sum,c)=>sum+c.energyJ,0));
 close(s.extensionM,s.cells.reduce((sum,c)=>sum+c.currentLengthM-c.referenceLengthM,0));
 close(s.totalCurrentLengthM-s.totalReferenceLengthM,s.extensionM);
 const minX=cell=>Math.min(...cell.currentVertices.map(v=>v[0])),maxX=cell=>Math.max(...cell.currentVertices.map(v=>v[0]));
 close(minX(s.cells[0]),0);close(minX(s.cells[1])-maxX(s.cells[0]),s.spacerLengthM);
 close(maxX(s.cells[1])-minX(s.cells[0]),s.totalCurrentLengthM);
 assert.ok(s.cells[0].stretch>s.cells[1].stretch);
 assert.ok(s.cells[0].currentAreaM2<s.cells[0].referenceAreaM2);
});

test('all supported load, area, ratio and modulus corners fit the positive bracket and independent root',()=>{
 for(const area of [.0003,.001])for(const ratio of [.5,4])for(const mu of [500,5000])for(const force of [-.1,0,.1]){
  const p={...SERIAL_DEFAULTS,area,ratio,mu,force},s=serialSpecimen(p);
  assert.equal(s.converged,true);
  for(const cell of s.cells){verifyCell(p,cell);assert.ok(cell.stretch>=.6&&cell.stretch<=1.75);}
 }
});

test('full constrained energy differentiates to the signed axial resultant, for each block and the assembly',()=>{
 for(const force of [-.1,-.03,0,.04,.1]){
  const p={...SERIAL_DEFAULTS,force},s=serialSpecimen(p);
  for(const cell of s.cells){
   const dLambda=1e-5,L0=cell.referenceLengthM,A0=cell.referenceAreaM2;
   const fullEnergy=lambda=>{const b=1/Math.sqrt(lambda);return A0*L0*p.mu/2*(lambda*lambda+2*b*b-3);};
   const derivative=(fullEnergy(cell.stretch+dLambda)-fullEnergy(cell.stretch-dLambda))/(2*L0*dLambda);
   close(derivative,force,{abs:2e-9,rel:2e-8});
   const implemented=(energyDensity(p.mu,cell.stretch+dLambda)-energyDensity(p.mu,cell.stretch-dLambda))*A0/(2*dLambda);
   close(implemented,force,{abs:2e-9,rel:2e-8});
  }
  if(Math.abs(force)<.1){
   const h=1e-6,plus=serialSpecimen({...p,force:force+h}),minus=serialSpecimen({...p,force:force-h});
   close((plus.totalEnergyJ-minus.totalEnergyJ)/(plus.totalCurrentLengthM-minus.totalCurrentLengthM),force,{abs:2e-9,rel:2e-8});
  }
 }
});

test('nominal stress is strictly increasing and equals the derivative of the constrained energy',()=>{
 for(const mu of [500,1500,5000]){
  let previous=-Infinity;
  for(const lambda of [.6,.7,.9,1,1.1,1.4,1.75]){
   const value=nominalStress(mu,lambda);assert.ok(value>previous);previous=value;
   const h=1e-5,derivative=(energyDensity(mu,lambda+h)-energyDensity(mu,lambda-h))/(2*h);
   close(value,derivative,{abs:1e-5,rel:2e-8});assert.ok(energyDensity(mu,lambda)>=0);
  }
 }
});

test('material, geometry, force reversal and equal-area controls change solved lengths and areas coherently',()=>{
 const p={...SERIAL_DEFAULTS},base=serialSpecimen(p),stiff=serialSpecimen({...p,mu:3000}),wider=serialSpecimen({...p,area:.0006});
 for(let i=0;i<2;i++){assert.ok(stiff.cells[i].stretch<base.cells[i].stretch);close(stiff.cells[i].stretch,wider.cells[i].stretch);}
 const reversed=serialSpecimen({...p,ratio:.5});assert.ok(reversed.cells[1].stretch>reversed.cells[0].stretch);
 const equal=serialSpecimen({...p,ratio:1});close(equal.cells[0].stretch,equal.cells[1].stretch);
 const compressed=serialSpecimen({...p,force:-p.force});
 assert.ok(compressed.extensionM<0);for(const c of compressed.cells){assert.ok(c.stretch<1);assert.ok(c.currentAreaM2>c.referenceAreaM2);assert.ok(c.cauchyStressPa<0);}
 const zero=serialSpecimen({...p,force:0});close(zero.extensionM,0);close(zero.totalEnergyJ,0);
 for(const c of zero.cells){close(c.stretch,1);close(c.currentAreaM2,c.referenceAreaM2);close(c.cauchyStressPa,0);close(c.incompressibilityMultiplierPa,p.mu);}
});

test('coarse bisection retains valid volume but cannot claim converged shared-force equilibrium',()=>{
 const p={...SERIAL_DEFAULTS,mu:500,ratio:.5,iterations:8},coarse=serialSpecimen(p),fine=serialSpecimen({...p,iterations:64});
 assert.equal(coarse.converged,false);assert.equal(fine.converged,true);
 for(let i=0;i<2;i++){
  const c=coarse.cells[i],f=fine.cells[i],root=cubicRoot(c.referenceAreaM2,p.mu,p.force);
  assert.equal(c.solve.cap,8);assert.ok(c.solve.iterations<=8);
  close(c.currentBoundaryVolumeM3,c.referenceVolumeM3);close(c.J,1);
  assert.ok(Math.abs(c.stretch-root)>Math.abs(f.stretch-root));
  assert.ok(c.solve.bracketWidth>f.solve.bracketWidth);
  close(c.resultantN,c.referenceAreaM2*p.mu*(c.stretch-c.stretch**-2));
 }
 assert.ok(coarse.cells.some(c=>Math.abs(c.forceResidualN)>coarse.forceCriterionN));
});

test('triangle-volume readouts agree with an independent tetra oracle after arbitrary rigid transformations',()=>{
 const s=serialSpecimen({...SERIAL_DEFAULTS,force:-.1}),angle=.71,c=Math.cos(angle),sn=Math.sin(angle);
 const transform=([x,y,z])=>[c*x-sn*y+123,sn*x+c*y-37,z+81];
 for(const cell of s.cells){
  const rigid=cell.currentVertices.map(transform);
  const independent=tetraVolume(cell.referenceVertices,rigid);
  close(independent,cell.currentBoundaryVolumeM3,{abs:2e-15,rel:2e-11});
  close(boundaryMeasurements(rigid,BOX_FACES).signedVolumeM3,independent,{abs:2e-15,rel:2e-11});
 }
});

test('using current area in the nominal force law fails the independent reference-area equilibrium oracle',()=>{
 const p={...SERIAL_DEFAULTS},s=serialSpecimen(p);
 for(const cell of s.cells){
  const wrongN=cell.currentAreaM2*cell.nominalStressPa;
  assert.ok(Math.abs(wrongN-p.force)>1e-3);
  assert.throws(()=>close(wrongN,p.force,{abs:1e-10,rel:0}),assert.AssertionError);
 }
});

test('invalid parameters and unsupported solves reject without mutating valid input or output',()=>{
 const p={...SERIAL_DEFAULTS},saved=structuredClone(p),state=serialSpecimen(p),snapshot=structuredClone(state);
 for(const change of [{area:0},{area:.0002},{ratio:0},{ratio:4.1},{mu:0},{mu:499},{force:.101},{force:NaN},{length:0},{iterations:7},{iterations:65},{iterations:8.5}])assert.throws(()=>serialSpecimen({...p,...change}),RangeError);
 assert.deepEqual(p,saved);assert.deepEqual(state,snapshot);
 assert.throws(()=>validateSerialParameters({...p,mu:Infinity}),RangeError);
 assert.throws(()=>solveStretch(.00015,500,1,48),RangeError);
});

test('global-volume-only candidate is rejected despite correct weighted total, retaining the valid state',()=>{
 for(const ratio of [.5,1,2,4])for(const force of [-.1,.1]){
  const p={...SERIAL_DEFAULTS,ratio,force},s=serialSpecimen(p),snapshot=structuredClone(s),candidate=globalVolumeOnlyCandidate(p,s);
  assert.equal(candidate.accepted,false);
  close(candidate.currentBoundaryVolumeM3,s.referenceVolumeM3);close(candidate.totalVolumeRatio,1);
  for(let i=0;i<2;i++){
   const cell=candidate.candidateCells[i],expectedRatio=i===0?1.1:1-.1/ratio;
   close(cell.J,expectedRatio);close(cell.volumeRatio,expectedRatio);
   close(cell.currentBoundaryVolumeM3,s.cells[i].referenceVolumeM3*expectedRatio);
   close(cell.currentBoundaryVolumeM3,cell.currentAreaM2*cell.currentLengthM);
   assert.ok(Math.abs(cell.J-1)>1e-3);assert.ok(Math.abs(cell.lateralStressPa)>1);
  }
  assert.deepEqual(s,snapshot);
 }
});
