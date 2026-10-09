import {exportScene,parseScene} from './scene-file.js';
export const MAX_ARCHIVE_BYTES=4*1024*1024;
export const MAX_SOURCE_BYTES=1024*1024;
const sourceBytes=text=>new TextEncoder().encode(text).byteLength;

/** Download an explicit snapshot; no automatic storage or external requests. */
export function downloadSceneArchive(bytes){
 const url=URL.createObjectURL(new Blob([bytes],{type:'application/vnd.sqlite3'}));
 const link=document.createElement('a');link.href=url;link.download='scene.human.sqlite';
 document.body.append(link);link.click();link.remove();setTimeout(()=>URL.revokeObjectURL(url),1000);
}

/** Scene-file controller. Archive encode/decode may be synchronous or async.
 * loadFile resolves {status:'loaded'|'cancelled'|'stale'|'error'}; malformed or
 * stale reads never replace the current source scene. A newer chooser silently
 * supersedes earlier reads; a current read with intervening edits reports why.
 */
export function setupSceneFiles({model,archive,saveButton,openButton,fileInput,onChange=()=>{},onError=()=>{},download=downloadSceneArchive,readBytes=file=>file.arrayBuffer()}){
 let epoch=0,choice=null,disposed=false;
 const report=error=>onError(error instanceof Error?error:new Error(String(error)));
 const stale=ticket=>disposed||ticket.epoch!==epoch;
 function revisionChanged(ticket){return model.revision!==ticket.revision;}
 function checkCurrent(ticket){
  if(stale(ticket))return false;
  if(revisionChanged(ticket))throw Error('Scene changed while opening the file. Open it again to replace the current scene.');
  if(model.gestureActive)throw Error('Finish the current pose edit before opening a scene.');
  return true;
 }
 async function save(){
  try{
   if(disposed)return {status:'cancelled'};
   const source=exportScene(model.state);
   if(sourceBytes(source)>MAX_SOURCE_BYTES)throw Error('Scene source exceeds the 1 MiB limit.');
   const bytes=await archive.encode(source);
   if(disposed)return {status:'cancelled'};
   if(!(bytes instanceof Uint8Array)||bytes.byteLength>MAX_ARCHIVE_BYTES)throw Error('Scene archive exceeds the 4 MiB limit or has an invalid encoding.');
   await download(bytes);return {status:'saved'};
  }catch(error){if(!disposed)report(error);return {status:'error'};}
 }
 function open(){if(disposed)return;choice={epoch:++epoch,revision:model.revision};fileInput.value='';fileInput.click();}
 async function loadFile(file,ticket){
  if(disposed||!file)return {status:'cancelled'};
  ticket=ticket||{epoch:++epoch,revision:model.revision};
  try{
   if(!checkCurrent(ticket))return {status:'stale'};
   if(!Number.isFinite(file.size)||file.size<0||file.size>MAX_ARCHIVE_BYTES)throw Error('Choose a scene archive no larger than 4 MiB.');
   const raw=await readBytes(file);
   if(!checkCurrent(ticket))return {status:'stale'};
   const bytes=raw instanceof ArrayBuffer?new Uint8Array(raw):raw;
   if(!(bytes instanceof Uint8Array)||bytes.byteLength>MAX_ARCHIVE_BYTES)throw Error('Scene archive exceeds the 4 MiB limit or has an invalid encoding.');
   const source=await archive.decode(bytes);
   if(!checkCurrent(ticket))return {status:'stale'};
   if(typeof source!=='string'||sourceBytes(source)>MAX_SOURCE_BYTES)throw Error('Scene source exceeds the 1 MiB limit or has an invalid encoding.');
   const state=parseScene(source,model.baseGraph);
   // Parsing is pure and synchronous; replacement is one validated undo step.
   model.replaceScene(state);onChange();return {status:'loaded'};
  }catch(error){if(stale(ticket))return {status:'stale'};report(error);return {status:'error'};}
 }
 const selected=()=>{const file=fileInput.files?.[0],ticket=choice||{epoch:++epoch,revision:model.revision};choice=null;fileInput.value='';if(file)void loadFile(file,ticket);};
 const cancelled=()=>{choice=null;++epoch;};
 const saveClicked=()=>void save();
 saveButton.addEventListener('click',saveClicked);openButton.addEventListener('click',open);fileInput.addEventListener('change',selected);fileInput.addEventListener('cancel',cancelled);
 return {save,open,loadFile,dispose(){if(disposed)return;disposed=true;++epoch;choice=null;saveButton.removeEventListener('click',saveClicked);openButton.removeEventListener('click',open);fileInput.removeEventListener('change',selected);fileInput.removeEventListener('cancel',cancelled);}};
}
