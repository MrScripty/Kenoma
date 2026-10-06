/** Mesh/linear-algebra preparation only. No energy, force, optimizer or fit. */
import {EDGE_PAIRS} from '../web/anatomical-element.mjs';
const key=ids=>ids.slice().sort((a,b)=>a-b).join(',');
const sorted=x=>[...x].sort((a,b)=>a-b);
export const dot=(a,b)=>a.reduce((s,v,i)=>s+v*b[i],0);
export const maxAbs=x=>x.reduce((m,v)=>Math.max(m,Math.abs(v)),0);

export function meshPartition(source){
 const n=source.nodes_m.length,distal=new Set(source.distal_nodes),proximal=new Set(source.proximal_nodes),held=new Set([...distal,...proximal]);
 if([...distal].some(i=>proximal.has(i)))throw Error('Overlapping cap sets');
 if([...held].some(i=>!Number.isInteger(i)||i<0||i>=n))throw Error('Invalid cap node');
 const vertices=new Set(),edgeNodes=new Map(),nodeEdges=new Map(),faces=new Map(),used=new Set();
 for(const [element,ids] of source.elements_ten_node.entries()){
  if(ids.length!==10||new Set(ids).size!==10||ids.some(i=>!Number.isInteger(i)||i<0||i>=n))throw Error('Invalid ten-node connectivity');
  ids.forEach(i=>used.add(i));ids.slice(0,4).forEach(i=>vertices.add(i));
  EDGE_PAIRS.forEach(([a,b],k)=>{
   const endpoints=sorted([ids[a],ids[b]]),edge=key(endpoints),mid=ids[4+k];
   if(edgeNodes.has(edge)&&edgeNodes.get(edge)!==mid)throw Error('Shared edge has inconsistent P2 midpoint');
   if(nodeEdges.has(mid)&&key(nodeEdges.get(mid))!==edge)throw Error('P2 midpoint reused for another edge');
   edgeNodes.set(edge,mid);nodeEdges.set(mid,endpoints);
  });
  for(let omitted=0;omitted<4;omitted++){
   const local=[0,1,2,3].filter(i=>i!==omitted),v=local.map(i=>ids[i]),m=EDGE_PAIRS.flatMap(([a,b],k)=>local.includes(a)&&local.includes(b)?[ids[4+k]]:[]),id=key(v);
   if(!faces.has(id))faces.set(id,{vertices:sorted(v),nodes:sorted([...v,...m]),elements:[]});
   const f=faces.get(id);if(key(f.nodes)!==key([...v,...m]))throw Error('Nonconforming shared P2 face');f.elements.push(element);
   if(f.elements.length>2)throw Error('Nonmanifold tetrahedron face');
  }
 }
 if(used.size!==n||[...nodeEdges.keys()].some(i=>vertices.has(i))||vertices.size+nodeEdges.size!==n)throw Error('Incomplete/disjoint P2 vertex-edge partition');
 const capNodes=new Set(),lateralEdges=new Set(),capFaces=[],lateralFaces=[];
 for(const f of faces.values())if(f.elements.length===1){
  const cap=[distal,proximal].find(set=>f.vertices.every(i=>set.has(i)));
  if(cap){if(!f.nodes.every(i=>cap.has(i)))throw Error('Cap P2 face has an unconstrained midpoint');f.nodes.forEach(i=>capNodes.add(i));capFaces.push(f);}
  else{lateralFaces.push(f);for(const [a,b] of [[0,1],[0,2],[1,2]])lateralEdges.add(key([f.vertices[a],f.vertices[b]]));}
 }
 if(key([...capNodes])!==key([...held]))throw Error('Explicit held sets do not equal complete P2 cap traces');
 const free=Array.from({length:n},(_,i)=>i).filter(i=>!held.has(i)),freeVertices=free.filter(i=>vertices.has(i));
 const mids=free.filter(i=>nodeEdges.has(i)),capAdjacent=mids.filter(i=>nodeEdges.get(i).some(v=>held.has(v))),capAdjacentSet=new Set(capAdjacent);
 const lateral=mids.filter(i=>!capAdjacentSet.has(i)&&lateralEdges.has(key(nodeEdges.get(i)))),lateralSet=new Set(lateral);
 const interior=mids.filter(i=>!capAdjacentSet.has(i)&&!lateralSet.has(i));
 return {held:sorted(held),free,vertices:sorted(vertices),freeVertices,capAdjacentMidpoints:capAdjacent,lateralMidpoints:lateral,interiorMidpoints:interior,capFaceCount:capFaces.length,lateralFaceCount:lateralFaces.length,interiorFaceCount:[...faces.values()].filter(f=>f.elements.length===2).length,edgeEndpoints:Object.fromEntries([...nodeEdges].map(([node,ends])=>[node,ends]))};
}

// Original scalar columns: five free rings × three scalar shapes. Physical
// components use their Cartesian tensor product. Held rows are NOT classified
// by a floating mode-support threshold.
export function originalFreeColumns(source,nodeModes,partition=meshPartition(source)){
 const columns=Array.from({length:15},()=>new Float64Array(partition.free.length)),leaks=[];
 const freeIndex=new Map(partition.free.map((node,i)=>[node,i]));
 for(const [node,modes] of nodeModes.entries())for(const m of modes)if(m.base>=9&&m.base<54){
  if((m.base-9)%3!==0)throw Error('Original scalar-column layout changed');
  if(freeIndex.has(node))columns[(m.base-9)/3][freeIndex.get(node)]+=m.value;
  else if(m.value!==0)leaks.push({node,base:m.base,value:m.value});
 }
 return {columns,capLeaks:leaks};
}

const view=new DataView(new ArrayBuffer(8));
function dyadic(x){
 if(!Number.isFinite(x))throw Error('Finite structural coefficient required');
 view.setFloat64(0,x);const bits=view.getBigUint64(0),sign=bits>>63n?-1n:1n,exponent=Number(bits>>52n&2047n),fraction=bits&((1n<<52n)-1n);
 return {n:sign*(exponent?fraction+(1n<<52n):fraction),e:exponent?exponent-1023-52:-1074};
}
const abs=x=>x<0n?-x:x;
const gcd=(a,b)=>{a=abs(a);b=abs(b);while(b){[a,b]=[b,a%b];}return a;};
function primitive(row){
 const common=row.reduce((s,v)=>gcd(s,v),0n);if(!common)return row;
 const sign=row.find(v=>v!==0n)<0n?-1n:1n;return row.map(v=>sign*v/common);
}
/** Exact rank of stored binary64 columns, considered as dyadic rationals.
 * Small column count (15). Integer row operations preserve rational row span.
 */
export function exactDyadicRank(columns,rows){
 const pivots=[];
 for(const index of rows){
  const values=columns.map(c=>dyadic(c[index])),nonzero=values.filter(v=>v.n!==0n);
  if(!nonzero.length)continue;
  const exponent=Math.min(...nonzero.map(v=>v.e));
  let row=primitive(values.map(v=>v.n===0n?0n:v.n<<BigInt(v.e-exponent)));
  for(const p of pivots)if(row[p.column]!==0n){const a=p.row[p.column],b=row[p.column];row=primitive(row.map((v,k)=>a*v-b*p.row[k]));}
  const column=row.findIndex(v=>v!==0n);
  if(column>=0)pivots.push({nodeRow:index,column,row});
  if(pivots.length===columns.length)break;
 }
 return {rank:pivots.length,pivotRows:pivots.map(p=>p.nodeRow),pivotColumns:pivots.map(p=>p.column)};
}

export function orthonormalColumns(columns,remaining){
 const Q=[];
 for(const c of columns){
  const q=Float64Array.from(remaining,i=>c[i]),initial=Math.sqrt(dot(q,q));
  for(let pass=0;pass<2;pass++)for(const b of Q){const coefficient=dot(q,b);for(let i=0;i<q.length;i++)q[i]-=coefficient*b[i];}
  const norm=Math.sqrt(dot(q,q));if(norm>1e-11*Math.max(1,initial))Q.push(q.map(v=>v/norm));
 }
 return Q;
}

export function nestedFamily(partition,columns){
 const added=[[],partition.freeVertices,partition.capAdjacentMidpoints,partition.lateralMidpoints,partition.interiorMidpoints];
 const names=['original-free-modes','plus-free-P2-vertices','plus-cap-adjacent-midpoints','plus-lateral-midpoints','full-free-P2'];
 const selected=new Set();
 return added.map((nodes,level)=>{
  nodes.forEach(n=>selected.add(n));const chosen=sorted(selected),remaining=partition.free.flatMap((n,i)=>selected.has(n)?[]:[i]);
  const exact=exactDyadicRank(columns,remaining),Q=orthonormalColumns(columns,remaining);
  return {level,name:names[level],addedNodes:nodes,selectedNodes:chosen,remainingFreeIndices:remaining,exactTailRank:exact.rank,exactTailPivotRows:exact.pivotRows,exactTailPivotColumns:exact.pivotColumns,numericalTailRank:Q.length,scalarDimension:chosen.length+exact.rank,vectorDimension:3*(chosen.length+exact.rank),tailUnitColumns:Q};
 });
}

/** Direct-sum projector: selected nodal axes + orthonormal original-column
 * tails. No dense 1485×1485 matrix or optimizer is needed. */
export function projectScalar(stage,partition,vector){
 if(vector.length!==partition.free.length)throw Error('Scalar family dimensions');
 if(stage.exactTailRank!==stage.numericalTailRank)throw Error('Exact/numerical rank mismatch; no silent column dropping');
 const result=new Float64Array(vector.length),indices=new Map(partition.free.map((n,i)=>[n,i]));
 for(const n of stage.selectedNodes)result[indices.get(n)]=vector[indices.get(n)];
 const tail=Float64Array.from(stage.remainingFreeIndices,i=>vector[i]);
 for(const q of stage.tailUnitColumns){const d=dot(tail,q);for(const [j,i] of stage.remainingFreeIndices.entries())result[i]+=d*q[j];}
 return result;
}

export function projectVector(stage,partition,vector){
 if(vector.length!==3*partition.free.length)throw Error('Vector family dimensions');
 const projected=new Float64Array(vector.length);
 for(let axis=0;axis<3;axis++){
  const component=partition.free.map((_,i)=>vector[3*i+axis]),result=projectScalar(stage,partition,component);
  result.forEach((v,i)=>projected[3*i+axis]=v);
 }
 return projected;
}

export function cartesianColumns(scalarColumns){
 return scalarColumns.flatMap(c=>[0,1,2].map(axis=>Float64Array.from({length:3*c.length},(_,i)=>i%3===axis?c[Math.floor(i/3)]:0)));
}
