import {createSimpleGraph} from './client.js';
import {SceneModel} from './scene-state.js';
import {SceneRenderer} from './renderer.js';
const $=id=>document.getElementById(id);
const error=e=>{$('error').textContent=e.message||String(e);$('error').hidden=false;};
try{
 const client=await createSimpleGraph();const sample=client.request({version:1,operation:{type:'mannequin'}});if(!sample.ok)throw Error(sample.error.message);
 const model=new SceneModel(sample.graph);let renderer;
 function update(){const state=model.state,c=state.characters.find(c=>c.id===state.selectedId);$('character').replaceChildren(...state.characters.map(ch=>{const o=document.createElement('option');o.value=ch.id;o.textContent=ch.name;return o;}));$('character').value=state.selectedId||'';for(const id of ['color','remove','handle'])$(id).disabled=!c;
  if(c){$('color').value=c.color;}
  $('undo').disabled=!model.canUndo;$('redo').disabled=!model.canRedo;if(renderer){$('handle').value=renderer.selectedHandle;renderer.sync();const key=renderer.selectedHandle,limb=key.split(':')[0],status=c?.rig[limb]?.status;const text=c?$('handle').selectedOptions[0]?.textContent:'';$('handleBadge').textContent=text+(status&&status!=='reachable'?' · reach limit':'');$('handleBadge').hidden=!c;}
 }
 function run(fn){try{$('error').hidden=true;fn();update();}catch(e){error(e);}}
 renderer=new SceneRenderer($('viewport'),client,model,update,error);update();renderer.frame();
 $('add').onclick=()=>{run(()=>model.dispatch({type:'add'}));renderer.frame();};$('remove').onclick=()=>run(()=>model.dispatch({type:'remove',id:model.state.selectedId}));
 $('character').onchange=e=>run(()=>model.dispatch({type:'select',id:e.target.value}));$('handle').onchange=e=>{renderer.selectHandle(e.target.value);renderer.webgl.domElement.focus({preventScroll:true});};
 $('undo').onclick=()=>run(()=>model.undo());$('redo').onclick=()=>run(()=>model.redo());$('frame').onclick=()=>renderer.frame();
 for(const [id,type,field]of [['color','color','color']]){const input=$(id);input.addEventListener('pointerdown',()=>model.beginGesture());input.addEventListener('input',()=>run(()=>model.dispatch({type,id:model.state.selectedId,[field]:input.value})));input.addEventListener('change',()=>run(()=>model.commitGesture()));input.addEventListener('pointerup',()=>run(()=>model.commitGesture()));input.addEventListener('blur',()=>run(()=>model.commitGesture()));}
 document.addEventListener('keydown',e=>{if(e.key==='Escape'){renderer.cancelDrag();$('help').open=false;return;}if(/INPUT|SELECT|TEXTAREA/.test(e.target.tagName))return;if(e.target===renderer.webgl.domElement&&e.key.startsWith('Arrow')){e.preventDefault();run(()=>renderer.nudge(e.key,e));return;}if((e.ctrlKey||e.metaKey)&&e.key.toLowerCase()==='z'){e.preventDefault();run(()=>e.shiftKey?model.redo():model.undo());}else if(e.key==='Delete'||e.key==='Backspace'){e.preventDefault();if(model.state.selectedId)run(()=>model.dispatch({type:'remove',id:model.state.selectedId}));}else if(e.key.toLowerCase()==='f')renderer.frame();});
 window.simpleGraphEditor={client,sample,model,renderer,update,ready:false};
 await renderer.whenIdle();renderer.frame();window.simpleGraphEditor.ready=true;
}catch(e){error(e);}
