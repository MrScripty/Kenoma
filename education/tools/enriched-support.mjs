import {prepareCompressionBody,evaluateCompressionBody} from './anatomical-compression-quadrature.mjs';
import {modalPositions} from '../web/anatomical-modal.mjs';
export function liftDenseCoordinates(x){
 if(x.length!==460)throw Error('Original 460-coordinate arm required');
 const lifted=new Float64Array(466);lifted.set(x.slice(0,126));lifted.set(x.slice(126),132);return lifted;
}
export function retainedIndex(k){return k<126?k:k+6;}
export function independentEnrichedBody(body,coordinates,activation,material){
 const full=evaluateCompressionBody(prepareCompressionBody(body.source,body.nodeModes,2),modalPositions(body,coordinates),activation,material),gradientN=new Float64Array(body.ndof);
 for(const [node,modes] of body.nodeModes.entries())for(const mode of modes)for(let d=0;d<3;d++)gradientN[mode.base+d]+=mode.value*full.nodalGradientN[node][d];
 return {...full,gradientN};
}
