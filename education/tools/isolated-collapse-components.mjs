/** Diagnostic decomposition of the EXISTING law and reference integration. */
import {muscleMaterial,determinant,inverseTranspose} from '../web/anatomical-material.mjs';
import {quadraticShape} from '../web/anatomical-element.mjs';
export const TERMS=['matrix','volume','passiveFiber','activePotential'];
export const CORNERS=[[1,0,0,0],[0,1,0,0],[0,0,1,0],[0,0,0,1]];
const EDGES=[[0,1],[0,2],[0,3],[1,2],[1,3],[2,3]],CHILDREN=[[0,4,5,6],[1,4,7,8],[2,5,7,9],[3,6,8,9],[4,5,6,9],[4,5,7,9],[4,7,8,9],[4,6,8,9]];
const high=(5+3*Math.sqrt(5))/20,low=(5-Math.sqrt(5))/20,FOUR=CORNERS.map((_,i)=>CORNERS.map((_,j)=>i===j?high:low));
export function stressComponents(F,fibre,activation,material){
 const actual=muscleMaterial(F,fibre,activation,material),G=inverseTranspose(F,actual.J),I1=F.reduce((s,x)=>s+x*x,0),d=[0,1,2].map(r=>[0,1,2].reduce((s,k)=>s+F[3*r+k]*fibre[k],0)),n=d.map(x=>x/actual.lambda),tension=material.kf/material.b*Math.expm1(material.b*Math.max(actual.lambda-1,0));
 const stresses={matrix:F.map((x,i)=>material.mu*actual.J**(-2/3)*(x-I1/3*G[i])),volume:G.map(x=>material.bulk*Math.log(actual.J)*x),passiveFiber:F.map((_,i)=>tension*n[Math.floor(i/3)]*fibre[i%3]),activePotential:actual.Pactive.slice()};
 const sum=F.map((_,i)=>TERMS.reduce((s,t)=>s+stresses[t][i],0)),error=Math.max(...sum.map((x,i)=>Math.abs(x-actual.P[i]))),scale=Math.max(1,...actual.P.map(Math.abs));if(error>2e-14*scale)throw Error('Stress decomposition does not reproduce existing law');
 return {actual,stresses,I1,stressReconstructionMaximumErrorPa:error};
}
export const tensor=(nodes,gradient)=>Array.from({length:9},(_,k)=>nodes.reduce((s,X,i)=>s+X[Math.floor(k/3)]*gradient[i][k%3],0));
export function referencePoint(source,element,L,weight){
 const ids=source.elements_ten_node[element],shape=quadraticShape(L),R=tensor(ids.map(n=>source.nodes_m[n]),shape.gradient),J=determinant(R);if(!(J>1e-15))throw Error('Reference point outside unchanged geometry domain');const G=inverseTranspose(R,J);
 return {L,gradient:shape.gradient.map(g=>[0,1,2].map(i=>[0,1,2].reduce((s,j)=>s+G[3*i+j]*g[j],0))),weightM3:weight*J/6,fibre:source.reference_fibres[element],referenceJacobian:J};
}
function split(cell){const vertices=[...cell,...EDGES.map(([i,j])=>cell[i].map((x,k)=>(x+cell[j][k])/2))];return CHILDREN.map(ids=>ids.map(i=>vertices[i]));}
export function uniformCells(depth){if(!Number.isInteger(depth)||depth<0||depth>5)throw Error('Bounded diagnostic depth0..5 required');let cells=[{vertices:CORNERS,weight:1}];for(let level=0;level<depth;level++)cells=cells.flatMap(c=>split(c.vertices).map(vertices=>({vertices,weight:c.weight/8})));return cells;}
export function gradedCells(baseDepth,finalDepth,corner=0){if(baseDepth!==3||finalDepth<3||finalDepth>18)throw Error('Bounded graded corner depth3..18');const cells=uniformCells(baseDepth);for(let level=baseDepth;level<finalDepth;level++){const index=cells.findIndex(c=>c.vertices.some(v=>v[corner]===1));if(index<0)throw Error('Missing unique corner cell');const cell=cells[index];cells.splice(index,1,...split(cell.vertices).map(vertices=>({vertices,weight:cell.weight/8})));}return cells;}
export function* cellRule(cells){for(const cell of cells)for(const L of FOUR)yield {L:CORNERS.map((_,k)=>L.reduce((s,x,i)=>s+x*cell.vertices[i][k],0)),weight:cell.weight/4};}
