/** One in-flight request plus one latest request. No unbounded pointer-event queue. */
export class LatestWorker {
 constructor(worker,onResult,onError){this.worker=worker;this.onResult=onResult;this.onError=onError;this.serial=0;this.disposed=false;this.active=false;this.queued=null;worker.onmessage=({data})=>{if(this.disposed)return;this.active=false;if(data.id===this.serial){if(data.ok)this.onResult(data.state);else this.onError(new Error(data.error));}this.flush();};worker.onerror=e=>{if(this.disposed)return;this.active=false;this.queued=null;this.onError(new Error(e.message||'Lesson worker failed'));};}
 request(payload){if(this.disposed)throw new Error('Worker disposed');const id=++this.serial;this.queued={...payload,id};this.flush();return id;}
 flush(){if(this.active||!this.queued||this.disposed)return;const data=this.queued;this.queued=null;this.active=true;this.worker.postMessage(data);}
 dispose(){if(this.disposed)return;this.disposed=true;this.queued=null;this.worker.terminate();}
}
