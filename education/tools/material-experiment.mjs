import fs from 'node:fs';
import {createHash} from 'node:crypto';
import {compressionPair,MATERIAL_DEFAULTS,evaluateCompressionCandidate} from '../web/material-response.mjs';
import {materialSvg} from '../web/material-lab.mjs';
const defaults=compressionPair(),cases={default:defaults,highBulk:compressionPair({...MATERIAL_DEFAULTS,bulk:250000}),highShear:compressionPair({...MATERIAL_DEFAULTS,mu:5000}),zeroBulk:compressionPair({...MATERIAL_DEFAULTS,bulk:0}),weakBulk:compressionPair({...MATERIAL_DEFAULTS,bulk:500}),coarse:compressionPair({...MATERIAL_DEFAULTS,iterations:8}),restoredHeight:compressionPair({...MATERIAL_DEFAULTS,heightStretch:1})};
const paths=['web/tissue.mjs','web/material-response.mjs','web/material-lab.mjs','tools/material-experiment.mjs'];
const receipt={schema:1,node:process.version,inputs:Object.fromEntries(paths.map(p=>[p,createHash('sha256').update(fs.readFileSync(p)).digest('hex')])),cases,isochoricWallCandidate:evaluateCompressionCandidate(MATERIAL_DEFAULTS,1/Math.sqrt(.8),'confined'),scope:defaults.scope};
const assets=process.argv[2],out=process.argv[3];
if(assets){fs.mkdirSync(assets,{recursive:true});fs.writeFileSync(`${assets}/property-material.svg`,materialSvg(defaults));for(const name of ['highBulk','zeroBulk','weakBulk','coarse'])fs.writeFileSync(`${assets}/material-${name}.svg`,materialSvg(cases[name]));}
if(out)fs.writeFileSync(out,JSON.stringify(receipt,null,2)+'\n');else process.stdout.write(JSON.stringify(receipt,null,2)+'\n');
