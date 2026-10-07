/** Runtime refusal and append-only evidence. Independent of any material law. */
import fs from 'node:fs';import path from 'node:path';import {createHash} from 'node:crypto';
export class ResourceRefusal extends Error{constructor(reason,detail={}){super(reason);this.name='ResourceRefusal';this.reason=reason;this.detail=detail;}}
export class RuntimeLimits{
 constructor({plannedCalls=8847360,maximumCalls=9000000,wallMs=900000,rssBytes=8*1024**3,now=()=>performance.now(),rss=()=>process.memoryUsage.rss(),startedMs=null}={}){
  this.plannedCalls=plannedCalls;this.maximumCalls=maximumCalls;this.wallMs=wallMs;this.rssBytes=rssBytes;this.now=now;this.rss=rss;this.started=startedMs??now();this.reserved=0;this.actual=0;this.completed=0;this.batch=null;this.peakRss=0;this.lastPhase='created';
 }
 check(phase,{memory=true}={}){
  this.lastPhase=phase;const elapsed=this.now()-this.started;
  if(memory){const r=this.rss();this.peakRss=Math.max(this.peakRss,r);if(r>this.rssBytes)throw new ResourceRefusal('RSS_LIMIT',{phase,rssBytes:r,maximumRssBytes:this.rssBytes,elapsedMs:elapsed});}
  if(elapsed>=this.wallMs)throw new ResourceRefusal('WALL_LIMIT',{phase,elapsedMs:elapsed,maximumWallMs:this.wallMs});
 }
 beginBatch(count,label){this.check('before-batch');if(this.batch)throw Error('Batch already active');if(!Number.isInteger(count)||count<=0||this.reserved+count>this.plannedCalls||this.reserved+count>this.maximumCalls)throw new ResourceRefusal('RESERVATION_LIMIT',{count,reserved:this.reserved});this.reserved+=count;this.batch={label,count,startActual:this.actual};}
 invoke(callback){
  this.check('before-callback',{memory:this.actual%128===0});
  if(!this.batch||this.actual-this.batch.startActual>=this.batch.count||this.actual>=this.plannedCalls||this.actual>=this.maximumCalls)throw new ResourceRefusal('ACTUAL_CALLBACK_LIMIT',{actual:this.actual,reserved:this.reserved});
  this.actual++;let value,error;try{value=callback();this.completed++;}catch(e){error=e;}
  try{this.check('after-callback',{memory:this.actual%128===0});}catch(e){if(error)e.detail.callbackFailure=error.message;throw e;}
  if(error)throw error;return value;
 }
 endBatch(){this.check('after-batch');if(!this.batch||this.actual-this.batch.startActual!==this.batch.count)throw new ResourceRefusal('INCOMPLETE_BATCH',{batch:this.batch,actual:this.actual});this.batch=null;}
 finish(){this.check('after-final-batch-and-output');if(this.batch||this.actual!==this.plannedCalls||this.completed!==this.plannedCalls||this.reserved!==this.plannedCalls)throw new ResourceRefusal('INCOMPLETE_ACTUAL_COUNT',this.receipt());}
 receipt(){return {reservedCalls:this.reserved,actualConstitutiveCallbacks:this.actual,completedConstitutiveCallbacks:this.completed,plannedCalls:this.plannedCalls,maximumCalls:this.maximumCalls,elapsedMs:this.now()-this.started,maximumWallMs:this.wallMs,peakObservedRssBytes:this.peakRss,maximumRssBytes:this.rssBytes,lastPhase:this.lastPhase,activeBatch:this.batch};}
}
export class EvidenceStore{
 constructor(directory,{maximumBytes=256*1024**2,emergencyBytes=1024**2}={}){if(fs.existsSync(directory))throw Error('Preserve existing invocation/output directory');fs.mkdirSync(directory,{recursive:true});this.directory=directory;this.maximumBytes=maximumBytes;this.emergencyBytes=emergencyBytes;this.bytes=0;this.files={};}
 checkStorage(phase){let measured=0;for(const entry of fs.readdirSync(this.directory)){const s=fs.statSync(path.join(this.directory,entry));if(!s.isFile())throw Error('Unexpected output entry');measured+=s.size;}this.bytes=measured;if(measured>this.maximumBytes-this.emergencyBytes)throw new ResourceRefusal('STORAGE_LIMIT',{phase,bytes:measured,maximumNormalBytes:this.maximumBytes-this.emergencyBytes});}
 write(name,data,{emergency=false}={}){
  if(path.basename(name)!==name||this.files[name]||fs.existsSync(path.join(this.directory,name)))throw Error('Preserve existing evidence file');
  const b=Buffer.isBuffer(data)?data:Buffer.from(data),limit=emergency?this.maximumBytes:this.maximumBytes-this.emergencyBytes;
  if(this.bytes+b.length>limit)throw new ResourceRefusal('STORAGE_LIMIT',{bytes:this.bytes,nextBytes:b.length,maximumBytes:limit});
  const fd=fs.openSync(path.join(this.directory,name),'wx');let written=0;try{while(written<b.length)written+=fs.writeSync(fd,b,written,b.length-written);fs.fsyncSync(fd);}finally{fs.closeSync(fd);this.bytes+=written;}
  this.files[name]={bytes:written,sha256:createHash('sha256').update(b).digest('hex')};if(!emergency)this.checkStorage('after-write');return this.files[name];
 }
 json(name,value,options){return this.write(name,JSON.stringify(value)+'\n',options);}
 failure(error,context,limits){return this.json('incomplete-receipt.json',{schema:1,result:'INCOMPLETE_FIXED_PATCH_INTEGRATION',reason:error.reason??error.message,detail:error.detail??null,runtime:limits.receipt(),context,retainedFiles:this.files,storageBytesBeforeReceipt:this.bytes},{emergency:true});}
}
/** Catch neither resource nor callback failures as a retry. Preserve one compact
 * partial-state receipt, then propagate the original error to the caller. */
export function preservingFailure(store,limits,context,action){try{return action();}catch(error){store.failure(error,context(),limits);throw error;}}
