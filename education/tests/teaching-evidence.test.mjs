import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {createHash} from 'node:crypto';
import {lessonState,parameters,posePreset} from '../web/chapter-models.mjs';
import {SceneModel} from '../../browser/simple-graph/scene-state.js';
import {contactCases} from '../../browser/simple-graph/tests/contact-cases.mjs';
const read=path=>JSON.parse(readFileSync(new URL(path,import.meta.url)));
const atlas=read('../data/elbow-v1/data/bodyparts3d_right_arm_m.json');
const coupling=read('../data/anatomical-arm-v1/audit/coupling-results.json');
const apparatus={geometry:read('../data/anatomical-arm-v1/generated/arm-geometry.json'),trajectory:read('../data/anatomical-arm-v1/audit/arm-trajectory-results.json')};
const ids=['00-scope','04-anatomy','08-actual-data','06-tissue-graphics','11-interfaces','14-coupled-mechanics','15-anatomical-apparatus','13-coverage','04-research-path','05-sources'];
const registry=read('../book/examples/registry.json').examples;
const rows=scene=>Object.fromEntries(scene.metrics);
const close=(a,b,tol=1e-9)=>assert.ok(Math.abs(a-b)<tol,`${a} != ${b}`);
function asset(kind,p){return kind==='atlas'||(['coverage','research'].includes(kind)&&p.layer==='atlas')?atlas:kind==='apparatus'||(kind==='research'&&p.layer==='apparatus')?apparatus:kind==='coupled'?coupling:null;}
test('all ten evidence chapters supply three bounded executable worked states and an honest acceptance inventory',()=>{
 for(const id of ids){const lesson=read(`../book/examples/lessons/${id}.json`),kind=registry.find(e=>e.id===id).kind;
  assert.equal(lesson.chapter,id);assert.equal(lesson.steps.length,3);assert.equal(new Set(lesson.steps.map(s=>s.id)).size,3);
  assert.equal(new Set(lesson.steps.map(s=>JSON.stringify(s.parameters))).size,3);
  for(const step of lesson.steps){assert.ok(step.title&&step.explanation.length>60&&step.observe.length>30);const p=parameters(kind,step.parameters);const state=lessonState(kind,p,asset(kind,p));assert.equal(state.kind,kind);}
  for(const key of ['finding','change','remaining'])assert.ok(lesson.audit[key].length>30);
 }
});
test('atlas identities are bound to actual source OBJ bytes and preserve every triangle',()=>{
 for(let i=0;i<atlas.parts.length;i++){const part=atlas.parts[i],scene=lessonState('atlas',{part:String(i)},atlas),o=scene.objects[0];
  assert.equal(scene.objects.length,1);assert.equal(o.source.name,part.name);
  const bytes=readFileSync(new URL('../data/elbow-v1/'+o.source.path,import.meta.url));assert.equal(createHash('sha256').update(bytes).digest('hex'),o.source.hash);
  assert.deepEqual(o.faces,part.triangles_zero_based);assert.equal(o.vertices.length,part.vertex_count);
  o.vertices.forEach((v,j)=>assert.deepEqual(v,[part.vertices_m[j][0],part.vertices_m[j][2],-part.vertices_m[j][1]]));
 }
 const m=rows(lessonState('atlas',{},atlas));assert.equal(m.Vertices,'13852');assert.equal(m.Triangles,'20218');assert.equal(m['Subject registration'],'false');assert.equal(m['Clinical validation'],'false');
});
test('coverage reference and axial deformation isolate kinematics; atlas ignores that prescribed input',()=>{
 const reference=lessonState('coverage',{layer:'prescribed',stretch:1});assert.deepEqual(reference.objects[0].vertices,reference.objects[1].vertices);assert.equal(rows(reference)['det F'],'1');
 const stretched=lessonState('coverage',{layer:'prescribed',stretch:1.2});assert.equal(rows(stretched)['det F'],'1.2');assert.equal(rows(stretched)['Measured volume ratio'],'1.2');
 assert.deepEqual(lessonState('coverage',{layer:'atlas',stretch:.6},atlas).objects,lessonState('coverage',{layer:'atlas',stretch:1.4},atlas).objects);
});
test('coupled replay retains saved coordinates, shows the force path, and does not replace an unavailable sample',()=>{
 const scenes=[0,6,11].map(sample=>lessonState('coupled',{sample},coupling));
 for(const [i,sample] of [0,6,11].entries()){const scene=scenes[i],record=coupling.runs[0].rows[sample];
  assert.deepEqual(scene.objects[0].vertices,record.positionsM.map(v=>[v[0],-v[2],v[1]]));
  const lines=scene.objects.filter(o=>o.type==='line');assert.equal(lines.length,19); // one rigid lever, nine branches and nine diagrammatic carrier guides
  close(Math.hypot(...lines[0].points[1].map((v,d)=>v-lines[0].points[0][d])),.3);
  const branches=scene.objects.filter(o=>o.role==='tendon-branch'),guides=scene.objects.filter(o=>o.role==='rigid-carrier-guide');assert.equal(branches.length,9);assert.equal(guides.length,9);
  guides.forEach((guide,j)=>{assert.deepEqual(guide.points[0],branches[j].points[1]);assert.deepEqual(guide.points[1],lines[0].points[0]);});
  assert.match(scene.note,/diagrammatic mounting guides, not tendon extensions/);
  for(const branch of branches)assert.ok(scene.objects[0].vertices.some(v=>v.every((x,d)=>x===branch.points[0][d])),'tendon starts at an actual saved tissue node');
  close(parseFloat(rows(scene)['Work defect']),record.nonlinearEndpointWorkDefectJ,1e-6);
 }
 assert.ok(parseFloat(rows(scenes[1])['Hinge angle'])>parseFloat(rows(scenes[2])['Hinge angle']));
 assert.equal(rows(scenes[2]).Excitation,'0');assert.ok(parseFloat(rows(scenes[2])['Angular velocity'])<0);
 assert.ok(parseFloat(rows(scenes[0])['Maximum free nodal residual'])<1e-6);assert.ok(parseFloat(rows(scenes[0])['Work defect'])>.8);
 assert.throws(()=>lessonState('coupled',{sample:11},{runs:[{rows:coupling.runs[0].rows.slice(0,3)}]}),/unavailable/);
});
test('apparatus remains original reference geometry and keeps original rejection separate from later accepted evidence',()=>{
 const scene=lessonState('apparatus',{part:'muscles'},apparatus),m=rows(scene);
 assert.equal(scene.objects.length,7);assert.deepEqual(scene.objects[0].vertices,apparatus.geometry.muscles[0].nodes_m.map(v=>[v[0],v[2],-v[1]]));
 assert.equal(m['Historical accepted snapshots'],'0');assert.equal(m['Historical trajectory completed'],'false');assert.equal(m['Historical rejection'],'nonlinear iteration limit');assert.ok(parseFloat(m['Historical residual'])>parseFloat(m['Historical residual gate']));
 const later=read('../data/anatomical-arm-v1/audit/anatomical-dense-trajectory-recheck.json');assert.equal(later.verifiedSteps,15);close(later.rows.at(-1).timeS,.43);assert.ok(Math.min(...later.rows.map(r=>r.minimumCornerJ))<.713);
 assert.match(scene.note,/before the later reference repair/);assert.match(scene.note,/Later reduced-model trajectory/);
 assert.equal(lessonState('research',{layer:'atlas',part:'bones'},atlas).objects.length,3);assert.equal(lessonState('research',{layer:'atlas',part:'muscles'},atlas).objects.length,7);
});
test('artistic pose presets reuse tested geometric actions, preserve segment lengths and expose no fake physics',()=>{
 const positions=[[0,.95,0],[0,1.35,0],[0,1.55,0],[0,1.72,0],[.32,1.4,0],[.58,1.2,0],[.79,1,0],[-.32,1.4,0],[-.58,1.2,0],[-.79,1,0],[.15,.85,0],[.15,.48,0],[.15,.08,.08],[-.15,.85,0],[-.15,.48,0],[-.15,.08,.08]];
 const graph={nodes:positions.map((position,i)=>({position:[...position],radii:[.06,.06],root:i===0})),edges:[[0,1],[1,2],[2,3],[1,4],[4,5],[5,6],[1,7],[7,8],[8,9],[0,10],[10,11],[11,12],[0,13],[13,14],[14,15]].map(([a,b])=>({a,b}))};
 const distance=(a,b)=>Math.hypot(...a.map((v,i)=>v-b[i]));
 for(const preset of ['neutral','translated','hand-on-torso','crossed-arms']){
  const model=new SceneModel(graph),id=model.state.selectedId;for(const action of posePreset(preset))model.dispatch({...action,id});const character=model.state.characters[0];
  for(const {a,b} of graph.edges)close(distance(character.graph.nodes[a].position,character.graph.nodes[b].position),distance(positions[a],positions[b]));
  if(preset==='translated'){assert.deepEqual(character.position,[.4,0,0]);assert.deepEqual(character.graph,graph);}
  if(preset==='hand-on-torso'||preset==='crossed-arms')assert.deepEqual(posePreset(preset),contactCases.find(c=>c.name===preset).edits.map(edit=>({type:'ik',...edit})));
  const scene=lessonState('pose',{preset});assert.equal(scene.objects.length,0);assert.equal(rows(scene)['Force / pressure'],'Not modeled');assert.equal(rows(scene)['Contact response'],'Not modeled');
 }
 assert.throws(()=>posePreset('simulate-lift'),/Unsupported preset/);
});
