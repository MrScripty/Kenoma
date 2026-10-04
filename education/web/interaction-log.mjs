/** Bounded local UI diagnostics, separate from deterministic model traces. */
const histories=new WeakMap();
for(const type of ['pointerdown','pointerup','click'])document.addEventListener(type,event=>{
 const button=event.target?.closest?.('button[data-action]'),root=button?.closest('.laboratory');
 if(!root)return;
 const r=button.getBoundingClientRect(),v=window.visualViewport;
 const events=histories.get(root)||[];
 events.push({type,action:button.dataset.action,label:button.textContent.trim().replace(/\s+/g,' '),
  trusted:event.isTrusted,wallClockMs:Math.round(performance.now()),
  point:[event.clientX,event.clientY],touchSize:[event.width??null,event.height??null],
  buttonRect:[r.left,r.top,r.width,r.height],scroll:[window.scrollX,window.scrollY],
  viewport:[window.innerWidth,window.innerHeight],visualViewport:v?{width:v.width,height:v.height,offsetLeft:v.offsetLeft,offsetTop:v.offsetTop,scale:v.scale}:null,
  sceneState:root.dataset.sceneState||'uninitialized'});
 histories.set(root,events.slice(-32));
},true);
export function getInteractionDiagnostics(root){
 return {schema:1,scope:'Local UI event/geometry diagnostics. Wall-clock milliseconds are not simulation time. No typed input values are collected.',
  lab:root.id,events:[...(histories.get(root)||[])]};
}
