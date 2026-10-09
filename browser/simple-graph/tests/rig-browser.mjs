import assert from 'node:assert/strict';
import path from 'node:path';
import {createHash} from 'node:crypto';
import {writeFile} from 'node:fs/promises';
import {execFileSync} from 'node:child_process';
import {startServer,output} from './browser-support.mjs';
const {chromium}=await import(process.env.PLAYWRIGHT_MODULE||'playwright');
const server=await startServer();let browser;const checks=[];
const check=(value,name)=>{assert.ok(value,name);checks.push(name);};
try{
 browser=await chromium.launch({headless:true,executablePath:process.env.CHROMIUM||'/usr/bin/chromium'});
 const page=await browser.newPage({viewport:{width:1280,height:900}}),errors=[],wasmResponses=[];
 page.on('pageerror',e=>errors.push(e.message));page.on('response',r=>{if(r.url().endsWith('human_wasm_bg.wasm'))wasmResponses.push(r.body().then(bytes=>createHash('sha256').update(bytes).digest('hex')));});
 await page.goto(server.url+'/preview/index.html');await page.waitForFunction(()=>window.simpleGraphEditor?.ready);
 const cases=await page.evaluate(async()=>{
  const {contactCases}=await import('./tests/contact-cases.mjs'),{verifySurfaceTopology}=await import('./tests/surface-topology.mjs');
  const e=window.simpleGraphEditor,id=e.model.state.selectedId,item=e.renderer.characters.get(id),indices=JSON.stringify(item.mesh.indices),vertices=item.mesh.positions.length,results=[];
  window.rigAcceptanceCaptures=[];
  for(const c of contactCases){e.model.beginGesture();for(const edit of c.edits)e.model.dispatch({type:'ik',id,...edit});const started=performance.now();e.update();const enqueueMilliseconds=performance.now()-started;await e.renderer.whenIdle();const i=e.renderer.characters.get(id);results.push({name:c.name,enqueueMilliseconds,workerMilliseconds:i.workerTiming.workerMilliseconds,topology:verifySurfaceTopology(i.mesh),sameIndices:JSON.stringify(i.mesh.indices)===indices,sameVertices:i.mesh.positions.length===vertices,current:i.meshKey===i.graphKey});window.rigAcceptanceCaptures.push({name:c.name,state:e.model.state});e.model.cancelGesture();e.update();await e.renderer.whenIdle();}
  return results;
 });
 for(const c of cases){check(c.sameIndices&&c.sameVertices&&c.current,`${c.name}: rest topology and vertex identity retained`);check(c.topology.components===1&&c.topology.vertexLinks==='single cycles',`${c.name}: connected closed nondegenerate vertex-manifold`);}
 // Capture real deformed crossed/contact poses in the same actual editor.
 for(const name of ['hand-on-torso','crossed-arms','crossed-legs','deep-bends']){
  await page.evaluate(async name=>{const {contactCases}=await import('./tests/contact-cases.mjs');const e=window.simpleGraphEditor,id=e.model.state.selectedId;e.model.beginGesture();for(const edit of contactCases.find(c=>c.name===name).edits)e.model.dispatch({type:'ik',id,...edit});e.update();await e.renderer.whenIdle();e.renderer.frame();},name);
  await page.screenshot({path:path.join(output,`kenoma-stable-${name}.png`)});
  await page.evaluate(async()=>{const e=window.simpleGraphEditor;e.model.cancelGesture();e.update();await e.renderer.whenIdle();});
 }
 // Instrument real pointer handling; production code must never call main-realm WASM.
 await page.evaluate(()=>{const e=window.simpleGraphEditor,r=e.renderer;window.dragTimings=[];window.meshTimings=[];const receive=r.receiveMesh.bind(r);r.receiveMesh=result=>{const start=performance.now();receive(result);window.meshTimings.push(performance.now()-start);};r.client={request(){throw Error('WASM called on pointer/main render path');}};const original=r.applyHandle.bind(r);r.applyHandle=(handle)=>{const start=performance.now();original(handle);window.dragTimings.push({milliseconds:performance.now()-start,pending:r.pending,handle:handle.position.toArray()});};});
 await page.locator('#handle').selectOption('rightArm:target');
 const before=await page.evaluate(()=>window.simpleGraphEditor.model.state.characters[0].rig.rightArm.target),p=await page.evaluate(()=>window.simpleGraphEditor.renderer.projectHandle('rightArm:target'));
 await page.mouse.move(p.x,p.y);await page.mouse.down();await page.mouse.move(p.x-65,p.y+35,{steps:20});await page.mouse.up();
 const drag=await page.evaluate(async()=>{const e=window.simpleGraphEditor;await e.renderer.whenIdle();const i=e.renderer.characters.values().next().value;return {timings:window.dragTimings,meshTimings:window.meshTimings,target:e.model.state.characters[0].rig.rightArm.target,current:i.meshKey===i.graphKey};});
 check(drag.timings.length>=10&&JSON.stringify(drag.target)!==JSON.stringify(before),'actual 20-step mouse drag changes pose');
 check(drag.timings.some(t=>t.pending)&&drag.current,'handles update while geometry pending and final mesh catches up');
 const sorted=drag.timings.map(t=>t.milliseconds).sort((a,b)=>a-b),p95=sorted[Math.floor((sorted.length-1)*.95)];
 check(p95<50,`pointer-handler p95 below50ms (${p95.toFixed(2)}ms)`);
 const applySorted=drag.meshTimings.slice().sort((a,b)=>a-b),applyP95=applySorted[Math.floor((applySorted.length-1)*.95)];
 check(applySorted.length>0&&applyP95<50,`mesh-apply p95 below50ms (${applyP95?.toFixed(2)}ms)`);
 // Queue many revisions in one turn, then undo before the worker can reply.
 const stale=await page.evaluate(async()=>{const e=window.simpleGraphEditor,id=e.model.state.selectedId,before=JSON.stringify(e.model.state);e.model.beginGesture();for(let n=0;n<30;n++){e.model.dispatch({type:'head',id,yaw:n*.01});e.update();}const wasPending=e.renderer.pending;e.model.cancelGesture();e.update();await e.renderer.whenIdle();const i=e.renderer.characters.get(id);return {wasPending,same:JSON.stringify(e.model.state)===before,current:i.meshKey===i.graphKey};});
 check(stale.wasPending&&stale.same&&stale.current,'actual worker burst followed by cancellation cannot display stale pose');
 check(errors.length===0,`no browser exceptions: ${errors.join(';')}`);
 const receipt={checks,cases,servedWasmSha256:await Promise.all(wasmResponses),sourceDirty:execFileSync('git',['status','--porcelain'],{encoding:'utf8'}).trim()!=='',drag:{events:sorted.length,p95Milliseconds:p95,maxMilliseconds:sorted.at(-1),meshApplyP95Milliseconds:applyP95,meshApplyMaxMilliseconds:applySorted.at(-1)},browser:await browser.version(),sourceCommit:execFileSync('git',['rev-parse','HEAD'],{encoding:'utf8'}).trim(),capturedAt:new Date().toISOString()};
 await writeFile(path.join(output,'stable-rig-verification.json'),JSON.stringify(receipt,null,2)+'\n');console.log(JSON.stringify(receipt,null,2));
}finally{await browser?.close();await server.close();}
