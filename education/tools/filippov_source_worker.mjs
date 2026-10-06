/* Research adapter to the immutable source kernels; no source mutation.
 * OpenSim source notices remain in vertical-force-model.js and data/upstream.
 * Only the explicitly approved controller convention changes here.
 */
import fs from 'node:fs';
import readline from 'node:readline';
import {fileURLToPath} from 'node:url';
import path from 'node:path';
import {createVerticalForceLab} from '../web/vertical-force-model.js';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../..');
const P=JSON.parse(fs.readFileSync(path.join(root,'education/data/vertical-force-command-v1/protocol.json')));
const C=JSON.parse(fs.readFileSync(path.join(root,'education/data/millard-reference-v1/review/native-controls.json')));
const lab=createVerticalForceLab(P,C);
for await (const line of readline.createInterface({input:process.stdin})) {
  try {
    const r=JSON.parse(line),o=lab.output(r.z,r.cfg,{target:r.target});
    if(r.sliding){
      // G(p,B): excitation is the prescribed bound, without modifying I.
      o.u=r.bound;
      const a=r.z[2],u=o.u,tau=u>a?.01*(.5+1.5*a):.04/(.5+1.5*a);
      o.adot=(u-Math.max(.01,Math.min(1,a)))/tau;
    }
    o.kt=500*lab.C.tendon.value(o.s,true);
    console.log(JSON.stringify({ok:true,output:o}));
  } catch(e) {console.log(JSON.stringify({ok:false,code:e.code||'source-exception',message:e.message}));}
}
