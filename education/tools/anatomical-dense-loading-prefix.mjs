/** Freeze the first four actually accepted dense increments. A prefix is
 * an immutable source for sensitivity; it is never a completed trajectory. */
import fs from 'node:fs';
import {createHash} from 'node:crypto';
import {fileURLToPath} from 'node:url';
const root=fileURLToPath(new URL('../',import.meta.url)),base=root+'data/anatomical-arm-v1/',input=base+'audit/anatomical-dense-trajectory.json',out=base+'audit/anatomical-dense-loading-prefix.json',bytes=fs.readFileSync(input),run=JSON.parse(bytes),hash=p=>createHash('sha256').update(fs.readFileSync(root+p)).digest('hex');
if(fs.existsSync(out))throw Error('Preserve existing prefix');
if(run.snapshots.length<4||!run.held.accepted||!run.attempts.slice(0,4).every(a=>a.accepted)||run.pointsPerElement!==256)throw Error('Four accepted dense increments required');
for(const [p,h] of Object.entries(run.sourceHashes))if(hash(p)!==h)throw Error('Changed dense source '+p);
const prefix={...run,result:'ACCEPTED_DENSE_LOADING_PREFIX',sourceHashes:{...run.sourceHashes,'tools/anatomical-dense-loading-prefix.mjs':hash('tools/anatomical-dense-loading-prefix.mjs')},originReceiptSHA256AtFreeze:createHash('sha256').update(bytes).digest('hex'),schedule:run.schedule.slice(0,4),attempts:run.attempts.slice(0,4),snapshots:run.snapshots.slice(0,4),trace:run.trace.filter(r=>r.stage==='held'||r.stage<4),completedAllSteps:false,behavior:undefined,limits:[...run.limits,'Immutable prefix only: no complete lift/release behavior or convergence claim.']};
fs.writeFileSync(out,JSON.stringify(prefix,null,2)+'\n');console.log('FROZEN_DENSE_PREFIX',prefix.snapshots.length,prefix.snapshots.at(-1).timeS);
