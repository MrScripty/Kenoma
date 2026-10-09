import test from 'node:test';
import assert from 'node:assert/strict';
import {SceneModel} from '../scene-state.js';
import {LIMBS} from '../rig.js';
const positions=[[0,.95,0],[0,1.35,0],[0,1.55,0],[0,1.72,0],[.32,1.4,0],[.58,1.2,0],[.79,1,0],[-.32,1.4,0],[-.58,1.2,0],[-.79,1,0],[.15,.85,0],[.15,.48,0],[.15,.08,.08],[-.15,.85,0],[-.15,.48,0],[-.15,.08,.08]];
const graph=()=>({nodes:positions.map((position,i)=>({position:[...position],radii:[.06,.06],root:i===0})),edges:[[0,1],[1,2],[2,3],[1,4],[4,5],[5,6],[1,7],[7,8],[8,9],[0,10],[10,11],[11,12],[0,13],[13,14],[14,15]].map(([a,b])=>({a,b}))});
test('character poses, color, placement and head state are independent',()=>{
 const m=new SceneModel(graph()),first=m.state.selectedId; m.dispatch({type:'add'});const second=m.state.selectedId;
 const original=m.state.characters[0];
 m.dispatch({type:'color',id:second,color:'#FF0022'});m.dispatch({type:'placement',id:second,position:[3,0,2],yaw:1});
 m.dispatch({type:'head',id:second,yaw:.5,pitch:.2});m.dispatch({type:'ik',id:second,limb:'rightArm',target:[.6,1.6,.2]});
 assert.deepEqual(m.state.characters[0],original);assert.equal(m.state.characters[1].color,'#ff0022');
 m.dispatch({type:'select',id:first});m.dispatch({type:'remove',id:second});assert.equal(m.state.characters.length,1);
 m.undo();assert.equal(m.state.characters.length,2);m.redo();assert.equal(m.state.characters.length,1);
});
test('snapshots and input graph cannot mutate model',()=>{
 const g=graph(),m=new SceneModel(g);g.nodes[0].position[0]=99;
 assert.equal(m.state.characters[0].graph.nodes[0].position[0],0);
 assert.throws(()=>m.state.characters[0].graph.nodes[0].position[0]=33);
});
test('gesture undo redo cancel and invalid actions are atomic',()=>{
 const m=new SceneModel(graph()),id=m.state.selectedId,before=m.state;
 m.beginGesture();for(let i=0;i<20;i++)m.dispatch({type:'placement',id,position:[i,0,0]});m.commitGesture();
 m.undo();assert.deepEqual(m.state,before);m.redo();assert.equal(m.state.characters[0].position[0],19);
 const saved=m.state;m.beginGesture();m.dispatch({type:'color',id,color:'#123456'});m.cancelGesture();assert.deepEqual(m.state,saved);
 for(const action of [{type:'placement',id,position:[1,2,3],yaw:NaN},{type:'ik',id,limb:'rightArm',target:[1,2,3],pole:[NaN,0,0]},{type:'remove',id:'missing'},{type:'color',id,color:'red'},{type:'unknown',id}]){
  assert.throws(()=>m.dispatch(action));assert.deepEqual(m.state,saved);
 }
});
test('IDs never recycle, empty scene recovers, no-op edits preserve redo',()=>{
 const m=new SceneModel(graph());m.dispatch({type:'add'});const second=m.state.selectedId;m.undo();m.dispatch({type:'add'});assert.notEqual(m.state.selectedId,second);
 for(const c of m.state.characters)m.dispatch({type:'remove',id:c.id});assert.equal(m.state.selectedId,null);
 m.dispatch({type:'add'});const id=m.state.selectedId;m.dispatch({type:'color',id,color:'#123456'});m.undo();m.dispatch({type:'color',id,color:'#61b9b2'});assert.ok(m.canRedo);
});
test('IK changes only middle/end nodes and preserves rest lengths over repeated edits',()=>{
 const m=new SceneModel(graph()),id=m.state.selectedId;const distance=(a,b)=>Math.hypot(...a.map((v,i)=>v-b[i]));
 for(const [limb,[r,j,e]] of Object.entries(LIMBS)){
  const before=m.state.characters[0].graph;
  for(let i=0;i<100;i++)m.dispatch({type:'ik',id,limb,target:[Math.sin(i)*2,Math.cos(i)*2,Math.sin(i*.3)]});
  const after=m.state.characters[0].graph;
  for(let n=0;n<16;n++)if(n!==j&&n!==e)assert.deepEqual(after.nodes[n],before.nodes[n]);
  for(const [a,b]of [[r,j],[j,e]])assert.ok(Math.abs(distance(after.nodes[a].position,after.nodes[b].position)-distance(positions[a],positions[b]))<1e-8);
 }
});
test('new characters use a free floor slot after removals and manual placement',()=>{
 const m=new SceneModel(graph());m.dispatch({type:'add'});m.dispatch({type:'add'});
 const middle=m.state.characters[1].id;m.dispatch({type:'remove',id:middle});m.dispatch({type:'add'});
 let positions=m.state.characters.map(c=>c.position[0]);assert.equal(new Set(positions).size,3);
 m.dispatch({type:'placement',id:m.state.selectedId,position:[4.2,0,0]});m.dispatch({type:'add'});
 positions=m.state.characters.map(c=>c.position[0]);assert.equal(new Set(positions).size,4);
});
test('constructor rejects malformed graphs and zero-length segments',()=>{
 for(const change of [g=>g.nodes.pop(),g=>g.nodes[4].position=[NaN,0,0],g=>g.nodes[5].position=[...g.nodes[4].position],g=>g.nodes[1].radii=[-1,1],g=>g.edges.push({a:50,b:4}),g=>g.edges.pop(),g=>g.nodes[0].root=false]){
 const g=graph();change(g);assert.throws(()=>new SceneModel(g));
 }
 assert.throws(()=>new SceneModel(null));
});
test('sparse vectors and radii are rejected atomically',()=>{
 const m=new SceneModel(graph()),id=m.state.selectedId,before=m.state;
 m.beginGesture();
 for(const action of [{type:'ik',id,limb:'rightArm',target:new Array(3)},{type:'ik',id,limb:'rightArm',target:[1,2,3],pole:[0,,0]},{type:'placement',id,position:new Array(3)}]){
  assert.throws(()=>m.dispatch(action));assert.deepEqual(m.state,before);
 }
 m.commitGesture();assert.equal(m.canUndo,false);
 for(const sparse of [new Array(2),[.1,]]){
  const g=graph();g.nodes[0].radii=sparse;assert.throws(()=>new SceneModel(g));
 }
 const g=graph();g.nodes[0].radii=[,.1];assert.throws(()=>new SceneModel(g));
 const missingNode=graph();delete missingNode.nodes[1];assert.throws(()=>new SceneModel(missingNode));
});
test('selection-only gestures preserve history and redo',()=>{
 const m=new SceneModel(graph()),first=m.state.selectedId;m.dispatch({type:'add'});const second=m.state.selectedId;
 m.dispatch({type:'color',id:second,color:'#123456'});m.undo();assert.ok(m.canRedo);
 m.beginGesture();m.dispatch({type:'select',id:first});m.commitGesture();
 assert.equal(m.state.selectedId,first);assert.ok(m.canRedo);
 m.undo();assert.equal(m.state.characters.length,1);
 const alone=new SceneModel(graph());alone.beginGesture();alone.dispatch({type:'select',id:alone.state.selectedId});alone.commitGesture();assert.equal(alone.canUndo,false);
});
