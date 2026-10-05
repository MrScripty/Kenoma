/** Independent full P2 integration at a saved pose. No equilibrium solve,
 * parameter fitting, contact change or Galerkin enrichment occurs here.
 */
import {quadraticShape} from '../web/anatomical-element.mjs';
import {determinant,inverseTranspose,muscleMaterial} from '../web/anatomical-material.mjs';

const corners=[[1,0,0,0],[0,1,0,0],[0,0,1,0],[0,0,0,1]];
const edges=[[0,1],[0,2],[0,3],[1,2],[1,3],[2,3]];
const children=[[0,4,5,6],[1,4,7,8],[2,5,7,9],[3,6,8,9],[4,5,6,9],[4,5,7,9],[4,7,8,9],[4,6,8,9]];
const high=(5+3*Math.sqrt(5))/20,low=(5-Math.sqrt(5))/20;
const four=corners.map((_,i)=>corners.map((_,j)=>i===j?high:low));
export function compressionQuadrature(depth){
 if(!Number.isInteger(depth)||depth<0||depth>2)throw new RangeError('Diagnostic subdivision depth 0, 1 or 2');
 let cells=[corners];
 for(let level=0;level<depth;level++)cells=cells.flatMap(cell=>{
  const vertices=[...cell,...edges.map(([i,j])=>cell[i].map((v,k)=>(v+cell[j][k])/2))];
  return children.map(t=>t.map(i=>vertices[i]));
 });
 return cells.flatMap(cell=>four.map(L=>({L:corners.map((_,k)=>L.reduce((s,v,i)=>s+v*cell[i][k],0)),weight:1/(4*cells.length)})));
}
const tensor=(nodes,gradient)=>Array.from({length:9},(_,k)=>nodes.reduce((s,X,i)=>s+X[Math.floor(k/3)]*gradient[i][k%3],0));
function referencePoint(reference,L,weight,fibre){
 const shape=quadraticShape(L),jacobian=tensor(reference,shape.gradient),J=determinant(jacobian);
 if(!(J>1e-15))throw new RangeError('Invalid reference diagnostic Jacobian');
 const invT=inverseTranspose(jacobian,J);
 return {gradient:shape.gradient.map(g=>[0,1,2].map(i=>[0,1,2].reduce((s,j)=>s+invT[3*i+j]*g[j],0))),weightM3:weight*J/6,fibre};
}
export function prepareCompressionBody(source,nodeModes,depth){
 const rule=compressionQuadrature(depth);
 const elements=source.elements_ten_node.map((nodes,i)=>{
  const reference=nodes.map(n=>source.nodes_m[n]),fibre=source.reference_fibres[i];
  return {nodes,points:rule.map(p=>referencePoint(reference,p.L,p.weight,fibre)),corners:corners.map(L=>referencePoint(reference,L,0,fibre))};
 });
 return {source,nodeModes,depth,pointsPerElement:rule.length,elements,referenceVolumeM3:elements.reduce((s,e)=>s+e.points.reduce((v,p)=>v+p.weightM3,0),0)};
}
export function evaluateCompressionBody(body,positions,activation,material){
 const nodalGradient=body.source.nodes_m.map(()=>[0,0,0]),bulkNodalGradient=body.source.nodes_m.map(()=>[0,0,0]);
 const energies={matrix:0,volume:0,passiveFiber:0,activePotential:0};
 let minimumJ=Infinity,minimumCornerJ=Infinity,currentVolumeM3=0,referenceVolumeBelow09M3=0;
 for(const e of body.elements){
  const X=e.nodes.map(i=>positions[i]);
  for(const p of e.points){
   const F=tensor(X,p.gradient),r=muscleMaterial(F,p.fibre,activation,material),w=p.weightM3,invT=inverseTranspose(F,r.J),volumeP=invT.map(v=>material.bulk*Math.log(r.J)*v);
   for(const key of Object.keys(energies))energies[key]+=w*r.energy[key];
   minimumJ=Math.min(minimumJ,r.J);currentVolumeM3+=w*r.J;if(r.J<.9)referenceVolumeBelow09M3+=w;
   for(let i=0;i<10;i++)for(let d=0;d<3;d++)for(let k=0;k<3;k++){
    nodalGradient[e.nodes[i]][d]+=w*r.P[3*d+k]*p.gradient[i][k];
    bulkNodalGradient[e.nodes[i]][d]+=w*volumeP[3*d+k]*p.gradient[i][k];
   }
  }
  for(const p of e.corners)minimumCornerJ=Math.min(minimumCornerJ,determinant(tensor(X,p.gradient)));
 }
 function project(nodal){const result=new Float64Array(63);for(const [i,modes] of body.nodeModes.entries())for(const mode of modes)for(let d=0;d<3;d++)result[mode.base+d]+=mode.value*nodal[i][d];return result;}
 return {energyJ:Object.values(energies).reduce((s,v)=>s+v,0),energies,gradientN:project(nodalGradient),bulkGradientN:project(bulkNodalGradient),nodalGradientN:nodalGradient,minimumJ,minimumCornerJ,currentVolumeM3,globalVolumeRatio:currentVolumeM3/body.referenceVolumeM3,referenceVolumeFractionBelow09:referenceVolumeBelow09M3/body.referenceVolumeM3};
}
