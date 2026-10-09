import assert from 'node:assert/strict';
import path from 'node:path';
import {readFile} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {startServer,output,saveReceipt,verifyBinding} from './browser-support.mjs';
const {chromium}=await import(process.env.PLAYWRIGHT_MODULE||'playwright');
const server=await startServer();let browser;
const wasmAtStart=createHash('sha256').update(await readFile(new URL('../pkg/human_wasm_bg.wasm',import.meta.url))).digest('hex');
const checks=[];const check=(condition,label)=>{assert.ok(condition,label);checks.push(label);console.log('PASS',label);};
try{
 browser=await chromium.launch({headless:true,executablePath:process.env.CHROMIUM||'/usr/bin/chromium'});
 const page=await browser.newPage({viewport:{width:1440,height:900},deviceScaleFactor:1});
 const errors=[],requests=[],wasmResponses=[];page.on('response',r=>{if(r.url().endsWith('human_wasm_bg.wasm'))wasmResponses.push(r.body().then(bytes=>createHash('sha256').update(bytes).digest('hex')));});page.on('pageerror',e=>errors.push(e.message));page.on('request',r=>requests.push(r.url()));
 await page.goto(`${server.url}/embed.html`);
 const frame=page.frames().find(f=>f.url().endsWith('/preview/index.html'));check(frame,'static subpath iframe embedding');
 await frame.waitForFunction(()=>window.simpleGraphEditor?.ready===true);
 await frame.evaluate(()=>new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r))));
 checks.push(...await verifyBinding(frame));
 const idle=context=>context.evaluate(()=>window.simpleGraphEditor.renderer.whenIdle());
 const snapshot=()=>frame.evaluate(()=>window.simpleGraphEditor.model.state);
 const selected=state=>state.characters.find(c=>c.id===state.selectedId);
 async function setInput(id,value){await frame.locator('#'+id).evaluate((el,value)=>{el.value=String(value);el.dispatchEvent(new Event('input',{bubbles:true}));el.dispatchEvent(new Event('change',{bubbles:true}));},value);}
 async function drag(key,dx,dy){
  await frame.locator('#handle').selectOption(key);
  const p=await frame.evaluate(key=>window.simpleGraphEditor.renderer.projectHandle(key),key);
  assert.ok(p&&p.x>0&&p.x<1440&&p.y>50&&p.y<820,`visible handle ${key}: ${JSON.stringify(p)}`);
  await page.mouse.move(p.x,p.y);await page.mouse.down();await page.mouse.move(p.x+dx,p.y+dy,{steps:3});await page.mouse.up();
 }
 async function ringPoint(context,key,axis){
  await context.locator('#handle').selectOption(key);
  await context.evaluate(()=>new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r))));
  return context.evaluate(({key,axis})=>{const r=window.simpleGraphEditor.renderer,rect=r.webgl.domElement.getBoundingClientRect(),center=r.projectHandle(key);for(let y=center.y-105;y<center.y+105;y+=4)for(let x=center.x-105;x<center.x+105;x+=4){if(x<rect.left+2||x>rect.right-2||y<rect.top+2||y>rect.bottom-2)continue;r.gizmo.pointerHover({x:(x-rect.left)/rect.width*2-1,y:1-(y-rect.top)/rect.height*2,button:0});if(r.gizmo.axis===axis)return {x,y};}return null;},{key,axis});
 }
 async function rotate(key,axis,dx,dy){const point=await ringPoint(frame,key,axis);check(point,`${key} ${axis} rotation ring is pickable`);await page.mouse.move(point.x,point.y);await page.mouse.down();check(await frame.evaluate(()=>window.simpleGraphEditor.renderer.gizmo.dragging&&!window.simpleGraphEditor.renderer.drag),'rotation gizmo owns pointer');await page.mouse.move(point.x+dx,point.y+dy,{steps:3});await page.mouse.up();}
 const initial=await snapshot();const firstId=initial.selectedId;
 const viewport=await frame.locator('#viewport').boundingBox();check(viewport.height>700,'desktop viewport-first layout');
 await idle(frame);
 const rendering=await frame.evaluate(()=>{const r=window.simpleGraphEditor.renderer,i=r.characters.values().next().value;return {webgl:!!r.webgl.getContext().getParameter(r.webgl.getContext().VERSION),depth:i.body.material.depthTest,grid:r.grid.type==='GridHelper',head:i.head.children.length,calls:r.webgl.info.render.calls};});
 check(rendering.webgl&&rendering.depth&&rendering.calls>0,'real depth-tested WebGL rendering');check(rendering.grid,'grid floor');check(rendering.head===0,'head is integrated surface without independent primitive geometry');check(await frame.locator('input[type=range]').count()===0,'no slider controls');
 const surface=await frame.evaluate(()=>{const e=window.simpleGraphEditor,c=e.model.state.characters[0],i=e.renderer.characters.get(c.id);const start=performance.now(),bound=e.client.request({version:1,operation:{type:'rig_bind',rig_version:1}});if(!bound.ok)throw Error(bound.error.message);const bindMilliseconds=performance.now()-start;try{const deformStart=performance.now(),r=e.client.request({version:1,operation:{type:'rig_deform',rig_version:1,rig_id:bound.rig_id,graph:c.graph,head:c.head}});if(!r.ok)throw Error(r.error.message);return {bindMilliseconds,milliseconds:performance.now()-deformStart,vertices:r.mesh.positions.length,triangles:r.mesh.indices.length/3,allIndices:i.body.geometry.index.count===r.mesh.indices.length,deterministic:JSON.stringify(i.mesh)===JSON.stringify(r.mesh),currentMeshKey:i.meshKey===i.graphKey};}finally{const released=e.client.request({version:1,operation:{type:'rig_release',rig_version:1,rig_id:bound.rig_id}});if(!released.ok)throw Error(released.error.message);}});
 check(surface.allIndices&&surface.deterministic&&surface.currentMeshKey,'actual deterministic bound rig deformation rendered with all indices');
 const topology=await frame.evaluate(async()=>{const {verifySurfaceTopology}=await import('/preview/tests/surface-topology.mjs');return {neutral:verifySurfaceTopology(window.simpleGraphEditor.renderer.characters.values().next().value.mesh)};});check(topology.neutral.components===1,'actual neutral WASM topology is one closed oriented nondegenerate component with unit normals');
 // Locate the real X-axis picker by hovering, then test constrained movement
 // and Escape snapshot restoration rather than invoking a model action.
 await frame.locator('#handle').selectOption('rightArm:target');
 const center=await frame.evaluate(()=>window.simpleGraphEditor.renderer.projectHandle('rightArm:target'));
 let axisPoint;
 for(let x=20;x<100&&!axisPoint;x+=10)for(let y=-70;y<70&&!axisPoint;y+=10){
   await page.mouse.move(center.x+x,center.y+y);
   if(await frame.evaluate(()=>window.simpleGraphEditor.renderer.gizmo.axis)==='X')axisPoint={x:center.x+x,y:center.y+y};
 }
 check(axisPoint,'axis gizmo is pickable');
 const axisBefore=await snapshot(),undoBefore=await frame.evaluate(()=>window.simpleGraphEditor.model.canUndo);
 await page.mouse.down();
 check(await frame.evaluate(()=>!window.simpleGraphEditor.renderer.drag&&window.simpleGraphEditor.renderer.gizmo.dragging),'real axis drag starts');
 await page.mouse.move(axisPoint.x+40,axisPoint.y,{steps:3});
 const constrained=selected(await snapshot()).rig.rightArm.target,prior=selected(axisBefore).rig.rightArm.target;
 check(Math.abs(constrained[0]-prior[0])>1e-4&&Math.abs(constrained[1]-prior[1])<1e-7&&Math.abs(constrained[2]-prior[2])<1e-7,'axis gizmo constrains movement');
 await page.keyboard.press('Escape');await page.mouse.up();
 check(JSON.stringify(await snapshot())===JSON.stringify(axisBefore)&&(await frame.evaluate(()=>window.simpleGraphEditor.model.canUndo))===undoBefore,'Escape cancels axis drag without pose or history changes');
 await drag('rightArm:target',-45,30);
 let posed=await snapshot();check(JSON.stringify(selected(posed).graph)!==JSON.stringify(selected(initial).graph),'real hand IK handle drag changes pose');
 const afterHand=structuredClone(posed);
 await page.keyboard.press('Control+z');check(JSON.stringify((await snapshot()).characters)===JSON.stringify(initial.characters),'keyboard undo groups full handle drag');
 await page.keyboard.press('Control+Shift+z');check(JSON.stringify((await snapshot()).characters)===JSON.stringify(afterHand.characters),'keyboard redo restores pose');
 for(const [key,dx,dy]of [['rightArm:pole',35,25],['rightLeg:target',28,-30],['rightLeg:pole',25,-20],['leftArm:target',30,20],['leftLeg:target',-20,-18]]){
   const before=selected(await snapshot());await drag(key,dx,dy);const after=selected(await snapshot());const [limb,kind]=key.split(':');check(JSON.stringify(before.rig[limb][kind])!==JSON.stringify(after.rig[limb][kind]),`real ${key} drag`);
 }
 const lengths=await frame.evaluate(()=>{const {model,sample}=window.simpleGraphEditor;const graph=model.state.characters[0].graph;return sample.graph.edges.map(e=>{const length=g=>Math.hypot(...g.nodes[e.a].position.map((v,i)=>v-g.nodes[e.b].position[i]));return Math.abs(length(graph)-length(sample.graph));});});
 check(Math.max(...lengths)<1e-6,'all graph edge lengths preserved by IK');
 const beforeRoot=selected(await snapshot()).position;await drag('root',-45,10);check(JSON.stringify(selected(await snapshot()).position)!==JSON.stringify(beforeRoot),'root handle moves character in 3D');
 const yawBefore=selected(await snapshot()).yaw;await rotate('root:rotate','Y',32,15);check(Math.abs(selected(await snapshot()).yaw-yawBefore)>1e-4,'real root yaw ring drag');
 const headBefore=selected(await snapshot()).head;await rotate('head','Y',25,14);check(Math.abs(selected(await snapshot()).head.yaw-headBefore.yaw)>1e-4,'real head yaw ring drag under rotated root');
 const pitchBefore=selected(await snapshot()).head.pitch;await rotate('head','X',-18,25);check(Math.abs(selected(await snapshot()).head.pitch-pitchBefore)>1e-4,'real head pitch ring drag');
 const head=await frame.evaluate(()=>{const e=window.simpleGraphEditor,c=e.model.state.characters[0],i=e.renderer.characters.get(c.id);return {state:c.head,rotation:i.head.rotation.toArray().slice(0,3),key:i.graphKey};});
 check(Math.abs(head.rotation[1]-head.state.yaw)<1e-8&&head.key.includes('head'),'head orientation is included in surface cache and anchor');
 const beforeNudge=selected(await snapshot()).head;await page.keyboard.press('ArrowRight');await page.keyboard.press('ArrowUp');const nudged=selected(await snapshot()).head;check(Math.abs(nudged.yaw-beforeNudge.yaw-5*Math.PI/180)<1e-8&&Math.abs(nudged.pitch-beforeNudge.pitch-5*Math.PI/180)<1e-8,'keyboard head yaw and pitch nudges');
 await frame.locator('#handle').selectOption('root:rotate');const beforeTurn=selected(await snapshot()).yaw;await page.keyboard.press('Shift+ArrowLeft');check(Math.abs(selected(await snapshot()).yaw-beforeTurn+Math.PI/180)<1e-8,'keyboard fine root yaw');
 await frame.locator('#handle').selectOption('root');const beforeMove=selected(await snapshot()).position;await page.keyboard.press('ArrowRight');await page.keyboard.press('ArrowUp');await page.keyboard.press('Alt+ArrowUp');const moved=selected(await snapshot()).position;check(moved.every((x,i)=>Math.abs(x-beforeMove[i]-.025)<1e-8),'keyboard root translation in all three dimensions');
 await setInput('color','#de8a62');const firstBeforeAdd=selected(await snapshot());
 await frame.locator('#add').click();let multi=await snapshot();const secondId=multi.selectedId;check(multi.characters.length===2&&secondId!==firstId,'add independent second character');
 await setInput('color','#8299e8');await frame.locator('#handle').selectOption('head');await page.keyboard.press('ArrowLeft');
 check(JSON.stringify((await snapshot()).characters.find(c=>c.id===firstId))===JSON.stringify(firstBeforeAdd),'pose placement head and color isolated between characters');
 const materialColors=await frame.evaluate(()=>[...window.simpleGraphEditor.renderer.characters.values()].map(i=>i.material.color.getHexString()));check(materialColors.includes('de8a62')&&materialColors.includes('8299e8'),'independent rendered colors');
 await frame.locator('#handle').selectOption('root');await frame.locator('#character').selectOption(firstId);check((await snapshot()).selectedId===firstId,'character selector');
 await idle(frame);
 // Pick the other character's head through the actual canvas raycaster.
 const headPoint=await frame.evaluate(id=>{const r=window.simpleGraphEditor.renderer,h=r.characters.get(id).head;h.updateWorldMatrix(true,false);const p=h.getWorldPosition(h.position.clone()).project(r.camera),b=r.webgl.domElement.getBoundingClientRect();return {x:b.left+(p.x+1)*b.width/2,y:b.top+(1-p.y)*b.height/2};},secondId);
 await page.mouse.click(headPoint.x,headPoint.y);check((await snapshot()).selectedId===secondId,'3D mesh picking selects character');
 await page.keyboard.press('Delete');check((await snapshot()).characters.length===1,'keyboard character removal');
 await page.keyboard.press('Control+z');check((await snapshot()).characters.length===2,'undo restores removed character and its state');
 await frame.locator('#remove').click();check((await snapshot()).characters.length===1,'remove button');await frame.locator('#undo').click();
 const cameraBefore=await frame.evaluate(()=>window.simpleGraphEditor.renderer.camera.position.toArray());
 const box=await frame.locator('canvas').boundingBox();await page.mouse.move(box.x+40,box.y+50);await page.mouse.down();await page.mouse.move(box.x+140,box.y+80,{steps:3});await page.mouse.up();await page.waitForTimeout(200);
 const cameraAfter=await frame.evaluate(()=>window.simpleGraphEditor.renderer.camera.position.toArray());check(JSON.stringify(cameraBefore)!==JSON.stringify(cameraAfter),'camera orbit interaction');
 await page.mouse.wheel(0,-180);await page.waitForTimeout(200);check(JSON.stringify(await frame.evaluate(()=>window.simpleGraphEditor.renderer.camera.position.toArray()))!==JSON.stringify(cameraAfter),'camera zoom interaction');
 const panBefore=await frame.evaluate(()=>window.simpleGraphEditor.renderer.controls.target.toArray());
 await page.mouse.move(box.x+40,box.y+60);await page.mouse.down({button:'right'});await page.mouse.move(box.x+80,box.y+80,{steps:3});await page.mouse.up({button:'right'});await page.waitForTimeout(150);
 check(JSON.stringify(await frame.evaluate(()=>window.simpleGraphEditor.renderer.controls.target.toArray()))!==JSON.stringify(panBefore),'camera pan interaction');
 await idle(frame);await frame.locator('#frame').click();
 // Exercise exact singular/unreachable inputs in the browser's headless model;
 // pointer-driven behavior above separately proves real handle interactions.
 const edgeCases=await frame.evaluate(()=>{const e=window.simpleGraphEditor,id=e.model.state.selectedId;const before=e.model.state;const root=before.characters.find(c=>c.id===id).graph.nodes[4].position;const statuses=[];e.model.beginGesture();for(const target of [root,[100,100,100]]){e.model.dispatch({type:'ik',id,limb:'rightArm',target,pole:root});e.update();const c=e.model.state.characters.find(c=>c.id===id);if(!c.graph.nodes.every(n=>n.position.every(Number.isFinite)))throw Error('nonfinite IK');statuses.push(c.rig.rightArm.status);}e.model.cancelGesture();e.update();return statuses;});
 check(edgeCases.includes('clamped-near')&&edgeCases.includes('clamped-far'),'browser singular and unreachable targets remain finite and bounded');
 await frame.locator('#handle').selectOption('rightArm:target');
 await idle(frame);await page.screenshot({path:path.join(output,'kenoma-stable-editor-desktop.png')});
 topology.posed=await frame.evaluate(async()=>{const {verifySurfaceTopology}=await import('/preview/tests/surface-topology.mjs');return [...window.simpleGraphEditor.renderer.characters.values()].map(i=>verifySurfaceTopology(i.mesh));});check(topology.posed.every(t=>t.components===1),'actual posed WASM topology remains closed connected oriented with valid normals');
 const scene=await snapshot();
 const originalCamera=await frame.evaluate(()=>{const r=window.simpleGraphEditor.renderer,c=r.characters.get(window.simpleGraphEditor.model.state.selectedId);const saved={position:r.camera.position.toArray(),target:r.controls.target.toArray()};c.head.updateWorldMatrix(true,false);const head=c.head.getWorldPosition(c.head.position.clone());r.gizmo.detach();r.handleGroup.visible=false;r.controls.target.copy(head);r.camera.position.copy(head).add(head.clone().set(.28,.08,.65));r.controls.update();return saved;});
 await page.waitForTimeout(150);await page.screenshot({path:path.join(output,'kenoma-stable-head-closeup.png'),clip:{x:420,y:146,width:600,height:600}});
 await frame.evaluate(id=>{const e=window.simpleGraphEditor,r=e.renderer,c=e.model.state.characters.find(c=>c.id===id),item=r.characters.get(id);item.group.updateWorldMatrix(true,false);const joint=item.group.localToWorld(item.group.position.clone().fromArray(c.graph.nodes[5].position));r.controls.target.copy(joint);r.camera.position.copy(joint).add(joint.clone().set(.20,.06,.55));r.controls.update();},firstId);await page.waitForTimeout(150);await page.screenshot({path:path.join(output,'kenoma-stable-joint-closeup.png'),clip:{x:420,y:146,width:600,height:600}});
 await frame.evaluate(saved=>{const e=window.simpleGraphEditor,r=e.renderer;r.camera.position.fromArray(saved.position);r.controls.target.fromArray(saved.target);r.controls.update();e.update();},originalCamera);

 // Phone layout and touch handle interaction.
 const phone=await browser.newPage({viewport:{width:390,height:844},deviceScaleFactor:1,isMobile:true,hasTouch:true});phone.on('pageerror',e=>errors.push(e.message));phone.on('response',r=>{if(r.url().endsWith('human_wasm_bg.wasm'))wasmResponses.push(r.body().then(bytes=>createHash('sha256').update(bytes).digest('hex')));});
 await phone.goto(`${server.url}/preview/index.html`);await phone.waitForFunction(()=>window.simpleGraphEditor?.ready);
 const phoneLayout=await phone.evaluate(()=>({scroll:document.documentElement.scrollWidth,width:innerWidth,viewport:document.querySelector('#viewport').getBoundingClientRect().height,app:document.querySelector('#app').getBoundingClientRect().height}));
 check(phoneLayout.scroll<=390&&phoneLayout.viewport>480&&phoneLayout.app<=844,'phone layout keeps viewport without page overflow');
 const session=await phone.context().newCDPSession(phone);
 await phone.locator('#handle').selectOption('root');
 const phoneAxisBefore=await phone.evaluate(()=>window.simpleGraphEditor.model.state);
 const rootPoint=await phone.evaluate(()=>window.simpleGraphEditor.renderer.projectHandle('root'));
 const axisTouch={id:11,x:rootPoint.x+20,y:rootPoint.y};
 await session.send('Input.dispatchTouchEvent',{type:'touchStart',touchPoints:[axisTouch]});
 check(await phone.evaluate(()=>window.simpleGraphEditor.renderer.gizmo.dragging),'phone axis drag starts');
 await session.send('Input.dispatchTouchEvent',{type:'touchStart',touchPoints:[axisTouch,{id:12,x:rootPoint.x,y:rootPoint.y}]});
 await session.send('Input.dispatchTouchEvent',{type:'touchMove',touchPoints:[axisTouch,{id:12,x:rootPoint.x+10,y:rootPoint.y+10}]});
 check(JSON.stringify(await phone.evaluate(()=>window.simpleGraphEditor.model.state))===JSON.stringify(phoneAxisBefore),'second touch cannot change axis-owned pose');
 await session.send('Input.dispatchTouchEvent',{type:'touchEnd',touchPoints:[{id:12,x:rootPoint.x+10,y:rootPoint.y+10}]});
 check(await phone.evaluate(()=>window.simpleGraphEditor.renderer.gizmo.dragging),'second touch release preserves axis drag');
 await session.send('Input.dispatchTouchEvent',{type:'touchMove',touchPoints:[{...axisTouch,x:axisTouch.x+25}]});
 await session.send('Input.dispatchTouchEvent',{type:'touchEnd',touchPoints:[]});
 check(JSON.stringify(await phone.evaluate(()=>window.simpleGraphEditor.model.state.characters[0].position))!==JSON.stringify(phoneAxisBefore.characters[0].position),'owner touch moves constrained root');
 await phone.locator('#undo').click();
 check(JSON.stringify(await phone.evaluate(()=>window.simpleGraphEditor.model.state))===JSON.stringify(phoneAxisBefore),'phone axis gesture undo is exact');
 await phone.locator('#handle').selectOption('rightArm:target');
 const touchPoint=await phone.evaluate(()=>window.simpleGraphEditor.renderer.projectHandle('rightArm:target'));
 const phoneBefore=await phone.evaluate(()=>window.simpleGraphEditor.model.state.characters[0].rig.rightArm.target);
 await session.send('Input.dispatchTouchEvent',{type:'touchStart',touchPoints:[{id:1,x:touchPoint.x,y:touchPoint.y}]});
 await session.send('Input.dispatchTouchEvent',{type:'touchStart',touchPoints:[{id:1,x:touchPoint.x,y:touchPoint.y},{id:2,x:touchPoint.x+2,y:touchPoint.y+2}]});
 await session.send('Input.dispatchTouchEvent',{type:'touchMove',touchPoints:[{id:1,x:touchPoint.x,y:touchPoint.y},{id:2,x:touchPoint.x+25,y:touchPoint.y+25}]});
 check(JSON.stringify(await phone.evaluate(()=>window.simpleGraphEditor.model.state.characters[0].rig.rightArm.target))===JSON.stringify(phoneBefore),'second touch cannot move owner handle');
 await session.send('Input.dispatchTouchEvent',{type:'touchEnd',touchPoints:[{id:2,x:touchPoint.x+25,y:touchPoint.y+25}]});
 check(await phone.evaluate(()=>window.simpleGraphEditor.renderer.drag!==null),'second touch release preserves owner drag');
 for(let i=1;i<=3;i++)await session.send('Input.dispatchTouchEvent',{type:'touchMove',touchPoints:[{id:1,x:touchPoint.x-i*5,y:touchPoint.y+i*5}]});
 await session.send('Input.dispatchTouchEvent',{type:'touchEnd',touchPoints:[]});
 check(JSON.stringify(await phone.evaluate(()=>window.simpleGraphEditor.model.state.characters[0].rig.rightArm.target))!==JSON.stringify(phoneBefore),'phone touch drags IK handle');
 for(const [key,axis]of [['root:rotate','Y'],['head','Y'],['head','X']]){const point=await ringPoint(phone,key,axis);check(point,`phone ${key} ${axis} rotation ring visible`);const before=await phone.evaluate(()=>window.simpleGraphEditor.model.state.characters[0]);await session.send('Input.dispatchTouchEvent',{type:'touchStart',touchPoints:[{id:21,x:point.x,y:point.y}]});check(await phone.evaluate(()=>window.simpleGraphEditor.renderer.gizmo.dragging),'phone rotation touch begins gizmo drag');await session.send('Input.dispatchTouchEvent',{type:'touchMove',touchPoints:[{id:21,x:point.x+22,y:point.y+14}]});await session.send('Input.dispatchTouchEvent',{type:'touchEnd',touchPoints:[]});const after=await phone.evaluate(()=>window.simpleGraphEditor.model.state.characters[0]);check(key==='head'?JSON.stringify(before.head)!==JSON.stringify(after.head):before.yaw!==after.yaw,`phone touch ${key} ${axis} changes orientation`);}
 await phone.locator('#add').click();check(await phone.locator('#character option').count()===2,'phone add character');
 await phone.locator('#character').selectOption('character-1');await phone.locator('#remove').click();check(await phone.locator('#character option').count()===1,'phone select/remove character');await phone.locator('#undo').click();
 await idle(phone);await phone.screenshot({path:path.join(output,'kenoma-stable-editor-phone.png')});
 check(errors.length===0,`no browser exceptions: ${errors.join('; ')}`);
 check(requests.some(url=>url.endsWith('human_wasm_bg.wasm'))&&requests.every(url=>url.startsWith(server.url)),'actual WASM and local-only runtime requests');
 const servedHashes=await Promise.all(wasmResponses);check(servedHashes.length>0&&servedHashes.every(h=>h===wasmAtStart)&&createHash('sha256').update(await readFile(new URL('../pkg/human_wasm_bg.wasm',import.meta.url))).digest('hex')===wasmAtStart,'served WASM remains identical through browser checks');
 const receipt=await saveReceipt(browser,{checks,scene,phoneLayout,surface,topology,servedWasmSha256:servedHashes,desktop:{width:1440,height:900},phone:{width:390,height:844},kinematics:'Analytic two-bone IK, no forces or simulation',screenshots:['kenoma-stable-editor-desktop.png','kenoma-stable-editor-phone.png','kenoma-stable-head-closeup.png','kenoma-stable-joint-closeup.png']});
 console.log(JSON.stringify({checks:checks.length,browser:receipt.browser,output,phoneLayout}));
}finally{if(browser)await browser.close();await server.close();}
