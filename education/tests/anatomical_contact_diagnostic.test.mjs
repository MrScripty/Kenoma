import test from 'node:test';
import assert from 'node:assert/strict';
import {addContact,CONTACT_ASSUMPTIONS} from '../web/anatomical-contact.mjs';
import {triangleTree} from '../web/anatomical-distance.mjs';
import {JOINT_SCALE_M} from '../web/anatomical-apparatus.mjs';

test('co-moving tendon guides and bone sum every repeated joint column in fallback torque',()=>{
 const vertices=[[-.1,-.1,-.1],[.1,-.1,-.1],[.1,.1,-.1],[-.1,.1,-.1],[-.1,-.1,.1],[.1,-.1,.1],[.1,.1,.1],[-.1,.1,.1]],triangles=[[0,2,1],[0,3,2],[4,5,6],[4,6,7],[0,1,5],[0,5,4],[1,2,6],[1,6,5],[2,3,7],[2,7,6],[3,0,4],[3,4,7]];
 const model={ndof:1,jointIndex:0,frame:{origin_m:[0,0,0],axis_unit:[0,0,1],atlas_bind_angle_rad:0},bodies:[],branches:[{A0M2:.0001,path:[{kind:'bone',moving:true,referenceM:[.1,.03,.02]},{kind:'bone',moving:true,referenceM:[.1,.07,.04]}]}]};
 const contact={surfaces:[],bones:[{moving:true,tree:triangleTree(vertices,triangles),bounds:{lo:[-.1,-.1,-.1],hi:[.1,.1,.1]},samples:[]}]};
 const evaluate=q=>addContact(model,contact,Float64Array.of(q*JOINT_SCALE_M),{positions:[],energy:0,gradient:new Float64Array(1),hessian:new Float64Array(1)},{parameters:CONTACT_ASSUMPTIONS});
 const r=evaluate(.4),h=1e-5,energyTorque=-(evaluate(.4+h).energy-evaluate(.4-h).energy)/(2*h);
 assert.equal(r.contact.curvatureFallbacks,5);
 assert.equal(r.contact.activeTendonSamples,5);
 assert.ok(r.energy>0);
 assert.ok(Math.abs(r.gradient[0])<1e-10);
 assert.ok(Math.abs(energyTorque)<1e-8);
 assert.ok(Math.abs(r.contact.boneTorqueNm+r.gradient[0]*JOINT_SCALE_M)<1e-10,`reported torque ${r.contact.boneTorqueNm} N m; assembled torque ${-r.gradient[0]*JOINT_SCALE_M} N m`);
});
