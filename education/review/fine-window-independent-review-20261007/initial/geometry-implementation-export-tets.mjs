import fs from 'node:fs';
import {recipe} from '/tmp/Kenoma-fine-window-runner/education/tools/fine-window-protocol.mjs';
import {regionTetrahedra,exactCoverage} from '/tmp/Kenoma-fine-window-runner/education/tools/fine-window-maps.mjs';
import {shells} from '/tmp/Kenoma-fine-window-runner/education/tools/element247-shell-protocol.mjs';
const fd=fs.openSync('/tmp/fine-window-geometry-independent/implementation-tets.jsonl','wx');
const topology=[];
try{for(const id of ['I0','I1'])for(const e of [247,206,203,197]){const r=recipe(e,id);topology.push(exactCoverage(r));for(const s of shells(20))for(const tet of regionTetrahedra(r,s))fs.writeSync(fd,JSON.stringify({id,corner:r.corner,region:s.id,vertices:tet.vertices,det:String(tet.det),D:tet.D,index:tet.index})+'\n');}}finally{fs.closeSync(fd);}
fs.writeFileSync('/tmp/fine-window-geometry-independent/implementation-topology.json',JSON.stringify(topology,null,2)+'\n',{flag:'wx'});
