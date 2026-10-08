import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import {fileURLToPath} from 'node:url';
import {validateModel,section} from './geometry.mjs';
const here=path.dirname(fileURLToPath(import.meta.url));
const args=process.argv.slice(2);
if(args.length!==4||args[0]!=='--data'||args[2]!=='--out')throw Error('Use --data ABSOLUTE_RETAINED_DATA_ROOT --out ABSOLUTE_NEW_OUTPUT');
const data=args[1],out=args[3];
if(!path.isAbsolute(data)||!path.isAbsolute(out)||fs.existsSync(out))throw Error('Explicit absolute input and new output required');
if(out===data||out.startsWith(data+path.sep)||out.startsWith(path.resolve(here,'../../..')+path.sep))throw Error('Output must be outside retained data and source checkout');
for(const root of [data,path.dirname(out)])for(let p=root;;p=path.dirname(p)){if(fs.lstatSync(p).isSymbolicLink())throw Error('Symlink root');if(p===path.dirname(p))break;}
const sha=b=>crypto.createHash('sha256').update(b).digest('hex');
const lock=JSON.parse(fs.readFileSync(path.join(here,'inputs.lock.json')));
const bytes=new Map();
for(const f of lock.files) {
  if(path.isAbsolute(f.path)||f.path.split('/').some(p=>p==='..'||p===''))throw Error('Unsafe input path');
  const p=path.join(data,f.path);for(let q=p;q!==data;q=path.dirname(q))if(fs.lstatSync(q).isSymbolicLink())throw Error('Symlink input');
  if(!fs.lstatSync(p).isFile())throw Error('Nonfile input');
  const b=fs.readFileSync(p);if(b.length!==f.bytes||sha(b)!==f.sha256)throw Error('Input identity: '+f.path);
  const blob=crypto.createHash('sha1').update(Buffer.from('blob '+b.length+'\0')).update(b).digest('hex');
  if(blob!==f.gitBlob)throw Error('Git blob identity: '+f.path);bytes.set(f.path,b);
}
const json=n=>JSON.parse(bytes.get(n));
const reference=json('anatomical-arm-v1/generated/arm-reference.json');
const atlas=json('elbow-v1/data/bodyparts3d_right_arm_m.json');
const attachments=json('anatomical-arm-v1/config/attachments-apparatus.json');
const audit=json('anatomical-arm-v1/audit/anatomical-calibration-nodal.json');
if(audit.sourceHashes['data/anatomical-arm-v1/generated/arm-reference.json']!==sha(bytes.get('anatomical-arm-v1/generated/arm-reference.json')))throw Error('Frozen geometry source binding');
if(reference.source_sha256!==sha(bytes.get('elbow-v1/data/bodyparts3d_right_arm_m.json'))||attachments.source_sha256!==reference.source_sha256)throw Error('Atlas source binding');
for(const p of atlas.parts)if(p.source_sha256!==sha(bytes.get('elbow-v1/'+p.source_obj)))throw Error('Original OBJ source binding: '+p.element_id);
const model={schema:1,sourceCommit:lock.sourceCommit,stationarityToleranceN:audit.unchangedStationarityToleranceN,
  bones:atlas.parts.filter(p=>['FJ3368','FJ3349','FJ3391'].includes(p.element_id)).map(p=>({element_id:p.element_id,name:p.name,vertices_m:p.vertices_m,triangles:p.triangles_zero_based,source_obj:p.source_obj,source_sha256:p.source_sha256})),
  patches:attachments.patches,attachments:attachments.muscles,
  muscles:reference.muscles.map(m=>{const row=audit.rows.find(r=>r.elementId===m.element_id);return {...m,frozen:row?{positions_m:row.nodes.map(n=>n.positionM),held:row.nodes.map(n=>n.held),activation:row.activation,maximumFreeNodalComponentN:row.maximumFreeNodalComponentN,passesFullNodalForceGateAtFrozenPose:row.passesFullNodalForceGateAtFrozenPose,globalVolumeRatio:row.globalVolumeRatio,minimumCornerJ:row.minimumCornerJ}:null};}),
  limits:['Atlas reference; source-derived repaired belly meshes and authored attachment candidates. No anatomical acceptance.','Three fully activated calibration fields are recorded, fixed-cap and nonstationary in full nodal space. Other four bodies have reference geometry only.','Cuts are reference/material planes mapped through recorded P2 positions. Current material sections can be curved; they are not current-space planar slices. Tessellated surface area and projected dimensions are geometric approximations, not local J, PCSA, equilibrium or empirical measurements.','No solver, material evaluation, quadrature, new Lean compilation or anatomical campaign executes.']};
validateModel(model);
const rows=[];
for(const m of model.muscles)for(const f of [.2,.35,.5,.65,.8]) {
  const a=section(m,f,4),b=section(m,f,8);
  rows.push({body:m.element_id,fraction:f,reference:a.reference,current:a.current,maximumSampleDisplacementMm:a.maximumSampleDisplacementMm,tessellation4to8AreaChangeMm2:b.current.tessellatedAreaMm2-a.current.tessellatedAreaMm2,triangles:a.triangles.length});
}
fs.mkdirSync(out);
for(const name of ['index.html','app.mjs','geometry.mjs','style.css','README.md','inputs.lock.json'])fs.copyFileSync(path.join(here,name),path.join(out,name));
fs.mkdirSync(path.join(out,'sources'));
for(const [name,b]of bytes){const p=path.join(out,'sources',name);fs.mkdirSync(path.dirname(p),{recursive:true});fs.writeFileSync(p,b,{flag:'wx'});}
const modelBytes=Buffer.from(JSON.stringify(model));fs.writeFileSync(path.join(out,'model.json'),modelBytes,{flag:'wx'});
const receipt={schema:1,result:'PASS_STATIC_GEOMETRY_EXTRACTION',sourceCommit:lock.sourceCommit,inputFiles:lock.files.length,inputBytes:lock.files.reduce((s,f)=>s+f.bytes,0),bones:3,muscles:7,patches:Object.keys(model.patches).length,frozenFields:3,modelSha256:sha(modelBytes),rows,limits:model.limits};
fs.writeFileSync(path.join(out,'geometry-receipt.json'),JSON.stringify(receipt,null,2)+'\n');
const files=[];
function walk(dir){for(const n of fs.readdirSync(dir)){const p=path.join(dir,n);if(fs.statSync(p).isDirectory())walk(p);else{const b=fs.readFileSync(p);files.push({path:path.relative(out,p).split(path.sep).join('/'),bytes:b.length,sha256:sha(b)});}}}walk(out);
fs.writeFileSync(path.join(out,'manifest.json'),JSON.stringify({schema:1,sourceCommit:lock.sourceCommit,modelSha256:sha(modelBytes),files},null,2)+'\n');
console.log(JSON.stringify({result:receipt.result,out,inputFiles:receipt.inputFiles,rows:rows.length,modelSha256:receipt.modelSha256}));
