/** Same repaired anatomy and accepted q. Naive bone weights are an authored
 * linear longitudinal rule, not measured skinning or a separate skin mesh.
 * The closed-form LBS gradient is quadratic in reference position and agrees
 * with the full straight-reference P2 nodal interpolant; tests verify this.
 */
import {attachmentMap} from './anatomical-transfer.mjs';import {determinant} from './anatomical-material.mjs';
const sub=(a,b)=>a.map((v,i)=>v-b[i]),dot=(a,b)=>a.reduce((s,v,i)=>s+v*b[i],0);
function weight(m,X){const z=dot(sub(X,m.basis.origin),m.basis.axis),[lo,hi]=m.belly_interval_m;return (hi-z)/(hi-lo);}
export function weightingPositions(m,frame,q){return m.nodes_m.map(X=>{const w=Math.max(0,Math.min(1,weight(m,X))),Y=attachmentMap(X,frame,q).position;return X.map((v,d)=>(1-w)*v+w*Y[d]);});}
function rotationDifference(frame,q){const O=frame.origin_m;return Array.from({length:9},(_,i)=>{const row=Math.floor(i/3),column=i%3,P=O.map((v,d)=>v+(d===column?1:0)),Y=attachmentMap(P,frame,q).position;return Y[row]-O[row]-(row===column?1:0);});}
export function weightingGradient(m,frame,q,X,D=rotationDifference(frame,q)){const O=frame.origin_m,r=sub(X,O),v=Array.from({length:3},(_,i)=>dot(D.slice(3*i,3*i+3),r)),w=weight(m,X),length=m.belly_interval_m[1]-m.belly_interval_m[0],dw=m.basis.axis.map(v=>-v/length);return Array.from({length:9},(_,i)=>(Math.floor(i/3)===i%3?1:0)+w*D[i]+v[Math.floor(i/3)]*dw[i%3]);}
export function anatomyWeightingComparison(model,q){const D=rotationDifference(model.frame,q);return model.bodies.map(body=>{const m=body.modal.source;let volume=0,minJ=Infinity,nonpositive=0;for(const p of body.modal.points){const F=weightingGradient(m,model.frame,q,p.referencePointM,D),J=determinant(F);volume+=p.weightM3*J;minJ=Math.min(minJ,J);if(J<=0)nonpositive++;}return {elementId:m.element_id,nodesM:weightingPositions(m,model.frame,q),signedCurrentVolumeM3:volume,referenceVolumeM3:m.reference_volume_m3,volumeRatio:volume/m.reference_volume_m3,minimumJ:minJ,nonpositiveQuadraturePoints:nonpositive,quadrature:body.modal.quadrature,limits:'Identical repaired reference anatomy, topology and q; authored linear distal-to-proximal bone weights. Exposed tissue comparison, no external skin.'};});}
