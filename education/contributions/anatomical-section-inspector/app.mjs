import {validateModel,section,dot,sub} from './geometry.mjs';
const $=id=>document.getElementById(id);
let model,last;
const fmt=x=>x.toFixed(3);
function canvas(id) {
  const c=$(id),r=c.getBoundingClientRect(),scale=Math.min(devicePixelRatio||1,2);
  c.width=Math.round(r.width*scale);c.height=Math.round(r.height*scale);
  const ctx=c.getContext('2d');ctx.scale(scale,scale);ctx.clearRect(0,0,r.width,r.height);
  return {ctx,w:r.width,h:r.height};
}
function project(points,axes,w,h) {
  const xy=points.map(p=>axes(p)),xs=xy.map(p=>p[0]),ys=xy.map(p=>p[1]);
  const x0=Math.min(...xs),x1=Math.max(...xs),y0=Math.min(...ys),y1=Math.max(...ys);
  const s=Math.min((w-50)/Math.max(x1-x0,1e-6),(h-50)/Math.max(y1-y0,1e-6));
  return {point:p=>{const [x,y]=axes(p);return [w/2+(x-(x0+x1)/2)*s,h/2-(y-(y0+y1)/2)*s];},scale:s};
}
function face(ctx,ps,fill,stroke) {
  ctx.beginPath();ctx.moveTo(...ps[0]);for(const p of ps.slice(1))ctx.lineTo(...p);ctx.closePath();
  if(fill){ctx.fillStyle=fill;ctx.fill();}if(stroke){ctx.strokeStyle=stroke;ctx.stroke();}
}
function anatomy(m) {
  const {ctx,w,h}=canvas('anatomy'),view=$('view').value;
  const axes=p=>view==='posterior'?[p[0],p[2]]:view==='lateral'?[p[1],p[2]]:[p[0],p[1]];
  const all=[...model.bones.flatMap(b=>b.vertices_m),...m.nodes_m,...(m.frozen?.positions_m??[])];
  const p=project(all,axes,w,h).point;
  const depth=pt=>view==='posterior'?pt[1]:view==='lateral'?pt[0]:pt[2];
  const faces=model.bones.flatMap((b,i)=>b.triangles.map(t=>({ps:t.map(n=>b.vertices_m[n]),i})));
  faces.sort((a,b)=>a.ps.reduce((s,q)=>s+depth(q),0)-b.ps.reduce((s,q)=>s+depth(q),0));
  ctx.lineWidth=.35;
  for(const f of faces)face(ctx,f.ps.map(p),['#dbd4c4','#c5cabb','#bbc7c8'][f.i],'#78877d40');
  const patch=model.patches[$('patch').value],bone=model.bones.find(b=>b.element_id===patch.element_id);
  ctx.lineWidth=1;
  for(const n of patch.triangle_indices_zero_based)face(ctx,bone.triangles[n].map(i=>p(bone.vertices_m[i])),'#43ad8799','#086b4e');
  ctx.lineWidth=.7;
  for(const t of m.surface_triangles)face(ctx,t.map(n=>p(m.nodes_m[n])),null,'#15597850');
  if(m.frozen&&$('overlay').checked)for(const t of m.surface_triangles)face(ctx,t.map(n=>p(m.frozen.positions_m[n])),null,'#c4663255');
  ctx.fillStyle='#395460';ctx.font='13px system-ui';ctx.fillText('Shared atlas frame · metres',15,20);
}
function slice(m,s) {
  const {ctx,w,h}=canvas('section');
  const axes=p=>[dot(sub(p,m.basis.origin),m.basis.u),dot(sub(p,m.basis.origin),m.basis.v)];
  const p=project(s.triangles.flatMap(t=>t.vertices.flatMap(v=>[v.reference,v.current])),axes,w,h);
  ctx.lineWidth=.35;
  for(const t of s.triangles)face(ctx,t.vertices.map(v=>p.point(v.reference)),'#15597822','#15597845');
  if(m.frozen&&$('overlay').checked)for(const t of s.triangles)face(ctx,t.vertices.map(v=>p.point(v.current)),'#c4663233','#c4663260');
  const bar=.01*p.scale;ctx.strokeStyle='#182f3a';ctx.lineWidth=2;ctx.beginPath();ctx.moveTo(20,h-25);ctx.lineTo(20+bar,h-25);ctx.stroke();
  ctx.fillStyle='#182f3a';ctx.font='13px system-ui';ctx.fillText('10 mm',20,h-35);ctx.fillText('Fixed reference u / v axes',15,20);
}
function render() {
  const m=model.muscles.find(m=>m.element_id===$('body').value);
  const fraction=Number($('station').value)/100,resolution=Number($('resolution').value);
  last={body:m.element_id,bodyName:m.name,sourceCommit:model.sourceCommit,modelSha256:model.modelSha256,patchId:$('patch').value,section:section(m,fraction,resolution),limits:model.limits};
  const s=last.section,patch=model.patches[last.patchId];
  $('stationValue').value=`${Math.round(fraction*100)}% distal → proximal`;
  $('attachment').textContent=`${patch.anatomical_label} · ${patch.triangle_indices_zero_based.length} source faces · ${(patch.area_m2*1e6).toFixed(2)} mm². Distributed authored candidate; the inspection seed is not a mechanical cap anchor.`;
  const owner=model.attachments.find(a=>a.element_id===m.element_id);
  const describe=a=>a.kind==='distributed_bone_patch'?`authored distributed patch ${a.patch_id}`:'authored fixed scapular origin estimate; measured landmark and distributed proximal map remain unavailable';
  const owned=[owner.proximal.patch_id,owner.distal.patch_id].includes(last.patchId);
  $('ownership').textContent=`Declared proximal attachment: ${describe(owner.proximal)}. Declared distal attachment: ${describe(owner.distal)}.${owned?'':' The currently inspected patch is not assigned to this belly.'} Internal aponeurosis/fibre architecture and anatomical tendon mapping remain separate review gates.`;
  $('sectionNote').textContent=`${m.name} · material station ${(s.stationM*1000).toFixed(2)} mm from its authored basis origin · ${s.triangles.length} tessellation triangles. Same connected P2 body; no independent radius scaling.`;
  $('failure').textContent=m.frozen?`Recorded fully activated calibration: full nodal force gate FAILED. Maximum free component ${m.frozen.maximumFreeNodalComponentN.toFixed(6)} N > unchanged ${model.stationarityToleranceN} N gate. Both source caps held.`:'Reference geometry only. No frozen calibration field is provided for this body; no deformation or force result is inferred.';
  const entries=[['Tessellated material surface area','tessellatedAreaMm2','mm²'],['Projected u width','widthMm','mm'],['Projected v depth','depthMm','mm']];
  $('metrics').innerHTML='<table><thead><tr><th>Section quantity</th><th>Reference</th><th>Recorded field</th></tr></thead><tbody>'+entries.map(([name,k,unit])=>`<tr><th>${name}</th><td data-key="reference-${k}">${fmt(s.reference[k])} ${unit}</td><td data-key="current-${k}">${m.frozen?fmt(s.current[k])+' '+unit:'Unavailable'}</td></tr>`).join('')+'</tbody></table>';
  $('bounds').textContent=m.frozen?`Maximum section sample displacement: ${fmt(s.maximumSampleDisplacementMm)} mm. Retained whole-body volume ratio: ${m.frozen.globalVolumeRatio.toFixed(6)}; retained minimum corner J: ${m.frozen.minimumCornerJ.toFixed(6)}. These are original audit quantities, not recomputed by the viewer. Section area is an approximation at ${resolution} subdivisions.`:'Other four bellies are inspectable as reference geometry; original surfaces and attachment ownership remain available.';
  $('workspace').dataset.state=JSON.stringify({body:m.element_id,fraction,resolution,patch:last.patchId,view:$('view').value,overlay:$('overlay').checked,reference:s.reference,current:s.current,forceGate:m.frozen?false:null});
  anatomy(m);slice(m,s);
}
function setBodyPatch() {
  const a=model.attachments.find(a=>a.element_id===$('body').value);
  const recommended=a.distal.kind==='distributed_bone_patch'?a.distal.patch_id:a.proximal.patch_id;
  $('patch').value=recommended;
  render();
}
async function boot() {
  const manifest=await (await fetch('manifest.json')).json();
  const response=await fetch('model.json');if(!response.ok)throw Error('Missing local geometry');
  const bytes=await response.arrayBuffer();
  const hash=[...new Uint8Array(await crypto.subtle.digest('SHA-256',bytes))].map(x=>x.toString(16).padStart(2,'0')).join('');
  if(hash!==manifest.modelSha256)throw Error('Model identity mismatch');
  model=JSON.parse(new TextDecoder().decode(bytes));validateModel(model);model.modelSha256=hash;
  for(const m of model.muscles)$('body').add(new Option(m.name,m.element_id));
  for(const [id,p]of Object.entries(model.patches))$('patch').add(new Option(p.anatomical_label,id));
  $('loading').hidden=true;$('workspace').hidden=false;
  $('body').addEventListener('change',setBodyPatch);
  for(const id of ['patch','view','station','resolution','overlay'])$(id).addEventListener('input',render);
  $('reset').addEventListener('click',()=>{$('body').value='FJ1486';$('view').value='posterior';$('station').value='50';$('resolution').value='4';$('overlay').checked=true;setBodyPatch();});
  $('export').addEventListener('click',()=>{
    const blob=new Blob([JSON.stringify(last,null,2)+'\n'],{type:'application/json'}),url=URL.createObjectURL(blob),a=document.createElement('a');
    a.href=url;a.download=`kenoma-material-section-${last.body}-${Math.round(last.section.fraction*100)}.json`;a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);
  });
  window.addEventListener('resize',()=>render());setBodyPatch();
}
boot().catch(e=>{$('loading').textContent='Inspection refused: '+e.message;$('loading').dataset.error='true';$('workspace').hidden=true;});
