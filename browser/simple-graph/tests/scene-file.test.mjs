import test from 'node:test';
import assert from 'node:assert/strict';
import {SceneModel} from '../scene-state.js';
import {exportScene,parseScene,MAX_SCENE_BYTES} from '../scene-file.js';
const points=[[0,.95,0,.16],[0,1.35,0,.21],[0,1.55,0,.07],[0,1.72,0,.13],[.32,1.4,0,.085],[.58,1.2,0,.065],[.79,1,0,.055],[-.32,1.4,0,.085],[-.58,1.2,0,.065],[-.79,1,0,.055],[.15,.85,0,.10],[.15,.48,0,.075],[.15,.08,.08,.065],[-.15,.85,0,.10],[-.15,.48,0,.075],[-.15,.08,.08,.065]];
const links=[[0,1],[1,2],[2,3],[1,4],[4,5],[5,6],[1,7],[7,8],[8,9],[0,10],[10,11],[11,12],[0,13],[13,14],[14,15]];
const graph=()=>({nodes:points.map(([x,y,z,r],i)=>({position:[x,y,z].map(Math.fround),radii:[r,r].map(Math.fround),root:i===0})),edges:links.map(([a,b])=>({a,b}))});
const model=()=>new SceneModel(graph());
function rich(){const m=model();m.dispatch({type:'add'});const id=m.state.selectedId;
 m.dispatch({type:'color',id,color:'#ee3366'});m.dispatch({type:'head',id,yaw:.8,pitch:-.6});m.dispatch({type:'placement',id,position:[2,.1,-3],yaw:1.4});
 m.dispatch({type:'ik',id,limb:'rightArm',target:[.04,1.22,.20],pole:[.62,1.08,.30]});
 m.dispatch({type:'ik',id,limb:'leftLeg',target:[-3,-2,1],pole:[0,1,1]});return m;}
test('initial and posed multi-character state round-trip exactly without mesh or drift',()=>{
 for(const m of [model(),rich()]){
  const expected=m.state;let state=expected;
  for(let i=0;i<20;i++){const text=exportScene(state);assert.ok(!text.includes('indices'));assert.ok(!text.includes('normals'));assert.ok(!text.includes('"graph"'));state=parseScene(text,m.baseGraph);assert.deepEqual(state,expected);}
  assert.deepEqual(m.state,expected);
 }
});
test('names, colors, selection and empty scenes survive source reconstruction',()=>{
 const m=rich(),value=JSON.parse(exportScene(m.state));value.characters[0].name='A person — 漢字';value.characters[1].color='#ABCDEF';value.selectedId=value.characters[0].id;
 const state=parseScene(JSON.stringify(value),m.baseGraph);m.replaceScene(state);assert.equal(m.state.characters[0].name,'A person — 漢字');assert.equal(m.state.characters[1].color,'#ABCDEF');assert.equal(m.state.selectedId,state.selectedId);
 for(const c of m.state.characters)m.dispatch({type:'remove',id:c.id});assert.deepEqual(parseScene(exportScene(m.state),m.baseGraph),m.state);
});
test('malformed, future, duplicate and inconsistent data fail before replacement',()=>{
 const m=rich(),text=exportScene(m.state),before=m.state,revision=m.revision;
 const changes=[
  v=>v.version=2,v=>v.rigVersion=2,v=>v.format='other',v=>v.extra='unsupported',v=>delete v.nextId,
  v=>v.characters.push(structuredClone(v.characters[0])),v=>v.nextId=1,v=>v.nextId=2.5,
  v=>v.characters[0].id='character-01',v=>v.characters[0].id='character-9007199254740992',
  v=>v.selectedId='missing',v=>v.characters[0].name='',v=>v.characters[0].name='x'.repeat(129),
  v=>v.characters[0].color='red',v=>v.characters[0].position=[null,0,0],v=>v.characters[0].position=[0,0],
  v=>v.characters[0].yaw=1000001,v=>v.characters[0].head.pitch='0',v=>v.characters[0].head.extra=0,
  v=>v.characters[0].rig.rightArm.target=[1e10,0,0],v=>delete v.characters[0].rig.leftLeg,
  v=>v.characters[0].pose[5][0]+=.01,v=>v.characters[0].pose[0][0]=.2,v=>v.characters[0].pose.pop(),
 ];
 for(const change of changes){const value=JSON.parse(text);change(value);assert.throws(()=>m.replaceScene(parseScene(JSON.stringify(value),m.baseGraph)));assert.deepEqual(m.state,before);assert.equal(m.revision,revision);}
 for(const invalid of ['', '{', 'null','[]','1','"hello"'])assert.throws(()=>parseScene(invalid,m.baseGraph));
 const parsed=parseScene(text,m.baseGraph);parsed.characters[0].graph.nodes[5].position[0]+=.01;assert.throws(()=>m.replaceScene(parsed));assert.deepEqual(m.state,before);
});
test('byte, character and safe counter budgets are enforced',()=>{
 const m=model();assert.throws(()=>parseScene(' '.repeat(MAX_SCENE_BYTES+1),m.baseGraph),/1 MiB/);
 assert.throws(()=>parseScene('漢'.repeat(MAX_SCENE_BYTES/2),m.baseGraph),/1 MiB/);
 const value=JSON.parse(exportScene(m.state));value.characters=Array.from({length:65},(_,i)=>({...structuredClone(value.characters[0]),id:`character-${i+1}`}));value.nextId=66;
 assert.throws(()=>parseScene(JSON.stringify(value),m.baseGraph),/64/);
 const full=model();for(let i=1;i<64;i++)full.dispatch({type:'add'});const before=full.state;assert.throws(()=>full.dispatch({type:'add'}),/64/);assert.deepEqual(full.state,before);
 const end=JSON.parse(exportScene(m.state));end.nextId=Number.MAX_SAFE_INTEGER;const last=model();last.replaceScene(parseScene(JSON.stringify(end),last.baseGraph));assert.throws(()=>last.dispatch({type:'add'}),/exhausted/);
});
test('valid replacement is one undo step, snapshots independent, imported IDs never recycle',()=>{
 const m=model(),original=m.state,value=JSON.parse(exportScene(rich().state));value.characters[0].id='character-80';value.nextId=81;
 const replacement=parseScene(JSON.stringify(value),m.baseGraph);m.replaceScene(replacement);replacement.characters[0].position[0]=100;assert.notEqual(m.state.characters[0].position[0],100);
 assert.equal(m.state.nextId,81);m.dispatch({type:'add'});assert.equal(m.state.selectedId,'character-81');m.undo();assert.equal(m.state.characters.length,2);m.undo();assert.deepEqual(m.state.characters,original.characters);assert.equal(m.state.nextId,82);
 m.redo();assert.equal(m.state.characters[0].id,'character-80');m.undo();m.dispatch({type:'add'});assert.equal(m.state.selectedId,'character-82');
 const lower=model();m.replaceScene(lower.state);m.dispatch({type:'add'});assert.equal(m.state.selectedId,'character-83');
});
test('revision changes on edits, selection, gestures, undo/redo and import; failures do not change it',()=>{
 const m=rich();let revision=m.revision;
 const changed=action=>{action();assert.ok(m.revision>revision);revision=m.revision;};
 changed(()=>m.dispatch({type:'select',id:m.state.characters[0].id}));
 changed(()=>m.beginGesture());assert.ok(m.gestureActive);
 assert.throws(()=>m.replaceScene(m.state),/gesture/);assert.equal(m.revision,revision);
 changed(()=>m.cancelGesture());assert.equal(m.gestureActive,false);
 changed(()=>m.beginGesture());changed(()=>m.commitGesture());
 changed(()=>m.undo());changed(()=>m.redo());changed(()=>m.replaceScene(m.state));
 assert.throws(()=>m.dispatch({type:'color',id:m.state.selectedId,color:'bad'}));assert.equal(m.revision,revision);
});
test('sparse object-source arrays are rejected without modifying scene',()=>{
 const m=model(),state=structuredClone(m.state),before=m.state;
 state.characters[0].position=new Array(3);assert.throws(()=>m.replaceScene(state));assert.deepEqual(m.state,before);
 state.characters[0].position=[0,0,0];delete state.characters[0].graph.nodes[1];assert.throws(()=>m.replaceScene(state));assert.deepEqual(m.state,before);
});
