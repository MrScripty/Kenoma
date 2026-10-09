/** Latest-pose asynchronous scheduling, independent of renderer and WASM implementation.
 * One job is in flight; pending poses replace older poses for that character.
 * An incarnation token prevents responses from deleted characters reaching re-added IDs.
 */
export class AsyncRigBridge {
 constructor({workerFactory=()=>new Worker(new URL('./rig-worker.js',import.meta.url),{type:'module'}),onMesh=()=>{},onError=()=>{}}={}){
  this.worker=workerFactory();this.onMesh=onMesh;this.onError=onError;this.characters=new Map();this.queue=[];this.inflight=null;this.serial=0;this.jobSerial=0;this.waiters=[];this.disposed=false;this.failure=null;
  this.worker.addEventListener('message',event=>this.receive(event.data));
  this.worker.addEventListener('error',event=>this.fail(new Error(event.message||'Rig worker failed')));
  this.worker.addEventListener('messageerror',()=>this.fail(new Error('Rig worker returned an unreadable message')));
 }
 bind(id,graph){if(this.disposed)throw Error('Rig bridge is disposed');if(this.characters.has(id))this.remove(id);const state={id,generation:++this.serial,revision:0,bound:false,pose:null,queued:false,error:null};this.characters.set(id,state);this.queue.push({type:'bind',id,generation:state.generation,graph:structuredClone(graph),revision:0});this.pump();return state.generation;}
 pose(id,graph,head){const state=this.characters.get(id);if(!state)throw Error('Unknown rig character');if(!state.bound&&state.error)throw state.error;const pose={graph:structuredClone(graph),head:structuredClone(head)};const key=JSON.stringify(pose);if(state.pose?.key===key)return state.revision;state.revision++;state.pose={...pose,key};state.error=null;if(!state.queued){state.queued=true;this.queue.push({type:'pose',id,generation:state.generation});}this.pump();return state.revision;}
 remove(id){const state=this.characters.get(id);if(!state)return;this.characters.delete(id);this.queue=this.queue.filter(job=>job.id!==id||job.generation!==state.generation);this.queue.push({type:'release',id,generation:state.generation});this.pump();}
 get pending(){return !!this.inflight||this.queue.length>0;}
 whenIdle(){if(this.disposed)return Promise.reject(Error('Rig bridge is disposed'));if(this.failure)return Promise.reject(this.failure);if(!this.pending){const error=[...this.characters.values()].find(c=>c.error)?.error;return error?Promise.reject(error):Promise.resolve();}return new Promise((resolve,reject)=>this.waiters.push({resolve,reject}));}
 pump(){if(this.disposed||this.failure||this.inflight)return;let job;while((job=this.queue.shift())){const state=this.characters.get(job.id);if(job.type!=='release'&&(!state||state.generation!==job.generation))continue;if(job.type==='pose'){state.queued=false;if(!state.bound){if(state.error)continue;state.queued=true;this.queue.push(job);break;}job={...job,...state.pose,revision:state.revision};}job.jobId=++this.jobSerial;this.inflight=job;try{this.worker.postMessage(job);}catch(error){this.fail(error);}return;}this.settle();}
 receive(result){const job=this.inflight;if(!job||result.jobId!==job.jobId)return;this.inflight=null;const state=this.characters.get(job.id),current=state&&state.generation===job.generation;
  if(current){if(!result.ok){const error=new Error(result.error?.message||'Rig worker operation failed');if(job.type==='bind'||job.revision===state.revision){state.error=error;this.onError(error,{id:job.id,generation:job.generation});}}
   else if(job.type==='bind'){state.bound=true;if(!state.pose)this.onMesh({id:job.id,generation:job.generation,revision:0,key:null,mesh:result.mesh,timing:result.timing});}
   else if(job.type==='pose'&&job.revision===state.revision){state.error=null;this.onMesh({id:job.id,generation:job.generation,revision:job.revision,key:job.key,mesh:result.mesh,timing:result.timing});}}
  this.pump();
 }
 settle(){if(this.pending)return;const error=this.failure||[...this.characters.values()].find(c=>c.error)?.error;for(const waiter of this.waiters.splice(0))error?waiter.reject(error):waiter.resolve();}
 fail(error){if(this.failure||this.disposed)return;this.failure=error;this.inflight=null;this.queue=[];this.onError(error);this.settle();}
 dispose(){if(this.disposed)return;this.disposed=true;this.worker.terminate();this.characters.clear();this.queue=[];this.inflight=null;for(const waiter of this.waiters.splice(0))waiter.reject(Error('Rig bridge is disposed'));}
}
