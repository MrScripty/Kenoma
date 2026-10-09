/** Representative ordinary self-contact/crossing and deep-bend regression poses.
 * Targets use the existing analytic IK so bone lengths stay unchanged.
 */
import {SceneModel} from '../scene-state.js';
export const contactCases = [
 {name:'hand-on-torso', edits:[{limb:'rightArm',target:[.04,1.22,.20],pole:[.62,1.08,.30]}]},
 {name:'crossed-arms', edits:[{limb:'rightArm',target:[-.18,1.28,.24],pole:[.45,.95,.28]},{limb:'leftArm',target:[.18,1.18,.28],pole:[-.45,.94,.30]}]},
 {name:'crossed-legs', edits:[{limb:'rightLeg',target:[-.17,.14,.16],pole:[.16,.45,.36]},{limb:'leftLeg',target:[.18,.14,-.06],pole:[-.16,.45,.22]}]},
 {name:'deep-bends', edits:[{limb:'rightArm',target:[.34,1.38,.06],pole:[.70,1.7,.20]},{limb:'rightLeg',target:[.17,.75,.15],pole:[.15,.40,.60]}]},
];
export function posedCases(baseGraph){return contactCases.map(({name,edits})=>{const model=new SceneModel(baseGraph),id=model.state.selectedId;for(const edit of edits)model.dispatch({type:'ik',id,...edit});return {name,graph:model.state.characters[0].graph,head:{yaw:0,pitch:0}};});}
