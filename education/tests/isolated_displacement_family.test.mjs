import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {prepareModalBody} from '../web/anatomical-modal.mjs';
import {meshPartition,originalFreeColumns,nestedFamily,projectScalar,projectVector,exactDyadicRank,cartesianColumns,dot,maxAbs} from '../tools/isolated-displacement-family.mjs';
const geometry=JSON.parse(fs.readFileSync(new URL('../data/anatomical-arm-v1/generated/arm-reference.json',import.meta.url)));
const source=geometry.muscles.find(m=>m.element_id==='FJ1478'),body=prepareModalBody(source),partition=meshPartition(source),original=originalFreeColumns(source,body.nodeModes,partition),family=nestedFamily(partition,original.columns);
const near=(a,b,t=1e-11)=>assert.ok(Math.abs(a-b)<=t,`${a} vs ${b}`);

test('explicit cap sets cover all six P2 nodes on every cap face; topology groups partition all free nodes',()=>{
 assert.equal(partition.held.length,90);assert.equal(partition.free.length,495);assert.equal(partition.capFaceCount,28);
 const all=[...partition.freeVertices,...partition.capAdjacentMidpoints,...partition.lateralMidpoints,...partition.interiorMidpoints];
 assert.equal(all.length,495);assert.equal(new Set(all).size,495);assert.deepEqual(all.sort((a,b)=>a-b),partition.free);
 assert.deepEqual(original.capLeaks,[{node:519,base:45,value:1.1546319456101628e-14}]);
 const damaged=structuredClone(source);damaged.proximal_nodes=damaged.proximal_nodes.filter(n=>n!==519);
 assert.throws(()=>meshPartition(damaged),/unconstrained midpoint|complete P2 cap/);
});

test('a shared-edge midpoint identity mismatch is rejected even when coordinates coincide',()=>{
 const damaged=structuredClone(source),mid=source.elements_ten_node[0][4];
 const occurrences=source.elements_ten_node.flatMap((ids,element)=>ids.includes(mid)?[element]:[]);assert.ok(occurrences.length>1);
 const element=occurrences[0],k=damaged.elements_ten_node[element].indexOf(mid);
 damaged.elements_ten_node[element][k]=damaged.nodes_m.length;damaged.nodes_m.push(source.nodes_m[mid].slice());
 assert.throws(()=>meshPartition(damaged),/Shared edge|inconsistent|Nonconforming/);
});

test('exact dyadic rank exposes a tiny independent direction that numerical rank would drop',()=>{
 const columns=[[1,1,0],[2,2,Number.MIN_VALUE]],rows=[0,1,2];assert.equal(exactDyadicRank(columns,rows).rank,2);
 assert.equal(exactDyadicRank([[0,1],[1,0]],[0,1]).rank,2); // unordered pivot columns
 const p={free:[0,1,2],freeVertices:[],capAdjacentMidpoints:[],lateralMidpoints:[],interiorMidpoints:[0,1,2]},s=nestedFamily(p,columns)[0];
 assert.equal(s.exactTailRank,2);assert.equal(s.numericalTailRank,1);
 assert.throws(()=>projectScalar(s,p,[1,2,3]),/no silent column dropping/);
});

test('all levels preserve every original free scalar column and reach full P2 without releasing caps',()=>{
 assert.deepEqual(family.map(s=>s.vectorDimension),[45,285,555,1179,1485]);
 for(const stage of family){
  assert.equal(stage.exactTailRank,stage.numericalTailRank);
  for(const c of original.columns)near(maxAbs(projectScalar(stage,partition,c).map((v,k)=>v-c[k])),0,1e-12);
 }
 const v=partition.free.map((_,i)=>Math.sin(.13*i)),terminal=projectScalar(family[4],partition,v);
 assert.deepEqual(Array.from(terminal),v);
});

test('orthogonal projectors are self-adjoint, idempotent and nested for fixed structural vectors',()=>{
 const v=partition.free.map((_,i)=>Math.sin(.13*i)),w=partition.free.map((_,i)=>Math.cos(.23*i));
 for(const [i,s] of family.entries()){
  const Pv=projectScalar(s,partition,v),Pw=projectScalar(s,partition,w),PPv=projectScalar(s,partition,Pv);
  near(maxAbs(PPv.map((x,k)=>x-Pv[k])),0,1e-12);near(dot(v,Pw),dot(Pv,w),1e-10);
  if(i<4)near(maxAbs(projectScalar(family[i+1],partition,Pv).map((x,k)=>x-Pv[k])),0,1e-12);
 }
});

test('projected equilibrium need not be full nodal equilibrium; a new vector direction adds rank',()=>{
 const g=[1,-1],B=[1,1];assert.equal(dot(g,B),0);assert.equal(maxAbs(g),1);
 const vector=Float64Array.from({length:1485},(_,i)=>Math.sin(.17*i)),P=projectVector(family[0],partition,vector),omitted=vector.map((v,k)=>v-P[k]);
 assert.ok(Math.sqrt(dot(omitted,omitted))>1);
 assert.equal(exactDyadicRank(cartesianColumns(original.columns),Array.from({length:1485},(_,i)=>i)).rank,45);
 assert.equal(exactDyadicRank([...cartesianColumns(original.columns),omitted],Array.from({length:1485},(_,i)=>i)).rank,46);
});
