import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {lessonState,parameters} from '../web/chapter-models.mjs';
import {ELBOW,elbowInitial,elbowResults,elbowStep} from '../web/elbow.mjs';

const chapters={
 '01-force':'force','02-torque':'torque','03-energy':'energy',
 '04-muscle-physiology':'physiology','05-elbow':'elbow','07-tendon-tissue':'tendon'
};
const read=id=>JSON.parse(readFileSync(new URL(`../book/examples/lessons/${id}.json`,import.meta.url)));
const value=(scene,name)=>{const row=scene.metrics.find(([key])=>key===name);assert.ok(row,`Missing diagnostic ${name}`);return Number.parseFloat(row[1]);};
const close=(actual,expected,tolerance=1e-5)=>assert.ok(Math.abs(actual-expected)<=tolerance,`${actual} != ${expected} within ${tolerance}`);
const states=id=>read(id).steps.map(s=>lessonState(chapters[id],s.parameters));
const length=points=>Math.hypot(...points[0].map((v,i)=>v-points[1][i]));

test('all six foundation sequences have four executable, distinct worked states and explicit limits',()=>{
 for(const [id,kind] of Object.entries(chapters)){
  const lesson=read(id);assert.equal(lesson.chapter,id);assert.equal(lesson.steps.length,4);
  assert.equal(new Set(lesson.steps.map(s=>s.id)).size,4);
  assert.equal(new Set(lesson.steps.map(s=>JSON.stringify(s.parameters))).size,4);
  assert.ok(lesson.audit.finding&&lesson.audit.change&&lesson.audit.remaining);
  for(const step of lesson.steps){
   assert.ok(step.title&&step.explanation&&step.observe);
   assert.ok(/\d/.test(step.explanation+step.observe),`${id}/${step.id} needs a worked quantity`);
   const scene=lessonState(kind,parameters(kind,step.parameters));
   assert.ok(scene.objects.length);assert.ok(scene.metrics.every(([label,text])=>label&&!/undefined|NaN|Infinity/.test(text)));
  }
 }
});

test('force sequence isolates time, mass and sign and independently closes work',()=>{
 const [one,two,heavy,negative]=states('01-force');
 close(value(one,'Displacement'),1);close(value(one,'Velocity'),2);
 close(value(two,'Displacement'),4*value(one,'Displacement'));
 close(value(two,'Velocity'),2*value(one,'Velocity'));
 close(value(heavy,'Displacement'),value(two,'Displacement')/2);
 close(value(negative,'Displacement'),-4);close(value(negative,'Velocity'),-4);
 for(const s of [one,two,heavy,negative]){
  const {mass,force}=s.parameters;
  close(value(s,'Work'),force*value(s,'Displacement'));
  close(value(s,'Kinetic energy'),.5*mass*value(s,'Velocity')**2);
  close(value(s,'Work minus kinetic energy'),0);
 }
 const zero=lessonState('force',{force:0,time:2});close(value(zero,'Displacement'),0);close(value(zero,'Velocity'),0);
});

test('torque controls now reach zero and sign reversal with the expected cross product',()=>{
 const [horizontal,half,vertical,other]=states('02-torque');
 close(value(horizontal,'Torque about +Z'),-5*9.81*.3);
 close(value(half,'Torque about +Z'),value(horizontal,'Torque about +Z')/2);
 close(value(vertical,'Torque about +Z'),0,1e-12);
 close(value(other,'Torque about +Z'),-value(half,'Torque about +Z'));
 for(const s of [horizontal,half,vertical,other]){
  close(value(s,'Torque about +Z'),value(s,'Signed horizontal offset')*value(s,'Gravity force Y'));
  close(value(s,'Required static hold moment'),-value(s,'Torque about +Z'));
 }
});

test('oscillator comparison matches elapsed time and reveals hidden intermediate error',()=>{
 const [explicit,symplectic,verlet,fine]=states('03-energy');
 for(const s of [explicit,symplectic,verlet,fine])close(value(s,'Time'),2);
 close(value(explicit,'Energy'),.8*1.1**40,.0001);
 close(value(explicit,'Maximum energy deviation'),100*(1.1**40-1),.01);
 close(value(explicit,'Analytic position'),.2*Math.cos(2*Math.sqrt(40)),1e-6);
 for(const s of [symplectic,verlet])assert.ok(value(s,'Maximum energy deviation')>100*Math.abs(value(s,'Drift from 0.8 J'))/.8);
 assert.ok(value(verlet,'Maximum energy deviation')<value(symplectic,'Maximum energy deviation'));
 assert.ok(value(fine,'Maximum energy deviation')<value(verlet,'Maximum energy deviation')/20);
 assert.ok(value(fine,'Absolute position error')<value(verlet,'Absolute position error')/20);
 close(value(lessonState('energy',{steps:0}),'Maximum energy deviation'),0);
});

test('force and energy retain fixed metre rulers across checkpoints for a preserved camera',()=>{
 for(const [id,extent,tick] of [['01-force',4.5,1],['03-energy',1.6,.2]]){
  const sequence=states(id),ruler=sequence[0].objects[0];
  assert.equal(ruler.type,'line');close(ruler.points[0][0],-extent);close(ruler.points[1][0],extent);
  for(const scene of sequence)assert.deepEqual(scene.objects[0],ruler);
  close(sequence[0].objects[2].points[0][0]-sequence[0].objects[1].points[0][0],tick);
  for(const scene of sequence){
   const marker=scene.objects.find(o=>o.type==='sphere'&&o.color==='#067d91');
   assert.ok(Math.abs(marker.center[0])<extent);
  }
 }
});

test('physiology separates input, delayed activation, passive preload and moment-arm changes',()=>{
 const [start,rise,later,posed]=states('04-muscle-physiology');
 close(value(start,'Excitation'),.6);close(value(start,'Activation'),0);close(value(start,'Active force'),0);
 assert.ok(value(start,'Passive force')>16);
 close(value(rise,'Activation'),.6*(1-Math.exp(-1)),1e-6);
 close(value(later,'Activation'),.6*(1-Math.exp(-3)),1e-6);
 close(value(posed,'Activation'),value(later,'Activation'));
 close(value(rise,'Fiber length'),value(start,'Fiber length'));
 close(value(rise,'Passive force'),value(start,'Passive force'));
 assert.ok(value(posed,'Active force')<value(later,'Active force'));
 assert.ok(value(posed,'Muscle moment')>value(later,'Muscle moment'));
 close(value(posed,'Passive force'),0);
 const release=lessonState('physiology',{activation:.6,excitation:0,time:.15});
 close(value(release,'Activation'),.6*Math.exp(-1),1e-6);
 for(const s of [start,rise,later,posed]){
  const vector=s.objects.find(o=>o.type==='arrow').vector;
  close(Math.hypot(...vector),value(s,'Tension')*.0002,1e-7);
 }
});

test('forward hinge explains inertia, load sensitivity and the actual work residual',()=>{
 const [start,early,lift,heavy]=states('05-elbow');
 assert.ok(value(start,'Muscle moment')+value(start,'Gravity moment')<0);
 assert.ok(value(early,'Muscle moment')+value(early,'Gravity moment')>0);
 assert.ok(value(early,'Angular velocity')<0);assert.ok(value(early,'Angle')<30);
 close(value(lift,'Time'),value(heavy,'Time'));close(value(lift,'Activation'),value(heavy,'Activation'));
 assert.ok(value(lift,'Angle')>value(heavy,'Angle')+50);
 assert.ok(value(lift,'Angular velocity')>value(heavy,'Angular velocity'));
 for(const scene of [early,lift,heavy]){
  const p={...ELBOW,load:scene.parameters.load,excitation:scene.parameters.excitation};
  let state=elbowInitial(p);const initial=elbowResults(state,p).energy;
  for(let n=0;n<scene.parameters.steps;n++)state=elbowStep(state,p);
  close(value(scene,'Work balance residual'),elbowResults(state,p).energy-initial-state.work+state.dissipation,1e-10);
 }
});

test('domain-stop output retains the last accepted time and nonzero velocity without invented contact',()=>{
 const scene=lessonState('elbow',{load:0,excitation:1,steps:80});
 assert.equal(scene.metrics.find(([k])=>k==='Domain stop')[1],'true');
 assert.ok(value(scene,'Time')<.4);assert.ok(value(scene,'Angle')<135);
 assert.ok(value(scene,'Angular velocity')>30);
 assert.match(scene.note,/last admissible state/);
});

test('tendon sequence exposes equilibrium length redistribution and real contact-off penetration',()=>{
 const [passive,rigid,compliant,off]=states('07-tendon-tissue');
 close(value(passive,'Tension'),0);assert.ok(value(passive,'Plate reaction')>5);
 close(value(rigid,'Tendon storage'),0);
 close(value(rigid,'Path length'),value(compliant,'Path length'));
 assert.ok(value(compliant,'Fiber length')<value(rigid,'Fiber length')-.019);
 assert.ok(value(compliant,'Tendon length')>value(rigid,'Tendon length')+.019);
 assert.ok(value(compliant,'Tension')<value(rigid,'Tension'));
 close(value(compliant,'Tendon storage'),.5/30000*value(compliant,'Tension')**2,.00002);
 assert.ok(Math.abs(value(compliant,'Force residual'))<1e-9);close(value(compliant,'Length residual'),0);
 assert.equal(compliant.metrics.find(([k])=>k==='Admissible fiber')[1],'true');
 close(value(compliant,'Plate penetration'),0);assert.ok(value(compliant,'Lateral stress residual')<1e-8);
 close(value(off,'Tension'),value(compliant,'Tension'));close(value(off,'Tendon storage'),value(compliant,'Tendon storage'));
 close(value(off,'Plate reaction'),0);close(value(off,'Tissue volume ratio'),1);
 close(value(off,'Plate penetration'),.06-(.085-.055*Math.sin(Math.PI/4)),1e-7);
 for(const scene of [rigid,compliant,off]){
  const fiber=scene.objects[2],tendon=scene.objects[3];
  assert.equal(fiber.type,'line');assert.equal(tendon.type,'line');
  close(length(fiber.points),value(scene,'Fiber length'),1e-6);
  close(length(tendon.points),value(scene,'Tendon length'),1e-6);
  assert.deepEqual(fiber.points[1],tendon.points[0]);
  const block=scene.objects.find(o=>o.type==='mesh');
  const extent=d=>Math.max(...block.vertices.map(v=>v[d]))-Math.min(...block.vertices.map(v=>v[d]));
  close(extent(0)*extent(1)*extent(2)/(.08*.06*.05),value(scene,'Tissue volume ratio'),1e-6);
 }
});
