"""Actual SLS controls, numerical histories, SVG coordinates and negative copies."""
from pathlib import Path
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread
from tempfile import TemporaryDirectory
import argparse, hashlib, json, math, os, shutil, subprocess, sys
from playwright.sync_api import sync_playwright, expect
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from build_dissipative_preview import build

def snapshot(lab):
    lab.locator('[data-action=copy]').click()
    return json.loads(lab.locator('.preset').input_value())

def verify_trace(payload):
    p=payload['parameters'];rows=payload['trace']
    assert rows[0]['step']==0 and rows[0]['time']==0 and rows[0]['workJ']==rows[0]['storageJ']==rows[0]['dissipationJ']==0
    assert len(rows)==payload['samples']==payload['steps']+1
    previous=-1.;loss=0.
    for i,row in enumerate(rows):
        assert row['step']==i and row['time']>previous
        assert row['storageJ']>=-1e-12 and row['dissipationJ']>=loss-1e-12
        assert row['dissipationRateW']>=0 and row['maxStrain']<=.05+1e-12
        residual=row['workJ']-row['storageJ']-row['dissipationJ']
        assert abs(residual)<1e-9, ('Independent W-U-D ledger',i,residual)
        assert abs(residual-row['balanceResidualJ'])<1e-11
        for sample in row['samples']:
            stress=(p['E0']+p['E1'])*sample['strain']-p['E1']*sample['viscousStrain']
            assert abs(sample['areaM2']*stress-row['force'])<1e-10
        previous=row['time'];loss=row['dissipationJ']
    return rows

def run(lab):
    lab.locator('[data-action=run]').click()
    expect(lab).to_have_attribute('data-running','false',timeout=30000)
    assert lab.get_attribute('data-phase')=='done',lab.locator('.announce').inner_text()
    result=snapshot(lab);verify_trace(result)
    assert result['state']['time']==2*result['parameters']['ramp']+result['parameters']['hold']+result['parameters']['recovery']
    assert lab.locator('[data-action=step]').is_disabled()
    return result

def row_at(rows,t):
    return min(rows,key=lambda row:abs(row['time']-t))

def check(page,out,full=True):
    lab=page.locator('[data-dissipative]');expect(lab).to_have_count(1)
    lab.locator('[data-action=reset]').click()
    initial=snapshot(lab);verify_trace(initial)
    assert initial['parameters']['E0']==100000 and initial['parameters']['force']==.6
    assert initial['display']['axialDisplacementMagnification']==10 and initial['display']['strainPalette']==[-.05,.05]
    cases={}
    # Loading and both hold histories checked against separate Python exponentials.
    for mode in ['force','extension']:
        lab.locator('[data-action=reset]').click()
        lab.locator('select[data-param=holdMode]').select_option(mode)
        result=run(lab);rows=result['trace'];p=result['parameters']
        at1=row_at(rows,1);at3=row_at(rows,3)
        E0,E1,eta,F=p['E0'],p['E1'],p['eta'],p['force']
        k=E0*E1/(eta*(E0+E1));z1=F/E0*(1+math.expm1(-k)/k);c1=(F+E1*z1)/(E0+E1)
        Cg=sum(sample['dxM']/sample['areaM2'] for sample in at1['samples'])
        assert abs(at1['extensionM']-Cg*c1)<1e-12
        held=[r for r in rows if 1-1e-10<=r['time']<=3+1e-10]
        if mode=='force':
            z3=F/E0+(z1-F/E0)*math.exp(-k*2);c3=(F+E1*z3)/(E0+E1)
            assert all(abs(r['force']-F)<1e-10 for r in held)
            assert at3['extensionM']>at1['extensionM']*1.2
            assert abs(at3['extensionM']-Cg*c3)<1e-12
        else:
            expected=E0*c1+E1*(c1-z1)*math.exp(-E1/eta*2)
            assert max(r['extensionM'] for r in held)-min(r['extensionM'] for r in held)<1e-12, 'Held extension must stay fixed'
            assert at3['force']<at1['force']*.8 and abs(at3['force']-expected)<1e-10
            assert max(r['workJ'] for r in held)-min(r['workJ'] for r in held)<1e-12
        assert {'load','hold','unload','recovery','done'}<=set(r['phase'] for r in rows)
        assert all(abs(r['force'])<1e-12 for r in rows if r['phase'] in ['recovery','done'])
        assert rows[-1]['extensionM']<row_at(rows,4)['extensionM']
        for name,key in [('dissipative-history','force'),('dissipative-history','extensionM'),('dissipative-energy','dissipationJ')]:
            points=lab.locator(f'.{name} [data-series={key}]').get_attribute('points').split()
            assert len(points)==len(rows) and abs(float(points[-1].split(',')[0])-555)<1e-9
        (out/f'{mode}-hold-trace.json').write_text(json.dumps(result,indent=2)+'\n')
        lab.screenshot(path=str(out/f'{mode}-hold-completed.png'))
        cases[mode]=result
    if not full:return cases
    assert cases['force']['trace'][150]['extensionM']>cases['extension']['trace'][150]['extensionM']*1.2
    # SVG cells must actually move by the exported axial displacement.
    lab.locator('[data-action=reset]').click()
    initial_right=lab.locator('.dissipative-scene rect[data-strain]').last.evaluate('(r)=>Number(r.getAttribute("x"))+Number(r.getAttribute("width"))')
    lab.evaluate('(lab)=>{for(let i=0;i<150;i++)lab.querySelector("[data-action=step]").click()}')
    loaded=snapshot(lab);verify_trace(loaded)
    right=lab.locator('.dissipative-scene rect[data-strain]').last.evaluate('(r)=>Number(r.getAttribute("x"))+Number(r.getAttribute("width"))')
    assert abs(right-initial_right-10*1600*loaded['trace'][-1]['extensionM'])<1e-8 and right>initial_right+20
    lab.screenshot(path=str(out/'force-hold-loaded.png'))
    # Empty/out-of-range controls retain actual state and trace; valid edits reset.
    control=lab.locator('input[type=number][data-param=ramp]');control.fill('')
    expect(control).to_have_attribute('aria-invalid','true');invalid=snapshot(lab)
    assert invalid==loaded
    control.fill('3');expect(control).to_have_attribute('aria-invalid','true');assert snapshot(lab)==loaded
    control.fill('.7');changed=snapshot(lab)
    assert changed['parameters']['ramp']==.7 and changed['state']['time']==0 and changed['steps']==0 and changed['samples']==1
    assert changed['state']['z']==changed['state']['workJ']==changed['state']['dissipationJ']==0
    expect(lab.locator('.dissipative-policy')).to_contain_text('new experiment')
    # Elastic branch recovers the passive bar and the independent profile formula.
    elastic=[]
    for count in [8,128]:
        lab.locator('[data-action=reset]').click();lab.locator('select[data-param=E1]').select_option('0')
        lab.locator('select[data-param=segments]').select_option(str(count))
        result=run(lab);rows=result['trace'];p=result['parameters'];exact=p['length']/p['area']*math.log(p['ratio'])/(p['ratio']-1)
        peak=row_at(rows,1)
        assert all(abs(r['dissipationJ'])<1e-15 for r in rows)
        assert abs(peak['exactProfileExtensionM']-p['force']/p['E0']*exact)<1e-12
        assert rows[-1]['extensionM']==0
        elastic.append(abs(peak['profileQuadratureErrorM']))
    assert elastic[1]<elastic[0]/100
    # Reversed stepped profile: the narrower last half strains twice as much.
    lab.locator('[data-action=reset]').click();lab.locator('select[data-param=E1]').select_option('0')
    lab.locator('select[data-param=shape]').select_option('two-segment');lab.locator('input[type=number][data-param=ratio]').fill('.5')
    stepped=run(lab);row=row_at(stepped['trace'],1)
    assert abs(row['samples'][-1]['strain']-2*row['samples'][0]['strain'])<1e-12
    # Viscosity changes creep history, while the force-hold condition stays fixed.
    creep=[]
    for viscosity in ['20000','500000']:
        lab.locator('[data-action=reset]').click();lab.locator('select[data-param=eta]').select_option(viscosity)
        result=run(lab);creep.append(row_at(result['trace'],3)['extensionM'])
    assert creep[0]>creep[1]*1.2
    # A genuine animation-frame boundary exposes exactly one bounded batch.
    lab.locator('[data-action=reset]').click()
    for key,value in [('ramp','2'),('hold','5'),('recovery','5')]:lab.locator(f'input[type=number][data-param={key}]').fill(value)
    lab.locator('select[data-param=dt]').select_option('0.01')
    await_result=lab.evaluate('''async lab=>{const run=lab.querySelector('[data-action=run]');run.click();await new Promise(resolve=>requestAnimationFrame(resolve));run.click();return Number(lab.dataset.step);}''')
    paused=snapshot(lab);assert 0<await_result==paused['steps']<=64
    page.wait_for_timeout(150);assert snapshot(lab)==paused
    resumed=run(lab);assert resumed['steps']==1400 and resumed['samples']==1401
    # Ordinary playback is paced and does not announce every animation frame.
    lab.locator('[data-action=reset]').click();lab.locator('[data-action=play]').click()
    lab.locator('.announce').evaluate('(el)=>{el.changes=0;el.observer=new MutationObserver(rows=>el.changes+=rows.length);el.observer.observe(el,{childList:true,subtree:true,characterData:true});}')
    page.wait_for_timeout(350)
    mutations=lab.locator('.announce').evaluate('(el)=>{el.observer.disconnect();return el.changes;}');assert mutations==0
    lab.locator('[data-action=play]').click();paced=snapshot(lab);assert 0<paced['state']['time']<1.5
    page.wait_for_timeout(120);assert snapshot(lab)==paced
    lab.locator('[data-action=step]').click();assert snapshot(lab)['steps']==paced['steps']+1
    with page.expect_download() as info:lab.locator('[data-action=export]').click()
    info.value.save_as(str(out/'actual-downloaded-trace.json'));verify_trace(json.loads((out/'actual-downloaded-trace.json').read_text()))
    lab.locator('[data-action=summary]').click();expect(lab.locator('.announce')).to_contain_text('Phase:')
    page.set_viewport_size({'width':390,'height':844});lab.locator('[data-action=reset]').click()
    assert not page.evaluate('document.documentElement.scrollWidth>innerWidth+1')
    lab.screenshot(path=str(out/'mobile-default.png'))
    cases.update(loaded=loaded,elasticQuadratureErrors=elastic,viscosityCreep=creep,paused=paused,resumedSteps=resumed['steps'],paced=paced)
    return cases

def displayed_proofs(page,site):
    receipt=site/'dissipative-real-proof-status.json'
    if not receipt.exists():
        assert page.locator('.proof-card').count()==0,'Integrated lesson is missing its SLS proof receipt'
        return None
    record=json.loads(receipt.read_text());source=site/record['source'];mapping=site/'proofs/dissipative-real-claims.json'
    assert record['source_sha256']==hashlib.sha256(source.read_bytes()).hexdigest()==hashlib.sha256((ROOT/record['source']).read_bytes()).hexdigest()
    assert record['claims_sha256']==hashlib.sha256(mapping.read_bytes()).hexdigest()==hashlib.sha256((ROOT/'proofs/dissipative-real-claims.json').read_bytes()).hexdigest()
    assert len(record['claims'])==11
    cards=[]
    normal=lambda text:' '.join(text.split())
    for claim in record['claims']:
        assert claim['status']=='checked' and set(claim['axioms'])<={'propext','Classical.choice','Quot.sound'}
        card=page.locator('#proof-'+claim['id']);expect(card).to_have_count(1)
        text=card.inner_text();statement=card.locator('pre').first.inner_text()
        assert 'theorem '+claim['theorem'].split('.')[-1] in statement
        for key in ['claim','assumptions','limitations','implementation']:assert normal(claim[key]) in normal(text),(claim['id'],key)
        cards.append({'id':claim['id'],'theorem':claim['theorem'],'card_text':text,'card_text_sha256':hashlib.sha256(text.encode()).hexdigest(),'statement_text_sha256':hashlib.sha256(statement.encode()).hexdigest()})
    return {'scope':'Literal displayed claims compared with delivered kernel receipt/source; this browser check does not rerun Lean','receipt_sha256':hashlib.sha256(receipt.read_bytes()).hexdigest(),'source_sha256':record['source_sha256'],'claims_sha256':record['claims_sha256'],'cards':cards}

def qualify(site,out,full=True):
    class Quiet(SimpleHTTPRequestHandler):
        def log_message(self,*args):pass
    server=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(site)))
    Thread(target=server.serve_forever,daemon=True).start()
    try:
      with sync_playwright() as p:
        browser=p.chromium.launch(headless=True,executable_path=os.environ.get('CHROMIUM_EXECUTABLE') or shutil.which('chromium'))
        context=browser.new_context(viewport={'width':1280,'height':1000},reduced_motion='reduce')
        page=context.new_page();page.set_default_timeout(30000);errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
        page.goto(f'http://127.0.0.1:{server.server_port}/index.html',wait_until='networkidle')
        proofs=displayed_proofs(page,site)
        result=check(page,out,full);assert not errors,errors
        version=browser.version;cards=page.locator('.proof-card').count();browser.close()
        return {'status':'PASS','browser_version':version,'observed':result,'javascript_errors':errors,'proof_cards':cards,'proof_evidence':proofs}
    finally:server.shutdown();server.server_close()

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('site',nargs='?',type=Path);parser.add_argument('--output',type=Path,default=ROOT/'.artifacts/dissipative-browser');parser.add_argument('--negative-controls',action='store_true');args=parser.parse_args()
    out=args.output.resolve();out.mkdir(parents=True,exist_ok=True)
    (out/'receipt.json').unlink(missing_ok=True)
    temporary=ROOT/'.browser-tmp';temporary.mkdir(exist_ok=True)
    with TemporaryDirectory(dir=temporary) as temp:
        base=Path(temp);site=args.site.resolve() if args.site else base/'site'
        if args.site is None:build(site)
        inputs={str(p.relative_to(site)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(site.rglob('*')) if p.is_file() and p.suffix in ['.html','.mjs','.js','.css']}
        source_names=['web/dissipative-bar.mjs','web/dissipative-lab.mjs','web/dissipative-lab.css','web/app.mjs','tools/dissipative_lab.py','tools/build_dissipative_preview.py','tests/dissipative_browser.py']
        source_hashes={name:hashlib.sha256((ROOT/name).read_bytes()).hexdigest() for name in source_names}
        result=qualify(site,out);result.update(scope='Actual production SLS controls and model; numerical/browser checks, not Lean or full-book release qualification',delivered_input_sha256=inputs,test_sha256=source_hashes['tests/dissipative_browser.py'],source_input_sha256=source_hashes,source_base_revision=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),worktree_dirty=bool(subprocess.check_output(['git','status','--porcelain'],cwd=ROOT,text=True).strip()),renderer_source_sha256=source_hashes['web/dissipative-lab.mjs'],model_source_sha256=source_hashes['web/dissipative-bar.mjs'],app_source_sha256=source_hashes['web/app.mjs'],app_bundle_sha256=hashlib.sha256((site/'assets/app.js').read_bytes()).hexdigest() if (site/'assets/app.js').exists() else None,build_manifest_sha256=hashlib.sha256((site/'build-manifest.json').read_bytes()).hexdigest() if (site/'build-manifest.json').exists() else None)
        assert all(hashlib.sha256((site/name).read_bytes()).hexdigest()==digest for name,digest in inputs.items()), 'Delivered source changed during browser checks'
        assert all(hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==digest for name,digest in source_hashes.items()), 'Source changed during browser checks'
        result['default_hold_frames']={mode:{'loaded':row_at(result['observed'][mode]['trace'],1),'held':row_at(result['observed'][mode]['trace'],3),'unloaded':row_at(result['observed'][mode]['trace'],4),'final':result['observed'][mode]['trace'][-1]} for mode in ['force','extension']}
        captures=['actual-downloaded-trace.json','force-hold-trace.json','extension-hold-trace.json','force-hold-completed.png','extension-hold-completed.png','force-hold-loaded.png','mobile-default.png']
        result['output_sha256']={name:hashlib.sha256((out/name).read_bytes()).hexdigest() for name in captures}
        if args.negative_controls:
            negatives=[]
            for name,old,new in [('forged-loss','dissipationJ:s.dissipationJ,balanceResidualJ:','dissipationJ:0,balanceResidualJ:'),('lost-extension-hold',"s.phase==='hold'&&p.holdMode==='extension'?extensionSegment",'false?extensionSegment')]:
                copy=base/name;build(copy);module=copy/'web/dissipative-bar.mjs';source=module.read_text();assert source.count(old)==1,(name,'Mutation target changed');module.write_text(source.replace(old,new))
                negative_out=out/'negative-controls'/name;negative_out.mkdir(parents=True,exist_ok=True)
                shutil.copy2(module,negative_out/'delivered-dissipative-bar.mjs')
                try:qualify(copy,negative_out,False)
                except AssertionError as error:negatives.append({'case':name,'detected':True,'reason':str(error),'delivered_module_sha256':hashlib.sha256(module.read_bytes()).hexdigest(),'output_sha256':{str(p.relative_to(out)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(negative_out.rglob('*')) if p.is_file()}})
                else:raise AssertionError('Negative control unexpectedly passed: '+name)
            result['negative_controls']=negatives
        (out/'receipt.json').write_text(json.dumps(result,indent=2)+'\n')
        print('PASS actual dissipative controls at '+str(out))

if __name__=='__main__':main()
