/** Completely synthetic virtual modules. No atlas/material/real module import. */
import {numericalWorker} from '../tools/arm-validation/worker.mjs';import {sha256,instrument} from '../tools/arm-validation/core.mjs';import {POLICY} from '../tools/arm-validation/prepare.mjs';
const which=process.argv[2],run=which.startsWith('D')?'D':which.startsWith('C')?'C':which;
const state={coordinatesM:Array(460).fill(0),qRad:0,omegaRadPerS:0,activation:0,timeS:0,step:0,effort:0,massKg:.5,massEvents:[],history:[],mechanicalWorkJ:0};
const parameters={stepS:.01,stationarityToleranceN:1e-4,gMPerS2:0,segmentMassKg:0,stopStiffnessNmPerRad:0,minimumAngleRad:-1,maximumAngleRad:1,jointDampingNmS:0};
const entries={
 'anatomical-arm':`
 export function prepareAnatomicalArm(){return {model:{ndof:460,jointIndex:459,frame:{atlas_bind_angle_rad:0},branches:{length:585},bodies:[{modal:{points:{length:56448}},internalAponeuroses:{branches:{length:48}}}]},parameters:${JSON.stringify(parameters)},contact:{rule:{schema:1}},initialContactRule:{schema:1},baseInertiaKgM2:0,gripRadiusSquaredM2:0};}
 export function anatomicalConfiguration(arm,x,a){globalThis.__kenomaValidation.budget.charge('configurationEntries');return {gradient:new Float64Array(460),positions:[],physicalPotentialJ:3+a,energies:{activePotentialJ:a},headResults:[{minJ:1}],contact:{maximumSampledBonePenetrationM:0,maximumSampledSoftPenetrationM:0,maximumSampledTendonPenetrationM:0}};}
 export function stepAnatomicalArm(arm,s,o){return globalThis.__kenomaValidation.attempt(arm,s,o,()=>{
 ${which==='C-budget'?"try{globalThis.__kenomaValidation.budget.charge('configurationEntries',999);}catch{}":''}
 if(${JSON.stringify(which)}==='C-returned-exception')return {accepted:false,state:s,retryable:false,error:'synthetic terminal error',substepIntegration:{attempts:[{exception:'synthetic terminal error'}]}};
 if(${JSON.stringify(which)}==='D-fail'&&s.step===1)return {accepted:false,state:s,reason:'synthetic late-half refusal'};
 const receipt={activeMechanicalWorkJ:0,maximumFreeModalGradientN:0,referenceQuadratureUpdateJ:0,oldMechanicalJ:3,newMechanicalJ:3,nonlinearWorkDefectJ:0,impulseResidualNmS:0};
 return {accepted:true,state:{...s,timeS:s.timeS+o.h,step:s.step+1,effort:o.effort,contactRule:{schema:1},history:[...s.history,receipt]},receipt};});}
 `,
 'anatomical-contact-refinement':`export function contactRecipe(c){return structuredClone(c.rule);}export function restoreContactRecipe(c,r){c.rule=structuredClone(r);}`,
 'anatomical-audit':`export const finitePoseAudit=()=>({transverseCrossingPairs:0});`,
 'anatomical-routing-audit':`export const finiteRoutingAudit=()=>({accepted:true});`,
 'anatomical-transfer':`export const attachmentMap=()=>({position:[0,0,0],B:[0,0,0]});`,
 'anatomical-apparatus':`export const JOINT_SCALE_M=1;`,
};
entries['anatomical-arm']+='function configuration(arm,x,a,{hessian=true}={}){return null;}function attemptAnatomicalArmStep(){return null;}';
const modules={};for(const [n,text] of Object.entries(entries)){const p='education/web/'+n+'.mjs';modules[p]={text,sha256:sha256(text),transformedSHA256:sha256(instrument(p,text))};}
const contracts='export const heldDomain=()=>{};export const stateLineage=()=>{};';modules['education/tools/anatomical-replay-contracts.mjs']={text:contracts,sha256:sha256(contracts),transformedSHA256:sha256(contracts)};
const input=value=>{const text=JSON.stringify(value);return {text,sha256:sha256(text)};};
const manifest={scope:'SYNTHETIC_TEST_ONLY',operatorCommit:'SYNTHETIC_NO_PHYSICS',harnessCommit:'SYNTHETIC_NO_PHYSICS',policy:POLICY,modules,inputs:{'audit/arm-rest-results.json':input({accepted:true,quadrature:'subdivided32',state,parameters,contactParameters:{}}),'generated/arm-reference.json':input({}),'config/attachments-apparatus.json':input({}),'audit/modal-fixed-end-results.json':input({}),'config/apparatus-routing.json':input({})}};
const packet=await numericalWorker(manifest,run);process.stdout.write(JSON.stringify({syntheticOnly:true,physicalImports:0,physicalEvaluations:0,packet}));
