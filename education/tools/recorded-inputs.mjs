/** Verify recorded bytes, without relabelling them as current execution source.
 * Only the enumerated release transition may use the preserved original bytes.
 * Current source code must also match the reviewed replacement hash. Pure
 * replayers use this; new nonlinear executions still require current digests.
 */
import fs from 'node:fs';import {createHash} from 'node:crypto';import {fileURLToPath} from 'node:url';
const root=fileURLToPath(new URL('../',import.meta.url));
const digest=p=>createHash('sha256').update(fs.readFileSync(root+p)).digest('hex');
export function recordedInputMatches(relative,expected){
 if(typeof relative!=='string'||relative.startsWith('/')||relative.split('/').includes('..')||!/^[a-f0-9]{64}$/.test(expected))return false;
 if(digest(relative)===expected)return true;
 const transition=JSON.parse(fs.readFileSync(root+'tools/release-source-transition.json')).files[relative];
 if(!transition||transition.recordedSHA256!==expected||digest(transition.archivePath)!==expected)return false;
 if(transition.kind==='source')return digest(relative)===transition.currentSHA256;
 // The old recheck is a historical input to the original execution. The
 // new recheck is separately rerun and bound to its current verifier/receipts.
 return transition.kind==='historical-derived-receipt';
}
