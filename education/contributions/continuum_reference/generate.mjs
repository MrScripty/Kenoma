/** Reproduce authored evidence using the exact module the renderer imports.
 * Wall-clock samples vary; numerical fixtures are deterministic in this Node.
 * All output paths are bounded to this contribution. No dependencies installed.
 */
import {readFileSync,writeFileSync,existsSync} from 'node:fs';
import {createHash} from 'node:crypto';
import {execFileSync,spawnSync} from 'node:child_process';
import {cpus,platform,release,arch} from 'node:os';
import {fileURLToPath} from 'node:url';
import {performance} from 'node:perf_hooks';
import {makeCase,solveReference,solveCompliant,diagnose,continuumError,difference} from './continuum.mjs';
const root=fileURLToPath(new URL('.',import.meta.url));
const sha=path=>createHash('sha256').update(readFileSync(root+path)).digest('hex');
const json=(path,value)=>writeFileSync(root+path,JSON.stringify(value,(_,v)=>ArrayBuffer.isView(v)?Array.from(v):v,2)+'\n');
const base='19625dd9a96adbdb392674075afd972c28c27db0';
const source={repository:'https://github.com/MrScripty/Kenoma',branch:'education/tendon-tissue',commit:base,tree:execFileSync('git',['rev-parse',base+'^{tree}'],{cwd:root,encoding:'utf8'}).trim(),moduleSha256:sha('continuum.mjs'),generatorSha256:sha('generate.mjs')};
const environment={utc:new Date().toISOString(),node:process.version,v8:process.versions.v8,os:platform(),kernel:release(),arch:arch(),cpu:cpus()[0]?.model,visibleLogicalCpus:cpus().length,scope:'Single-thread Node in shared virtualized executor. No renderer, GPU or network in timed regions. Host contention/frequency/quota are uncontrolled.'};
const compact=d=>Object.fromEntries(Object.entries(d).filter(([k])=>!['reactions','strain','stressPa'].includes(k)));
const reference={schemaVersion:1,source,parameters:{lengthsM:[.04,.02,.02],E_Pa:100000,nu:.25,rhoKgM3:1000,maximumExactStrain:.02},staticRefinement:[]};
for(const n of [1,2,4,8,12]) {
  const p=makeCase({n}),r=solveReference(p);if(!r.converged) throw new Error('static solve failed');
  reference.staticRefinement.push({n,nodes:p.mesh.nodes.length,tetrahedra:p.elements.length,freeDofs:p.fixed.reduce((s,x)=>s+1-x,0),iterations:r.iterations,stiffnessApplications:r.stiffnessApplications,targetN:r.targetN,...continuumError(p,r.u),...compact(diagnose(p,r.u))});
}
for(let i=1;i<reference.staticRefinement.length;i++) {
  const a=reference.staticRefinement[i-1],b=reference.staticRefinement[i],ratio=b.n/a.n;
  b.observedL2Order=Math.log(a.relativeL2/b.relativeL2)/Math.log(ratio);
  b.observedEnergyOrder=Math.log(a.relativeEnergy/b.relativeEnergy)/Math.log(ratio);
}
const p=makeCase({n:3}),h=.0005,r=solveReference(p,{h}),staticResult=solveReference(p);
if(!r.converged||!staticResult.converged) throw new Error('example solve failed');
const sweeps=[0,1,2,5,10,20,50],states=sweeps.map(s=>solveCompliant(p,{h,sweeps:s}));
reference.matched={n:3,hSeconds:h,initialState:'u=v=0; multipliers reset',modelMismatch:'None between solvers: same 162 linear tets, six-mode energy, lumped mass, dead loads and clamp. Both differ from nonlinear anatomical tissue and from static equilibrium.',reference:{iterations:r.iterations,stiffnessApplications:r.stiffnessApplications,elementVisits:r.elementVisits,targetN:r.targetN,...compact(diagnose(p,r.u,{h}))},finiteSweeps:states.map(x=>({sweeps:x.sweeps,constraintVisits:x.constraintVisits,...difference(p,x.u,r.u,{h}),...compact(diagnose(p,x.u,{h}))}))};
reference.stepSensitivity=[];
for(const step of [.0005,.001,.002,.005]) {
  const ref=solveReference(p,{h:step});if(!ref.converged) throw new Error('step comparison reference failed');
  const fast=solveCompliant(p,{h:step,sweeps:5});
  reference.stepSensitivity.push({hSeconds:step,pcgIterations:ref.iterations,...difference(p,fast.u,ref.u,{h:step}),...compact(diagnose(p,fast.u,{h:step}))});
}
reference.meshSolverSensitivity=[];
for(const n of [1,2,3,4]) {
  const caseN=makeCase({n}),ref=solveReference(caseN,{h});if(!ref.converged) throw new Error('mesh comparison failed');
  const fast=solveCompliant(caseN,{h,sweeps:5});
  reference.meshSolverSensitivity.push({n,nodes:caseN.mesh.nodes.length,tetrahedra:caseN.elements.length,...difference(caseN,fast.u,ref.u,{h}),relativeResidual:diagnose(caseN,fast.u,{h}).relativeResidual});
}
const example={schemaVersion:1,source,units:{positions:'m',displacements:'m',force:'N',nodalMass:'kg',stress:'Pa',strain:'dimensionless'},nodeLayout:'nodes[v]=[x,y,z]; u[3*v+d], force[3*v+d], fixed[3*v+d]; d=x:0,y:1,z:2',stressOrder:['xx','yy','zz','xy','yz','zx'],strainOrder:['xx','yy','zz','gamma_xy','gamma_yz','gamma_zx'],parameters:reference.parameters,n:3,hSeconds:h,nodes:p.mesh.nodes,tetrahedra:p.mesh.tets,surface:p.mesh.surface,fixed:p.fixed,forceN:p.force,massKgPerDof:p.mass,exactStaticU:p.mesh.nodes.flatMap(p.exact),static:{u:staticResult.u,converged:staticResult.converged,...diagnose(p,staticResult.u)},implicit:{u:r.u,converged:r.converged,...diagnose(p,r.u,{h})},compliant:states.map(x=>({sweeps:x.sweeps,u:x.u,...difference(p,x.u,r.u,{h}),...diagnose(p,x.u,{h})}))};
// Warm each measured code path, then interleave measurement order to reduce JIT/order bias.
const paths=[{name:'pcg',call:()=>solveReference(p,{h})},...sweeps.filter(s=>s>0).map(s=>({name:'compliant-'+s,call:()=>solveCompliant(p,{h,sweeps:s})}))];
for(let w=0;w<8;w++) for(const f of paths) f.call();
const samples=Object.fromEntries(paths.map(f=>[f.name,[]]));
for(let sample=0;sample<31;sample++) for(const f of sample%2===0?paths:paths.slice().reverse()) {
  const start=performance.now();f.call();samples[f.name].push(performance.now()-start);
}
const stats=raw=>{const x=raw.slice().sort((a,b)=>a-b);return {medianMs:x[15],p10Ms:x[3],p90Ms:x[27],rawMs:raw};};
const setup=[];for(let i=0;i<8;i++) makeCase({n:3});for(let i=0;i<31;i++) {const start=performance.now();makeCase({n:3});setup.push(performance.now()-start);}
const diagnostic=[];for(let i=0;i<31;i++) {const start=performance.now();diagnose(p,r.u,{h});diagnostic.push(performance.now()-start);}
reference.cost={environment,warmupRunsPerPath:8,samplesPerPath:31,measurement:'Each sample is one complete solve call on a preassembled case, including per-call arrays, validation, multiplier reset and solver setup. Reference includes final recomputed residual. Diagnostics/error norms/rendering excluded. Shared case assembly builds BOTH representations and is separately timed; no individual end-to-end solver setup advantage is asserted.',assembly:stats(setup),diagnostics:stats(diagnostic),solves:Object.fromEntries(Object.entries(samples).map(([k,v])=>[k,stats(v)]))};
json('data/reference.json',reference);json('data/example.json',example);
const f=x=>x.toExponential(3),percent=x=>(100*x).toFixed(3),cost=reference.cost.solves;
let tables='# Generated continuum evidence\n\nGenerated by `generate.mjs` by executing `continuum.mjs`. All cases are authored; no measurements of human tissue. Full precision, raw timing samples, parameters and source hashes: `reference.json`. Renderer geometry/fields: `example.json`.\n\n## Static spatial convergence against the quadratic continuum solution\n\n| n per direction | nodes / tets | PCG iterations | relative displacement L2 | relative energy norm | observed L2 order | free residual (N) |\n|---:|:---|---:|---:|---:|---:|---:|\n';
for(const x of reference.staticRefinement) tables+=`| ${x.n} | ${x.nodes} / ${x.tetrahedra} | ${x.iterations} | ${f(x.relativeL2)} | ${f(x.relativeEnergy)} | ${x.observedL2Order?.toFixed(2)??'—'} | ${f(x.residualN)} |\n`;
tables+='\n## Same discrete implicit step, n=3, h=0.0005 s, from rest\n\n| method / sweeps | work count | relative objective-norm error | max nodal error (m) | relative free force residual | median solve (ms) | p10–p90 (ms) |\n|:---|---:|---:|---:|---:|---:|:---|\n';
const rc=cost.pcg;tables+=`| PCG, ${r.iterations} iterations | ${r.elementVisits} element visits | reference | reference | ${f(reference.matched.reference.relativeResidual)} | ${rc.medianMs.toFixed(3)} | ${rc.p10Ms.toFixed(3)}–${rc.p90Ms.toFixed(3)} |\n`;
for(const x of reference.matched.finiteSweeps) {const t=cost['compliant-'+x.sweeps];tables+=`| compliant, ${x.sweeps} | ${x.constraintVisits} constraint visits | ${f(x.relativeObjectiveNorm)} | ${f(x.maxNodalM)} | ${f(x.relativeResidual)} | ${t?.medianMs.toFixed(3)??'unmeasured predictor'} | ${t?`${t.p10Ms.toFixed(3)}–${t.p90Ms.toFixed(3)}`:'—'} |\n`;}
tables+=`\nElement and scalar-constraint visits perform different work. Assembly median ${reference.cost.assembly.medianMs.toFixed(3)} ms; diagnostic median ${reference.cost.diagnostics.medianMs.toFixed(3)} ms, separate from solve times. ${environment.node}, V8 ${environment.v8}, ${environment.os} ${environment.kernel}, ${environment.arch}, ${environment.cpu}, ${environment.visibleLogicalCpus} visible logical CPUs. Single thread, virtualized shared host; these timings are not universal benchmarks or browser-frame rates.\n\n## Five sweeps with different implicit steps\n\nEach row uses its own matched PCG target; changing h changes the physical discrete-time solution. This is solver sensitivity, not a temporal convergence experiment.\n\n| h (s) | relative objective-norm error | max nodal error (m) | max strain tensor norm |\n|---:|---:|---:|---:|\n`;
for(const x of reference.stepSensitivity) tables+=`| ${x.hSeconds} | ${f(x.relativeObjectiveNorm)} | ${f(x.maxNodalM)} | ${f(x.maxStrain)} |\n`;
tables+='\n## Five sweeps with different meshes, h=0.0005 s\n\nEach row uses its own matched PCG target. This isolates algebraic solver error, separately from static continuum discretization error.\n\n| n | nodes / tets | relative objective-norm error | relative free residual |\n|---:|:---|---:|---:|\n';
for(const x of reference.meshSolverSensitivity) tables+=`| ${x.n} | ${x.nodes} / ${x.tetrahedra} | ${f(x.relativeObjectiveNorm)} | ${f(x.relativeResidual)} |\n`;
writeFileSync(root+'data/tables.md',tables);
if(existsSync(root+'chapter.md')) {
  const chapter=readFileSync(root+'chapter.md','utf8');
  const block=tables.replace('# Generated continuum evidence', '### Executed evidence');
  writeFileSync(root+'chapter.md',chapter.replace(/<!-- BEGIN GENERATED EVIDENCE -->[\s\S]*?<!-- END GENERATED EVIDENCE -->/, '<!-- BEGIN GENERATED EVIDENCE -->\n'+block+'\n<!-- END GENERATED EVIDENCE -->'));
}
const run=spawnSync(process.execPath,['--test',root+'tests/continuum.test.mjs'],{encoding:'utf8'});
json('data/test-receipt.json',{schemaVersion:1,utc:new Date().toISOString(),environment,command:'node --test education/contributions/continuum_reference/tests/continuum.test.mjs',moduleSha256:sha('continuum.mjs'),testSha256:sha('tests/continuum.test.mjs'),exitCode:run.status,stdout:run.stdout,stderr:run.stderr,scope:'Numerical module only; no browser, assembly, PDF, Lean or hosted CI certification.'});
if(run.status!==0) throw new Error('focused tests failed: '+run.stdout+run.stderr);
const files=['continuum.mjs','generate.mjs','tests/continuum.test.mjs','sources.json','README.md','chapter.md','VALIDATION.md','data/reference.json','data/example.json','data/tables.md','data/test-receipt.json'];
json('data/provenance.json',{schemaVersion:1,source,generatedUtc:environment.utc,authorship:'Original Kenoma teaching module, synthetic geometry/load data, numerical results, tests and prose. No primary-source PDF/figure or new medical data redistributed.',files:Object.fromEntries(files.map(path=>[path,{sha256:sha(path),bytes:readFileSync(root+path).length}]))});
console.log(tables);
console.log('Focused tests passed; source-bound receipt and data hashes saved.');
