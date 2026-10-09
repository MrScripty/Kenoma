/** Metadata-only manifest preparation. It never imports/evaluates physical code. */
import fs from 'node:fs';import path from 'node:path';import {execFileSync} from 'node:child_process';import {fileURLToPath} from 'node:url';
import {sha256,instrument,json} from './core.mjs';
import {CAPTURE_POLICY,CAMERA,CAMERA_SHA256} from './capture.mjs';
export const OPERATOR='0b18a4146768ab6a49cb2febdea696bf0c073434';
export const INPUT='0b83819ad3fdaed7405c6bbe617bc01640eef914';
export const INPUTS={
 'generated/arm-reference.json':'1b80c1d3d9f2eb4370cd298f58f5e9c582625574f27072f6d3a1ea898ce4c036',
 'config/attachments-apparatus.json':'070fee738e73e127e334ee5cbe680cb622f100396ad0728eb9df6723c2232389',
 'config/apparatus-routing.json':'b8580e8158e17730b65b64d0fdbe0f1cbbafc76235b9a5f0c2b01020818cd93f',
 'audit/modal-fixed-end-results.json':'b0eeecdade262b682279d9ebeb7a8147a4525a992976a85afc0ce5e63270d8b4',
 'audit/arm-rest-results.json':'8dc23d896adce4b428f39cb172d76f3c74c828f49c2007c66155e45e8ea359c7',
 'audit/arm-rest-recheck.json':'3d1159de78088207320d3b19b17ffc83cb08a531781e26715c8167dd7efbecab',
};
export const POLICY={runs:[{id:'A',attempts:0,configurationEntries:1,wallSeconds:60,muscleMaterial:56448,tendonMaterial:633,materialTensor:0,hessianProducts:0},
 ...[['D',2],['B',1]].map(([id,attempts])=>({id,attempts,configurationEntries:512,wallSeconds:240,muscleMaterial:28901376,tendonMaterial:324096,materialTensor:28901376,hessianProducts:3528840*attempts}))],
 aggregateWallSeconds:540,ownedRSSBytes:1000000000,cgroupBytes:16000000000,perRunOutputBytes:4194304,aggregateOutputBytes:16777216,perRunTranscriptBytes:262144,aggregateTranscriptBytes:1048576,pollSeconds:.01,reservedReceiptBytes:65536,reservedTranscriptBytes:1024,claimDirectory:'/tmp/kenoma-arm-validation-approval-claims',
 capture:CAPTURE_POLICY,outputs:['manifest.json','rest-recheck.json','explicit-halves.json','default.json','comparison.json','resource-receipt.json','transcript.log','geometry-A.slots','geometry-D.slots','geometry-B.slots']};
export const BASELINE_HASHES={"default.json":{"bytes":181,"sha256":"747556ce097e0b45547f031b7609ae5ad35dcd6babeba9cf5ffb466cc9035614"},"comparison.json":{"bytes":54,"sha256":"0a35867dcff565f7c98b1b8395d0b9274492f32b30deb3ce58479ef624029bbe"},"resource-receipt.json":{"bytes":3092,"sha256":"79a2212e17ee668cffc6e74963f6ed0185d1addef239ddb24e24544dd8a5248d"},"transcript.log":{"bytes":6825,"sha256":"eb5f92106489ba5f3ac108d934cf45f1dda2da02f57ad348761cda2193802d04"}};
export function retainedBaseline(){
 const files={};for(const [name,expected] of Object.entries(BASELINE_HASHES)){const b=fs.readFileSync('/tmp/kenoma-arm-four-run-e578474-20261009/'+name);if(b.length!==expected.bytes||sha256(b)!==expected.sha256)throw Error('Changed retained baseline '+name);files[name]={...expected,text:b.toString()};}
 return {operatorCommit:'e57847418a13da39db78cbfcdba070c285f3bfde',manifestSHA256:'c312f2d229ff73c78e810f419e19c11a6edadd6a1b1a689faf6fa71b93a630b2',status:'RESOURCE_INCONCLUSIVE',defaultFinalCountersAvailable:false,files};
}
export function buildManifest(repo,review=null,reviewText=null,destination='/tmp/kenoma-arm-animation-capture-unrun-20261009'){
 if(!path.isAbsolute(destination)||path.resolve(destination)!==destination)throw Error('Exact absolute destination required');
 const git=(...args)=>execFileSync('git',['--no-optional-locks','-C',repo,...args],{maxBuffer:32*1024*1024});
 const modules={};function add(p){if(modules[p])return;const text=git('show',OPERATOR+':'+p).toString();const transformed=instrument(p,text);modules[p]={text,sha256:sha256(text),transformedSHA256:sha256(transformed)};
  const specs=[...text.matchAll(/(?:from\s*|import\s*)['"]([^'"]+)['"]/g)].map(m=>m[1]);for(const spec of specs){if(!spec.startsWith('.'))throw Error('Unlisted physical import '+spec);add(path.posix.normalize(path.posix.join(path.posix.dirname(p),spec)));}}
 for(const p of ['education/web/anatomical-arm.mjs','education/web/anatomical-contact-refinement.mjs','education/web/anatomical-audit.mjs','education/web/anatomical-routing-audit.mjs','education/web/anatomical-transfer.mjs','education/tools/anatomical-replay-contracts.mjs'])add(p);
 const inputs={};for(const [rel,expected] of Object.entries(INPUTS)){const text=git('show',INPUT+':education/data/anatomical-arm-v1/'+rel).toString();if(sha256(text)!==expected)throw Error('Changed input '+rel);inputs[rel]={text,sha256:expected};}
 const harnessFiles={};for(const name of ['core.mjs','prepare.mjs','loader.mjs','replay.mjs','worker.mjs','watchdog.py','capture.mjs','capture_store.py','geometry.mjs','render-browser.mjs','render-build.mjs','render.py','render_worker.py','gif_encode.py']){const rel='education/tools/arm-validation/'+name,b=git('show','HEAD:'+rel);if(!fs.readFileSync(path.join(repo,rel)).equals(b))throw Error('Uncommitted harness '+name);harnessFiles[rel]=sha256(b);}
 const commit=git('rev-parse','HEAD').toString().trim();if(review&&(review.verdict!=='PASS_RUN_READY_SOURCE_ONLY'||review.sourceCommit!==commit))throw Error('Review receipt does not approve this exact harness');
 return {rendererProvenance:{historicalCommit:'611c0554ccb98b04673e5903643f2f01af87d099',historicalInspectorSHA256:'692e7d63993a56ed05cd753e44554f5e3a8eb5b8ccca1e598284c7edcc88dfde',geometryFormulaCommit:OPERATOR,omittedGuideCoordinates:[441,458],acceptedPhysicalMotion:false},camera:CAMERA,cameraSHA256:CAMERA_SHA256,baselineEvidence:retainedBaseline(),schema:1,scope:'BOUNDED_REDUCED_ARM_VALIDATION_NOT_ANATOMICAL_QUALIFICATION',harnessCommit:commit,operatorCommit:OPERATOR,inputCommit:INPUT,nodeVersion:process.version,policy:POLICY,harnessFiles,modules,inputs,reviewReceipt:review,reviewReceiptText:review?(reviewText??json(review)):null,reviewReceiptSHA256:review?sha256(reviewText??json(review)):null,executionDestination:destination,anatomicalQualification:false};
}
if(process.argv[1]&&path.resolve(process.argv[1])===fileURLToPath(import.meta.url)){
 const [repo,out,reviewPath,destination]=process.argv.slice(2);if(!repo||!out)throw Error('Usage: prepare.mjs REPOSITORY NEW_MANIFEST_PATH [REVIEW_RECEIPT] [EXACT_NUMERICAL_DESTINATION]');
 const reviewText=reviewPath?fs.readFileSync(reviewPath,'utf8'):null,receipt=reviewText?JSON.parse(reviewText):null;
 const bytes=json(buildManifest(path.resolve(repo),receipt,reviewText,destination))+'\n';fs.writeFileSync(out,bytes,{flag:'wx'});console.log(json({manifest:out,bytes:Buffer.byteLength(bytes),sha256:sha256(bytes),physicalImports:0,physicalEvaluations:0}));
}
