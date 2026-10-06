/* Incoming-only activation-equality research adapter. Immutable source kernels.
 * One-sided extensions retain the original activation/deactivation formulas.
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
    const r=JSON.parse(line);
    if(r.sliding)throw Object.assign(new Error('Sliding prohibited'),{code:'activation-no-sliding'});
    const o=lab.output(r.z,r.cfg,{target:r.target});
    if(r.activation_branch){
      if(!['activation','deactivation'].includes(r.activation_branch))throw new Error('Unknown activation branch');
      const a=r.z[2],tau=r.activation_branch==='activation'?.01*(.5+1.5*a):.04/(.5+1.5*a);
      o.adot=(o.u-Math.max(.01,Math.min(1,a)))/tau;
    }
    o.kt=500*lab.C.tendon.value(o.s,true);
    console.log(JSON.stringify({ok:true,output:o}));
  } catch(e) {console.log(JSON.stringify({ok:false,code:e.code||'source-exception',message:e.message}));}
}
