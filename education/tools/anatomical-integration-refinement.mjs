/** A separate 2048-point frozen-pose rule. No changes to the source-bound
 * 4/32/256-point operators or any accepted state. */
import {compressionQuadrature} from './anatomical-compression-quadrature.mjs';
import {quadraticShape} from '../web/anatomical-element.mjs';
import {determinant,inverseTranspose} from '../web/anatomical-material.mjs';
const corners=[[1,0,0,0],[0,1,0,0],[0,0,1,0],[0,0,0,1]],edges=[[0,1],[0,2],[0,3],[1,2],[1,3],[2,3]],vertices=[...corners,...edges.map(([i,j])=>corners[i].map((v,k)=>(v+corners[j][k])/2))],children=[[0,4,5,6],[1,4,7,8],[2,5,7,9],[3,6,8,9],[4,5,6,9],[4,5,7,9],[4,7,8,9],[4,6,8,9]];
export function furtherQuadrature(){return children.flatMap(t=>compressionQuadrature(2).map(p=>({L:corners.map((_,k)=>p.L.reduce((s,v,i)=>s+v*vertices[t[i]][k],0)),weight:p.weight/8})));}
export function prepareFurtherBody(source,nodeModes){
 const rule=furtherQuadrature();
 function point(nodes,L,weight,fibre){const shape=quadraticShape(L),jacobian=Array.from({length:9},(_,k)=>nodes.reduce((s,node,i)=>s+source.nodes_m[node][Math.floor(k/3)]*shape.gradient[i][k%3],0)),J=determinant(jacobian);if(!(J>1e-15))throw Error('Invalid reference Jacobian');const G=inverseTranspose(jacobian,J);return {gradient:shape.gradient.map(g=>[0,1,2].map(i=>[0,1,2].reduce((s,j)=>s+G[3*i+j]*g[j],0))),weightM3:weight*J/6,fibre};}
 const elements=source.elements_ten_node.map((nodes,i)=>({nodes,points:rule.map(p=>point(nodes,p.L,p.weight,source.reference_fibres[i])),corners:corners.map(L=>point(nodes,L,0,source.reference_fibres[i]))}));
 return {source,nodeModes,depth:3,pointsPerElement:2048,elements,referenceVolumeM3:elements.reduce((s,e)=>s+e.points.reduce((v,p)=>v+p.weightM3,0),0)};
}
