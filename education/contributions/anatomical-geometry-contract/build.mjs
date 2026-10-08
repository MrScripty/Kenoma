/** Build a consumable geometry contract from locally retained immutable inputs. */
import fs from 'node:fs';import path from 'node:path';import crypto from 'node:crypto';import {execFileSync} from 'node:child_process';import {fileURLToPath} from 'node:url';
import {prepareGeometryContract,evaluateGeometry} from './contract.mjs';
import {validateModel} from '../anatomical-section-inspector/geometry.mjs';
const here=path.dirname(fileURLToPath(import.meta.url)),repo=path.resolve(here,'../../..');
const args=process.argv.slice(2);if(args.length!==4||args[0]!=='--data'||args[2]!=='--out')throw Error('Use --data ABSOLUTE_RETAINED_ROOT --out ABSOLUTE_NEW_OUTPUT');
const [data,out]=[args[1],args[3]];if(!path.isAbsolute(data)||!path.isAbsolute(out)||fs.existsSync(out)||out===data||out.startsWith(data+path.sep)||out.startsWith(repo+path.sep))throw Error('Fresh output outside retained inputs and checkout required');
for(const root of [data,path.dirname(out)])for(let p=root;;p=path.dirname(p)){if(fs.lstatSync(p).isSymbolicLink())throw Error('Symlink root');if(p===path.dirname(p))break;}
const sha=b=>crypto.createHash('sha256').update(b).digest('hex'),lock=JSON.parse(fs.readFileSync(path.join(here,'inputs.lock.json'))),bytes=new Map();
for(const f of lock.files){
 if(path.isAbsolute(f.path)||f.path.split('/').some(p=>p==='..'||p===''))throw Error('Unsafe source path');
 const p=path.join(data,f.path);for(let q=p;q!==data;q=path.dirname(q))if(fs.lstatSync(q).isSymbolicLink())throw Error('Symlink input');
 const b=fs.readFileSync(p);if(b.length!==f.bytes||sha(b)!==f.sha256)throw Error('Source identity '+f.path);
 if(crypto.createHash('sha1').update(Buffer.from('blob '+b.length+'\0')).update(b).digest('hex')!==f.gitBlob)throw Error('Git blob identity');bytes.set(f.path,b);
}
const provenance=[];
for(const f of lock.routingSourceBindings){const b=execFileSync('git',['-C',repo,'show',f.commit+':'+f.path]);if(b.length!==f.bytes||sha(b)!==f.sha256)throw Error('Frozen routing implementation identity');provenance.push([f,b]);}
const json=n=>JSON.parse(bytes.get(n)),reference=json('anatomical-arm-v1/generated/arm-reference.json'),atlas=json('elbow-v1/data/bodyparts3d_right_arm_m.json'),attachments=json('anatomical-arm-v1/config/attachments-apparatus.json'),audit=json('anatomical-arm-v1/audit/anatomical-calibration-nodal.json'),routing=json('anatomical-arm-v1/config/apparatus-routing.json');
for(const [f]of provenance)if(routing.sourceHashes[f.path.slice('education/'.length)]!==f.sha256)throw Error('Recipe/source provenance mismatch');
if(audit.sourceHashes['data/anatomical-arm-v1/generated/arm-reference.json']!==sha(bytes.get('anatomical-arm-v1/generated/arm-reference.json'))||reference.source_sha256!==sha(bytes.get('elbow-v1/data/bodyparts3d_right_arm_m.json'))||attachments.source_sha256!==reference.source_sha256)throw Error('Geometry state/source binding');
const model={schema:1,bones:atlas.parts.filter(p=>['FJ3368','FJ3349','FJ3391'].includes(p.element_id)).map(p=>({...p,triangles:p.triangles_zero_based})),patches:attachments.patches,attachments:attachments.muscles,stationarityToleranceN:audit.unchangedStationarityToleranceN,
 muscles:reference.muscles.map(m=>{const row=audit.rows.find(r=>r.elementId===m.element_id);return {...m,frozen:row?{positions_m:row.nodes.map(n=>n.positionM),held:row.nodes.map(n=>n.held),maximumFreeNodalComponentN:row.maximumFreeNodalComponentN,passesFullNodalForceGateAtFrozenPose:row.passesFullNodalForceGateAtFrozenPose}:null};})};
validateModel(model);
const contract=prepareGeometryContract(model,reference,routing,{adapterParent:lock.adapterParent,sourceCommit:lock.sourceCommit,inputLockSha256:sha(fs.readFileSync(path.join(here,'inputs.lock.json'))),routingDistanceOriginalCommit:'611c0554ccb98b04673e5903643f2f01af87d099',routingClearance:'Historical authored data only; no fresh clearance evaluation'});
const referenceEvaluation=evaluateGeometry(contract,{fieldLabel:'source reference positions'});
const frozenFields=Object.fromEntries(contract.bodies.filter(b=>b.recordedField).map(b=>[b.id,b.recordedField.positionsM]));
const frozenEvaluation=evaluateGeometry(contract,{bodyPositionsById:frozenFields,fieldLabel:'three retained nonstationary calibration fields; other four reference only'});
for(const b of referenceEvaluation.bodies){const original=contract.bodies.find(c=>c.id===b.id);if(Math.abs(b.referenceVolumeM3-original.declaredReferenceVolumeM3)>1e-15)throw Error('Reference volume/source mismatch');}
const receipt={result:'PASS_CONSUMABLE_GEOMETRY_CONTRACT',sourceIdentity:contract.sourceIdentity,bodyCount:7,materialRegions:42,adjacentInterfaces:35,routeCount:585,capSamples:contract.bodies.reduce((s,b)=>s+b.caps.proximal.length+b.caps.distal.length,0),sourcePatchSamples:contract.patches.reduce((s,p)=>s+p.samples.length,0),endpointBindings:contract.routes.flatMap(r=>[r.a,r.b]).reduce((s,b)=>({...s,[b.kind]:(s[b.kind]||0)+1}),{}),limits:contract.limits};
fs.mkdirSync(out);
for(const [name,value]of [['geometry-contract.json',contract],['reference-observables.json',referenceEvaluation],['frozen-observables.json',frozenEvaluation],['geometry-contract-receipt.json',receipt]])fs.writeFileSync(path.join(out,name),JSON.stringify(value,null,2)+'\n');
for(const n of ['README.md','inputs.lock.json','compression-lab-backlog.md'])fs.copyFileSync(path.join(here,n),path.join(out,n));
for(const [n,b]of bytes){const p=path.join(out,'sources',n);fs.mkdirSync(path.dirname(p),{recursive:true});fs.writeFileSync(p,b);}
for(const [f,b]of provenance.filter(([f])=>f.path.startsWith('education/web/'))){const p=path.join(out,'routing-source-provenance',f.commit,f.path);fs.mkdirSync(path.dirname(p),{recursive:true});fs.writeFileSync(p,b);}
const adapter=path.join(out,'adapter','anatomical-geometry-contract'),dependency=path.join(out,'adapter','anatomical-section-inspector');fs.mkdirSync(adapter,{recursive:true});fs.mkdirSync(dependency,{recursive:true});
for(const n of ['contract.mjs','p2-volume.mjs','quantity-definitions.mjs'])fs.copyFileSync(path.join(here,n),path.join(adapter,n));
fs.copyFileSync(path.join(here,'../anatomical-section-inspector/geometry.mjs'),path.join(dependency,'geometry.mjs'));
const manifest=[];function walk(d){for(const n of fs.readdirSync(d)){const p=path.join(d,n);if(fs.statSync(p).isDirectory())walk(p);else{const b=fs.readFileSync(p);manifest.push({path:path.relative(out,p),bytes:b.length,sha256:sha(b)});}}}walk(out);
fs.writeFileSync(path.join(out,'manifest.json'),JSON.stringify({sourceIdentity:contract.sourceIdentity,files:manifest},null,2)+'\n');console.log(JSON.stringify(receipt));
