"""Qualify actual standalone controls, independently reconstructed Q2 map and GPU buffers.

Uses actual Chromium WebGL2 buffer readback, not only CPU mesh snapshots. This
is a bounded headless software-WebGL qualification, not a hardware/stability claim.
"""
from pathlib import Path
from functools import partial
from http.server import SimpleHTTPRequestHandler,ThreadingHTTPServer
from threading import Thread
import os,shutil
import argparse,hashlib,json,math,sys
import numpy as np
from playwright.sync_api import sync_playwright,expect
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def close(got,want,label,absolute=2e-12,relative=2e-10):
    assert math.isfinite(got) and math.isfinite(want)
    assert abs(got-want)<=absolute+relative*abs(want),(label,got,want)
def snap(lab):return lab.evaluate('(r)=>r.axisymmetricLab.snapshot()')
def ready(page):page.wait_for_function("document.querySelector('[data-axisymmetric]').dataset.busy==='false' && document.querySelector('[data-axisymmetric]').axisymmetricLab.state",timeout=120000)
def edit(page,lab,key,value):
    old=snap(lab);lab.locator(f'[data-setting={key}]').select_option(str(value));ready(page);new=snap(lab)
    assert new['solveCount']==old['solveCount']+1
    if key=='mesh':assert (new['configuration']['axialCells'],new['configuration']['radialCells'])==tuple(map(int,value.split(',')))
    else:close(new['configuration'][key],float(value),'Named control applies requested value',absolute=0,relative=0)
    for k,v in old['configuration'].items():
        if k!=key and not(key=='mesh' and k in ['axialCells','radialCells']):assert new['configuration'][k]==v,('Unrelated property changed',key,k)
    if old['scene']['camera']:assert new['scene']['camera']==old['scene']['camera'],'Physics edit must preserve camera'
    return new

def reconstruct(payload):
    c=payload['configuration'];nx,nr=c['axialCells'],c['radialCells'];nz,nnr=2*nx+1,2*nr+1;q=payload['state']['q'];u=np.zeros((nz,nnr,2));free=0
    for j in range(nz):
        for i in range(nnr):
            for component in range(2):
                if (component==0 and i==0) or (component==1 and (i==0 or j in [0,nz-1])):continue
                u[j,i,component]=q[free];free+=1
    assert free==len(q)
    u[-1,:,1]=payload['state']['epsilon']*.05
    u[1:-1,0,1]=(4*u[1:-1,1,1]-u[1:-1,2,1])/3
    def at(R,Z):
        a=.005*(1+(c['ratio']-1)*Z/.05);slope=.005*(c['ratio']-1)/.05
        i=min(nr-1,int(R/a*nr));j=min(nx-1,int(Z/.05*nx));xi=2*(R/a*nr-i)-1;eta=2*(Z/.05*nx-j)-1
        def basis(x):return np.array([x*(x-1)/2,1-x*x,x*(x+1)/2]),np.array([x-.5,-2*x,x+.5])
        n,dn=basis(xi);m,dm=basis(eta);disp=np.zeros(2);derivR=np.zeros(2);derivZ=np.zeros(2)
        for jj in range(3):
            for ii in range(3):
                nodal=u[2*j+jj,2*i+ii];disp+=n[ii]*m[jj]*nodal
                derivR+=dn[ii]*m[jj]*2*nr/a*nodal
                derivZ+=(dn[ii]*m[jj]*(-2*nr*R*slope/a**2)+n[ii]*dm[jj]*2*nx/.05)*nodal
        r,z=R+disp[0],Z+disp[1];v=[1+derivR[0],derivZ[0],derivR[1],1+derivZ[1],r/R if R else 1+derivR[0]]
        A,B,C,D,H=v;J=H*(A*D-B*C);F=np.array([[A,0,B],[0,H,0],[C,0,D]]);I=float(np.sum(F*F))
        stress=1500*J**(-5/3)*(F@F.T-I/3*np.eye(3))+30000*math.log(J)/J*np.eye(3)
        return {'r':r,'z':z,'v':v,'J':J,'stress':stress}
    return at,u

def verify_state(payload,oracle,experiment):
    c,s=payload['configuration'],payload['state'];d=s['diagnostics'];assert s['epsilon']==c['epsilon'] and d['quadratureOrder']==7
    close(d['forceScaleN'],1500*math.pi*.005**2,'Positive zero normalization')
    close(d['energyScaleJ'],1500*math.pi*.05*.005**2*(1+c['ratio']+c['ratio']**2)/3,'Positive zero energy normalization')
    assert s['converged']==(d['scaledMaxFreeResidual']<=s['tolerance'])
    at,u=reconstruct(payload);probe=payload['probe'];p=at(probe['R'],probe['Z'])
    for k in ['r','z','J']:close(probe[k],p[k],'Independent Q2 probe '+k)
    for got,want in zip(probe['v'],p['v']):close(got,want,'Independent full deformation components')
    close(probe['cauchy']['rr'],p['stress'][0,0],'Independent full Cauchy rr',absolute=2e-8)
    close(probe['cauchy']['zz'],p['stress'][2,2],'Independent full Cauchy zz',absolute=2e-8)
    assert np.all(u[:,0,0]==0) and np.all(u[0,:,1]==0) and np.all(u[-1,:,1]==s['epsilon']*.05)
    if c['cap']==25:
        assert s['converged'] and d['scaledMaxFreeResidual']<=1e-10
        if c['ratio']==1:
            o=next(o for o in oracle['cylinders'] if abs(o['lambda']-(1+s['epsilon']))<1e-14)
            for row in range(u.shape[0]):
                Z=.05*row/(u.shape[0]-1)
                for col in range(u.shape[1]):
                    R=.005*col/(u.shape[1]-1);p=at(R,Z)
                    close(p['r'],o['side_stretch']*R,'Independent uniform lateral geometry',absolute=2e-12)
                    close(p['z'],o['lambda']*Z,'Independent uniform axial geometry',absolute=2e-12)
                    close(p['J'],o['J'],'Independent free-lateral J',absolute=5e-10,relative=0)
                    close(p['stress'][0,0],0,'Uniform lateral traction',absolute=2e-5,relative=0)
            close(d['rightReactionN'],math.pi*.005**2*o['nominal_axial_pa'],'Independent uniform end resultant',absolute=2e-10)
            close(d['energyJ'],math.pi*.005**2*.05*o['energy_density_pa'],'Independent uniform stored energy')
        elif c['axialCells']==16 and c['radialCells']==8:
            expected=next(x for x in experiment['cases'] if x['ratio']==1.5 and x['axialCells']==16 and x['radialCells']==8 and x['order']==7 and x['epsilon']==s['epsilon'])
            for got,want in zip(s['q'],expected['state']['q']):close(got,want,'Actual browser/offline qualified Q2 state',absolute=2e-12)
            for k in ['energyJ','volumeM3','rightReactionN','weightedRmsJDefect']:close(d[k],expected['state']['diagnostics'][k],'Actual browser/offline '+k,absolute=2e-12)
    return {'configuration':c,'converged':s['converged'],'reactionN':d['rightReactionN'],'volumeRatio':d['volumeRatio'],'probeJ':probe['J'],'scaledResidual':d['scaledMaxFreeResidual']}

GPU_TRACK=r'''(()=>{window.__axisBuffers=[];const original=HTMLCanvasElement.prototype.getContext;HTMLCanvasElement.prototype.getContext=function(kind,...args){const gl=original.call(this,kind,...args);if(kind==='webgl2'&&gl&&!gl.__axisTracked){gl.__axisTracked=true;const data=gl.bufferData;gl.bufferData=function(target,source,...rest){const result=data.call(this,target,source,...rest);if(ArrayBuffer.isView(source)&&(target===gl.ARRAY_BUFFER||target===gl.ELEMENT_ARRAY_BUFFER)){const buffer=gl.getParameter(target===gl.ARRAY_BUFFER?gl.ARRAY_BUFFER_BINDING:gl.ELEMENT_ARRAY_BUFFER_BINDING);window.__axisBuffers.push({gl,buffer,target,constructor:source.constructor.name,values:Array.from(source)});}return result;};}return gl;};window.__axisReadGPU=(expected,targetName)=>{const record=[...window.__axisBuffers].reverse().find(r=>r.target===r.gl[targetName]&&r.values.length===expected.length&&r.values.every((v,i)=>v===expected[i]));if(!record)throw new Error('Actual expected buffer upload not found');const gl=record.gl,target=record.target,binding=gl.getParameter(target===gl.ARRAY_BUFFER?gl.ARRAY_BUFFER_BINDING:gl.ELEMENT_ARRAY_BUFFER_BINDING);gl.bindBuffer(target,record.buffer);const result=new window[record.constructor](expected.length);gl.getBufferSubData(target,0,result);gl.bindBuffer(target,binding);if(gl.getError()!==gl.NO_ERROR)throw new Error('GPU readback error');return {values:Array.from(result),constructor:record.constructor,version:gl.getParameter(gl.VERSION),vendor:gl.getParameter(gl.VENDOR),renderer:gl.getParameter(gl.RENDERER)};};})();'''

def verify_scene(page,payload):
    s,b=payload['scene'],payload['boundary'];assert s['state']=='ready' and s['canvasCount']==1 and s['drawCalls']>0 and s['physicalScale']==1
    positions=np.array(s['positions']).reshape(-1,3);indices=np.array(s['indices']).reshape(-1,3);at,_=reconstruct(payload);c=payload['configuration'];reference=b['referenceVertices']
    assert len(positions)==len(reference) and len(indices)==len(b['indices'])
    # Reconstruct from the solved nodal field rather than trusting boundary.vertices.
    for ring in range(b['rings']):
        Z=.05*ring/(b['rings']-1);R=.005*(1+(c['ratio']-1)*Z/.05);p=at(R,Z)
        for angle in range(b['azimuth']):
            t=2*math.pi*angle/b['azimuth'];want=[p['z'],p['r']*math.cos(t),p['r']*math.sin(t)]
            got=positions[ring*b['azimuth']+angle]
            for x,y in zip(got,want):close(float(x),y,'Actual displayed vertex from independent Q2 map',absolute=3e-9,relative=0)
    for center,Z in [(-2,0),(-1,.05)]:
        p=at(0,Z)
        for x,y in zip(positions[center],[p['z'],0,0]):close(float(x),y,'Actual end center',absolute=3e-9,relative=0)
    assert np.array_equal(indices,np.array(b['indices']))
    # Independent edge incidence/orientation and graph connectivity.
    counts={};graph=[set() for _ in positions]
    for triangle in indices:
        assert len(set(triangle))==3
        for a,bb in zip(triangle,np.roll(triangle,-1)):
            a,bb=int(a),int(bb);edge=tuple(sorted([a,bb]));counts.setdefault(edge,[]).append((a,bb));graph[a].add(bb);graph[bb].add(a)
    assert all(len(v)==2 and v[0]==v[1][::-1] for v in counts.values()),'Actual closed oriented indexed shell'
    visited={0};stack=[0]
    while stack:
        new=graph[stack.pop()]-visited;visited.update(new);stack.extend(new)
    assert len(visited)==len(positions),'Exactly one connected shell'
    v=positions[indices];volume=float(np.sum(np.einsum('ij,ij->i',v[:,0],np.cross(v[:,1],v[:,2])))/6)
    close(volume,payload['renderTessellationVolumeM3'],'Independent actual Float32 shell volume',absolute=3e-16)
    integrated=payload['state']['diagnostics']['volumeM3'];v0=math.pi*.05*.005**2*(1+c['ratio']+c['ratio']**2)/3
    if payload['state']['converged']:
        signal=abs(integrated/v0-1);bound=2e-4 if c['epsilon']==0 else .1*signal
        assert abs(volume-integrated)/v0<bound,'Finite rendered-volume error smaller than physical signal'
    read=page.evaluate('(s)=>({positions:window.__axisReadGPU(s.positions,"ARRAY_BUFFER"),indices:window.__axisReadGPU(s.indices,"ELEMENT_ARRAY_BUFFER")})',s)
    assert read['positions']['values']==s['positions'] and read['indices']['values']==s['indices'],'Actual WebGL2 GPU buffer readback'
    index_type=np.uint16 if read['indices']['constructor']=='Uint16Array' else np.uint32
    return {'vertexCount':len(positions),'triangleCount':len(indices),'connectedComponents':1,'closedOrientedShell':True,'physicalScale':1,'gpuPositionSHA256':hashlib.sha256(np.array(read['positions']['values'],dtype=np.float32).tobytes()).hexdigest(),'gpuIndexSHA256':hashlib.sha256(np.array(read['indices']['values'],dtype=index_type).tobytes()).hexdigest(),'gpuIndexConstructor':read['indices']['constructor'],'actualGPUVolumeM3':volume,'integratedVolumeM3':integrated,'gpuContext':{k:v for k,v in read['positions'].items() if k not in ['values','constructor']}}

class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self,*args):pass

def qualify(preview,out,oracle_file,experiment_file):
    test_sha=sha(Path(__file__))
    out.mkdir(parents=True,exist_ok=True);manifest=json.loads((preview/'axisymmetric-preview-manifest.json').read_text());before={n:sha(preview/n) for n in manifest['output_sha256']}
    assert before==manifest['output_sha256'],'Delivered preview hash mismatch'
    assert all(sha(ROOT/n)==h for n,h in manifest['input_sha256'].items()),'Source/preview mismatch'
    oracle=json.loads(oracle_file.read_text());experiment=json.loads(experiment_file.read_text());assert oracle['status']=='PASS'
    assert all(sha(ROOT/n)==h for n,h in oracle['input_sha256'].items()) and all(sha(ROOT/n)==h for n,h in experiment['inputs'].items())
    server=ThreadingHTTPServer(('127.0.0.1',0),partial(QuietHandler,directory=str(preview)));Thread(target=server.serve_forever,daemon=True).start();url='http://127.0.0.1:'+str(server.server_port)
    cases=[];errors=[];exports=[]
    def record(page,lab,name,scene=True,screenshot=False):
        p=snap(lab);row={'case':name,'state':verify_state(p,oracle,experiment)}
        if scene:row['scene']=verify_scene(page,p);row['canvasSHA256']=hashlib.sha256(lab.locator('canvas').screenshot()).hexdigest()
        if screenshot:lab.screenshot(path=str(out/(name+'.png')))
        (out/(name+'-state.json')).write_text(json.dumps(p)+'\n');cases.append(row);return p
    try:
        with sync_playwright() as pw:
            browser=pw.chromium.launch(executable_path=os.environ.get('CHROMIUM_EXECUTABLE') or shutil.which('chromium') or pw.chromium.executable_path,headless=True,args=['--no-sandbox','--use-angle=swiftshader','--enable-unsafe-swiftshader']);context=browser.new_context(viewport={'width':1200,'height':1000});context.add_init_script(GPU_TRACK);page=context.new_page();page.on('pageerror',lambda e:errors.append(str(e)));page.goto(url);ready(page);lab=page.locator('[data-axisymmetric]')
            assert lab.get_attribute('data-scene-state')=='idle';record(page,lab,'rest-static',False)
            lab.locator('[data-action=start]').click();expect(lab).to_have_attribute('data-scene-state','ready');rest=record(page,lab,'taper-rest',screenshot=True)
            edit(page,lab,'epsilon','0.1');tension=record(page,lab,'taper-tension',screenshot=True)
            edit(page,lab,'epsilon','-0.1');compression=record(page,lab,'taper-compression',screenshot=True)
            assert len({r['canvasSHA256'] for r in cases if 'canvasSHA256' in r})==3,'Actual framebuffers must change across three poses'
            assert compression['state']['diagnostics']['volumeRatio']<1<tension['state']['diagnostics']['volumeRatio']
            # Probe controls evaluate the same field and must not trigger a solve or remesh.
            before=snap(lab);lab.locator('[data-probe=z]').select_option('0.75');lab.locator('[data-probe=r]').select_option('0');probe=snap(lab)
            assert all(before[k]==probe[k] for k in ['configuration','state','boundary','solveCount','scene'])
            close(probe['probe']['v'][2],0,'Regular symmetry-axis axial derivative',absolute=2e-12);record(page,lab,'axis-probe')
            edit(page,lab,'mesh','8,4');record(page,lab,'medium-compression')
            edit(page,lab,'mesh','4,2');record(page,lab,'coarse-compression')
            edit(page,lab,'ratio','1');record(page,lab,'uniform-compression',screenshot=True)
            edit(page,lab,'epsilon','0.1');record(page,lab,'uniform-tension',screenshot=True)
            edit(page,lab,'epsilon','0');record(page,lab,'uniform-rest')
            edit(page,lab,'ratio','1.5');edit(page,lab,'epsilon','0.1');edit(page,lab,'cap','1');approx=record(page,lab,'one-iteration',screenshot=True)
            assert not approx['state']['converged'] and approx['state']['diagnostics']['scaledMaxFreeResidual']>1e-10
            warning=lab.locator('.solve-status').inner_text();assert 'Not converged' in warning
            # Inject an actual unsupported select entry and trigger the actual listener.
            lab.locator('[data-setting=ratio]').evaluate("el=>{el.add(new Option('unsupported','2'));el.value='2';el.dispatchEvent(new Event('change',{bubbles:true}));}")
            rejected=snap(lab);assert all(rejected[k]==approx[k] for k in ['configuration','state','boundary','scene','solveCount']);assert lab.locator('.solve-status').inner_text()==warning and 'Unsupported control' in lab.locator('.progress').inner_text()
            record(page,lab,'unsupported-retained')
            # Worker failure after a displayed approximation: keep complete state and warning.
            page.evaluate("(()=>{window.__originalWorker=window.Worker;window.Worker=class{constructor(){setTimeout(()=>this.onerror({message:'qualification injected worker failure'}),0)}postMessage(){}terminate(){}};})()")
            lab.locator('[data-setting=cap]').select_option('25');ready(page);failed=snap(lab)
            assert all(failed[k]==approx[k] for k in ['configuration','state','boundary','scene','solveCount']) and lab.locator('.solve-status').inner_text()==warning
            assert 'qualification injected worker failure' in lab.locator('.progress').inner_text();page.evaluate('()=>{window.Worker=window.__originalWorker;}');record(page,lab,'worker-failure-retained')
            # Actual pending solve cancellation: final controls and state must agree.
            lab.locator('[data-setting=cap]').select_option('25');lab.locator('[data-setting=epsilon]').select_option('-0.1');lab.locator('[data-setting=epsilon]').select_option('0.1');ready(page);assert snap(lab)['configuration']['epsilon']==.1 and snap(lab)['configuration']['cap']==25;record(page,lab,'latest-request-wins')
            before=snap(lab);lab.locator('[data-action=front]').click();front=snap(lab);assert front['state']==before['state'] and front['boundary']==before['boundary'] and front['scene']['camera']!=before['scene']['camera'];record(page,lab,'front-view',screenshot=True)
            with page.expect_download() as dl:lab.locator('[data-action=export]').click()
            downloaded=dl.value;downloaded.save_as(str(out/'exported-state.json'));exported=json.loads((out/'exported-state.json').read_text());assert exported['state']==snap(lab)['state'];exports.append('Current exported state matches actual numerical field')
            lab.locator('[data-action=reset]').click();ready(page);reset=record(page,lab,'explicit-reset',screenshot=True);assert reset['configuration']=={'epsilon':0,'ratio':1.5,'axialCells':16,'radialCells':8,'cap':25} and reset['state']['diagnostics']['energyJ']==0
            # Real WebGL extension context loss and retry; numerical state stays fixed.
            before=snap(lab);page.evaluate("document.querySelector('canvas').getContext('webgl2').getExtension('WEBGL_lose_context').loseContext()");expect(lab).to_have_attribute('data-scene-state','error');lost=snap(lab);assert lost['state']==before['state'] and lost['configuration']==before['configuration'];assert lab.locator('.scene-error').is_visible();record(page,lab,'context-lost',False,True)
            lab.locator('[data-action=start]').click();expect(lab).to_have_attribute('data-scene-state','ready');record(page,lab,'context-retry')
            mobile=browser.new_context(viewport={'width':390,'height':844},device_scale_factor=1,is_mobile=True,has_touch=True);mobile.add_init_script(GPU_TRACK);mpage=mobile.new_page();mpage.on('pageerror',lambda e:errors.append(str(e)));mpage.goto(url);ready(mpage);mlab=mpage.locator('[data-axisymmetric]');mlab.locator('[data-action=start]').click();expect(mlab).to_have_attribute('data-scene-state','ready');edit(mpage,mlab,'epsilon','-0.1');record(mpage,mlab,'mobile-compression',screenshot=True)
            assert mpage.evaluate('document.documentElement.scrollWidth<=innerWidth'),'Mobile horizontal overflow'
            # Actual getContext unavailable: numerical controls still solve, static reference visible.
            unavailable=browser.new_context(viewport={'width':1000,'height':900});unavailable.add_init_script("const old=HTMLCanvasElement.prototype.getContext;HTMLCanvasElement.prototype.getContext=function(kind,...args){return kind.startsWith('webgl')?null:old.call(this,kind,...args)};");upage=unavailable.new_page();upage.goto(url);ready(upage);ulab=upage.locator('[data-axisymmetric]');ulab.locator('[data-action=start]').click();expect(ulab).to_have_attribute('data-scene-state','error');edit(upage,ulab,'epsilon','0.1');record(upage,ulab,'webgl-unavailable-numerical',False,True);assert ulab.locator('.static-reference').is_visible()
            assert not errors,errors
            version=browser.version;browser.close()
    finally:server.shutdown()
    assert sha(Path(__file__))==test_sha,'Browser test changed during qualification'
    assert {n:sha(preview/n) for n in manifest['output_sha256']}==manifest['output_sha256'] and all(sha(ROOT/n)==h for n,h in manifest['input_sha256'].items())
    record={'status':'PASS','browser':'Chromium '+version,'render_scope':'Actual inspected headless Chromium controls, WebGL2 with SwiftShader; CPU map independently reconstructed and actual GPU position/index buffers read back. No physical mobile GPU or stability claim.','preview_manifest_sha256':sha(preview/'axisymmetric-preview-manifest.json'),'oracle_sha256':sha(oracle_file),'experiment_sha256':sha(experiment_file),'source_inputs':manifest['input_sha256'],'cases':cases,'exports':exports,'page_errors':errors,'test_sha256':test_sha}
    (out/'axisymmetric-browser-status.json').write_text(json.dumps(record,indent=2)+'\n');print('PASS actual connected browser controls, independent Q2 field, GPU buffers and failure/recovery: '+str(len(cases))+' cases')
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--preview',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--oracle',type=Path,required=True);p.add_argument('--experiment',type=Path,required=True);a=p.parse_args();qualify(a.preview.resolve(),a.out.resolve(),a.oracle.resolve(),a.experiment.resolve())
