import assert from 'node:assert/strict';
import path from 'node:path';
import {startServer,output,saveReceipt,verifyBinding} from './browser-support.mjs';
const {chromium}=await import(process.env.PLAYWRIGHT_MODULE||'playwright');
const server=await startServer();let browser;
const checks=[];const check=(condition,label)=>{assert.ok(condition,label);checks.push(label);};
try{
 browser=await chromium.launch({headless:true,executablePath:process.env.CHROMIUM||'/usr/bin/chromium'});
 const page=await browser.newPage({viewport:{width:1440,height:900},deviceScaleFactor:1});
 const errors=[],requests=[];page.on('pageerror',e=>errors.push(e.message));page.on('request',r=>requests.push(r.url()));
 await page.goto(`${server.url}/embed.html`);
 const frame=page.frames().find(f=>f.url().endsWith('/preview/index.html'));check(frame,'static subpath iframe embedding');
 await frame.waitForFunction(()=>window.simpleGraphEditor?.ready===true);
 await frame.evaluate(()=>new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r))));
 checks.push(...await verifyBinding(frame));
 const snapshot=()=>frame.evaluate(()=>window.simpleGraphEditor.model.state);
 const selected=state=>state.characters.find(c=>c.id===state.selectedId);
 async function setInput(id,value){await frame.locator('#'+id).evaluate((el,value)=>{el.value=String(value);el.dispatchEvent(new Event('input',{bubbles:true}));el.dispatchEvent(new Event('change',{bubbles:true}));},value);}
 async function drag(key,dx,dy){
  await frame.locator('#handle').selectOption(key);
  const p=await frame.evaluate(key=>window.simpleGraphEditor.renderer.projectHandle(key),key);
  assert.ok(p&&p.x>0&&p.x<1440&&p.y>50&&p.y<820,`visible handle ${key}: ${JSON.stringify(p)}`);
  await page.mouse.move(p.x,p.y);await page.mouse.down();await page.mouse.move(p.x+dx,p.y+dy,{steps:12});await page.mouse.up();
 }
 const initial=await snapshot();const firstId=initial.selectedId;
 const viewport=await frame.locator('#viewport').boundingBox();check(viewport.height>700,'desktop viewport-first layout');
 const rendering=await frame.evaluate(()=>{const r=window.simpleGraphEditor.renderer,i=r.characters.values().next().value;return {webgl:!!r.webgl.getContext().getParameter(r.webgl.getContext().VERSION),depth:i.body.material.depthTest,grid:r.grid.type==='GridHelper',head:i.head.children.length,calls:r.webgl.info.render.calls};});
 check(rendering.webgl&&rendering.depth&&rendering.calls>0,'real depth-tested WebGL rendering');check(rendering.grid,'grid floor');check(rendering.head>=6,'directional head has distinct facial/back geometry');
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
 await page.mouse.move(axisPoint.x+40,axisPoint.y,{steps:10});
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
 await setInput('yaw',35);await setInput('headYaw',55);await setInput('headPitch',-15);
 const head=await frame.evaluate(()=>{const e=window.simpleGraphEditor,c=e.model.state.characters[0],h=e.renderer.characters.get(c.id).head;return {state:c.head,rotation:h.rotation.toArray().slice(0,3)};});
 check(Math.abs(head.state.yaw-55*Math.PI/180)<1e-8&&Math.abs(head.rotation[1]-head.state.yaw)<1e-8,'head facing control changes rendered orientation');
 await setInput('color','#de8a62');const firstBeforeAdd=selected(await snapshot());
 await frame.locator('#add').click();let multi=await snapshot();const secondId=multi.selectedId;check(multi.characters.length===2&&secondId!==firstId,'add independent second character');
 await setInput('color','#8299e8');await setInput('headYaw',-40);
 check(JSON.stringify((await snapshot()).characters.find(c=>c.id===firstId))===JSON.stringify(firstBeforeAdd),'pose placement head and color isolated between characters');
 const materialColors=await frame.evaluate(()=>[...window.simpleGraphEditor.renderer.characters.values()].map(i=>i.material.color.getHexString()));check(materialColors.includes('de8a62')&&materialColors.includes('8299e8'),'independent rendered colors');
 await frame.locator('#character').selectOption(firstId);check((await snapshot()).selectedId===firstId,'character selector');
 // Pick the other character's head through the actual canvas raycaster.
 const headPoint=await frame.evaluate(id=>{const r=window.simpleGraphEditor.renderer,h=r.characters.get(id).head;h.updateWorldMatrix(true,false);const p=h.getWorldPosition(h.position.clone()).project(r.camera),b=r.webgl.domElement.getBoundingClientRect();return {x:b.left+(p.x+1)*b.width/2,y:b.top+(1-p.y)*b.height/2};},secondId);
 await page.mouse.click(headPoint.x,headPoint.y);check((await snapshot()).selectedId===secondId,'3D mesh picking selects character');
 await page.keyboard.press('Delete');check((await snapshot()).characters.length===1,'keyboard character removal');
 await page.keyboard.press('Control+z');check((await snapshot()).characters.length===2,'undo restores removed character and its state');
 await frame.locator('#remove').click();check((await snapshot()).characters.length===1,'remove button');await frame.locator('#undo').click();
 const cameraBefore=await frame.evaluate(()=>window.simpleGraphEditor.renderer.camera.position.toArray());
 const box=await frame.locator('canvas').boundingBox();await page.mouse.move(box.x+40,box.y+50);await page.mouse.down();await page.mouse.move(box.x+140,box.y+80,{steps:10});await page.mouse.up();await page.waitForTimeout(200);
 const cameraAfter=await frame.evaluate(()=>window.simpleGraphEditor.renderer.camera.position.toArray());check(JSON.stringify(cameraBefore)!==JSON.stringify(cameraAfter),'camera orbit interaction');
 await page.mouse.wheel(0,-180);await page.waitForTimeout(200);check(JSON.stringify(await frame.evaluate(()=>window.simpleGraphEditor.renderer.camera.position.toArray()))!==JSON.stringify(cameraAfter),'camera zoom interaction');
 const panBefore=await frame.evaluate(()=>window.simpleGraphEditor.renderer.controls.target.toArray());
 await page.mouse.move(box.x+40,box.y+60);await page.mouse.down({button:'right'});await page.mouse.move(box.x+80,box.y+80,{steps:8});await page.mouse.up({button:'right'});await page.waitForTimeout(150);
 check(JSON.stringify(await frame.evaluate(()=>window.simpleGraphEditor.renderer.controls.target.toArray()))!==JSON.stringify(panBefore),'camera pan interaction');
 await frame.locator('#frame').click();
 // Exercise exact singular/unreachable inputs in the browser's headless model;
 // pointer-driven behavior above separately proves real handle interactions.
 const edgeCases=await frame.evaluate(()=>{const e=window.simpleGraphEditor,id=e.model.state.selectedId;const before=e.model.state;const root=before.characters.find(c=>c.id===id).graph.nodes[4].position;const statuses=[];e.model.beginGesture();for(const target of [root,[100,100,100]]){e.model.dispatch({type:'ik',id,limb:'rightArm',target,pole:root});e.update();const c=e.model.state.characters.find(c=>c.id===id);if(!c.graph.nodes.every(n=>n.position.every(Number.isFinite)))throw Error('nonfinite IK');statuses.push(c.rig.rightArm.status);}e.model.cancelGesture();e.update();return statuses;});
 check(edgeCases.includes('clamped-near')&&edgeCases.includes('clamped-far'),'browser singular and unreachable targets remain finite and bounded');
 await frame.locator('#handle').selectOption('rightArm:target');
 await page.screenshot({path:path.join(output,'kenoma-scene-editor-desktop.png')});
 const scene=await snapshot();
 // Phone layout and touch handle interaction.
 const phone=await browser.newPage({viewport:{width:390,height:844},deviceScaleFactor:1,isMobile:true,hasTouch:true});phone.on('pageerror',e=>errors.push(e.message));
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
 for(let i=1;i<=8;i++)await session.send('Input.dispatchTouchEvent',{type:'touchMove',touchPoints:[{id:1,x:touchPoint.x-i*2,y:touchPoint.y+i*2}]});
 await session.send('Input.dispatchTouchEvent',{type:'touchEnd',touchPoints:[]});
 check(JSON.stringify(await phone.evaluate(()=>window.simpleGraphEditor.model.state.characters[0].rig.rightArm.target))!==JSON.stringify(phoneBefore),'phone touch drags IK handle');
 await phone.locator('#add').click();check(await phone.locator('#character option').count()===2,'phone add character');
 await phone.locator('#character').selectOption('character-1');await phone.locator('#remove').click();check(await phone.locator('#character option').count()===1,'phone select/remove character');await phone.locator('#undo').click();
 await phone.screenshot({path:path.join(output,'kenoma-scene-editor-phone.png')});
 check(errors.length===0,`no browser exceptions: ${errors.join('; ')}`);
 check(requests.some(url=>url.endsWith('human_wasm_bg.wasm'))&&requests.every(url=>url.startsWith(server.url)),'actual WASM and local-only runtime requests');
 const receipt=await saveReceipt(browser,{checks,scene,phoneLayout,desktop:{width:1440,height:900},phone:{width:390,height:844},kinematics:'Analytic two-bone IK, no forces or simulation',screenshots:['kenoma-scene-editor-desktop.png','kenoma-scene-editor-phone.png']});
 console.log(JSON.stringify({checks:checks.length,browser:receipt.browser,output,phoneLayout}));
}finally{if(browser)await browser.close();await server.close();}
