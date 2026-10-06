// Fixed, common SI colour scales. Display magnification never enters diagnostics.
export const CONTINUUM_SCALES=Object.freeze({stress:4000,error:.0005});
export function vonMises(s){
 const [xx,yy,zz,xy,yz,zx]=s;
 return Math.sqrt(((xx-yy)**2+(yy-zz)**2+(zz-xx)**2)/2+3*(xy*xy+yz*yz+zx*zx));
}
export function fieldColour(value,max){
 const t=Math.min(1,Math.max(0,value/max));
 return [t,.2,1-t];
}
export function surfaceOwners(mesh){
 const owners=new Map();
 mesh.tets.forEach((tet,i)=>{for(let opposite=0;opposite<4;opposite++){
  const key=tet.filter((_,j)=>j!==opposite).sort((a,b)=>a-b).join(',');
  owners.set(key,owners.has(key)?null:i);
 }});
 return mesh.surface.map(({tri})=>{const i=owners.get([...tri].sort((a,b)=>a-b).join(','));if(!Number.isInteger(i))throw new Error('Boundary face requires one owning element');return i;});
}
export function continuumFields(p,reference,comparison,referenceDiag,comparisonDiag,isStatic,mode,owners){
 if(!['stress','error'].includes(mode))throw new Error('Unknown continuum colour field');
 const target=isStatic?p.mesh.nodes.flatMap(X=>p.exact(X)):reference.u;
 const nodeError=u=>p.mesh.nodes.map((_,i)=>Math.hypot(...[0,1,2].map(d=>u[3*i+d]-target[3*i+d])));
 const nodalErrors=[nodeError(reference.u),nodeError(comparison.u)];
 const fields=mode==='stress'?[referenceDiag,comparisonDiag].map(diag=>owners.map(i=>vonMises(diag.stressPa[i]))):nodalErrors;
 const max=CONTINUUM_SCALES[mode],units=mode==='stress'?'Pa':'m';
 return {mode,max,units,location:mode==='stress'?'element; discontinuous boundary faces':'node; interpolated colour only',target:isStatic?'exact static displacement':'converged matched implicit displacement',fields,nodalErrors,
  observedMax:Math.max(...fields.flat()),clipped:fields.some(field=>field.some(v=>v>max))};
}
