import {validateContinuation} from './anatomical-replay-contracts.mjs';
/** Continue an accepted trajectory with finer release increments.
 * Every solve retains the original force, Jacobian and finite geometry gates.
 */
import fs from 'node:fs';
import {createHash} from 'node:crypto';
import {fileURLToPath} from 'node:url';
import {prepareAnatomicalArm,stepAnatomicalArm} from '../web/anatomical-arm.mjs';
const root=fileURLToPath(new URL('../',import.meta.url)),args=process.argv.slice(2),option=(k,d)=>{const i=args.indexOf(k);return i<0?d:args[i+1];},base=option('--base',root+'data/anatomical-arm-v1/audit/contact-coarse-release-base.json'),out=option('--output',root+'data/anatomical-arm-v1/audit/contact-fine-release-results.json'),h=Number(option('--step','.01')),steps=Number(option('--steps','27')),iterations=Number(option('--iterations','120')),run=JSON.parse(fs.readFileSync(base)),read=p=>JSON.parse(fs.readFileSync(root+'data/anatomical-arm-v1/'+p)),plain=v=>JSON.parse(JSON.stringify(v,(_,x)=>ArrayBuffer.isView(x)?Array.from(x):x)),hash=p=>createHash('sha256').update(fs.readFileSync(p)).digest('hex');
if(!(Number.isFinite(h)&&h>0&&Number.isInteger(steps)&&steps>0&&Number.isInteger(iterations)&&iterations>0&&run.snapshots.length&&run.attempts.every(a=>a.accepted)))throw Error('Invalid accepted continuation base');
validateContinuation(run,p=>hash(root+p));
const sourceHashes=Object.fromEntries(Object.keys(run.sourceHashes).map(p=>[p,hash(root+p)]));sourceHashes['tools/anatomical-release-refinement-experiment.mjs']=hash(fileURLToPath(import.meta.url));
let state={...run.held.state,...run.snapshots.at(-1),effort:run.attempts.at(-1).effort,step:run.snapshots.length,history:run.attempts.map(a=>a.receipt),mechanicalWorkJ:run.attempts.reduce((s,a)=>s+a.receipt.activeMechanicalWorkJ,0)};state.coordinatesM=Float64Array.from(state.coordinatesM);
const arm=prepareAnatomicalArm(read('generated/arm-reference.json'),read('config/attachments-apparatus.json'),read('audit/modal-fixed-end-results.json'),{parameters:run.parameters,contactParameters:run.contactParameters,routingRecipe:read('config/apparatus-routing.json'),contactRule:state.contactRule}),payload={schema:1,baseReceiptSHA256:hash(base),sourceHashes,initialState:plain(state),hS:h,requestedSteps:steps,maxIterationsPerFrozenRule:iterations,attempts:[],snapshots:[],completedAllSteps:false};
if(state.coordinatesM.length!==arm.model.ndof)throw Error('Continuation coordinate coverage');
const begin=performance.now();let stage=0;arm.onIteration=r=>{console.log(stage,r.iteration,r.maxGradient,r.step);fs.writeFileSync('/tmp/kenoma-fine-release-progress.json',JSON.stringify({stage,coordinatesM:Array.from(r.fullCoordinates),residualN:r.maxGradient,accepted:false}));};
function save(){payload.elapsedMS=performance.now()-begin;fs.writeFileSync(out,JSON.stringify(payload)+'\n');}
for(let i=0;i<steps;i++){
 stage=i;const start=performance.now(),step=stepAnatomicalArm(arm,state,{effort:0,h,maxIterations:iterations});
 payload.attempts.push(plain({label:'release',hS:h,effort:0,accepted:step.accepted,elapsedMS:performance.now()-start,receipt:step.receipt,reason:step.reason,residualN:step.maxGradientN,surfaceAudit:step.surfaceAudit,routingAudit:step.routingAudit}));
 if(!step.accepted){payload.rejectedCandidate=plain({coordinatesM:step.result.fullCoordinates,contactRule:step.result.candidateContactRule,contactRefinement:step.result.contactRefinement});save();console.log('REJECTED',stage,step.reason,step.maxGradientN);process.exitCode=2;break;}
 state=step.state;payload.snapshots.push(plain({coordinatesM:state.coordinatesM,contactRule:state.contactRule,qRad:state.qRad,omegaRadPerS:state.omegaRadPerS,activation:state.activation,timeS:state.timeS,massKg:state.massKg}));save();console.log('STEP',stage,state.qRad,state.omegaRadPerS,step.receipt.maximumFreeModalGradientN);
}
payload.completedAllSteps=payload.attempts.length===steps&&payload.attempts.every(a=>a.accepted);save();
