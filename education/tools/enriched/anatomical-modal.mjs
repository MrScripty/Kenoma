/** The original P2 displacement field plus two normalized excluded nodal
 * scalar shapes (three components each), only in the short biceps head. */
import {prepareModalBody as original,modalPositions,modalSample,evaluateModalBody,materialTensor} from '../../web/anatomical-modal.mjs';
import {excludedNodalDirection} from '../anatomical-nodal-probe.mjs';
import {denseModalBody} from '../anatomical-dense-quadrature.mjs';
export function prepareModalBody(source,options){
 const body=original(source,options);
 if(source.element_id!=='FJ1512')return denseModalBody(body);
 const first=excludedNodalDirection(body,98,0).direction.map(v=>v[0]),second=excludedNodalDirection(body,96,0).direction.map(v=>v[0]),dot=first.reduce((s,v,i)=>s+v*second[i],0);
 second.forEach((v,i)=>second[i]=v-dot*first[i]);const norm=Math.hypot(...second);if(!(norm>.5))throw Error('Dependent enrichment shape');second.forEach((v,i)=>second[i]=v/norm);
 const nodeModes=body.nodeModes.map((modes,i)=>[...modes,{base:63,value:first[i]},{base:66,value:second[i]}]);
 return {...denseModalBody({...body,nodeModes,ndof:69}),enrichment:{nodes:[98,96],scalarShapes:[first,second],norm:'Euclidean P2 nodal; mutually orthonormal and orthogonal to the original 63 body modes'}};
}
export {modalPositions,modalSample,evaluateModalBody,materialTensor};
