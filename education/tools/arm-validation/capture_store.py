"""Bounded framed geometry store. Fixed slots preserve complete beginning/latest.
No numerical imports. All records remain provisional, including step candidates.
"""
import base64, hashlib, json, math, os, struct, time
POLICY=dict(version=1,coordinates=460,slotBytes=8192,slotsPerAttempt=12,checkpoints=[1,2,4,8,16,32,64,128,256],maxRecords=dict(A=1,D=516,B=514),maxFrames=34,maxReadBytes=65536,pipeBytes=8192,maxSupervisorBuffersBytes=1048576)
HEADER=36
def digest(b):return hashlib.sha256(b).hexdigest()
def decode(raw):
    if len(raw)<HEADER:raise ValueError('Incomplete capture header')
    size=struct.unpack('>I',raw[:4])[0]
    if not 0<size<=POLICY['slotBytes']-HEADER or len(raw)!=HEADER+size:raise ValueError('Capture length ceiling')
    payload=raw[HEADER:]
    if hashlib.sha256(payload).digest()!=raw[4:HEADER]:raise ValueError('Capture checksum')
    row=json.loads(payload)
    coords=base64.b64decode(row['coordinatesFloat64LE'],validate=True)
    if len(coords)!=3680 or digest(coords)!=row['coordinatesSHA256'] or not all(math.isfinite(x) for x in struct.unpack('<460d',coords)):raise ValueError('Capture coordinates')
    if row.get('status')!='PROVISIONAL_NEWTON_ITERATE' or row.get('physicalMotionAccepted') is not False:raise ValueError('Capture authority spoof')
    return row
def pwrite_all(fd,b,offset):
    used=0
    while used<len(b):
        try:n=os.pwrite(fd,b[used:],offset+used)
        except InterruptedError:continue
        if n<=0:raise OSError('Capture write failed')
        used+=n
class Store:
    def __init__(self,path,run,identity,output=None):
        self.path=path;self.run=run;self.identity=dict(identity);self.output=output;self.buffer=bytearray();self.records=0;self.wireBytes=0;self.trailingBytes=0;self.writeSeconds=0;self.sequence=0;self.locals={};self.done=set();self.latest={};self.sealed=False;self.pid=None;self.check=lambda:None;self.primed=None;self.durableRecords=0;self.prelaunchWriteSeconds=0
        self.attempts=2 if run=='D' else 1
        self.bytes=self.attempts*12*8192
        if output:output.reserve(run,self.bytes+POLICY['maxSupervisorBuffersBytes'])
        self.fd=os.open(path,os.O_RDWR|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
        try:os.posix_fallocate(self.fd,0,self.bytes);os.fsync(self.fd)
        except BaseException:os.close(self.fd);raise
        if output:output.charges[run]+=self.bytes;output.captureBuffers[run]=POLICY['maxSupervisorBuffersBytes']
    def bind_process(self,pid,start):self.pid=pid;self.startTicks=start
    def prime_begin(self,coordinates,extra=None):
        """Durable frozen input BEFORE worker launch, independent of startup.
        Sequence zero is supervisor provenance, never a Newton callback.
        """
        if self.primed is not None or self.records or len(coordinates)!=460 or not all(type(v) in (int,float) and math.isfinite(v) for v in coordinates):raise ValueError('Frozen beginning')
        raw_coordinates=struct.pack('<460d',*coordinates)
        row=dict(self.identity,kind='BEGIN',attempt=0 if self.run=='A' else 1,sequence=0,attemptSequence=0,status='PROVISIONAL_NEWTON_ITERATE',physicalMotionAccepted=False,workerPID=None,origin='SUPERVISOR_FROZEN_INPUT_BEFORE_WORKER_LAUNCH',coordinatesFloat64LE=base64.b64encode(raw_coordinates).decode(),coordinatesSHA256=digest(raw_coordinates),**(extra or {}))
        payload=json.dumps(row,separators=(',',':'),allow_nan=False).encode();raw=struct.pack('>I',len(payload))+bytes.fromhex(digest(payload))+payload;decode(raw)
        start=time.monotonic();pwrite_all(self.fd,raw,0);os.fsync(self.fd);self.prelaunchWriteSeconds+=time.monotonic()-start;self.primed=row['coordinatesSHA256']
    def feed(self,b):
        if self.sealed:raise ValueError('Sealed capture')
        if len(b)>POLICY['maxReadBytes']:raise ValueError('Capture read ceiling')
        self.wireBytes+=len(b)
        if self.wireBytes>POLICY['maxRecords'][self.run]*8192:raise ValueError('Capture wire ceiling')
        self.buffer.extend(b)
        while len(self.buffer)>=HEADER:
            size=struct.unpack('>I',self.buffer[:4])[0]
            if not 0<size<=8192-HEADER:raise ValueError('Capture length ceiling')
            if len(self.buffer)<HEADER+size:break
            raw=bytes(self.buffer[:HEADER+size]);del self.buffer[:HEADER+size];self.commit(raw)
        if len(self.buffer)>=8192:raise ValueError('Capture buffer ceiling')
    def commit(self,raw):
        row=decode(raw)
        if any(row.get(k)!=v for k,v in self.identity.items()) or row.get('run')!=self.run:raise ValueError('Capture provenance')
        if self.pid is not None and row.get('workerPID')!=self.pid:raise ValueError('Capture worker identity')
        a=row.get('attempt');allowed=[0] if self.run=='A' else list(range(1,self.attempts+1))
        if type(a) is not int or a not in allowed or type(row.get('sequence')) is not int or row['sequence']!=self.sequence+1:raise ValueError('Capture sequence')
        kind=row.get('kind');local=row.get('attemptSequence')
        if type(local) is not int:raise ValueError('Capture local sequence')
        if kind=='BEGIN':
            if a in self.locals or local!=0 or self.run=='D' and (a!=len(self.locals)+1 or a==2 and 1 not in self.done):raise ValueError('Repeated/bad beginning')
        elif a not in self.locals or a in self.done or kind not in ['NEWTON_ITERATE','STEP_CANDIDATE']:raise ValueError('Capture before beginning')
        elif kind=='NEWTON_ITERATE':
            if local!=self.locals[a]+1 or type(row.get('iteration')) is not int or row['iteration']<0 or type(row.get('residualN')) not in (int,float) or not math.isfinite(row['residualN']):raise ValueError('Capture iteration')
        elif local!=self.locals[a]:raise ValueError('Capture candidate sequence')
        if self.records>=POLICY['maxRecords'][self.run]:raise ValueError('Capture record ceiling')
        start=time.monotonic();base=(0 if self.run=='A' else a-1)*12;slots=[]
        if kind=='BEGIN':
            if base==0 and self.primed is not None:
                if row['coordinatesSHA256']!=self.primed:raise ValueError('Changed frozen beginning')
            else:slots.append(base)
        if kind=='NEWTON_ITERATE' and local in POLICY['checkpoints']:slots.append(base+1+POLICY['checkpoints'].index(local))
        if self.run!='A':slots.append(base+10+(self.latest.get(a,1)^1))
        # Full checksummed record fits each fixed slot. Trailing prior bytes are
        # irrelevant: size/hash reject an interrupted replacement. The other
        # latest slot remains complete until this slot's fsync succeeds.
        # Processing and durability are distinct. Update the stream's consumed
        # sequence before I/O; mark each first COMPLETE fsync before a resource
        # check can throw. A killed refresh cannot contradict sealed slot data.
        self.records+=1;self.sequence=row['sequence'];self.locals[a]=local
        if kind=='STEP_CANDIDATE':self.done.add(a)
        durable=False
        try:
            for slot in slots:
                self.check();pwrite_all(self.fd,raw,slot*8192);os.fsync(self.fd)
                if not durable:self.durableRecords+=1;durable=True
                if slot-base>=10:self.latest[a]=slot-base-10
                self.check()
            if not slots and self.primed is not None:self.durableRecords+=1
        finally:self.writeSeconds+=time.monotonic()-start
    def seal(self):
        if self.sealed:return self.receipt
        self.trailingBytes=len(self.buffer);self.buffer.clear();os.fsync(self.fd);os.close(self.fd);self.sealed=True
        raw=self.path.read_bytes();frames=read_slots(self.path)
        self.receipt=dict(status='PROVISIONAL_GEOMETRY_ONLY',records=self.records,durableRecords=self.durableRecords,latestRetainedSequence=max((r['sequence'] for r in frames),default=None),frozenBeginningDurable=self.primed is not None,prelaunchWriteSeconds=self.prelaunchWriteSeconds,wireBytes=self.wireBytes,retainedBytes=self.bytes,validRetainedFrames=len(frames),trailingIncompleteBytes=self.trailingBytes,writeSeconds=self.writeSeconds,sha256=digest(raw),workerPID=self.pid,workerStartTicks=getattr(self,'startTicks',None),physicalMotionAccepted=False)
        if self.output:
            self.output.captureBuffers[self.run]=0;self.output.written[self.path.name]=dict(bytes=len(raw),sha256=digest(raw))
        return self.receipt
def read_slots(path):
    if path.stat().st_size not in [12*8192,24*8192]:raise ValueError('Capture slot inventory')
    data=path.read_bytes()
    if len(data) not in [12*8192,24*8192]:raise ValueError('Capture slot inventory')
    rows={};latest={}
    for off in range(0,len(data),8192):
        slot=data[off:off+8192]
        if not any(slot):continue
        size=struct.unpack('>I',slot[:4])[0]
        try:row=decode(slot[:HEADER+size])
        except (ValueError,KeyError,TypeError):continue
        if (off//8192)%12>=10:
            if row['attempt'] not in latest or latest[row['attempt']]['sequence']<row['sequence']:latest[row['attempt']]=row
        else:rows[row['sequence']]=row
    for row in latest.values():rows[row['sequence']]=row
    return [rows[k] for k in sorted(rows)]
