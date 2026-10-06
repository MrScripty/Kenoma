/** Visible lifecycle/errors for the real WebGL scene; no replacement renderer. */
export class SceneStatus {
 constructor(root,stop){
  this.root=root;this.stop=stop;this.host=root.querySelector('.scene-host');
  this.notice=root.querySelector('.scene-notice');this.button=root.querySelector('[data-action=start]');
  this.temporal=['force','energy','elbow','series'].includes(root.dataset.demo)||root.dataset.advanced==='spatial';
  this.idle();
 }
 detach(){this.canvas?.removeEventListener('webglcontextlost',this.lost);this.canvas=null;}
 idle(){
  this.detach();this.root.dataset.sceneState='idle';this.root.dataset.runDisplay='static';this.host.hidden=true;
  this.button.textContent='Start interactive 3D';
  this.notice.textContent=this.temporal?'Static reference diagram. Step, Play or Pulse starts live 3D; if unavailable, the display is explicitly numerical-only.':'Static reference diagram. Start interactive 3D to view current results; numerical controls also work without 3D.';
 }
 run(start){
  if(this.root.dataset.sceneState==='idle')start();
  if(this.root.dataset.sceneState==='ready'){this.root.dataset.runDisplay='live';return;}
  this.root.dataset.runDisplay='numerical-only';
  this.notice.textContent='Numerical-only run: readouts and traces advance. The static reference diagram does not move. Retry interactive 3D above.';
 }
 begin(){
  this.capabilities=null;
  this.root.dataset.sceneState='starting';this.host.hidden=false;
  this.host.querySelector('.scene-error')?.remove();this.notice.textContent='Starting 3D…';
 }
 watch(renderer){
  this.detach();this.canvas=renderer.domElement;
  this.capabilities=this.contextInfo(renderer);
  this.lost=event=>{event.preventDefault();this.fail(new Error('WebGL context was lost after initialization'),'context-lost');};
  this.canvas.addEventListener('webglcontextlost',this.lost);
  renderer.debug.onShaderError=(gl,program)=>{throw new Error('WebGL shader program failed: '+gl.getProgramInfoLog(program));};
 }
 ready(renderer){
  if(renderer.getContext().isContextLost())throw new Error('WebGL context is lost');
  if(renderer.info.render.calls===0)throw new Error('The scene made no draw calls');
  this.capabilities=this.contextInfo(renderer);
  this.root.dataset.sceneState='ready';this.root.dataset.runDisplay='live';this.button.textContent='Restart interactive 3D';
  this.notice.textContent='3D scene active. Change the controls below to explore it.';
 }
 draw(render){
  try{render();return true;}
  catch(error){this.fail(error,'draw');return false;}
 }
 contextInfo(renderer){
  const gl=renderer.getContext();
  return {version:gl.getParameter(gl.VERSION),vendor:gl.getParameter(gl.VENDOR),
   renderer:gl.getParameter(gl.RENDERER),lost:gl.isContextLost(),
   drawingBuffer:[gl.drawingBufferWidth,gl.drawingBufferHeight]};
 }
 fail(error,stage){
  const diagnostic={lab:this.root.id,stage,reason:String(error?.message||error),
   userAgent:navigator.userAgent,devicePixelRatio:window.devicePixelRatio,
   lastObservedContext:this.capabilities};
  this.stop();this.root.dataset.sceneState='error';this.root.dataset.runDisplay='numerical-only';this.root.classList.remove('active-scene');
  this.host.hidden=false;this.button.textContent='Retry interactive 3D';
  this.notice.textContent='Numerical-only display: 3D unavailable here. Readouts and traces still work; the static reference diagram does not move. See diagnostics below.';
  const panel=document.createElement('div');panel.className='scene-error';panel.setAttribute('role','alert');
  const explanation=document.createElement('p');
  explanation.textContent='The 3D scene could not run in this browser. The static diagram remains visible, and the numerical controls below still work without 3D. Retry above; if it fails again, share these diagnostic details.';
  const details=document.createElement('details'),summary=document.createElement('summary'),text=document.createElement('pre');
  summary.textContent='3D diagnostic details';text.textContent=JSON.stringify(diagnostic,null,2);details.append(summary,text);panel.append(explanation,details);this.host.replaceChildren(panel);
  console.error('Kenoma 3D scene failure',diagnostic);
 }
}
