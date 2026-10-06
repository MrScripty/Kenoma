/* Runs authored RK4 model; no source-runtime or physiological claim. */
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {createVerticalForceLab} from '../web/vertical-force-model.js';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../..'),out=path.join(root,'education/data/vertical-force-command-v1/review');
const P=JSON.parse(fs.readFileSync(path.join(root,'education/data/vertical-force-command-v1/protocol.json')));
const controls=JSON.parse(fs.readFileSync(path.join(root,'education/data/millard-reference-v1/review/native-controls.json')));
const lab=createVerticalForceLab(P,controls),W=.5*P.gravity_m_per_s2,md=lab.descendingMass();
const cases=[['baseline','baseline',.5,W,0],['pulse','pulse',.5,1.2*W,0],['lower','lower',.5,.8*W,0],['release','release',.5,0,0],['high','high',.5,120,0],['mass-025','mass',.25,5,0],['mass-05','mass',.5,5,0],['mass-1','mass',1,5,0],['desc-fixed-plus','descending_fixed',md,md*P.gravity_m_per_s2,1e-4],['desc-fixed-minus','descending_fixed',md,md*P.gravity_m_per_s2,-1e-4],['desc-pi-plus','descending_pi',md,md*P.gravity_m_per_s2,1e-4],['desc-pi-minus','descending_pi',md,md*P.gravity_m_per_s2,-1e-4]];
if(process.argv[1]===fileURLToPath(import.meta.url)){fs.mkdirSync(out,{recursive:true});const manifest=[];for(const [id,name,m,target,perturb] of cases){const cfg=lab.init(name,m,target,perturb);manifest.push({id,cfg});for(const [tag,dt] of [['coarse',P.coarse_step_s],['fine',P.fine_step_s]]){const result=lab.run(cfg,dt);fs.writeFileSync(path.join(out,`${id}-${tag}.json`),JSON.stringify(result)+'\n');console.log(id,tag,result.numericalStatus,result.acceptedTime,result.tracking.status);}}fs.writeFileSync(path.join(out,'cases.json'),JSON.stringify(manifest,null,2)+'\n');}
export {lab,cases,root,out};
