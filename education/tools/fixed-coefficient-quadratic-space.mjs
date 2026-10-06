/** Nested transverse-quadratic ring restriction of the SAME full P2 field.
 * No geometry, element degree, integration, constitutive or support change. */
import {prepareModalBody} from '../web/anatomical-modal.mjs';
import {denseModalBody} from './anatomical-dense-quadrature.mjs';
import {prepareCompressionBody} from './anatomical-compression-quadrature.mjs';
import {diagnoseControl,maximum,dot} from './fixed-coefficient-fixtures.mjs';
const sub=(a,b)=>a.map((v,d)=>v-b[d]);
export function liftAffineCoordinates(x){
 if(x.length!==63||!x.every(Number.isFinite))throw new RangeError('Finite affine-ring coordinates required');
 const y=new Float64Array(126);for(let r=0;r<7;r++)for(let k=0;k<9;k++)y[r*18+k]=x[r*9+k];return y;
}
export function quadraticRingFixture(source,depth=2){
 const old=prepareModalBody(source),[start,end]=source.belly_interval_m,L=end-start,b=source.basis,R=old.radiusM;
 const nodeModes=source.nodes_m.map((X,n)=>{
  const z=dot(sub(X,b.origin),b.axis),t=Math.max(0,Math.min(6,(z-start)/L*6)),r=Math.min(5,Math.floor(t)),f=t-r,center=source.centerline_m[r].map((v,d)=>v+f*(source.centerline_m[r+1][d]-v)),rel=sub(X,center),u=dot(rel,b.u)/R,v=dot(rel,b.v)/R,q=[u*u,u*v,v*v];
  const modes=old.nodeModes[n].map(m=>({base:Math.floor(m.base/9)*18+m.base%9,value:m.value}));
  for(const [ring,h] of [[r,1-f],[r+1,f]])for(let k=0;k<3;k++)if(Math.abs(h*q[k])>1e-14)modes.push({base:ring*18+(k+3)*3,value:h*q[k]});return modes;
 });
 const body=denseModalBody({...old,nodeModes,ndof:126},depth),free=Array.from({length:90},(_,i)=>i+18);
 return {source,body,prepared:prepareCompressionBody(source,nodeModes,depth),free,heldNodes:new Set([...source.distal_nodes,...source.proximal_nodes]),kind:'ideal',sheets:{strips:[],branches:[],matrix:[]},supports:{branches:[],interfaces:[]},description:'Seven planes × [1,u,v,u²,uv,v²] nodal scalar shapes × three components, interpolated by the unchanged ten-node P2 elements. 126 total / 90 free coordinates; both end-plane coefficients fixed. Original 63 affine coefficients are an exact subset.'};
}
export function projectQuadraticNodal(fixture,nodal){
 const g=new Float64Array(126);fixture.body.nodeModes.forEach((modes,n)=>modes.forEach(m=>{for(let d=0;d<3;d++)g[m.base+d]+=m.value*nodal[n][d];}));return g;
}
export function diagnoseQuadratic(fixture,x,a,material){
 // Reuse only the independently assembled full nodal forces/physical fields.
 // The original helper's 63-coordinate projection is discarded completely;
 // all 126 components are freshly projected here, with the actual free set.
 const {projectedGradientN:discarded,independentReducedResidualN:discardedResidual,...physical}=diagnoseControl({...fixture,free:[]},x,a,material);
 const g=projectQuadraticNodal(fixture,physical.nodalGradientN);
 return {...physical,projectedGradientN:Array.from(g),independentReducedResidualN:maximum(fixture.free.map(i=>g[i])),displacementSpace:fixture.description};
}
