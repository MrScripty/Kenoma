import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {CONTROLS,parameters,lessonState,projectedSamples,validateScene} from '../web/chapter-models.mjs';
import {compressionPair,MATERIAL_DEFAULTS} from '../web/material-response.mjs';
import {serialSpecimen,SERIAL_DEFAULTS} from '../web/serial-specimen.mjs';
import {solveSpatial,SPATIAL} from '../web/spatial.mjs';

const chapters={
 '09a-properties':'deformation','09aa-nonuniform-volume':'nonuniform',
 '09ab-architecture-force':'architecture','09b-material-response':'material',
 '09c-dissipative-response':'dissipative','09d-serial-specimen':'serial',
 '09-continuum-medical':'deformation','10-fast-methods':'continuum',
 '10a-spatial-continuum':'continuum','10b-pressure-projection':'projection',
 '12-spatial-capstone':'spatial'
};
const readLesson=id=>JSON.parse(readFileSync(new URL(`../book/examples/lessons/${id}.json`,import.meta.url)));
const metrics=s=>Object.fromEntries(s.metrics);
const value=(s,key)=>Number.parseFloat(metrics(s)[key]);
const near=(a,b,tol=1e-5)=>assert.ok(Math.abs(a-b)<=tol,`${a} differs from ${b}`);

for(const [id,kind] of Object.entries(chapters))test(`${id}: every worked step is complete, bounded and runnable`,()=>{
 const lesson=readLesson(id);
 assert.equal(lesson.chapter,id);
 assert.ok(lesson.steps.length>=3&&lesson.steps.length<=4);
 assert.equal(new Set(lesson.steps.map(s=>s.id)).size,lesson.steps.length);
 for(const s of lesson.steps){
  assert.match(s.id,/^[a-z0-9]+(?:-[a-z0-9]+)*$/);
  assert.ok(s.title&&s.explanation&&s.observe);
  assert.deepEqual(Object.keys(s.parameters).sort(),CONTROLS[kind].map(c=>c.key).sort(),'Steps must not depend on prior manual control values');
  assert.deepEqual(parameters(kind,s.parameters),s.parameters);
  const result=lessonState(kind,s.parameters);
  assert.equal(validateScene(result),result);
  assert.ok(result.metrics.every(([label,text])=>label&&!/NaN|Infinity|undefined/.test(text)));
 }
 assert.ok(lesson.audit.finding&&lesson.audit.change&&lesson.audit.remaining);
});

test('deformation begins at identity and distinguishes shear strain from rigid rotation',()=>{
 const base=lessonState('deformation'),sheared=lessonState('deformation',{shear:.25}),rotated=lessonState('deformation',{shear:.25,rotation:90});
 near(value(base,'det F'),1,1e-12);
 near(value(base,'Green strain norm'),0,1e-12);
 near(value(sheared,'det F'),1,1e-12);
 assert.ok(value(sheared,'Green strain norm')>.17);
 near(value(sheared,'Reference Y-line stretch'),Math.hypot(1,.25));
 near(value(rotated,'Green strain norm'),value(sheared,'Green strain norm'),1e-12);
 assert.notDeepEqual(rotated.objects[1].vertices,sheared.objects[1].vertices);
});

test('local J exposes cancellation that total volume hides; refinement retains nonzero mesh error',()=>{
 const raw=lessonState('nonuniform',{gradient:.4,compensate:'off',cells:8});
 near(value(raw,'Continuum volume ratio'),1);
 near(value(raw,'Minimum local J'),.6);
 near(value(raw,'Maximum local J'),1.4);
 const coarse=lessonState('nonuniform',{gradient:.4,compensate:'on',cells:8}),fine=lessonState('nonuniform',{gradient:.4,compensate:'on',cells:128});
 near(value(coarse,'Minimum local J'),1);
 near(value(coarse,'Maximum local J'),1);
 assert.ok(value(fine,'Mesh error')>0);
 assert.ok(value(fine,'Mesh error')<value(coarse,'Mesh error')/200);
});

test('material adapter exposes unconverged root truth and preserves the original geometry',()=>{
 const input={stretch:.8,bulk:50000,iterations:8},s=lessonState('material',input),model=compressionPair({...MATERIAL_DEFAULTS,heightStretch:input.stretch,bulk:input.bulk,iterations:input.iterations});
 assert.equal(metrics(s)['Free converged'],'false');
 assert.ok(Math.abs(value(s,'Free lateral residual'))>value(s,'Residual criterion'));
 const width=Math.max(...s.objects[0].vertices.map(v=>v[0]))-Math.min(...s.objects[0].vertices.map(v=>v[0]));
 near(width,model.free.widthM,1e-15);
 const resolved=lessonState('material',{...input,iterations:64});
 assert.equal(metrics(resolved)['Free converged'],'true');
 assert.ok(value(resolved,'Confined plate force')>9*value(resolved,'Free plate force'));
 const noBulk=lessonState('material',{stretch:.8,bulk:0});
 near(value(noBulk,'Free J'),.512);
 near(value(noBulk,'Wall reaction'),0);
});

test('reference/current stress-area pairs agree and pennation is projected exactly once',()=>{
 const s=lessonState('architecture',{angle:60,stretch:.8});
 near(value(s,'Current projected area'),100);
 near(value(s,'Cauchy fibre stress'),240);
 near(value(s,'Axial force'),24);
 near(value(s,'Current-cut force'),24);
 near(value(s,'Tendon-directed force'),12);
 near(value(s,'Current projected area')*1e-6*value(s,'Cauchy fibre stress')*1000,value(s,'Axial force'));
});

test('serial volume preservation does not hide an unresolved force root',()=>{
 const input={force:.1,ratio:2,iterations:8},s=lessonState('serial',input),model=serialSpecimen({...SERIAL_DEFAULTS,...input});
 assert.equal(metrics(s).Converged,'false');
 assert.ok(value(s,'Maximum force residual')>value(s,'Force criterion'));
 near(value(s,'First volume ratio'),1);
 near(value(s,'Second volume ratio'),1);
 assert.deepEqual(s.objects[0].vertices,model.cells[0].currentVertices);
 assert.deepEqual(s.objects[1].vertices,model.cells[1].currentVertices);
 assert.equal(s.objects[2].type,'line');
 const tension=lessonState('serial',{force:.1}),compression=lessonState('serial',{force:-.1});
 assert.ok(value(tension,'First stretch')>value(tension,'Second stretch'));
 assert.ok(value(compression,'First stretch')<value(compression,'Second stretch'));
 assert.equal(metrics(tension).Converged,'true');
});

test('force hold creeps, extension hold relaxes, finite recovery retains storage',()=>{
 const loaded=lessonState('dissipative',{time:1,holdMode:'force'}),creep=lessonState('dissipative',{time:2.8,holdMode:'force'}),relax=lessonState('dissipative',{time:2.8,holdMode:'extension'}),released=lessonState('dissipative',{time:7,holdMode:'force'});
 near(value(creep,'Axial force'),value(loaded,'Axial force'));
 assert.ok(value(creep,'Extension')>value(loaded,'Extension'));
 near(value(relax,'Extension'),value(loaded,'Extension'));
 near(value(relax,'External work'),value(loaded,'External work'),1e-12);
 assert.ok(value(relax,'Axial force')<value(loaded,'Axial force'));
 near(value(released,'Axial force'),0);
 assert.ok(value(released,'Extension')>0&&value(released,'Storage')>0);
 for(const s of [loaded,creep,relax,released]){
  near(value(s,'External work'),value(s,'Storage')+value(s,'Dissipated'),2e-9);
  assert.ok(Math.abs(value(s,'Work residual'))<1e-12);
 }
});

test('finite compliant solve reports both order dependence and measured convergence toward PCG',()=>{
 const one=lessonState('continuum',{sweeps:1}),reverse=lessonState('continuum',{sweeps:1,order:'reverse'}),five=lessonState('continuum',{sweeps:5}),twenty=lessonState('continuum',{sweeps:20});
 assert.equal(metrics(one)['Reference converged'],'true');
 assert.ok(value(one,'Reference residual')<=value(one,'Reference target'));
 assert.equal(value(one,'Constraint visits'),value(reverse,'Constraint visits'));
 assert.ok(Math.abs(value(one,'Maximum nodal difference')-value(reverse,'Maximum nodal difference'))>1);
 assert.ok(value(five,'Compliant residual')<value(one,'Compliant residual')/50);
 assert.ok(value(twenty,'Relative objective-norm error')<1e-8);
 assert.equal(value(twenty,'Constraint visits'),20*value(one,'Constraint visits'));
});

test('projection presets retain the fixed-field energy identity and represented-field exception',()=>{
 for(const field of ['unresolved','paired','constant'])for(const level of [1,2,4]){
  const s=projectedSamples(level,field);
  near(s.full,s.condensed+s.gap,1e-12);
  near(s.residual.reduce((sum,v,i)=>sum+v*s.projected[i]*s.weights[i],0),0,1e-12);
 }
 assert.equal(projectedSamples(2,'paired').gap,0);
 assert.equal(projectedSamples(1,'constant').gap,0);
 assert.throws(()=>projectedSamples(2,'arbitrary'));
});

test('spatial compression preserves failed convergence and returns original solve coordinates',()=>{
 const p={angle:90,activation:.6,sweeps:80,boneContact:'on'},s=lessonState('spatial',p),model=solveSpatial(Math.PI/2,p.activation,{...SPATIAL,sweeps:p.sweeps,boneContact:p.boneContact});
 assert.equal(metrics(s).Converged,'false');
 assert.ok(value(s,'Maximum free force')>1000*value(s,'Stopping criterion'));
 assert.deepEqual(s.objects[0].vertices,model.x);
 assert.deepEqual(s.objects[1].vertices,model.baseline);
 assert.ok(value(s,'Baseline minimum J')<value(s,'Minimum J'));
 const refined=lessonState('spatial',{...p,sweeps:320});
 assert.equal(metrics(refined).Converged,'false');
 assert.ok(value(refined,'Maximum penetration')<value(s,'Maximum penetration'));
 const noContact=lessonState('spatial',{...p,boneContact:'off'});
 assert.ok(value(noContact,'Maximum penetration')>0,'Disabling contact must not label penetration as zero');
});
