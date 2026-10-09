/** Geometry observation only. Never imports a model, solver or material module. */
import fs from 'node:fs';
import {performance} from 'node:perf_hooks';
import {sha256,json} from './core.mjs';
export const CAPTURE_POLICY=Object.freeze({version:1,coordinates:460,slotBytes:8192,slotsPerAttempt:12,checkpoints:[1,2,4,8,16,32,64,128,256],maxRecords:{A:1,D:516,B:514},maxFrames:34,maxReadBytes:65536,pipeBytes:8192,maxSupervisorBuffersBytes:1048576});
export const CAMERA=Object.freeze({renderer:'three@0.180.0',historicalCommit:'611c0554ccb98b04673e5903643f2f01af87d099',width:960,height:720,canvasHeight:560,viewPanels:1,background:0x15202a,halfHeightM:.35,nearM:.001,farM:10,centerOffsetM:[0,0,.015],eyeOffsetM:[0,-1,.08],up:[0,0,1],pixelRatio:1,jpegQuality:85,muscleOpacity:.84,ambientIntensity:2,directionalIntensity:3,directionalPosition:[-1,-1,2],cameraFit:'FIXED_NO_FRAME_RESCALE',depiction:'Seven reduced modal muscle surfaces and three atlas bones; guide and tendon paths omitted. Surfaces do not imply full nodal equilibrium.'});
export const CAMERA_SHA256=sha256(json(CAMERA));
export function provenance(manifest,run,manifestSHA256){return {schema:1,run,manifestSHA256,harnessCommit:manifest.harnessCommit,operatorCommit:manifest.operatorCommit,inputCommit:manifest.inputCommit,modelSHA256:manifest.inputs['generated/arm-reference.json'].sha256,inputStateSHA256:manifest.inputs['audit/arm-rest-results.json'].sha256,cameraSHA256:CAMERA_SHA256,coordinateUnits:'m; joint coordinate is 0.1 m/rad times q',jointScaleMPerRad:.1,workerPID:process.pid,supervisorPID:process.ppid};}
export function encodeFrame(record,coordinates){
 if(coordinates?.length!==460||!Array.from(coordinates).every(Number.isFinite))throw Error('Invalid detached capture coordinates');
 const raw=Buffer.alloc(460*8);for(let i=0;i<460;i++)raw.writeDoubleLE(coordinates[i],i*8);
 const payload=Buffer.from(json({...record,coordinatesFloat64LE:raw.toString('base64'),coordinatesSHA256:sha256(raw)}));
 if(payload.length>CAPTURE_POLICY.slotBytes-36)throw Error('Capture record ceiling');
 const header=Buffer.alloc(36);header.writeUInt32BE(payload.length);Buffer.from(sha256(payload),'hex').copy(header,4);return Buffer.concat([header,payload]);
}
export function createCapture(fd,identity,check=()=>{}){
 if(!Number.isInteger(fd)||fd<3||!fs.fstatSync(fd).isFIFO())throw Error('Missing dedicated capture pipe');
 let sequence=0,bytes=0,writeMilliseconds=0,records=0;const attempts=new Map();
 return {
  snapshot(kind,attempt,coordinates,extra={}){
   check();const local=attempts.get(attempt)??0;if(kind==='BEGIN'&&attempts.has(attempt))throw Error('Repeated capture beginning');
   if(kind!=='BEGIN'&&!attempts.has(attempt))throw Error('Capture before beginning');
   if(!['BEGIN','NEWTON_ITERATE','STEP_CANDIDATE'].includes(kind))throw Error('Capture kind');
   const attemptSequence=kind==='NEWTON_ITERATE'?local+1:local;
   if(records>=CAPTURE_POLICY.maxRecords[identity.run])throw Error('Capture cumulative record ceiling');
   // Copy to a fresh binary buffer before writing; no live alias escapes.
   const frame=encodeFrame({...identity,...extra,kind,attempt,sequence:++sequence,attemptSequence,status:'PROVISIONAL_NEWTON_ITERATE',physicalMotionAccepted:false},coordinates);
   const start=performance.now();let offset=0;while(offset<frame.length){check();try{const n=fs.writeSync(fd,frame,offset,frame.length-offset);if(n===0)throw Error('Closed capture pipe');offset+=n;}catch(e){if(e.code!=='EINTR')throw e;}}
   writeMilliseconds+=performance.now()-start;records++;bytes+=frame.length;attempts.set(attempt,attemptSequence);check();
  },
  receipt(){return {records,wireBytes:bytes,writeMilliseconds,maximumWireBytes:CAPTURE_POLICY.maxRecords[identity.run]*CAPTURE_POLICY.slotBytes,status:'PROVISIONAL_GEOMETRY_ONLY'};},
 };
}
