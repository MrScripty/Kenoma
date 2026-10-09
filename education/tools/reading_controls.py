"""Five explicit synthetic lab checks. No proof checker or anatomical imports."""
import json
import shutil
from pathlib import Path
from research_edition import LABS
from qualify_research_edition import near, parameter

def controls(browser, ctx, page, base, out, q, errors, requests):
    checks=[]
    page.goto(base+'labs/lateral-interface-transfer/');page.wait_for_function('window.lateralTransfer')
    page.locator('#rightg-number').fill('0');r=page.evaluate('lateralTransfer.snapshot()');near(r['upperForceN'],0);near(r['rightPullN'],.00005)
    page.locator('#leftg-number').fill('0');r=page.evaluate('lateralTransfer.snapshot()');near(r['rightPullN'],0);near(r['v'],r['delta'])
    page.locator('#reset').click();page.locator('#preset').select_option('unequal');page.locator('#export').click();assert json.loads(page.locator('#state-export').input_value())==page.evaluate('lateralTransfer.snapshot()')
    before=page.evaluate('lateralTransfer.snapshot()');page.locator('#delta-number').fill('');assert page.evaluate('lateralTransfer.snapshot()')==before
    for key,value in [('delta',1.5),('leftg',35),('rightg',45)]:
        field={'delta':'deltaMicrometres','leftg':'leftShearKPa','rightg':'rightShearKPa'}[key]
        page.locator('#'+key+'-number').fill(str(value));near(page.evaluate('lateralTransfer.snapshot().input')[field],value)
        slider=page.locator('#'+key);slider.evaluate('(e,v)=>{e.value=v;e.dispatchEvent(new Event("input",{bubbles:true}))}',value+(.1 if key=='delta' else 1))
        near(page.evaluate('lateralTransfer.snapshot().input')[field],value+(.1 if key=='delta' else 1))
    page.locator('#reset').click();near(page.evaluate('lateralTransfer.snapshot().input.deltaMicrometres'),1)
    checks.append('lateral zero-link branches, unequal preset, rejected blank, reset and actual exported state')
    checks.append('all six lateral numeric/slider controls update the actual admitted state')
    page.goto(base+'labs/directional-compression/');page.wait_for_selector('main[data-ready=true]');default=page.evaluate('labResult');assert default['state']['converged']
    parameter(page,'direction','Z');z=page.evaluate('labResult');near(z['state']['compressionResultantN']/default['state']['compressionResultantN'],1.2);near(z['state']['contactPressurePa'],default['state']['contactPressurePa'])
    parameter(page,'iterations',8);assert not page.evaluate('labResult.state.converged');assert 'FAILED' in page.locator('#readout').inner_text();parameter(page,'iterations',64);assert page.evaluate('labResult.state.converged')
    page.locator('#reset').click();parameter(page,'axialStretch',1.2);parameter(page,'heightStretch',1);assert page.evaluate('labResult.state.requiresTensileGrip')
    with page.expect_download() as d:page.locator('#export').click()
    d.value.save_as(q/'directional-displayed-state.json');assert json.loads((q/'directional-displayed-state.json').read_text())==page.evaluate('labResult')
    checks.append('direction permutation, actual failed/recovered residual, tensile grip and exact displayed download')
    page.locator('#reset').click()
    for key,value in [('axialStretch',.9),('heightStretch',.65),('mu',3500),('bulk',250000),('iterations',32)]:
        parameter(page,key,value);near(page.evaluate('labResult.parameters')[key],value)
    parameter(page,'iterations',64);assert page.evaluate('labResult.state.converged')
    before=page.evaluate('labResult');parameter(page,'heightStretch','');assert page.evaluate('labResult')==before
    parameter(page,'heightStretch',.4);assert page.evaluate('labResult')==before
    # Check the actual projected polygon vertices at a large free stretch.
    page.locator('#reset').click();parameter(page,'direction','Z');parameter(page,'heightStretch',.5);parameter(page,'bulk',250000)
    assert page.evaluate('''()=>{const s=document.querySelector('#scene svg'),v=s.viewBox.baseVal;
        return [...s.querySelectorAll('polygon')].every(p=>[...p.points].every(a=>a.x>=v.x&&a.x<=v.x+v.width&&a.y>=v.y&&a.y<=v.y+v.height));}''')
    checks.append('all directional controls, 32/64 caps, blank/domain rollback and extreme-shape vertices')
    page.goto(base+'labs/full-face-load-pressure/');page.wait_for_selector('main[data-ready=true]');default=page.evaluate('labResult');assert default['solve']['converged']
    parameter(page,'breadthFactor',2);wide=page.evaluate('labResult');near(wide['state']['compressionResultantN'],default['state']['compressionResultantN']);assert abs(wide['state']['stretches'][1]-default['state']['stretches'][1])>.01
    page.locator('#reset').click();parameter(page,'mode','pressure');one=page.evaluate('labResult');parameter(page,'breadthFactor',2);two=page.evaluate('labResult')
    for a,b in zip(one['state']['stretches'],two['state']['stretches']):near(a,b)
    near(two['state']['compressionResultantN'],2*one['state']['compressionResultantN']);near(two['state']['energyJ'],2*one['state']['energyJ'])
    parameter(page,'outerIterations',8);assert not page.evaluate('labResult.solve.converged');parameter(page,'outerIterations',64);assert page.evaluate('labResult.solve.converged')
    page.locator('#reset').click();before=page.evaluate('labResult');parameter(page,'forceN',100);assert page.evaluate('labResult')==before;assert 'not bracketed' in page.locator('#status').inner_text();page.locator('#reset').click()
    with page.expect_download() as d:page.locator('#export').click()
    d.value.save_as(q/'full-face-displayed-state.json');assert json.loads((q/'full-face-displayed-state.json').read_text())==page.evaluate('labResult')
    checks.append('fixed-force deformation and fixed-pressure area/material scaling; inverse failure, recovery, rejection and real export')
    for key,value in [('forceN',8),('axialStretch',1.1),('mu',2500),('bulk',75000),('direction','Z'),('breadthFactor',1.5),('outerIterations',32)]:
        parameter(page,key,value);assert page.evaluate('labResult.parameters')[key]==value
    parameter(page,'mode','pressure');parameter(page,'pressurePa',1800);near(page.evaluate('labResult.parameters.pressurePa'),1800)
    parameter(page,'outerIterations',64);assert page.evaluate('labResult.solve.converged')
    before=page.evaluate('labResult');parameter(page,'pressurePa','');assert page.evaluate('labResult')==before
    parameter(page,'breadthFactor',.4);assert page.evaluate('labResult')==before
    page.locator('#reset').click();assert page.evaluate('labResult.parameters')==default['parameters']
    checks.append('all full-face controls, material parameters, target modes, 32/64 caps and blank/domain rollback')
    # Check every enabled control at actual viewport sizes; no hidden root clipping.
    for width in [1280,393,320]:
        page.set_viewport_size({'width':width,'height':900})
        for slug in LABS:
            page.goto(base+'labs/'+slug+'/');page.wait_for_timeout(120)
            assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1'),(width,slug)
            if slug!='lateral-interface-transfer':page.wait_for_selector('main[data-ready=true]');assert page.evaluate('[...document.querySelectorAll("[data-param]")].filter(x=>!x.disabled).every(x=>x.checkValidity())')
            page.screenshot(path=str(q/f'{slug}-{width}.jpg'),type='jpeg',quality=85)
    static_ctx=browser.new_context(java_script_enabled=False);static=static_ctx.new_page()
    for width in [1280,393,320]:
        static.set_viewport_size({'width':width,'height':900})
        for name in ['index.html','book.html','additions.html']:
            static.goto(base+name,wait_until='networkidle');assert static.evaluate('document.documentElement.scrollWidth<=innerWidth+1'),(width,name)
            assert static.locator('img').evaluate_all('(xs)=>xs.every(x=>x.complete&&x.naturalWidth>0)')
            static.screenshot(path=str(q/f'{Path(name).stem}-{width}.jpg'),type='jpeg',quality=85)
    for slug in LABS:
        static.goto(base+'labs/'+slug+'/');assert static.locator('noscript').count()>0
        if slug!='lateral-interface-transfer':assert 'Default J' in static.locator('#readout').inner_text();assert 'theorem force_area_work' in static.locator('.proof-source').inner_text()
    checks.append('all new laboratories and complete reader at desktop/393/320; no-JavaScript defaults, figures and complete source')
    # Two real copied runtime defects are refused before model initialization.
    for slug in ['directional-compression','full-face-load-pressure']:
        damage=q/('damage-'+slug);shutil.copytree(out/'labs'/slug,damage);g=LABS[slug];f=damage/'education/contributions'/g/'model.mjs';f.write_text(f.read_text()+'\n// actual copied source damage\n')
        t=ctx.new_page();t.goto(base+'qualification/'+damage.name+'/');t.wait_for_function('document.querySelector("#status").textContent.includes("refused")');assert t.locator('#export').is_disabled();assert t.locator('main').get_attribute('data-ready') is None;t.close()
    checks.append('actual changed runtime source copies refused before import')
    # The accepted prior controls are referenced from exact preserved assets.
    page.goto(base+'preview/nonuniform/nonuniform-volume-lab.html');state=page.evaluate('KinematicLab.state()');page.locator('#compensate').uncheck();page.locator('#compensate').dispatch_event('input');off=page.evaluate('KinematicLab.state()');near(off['pointwiseJRange'][0],.6);near(off['pointwiseJRange'][1],1.4)
    page.goto(base+'preview/architecture-force/index.html');page.locator('#angle').fill('60');page.locator('#angle').dispatch_event('input');assert '12.00 N' in page.locator('#readout').inner_text()
    checks.append('retained accepted nonuniform and architecture controls still demonstrate their descriptions')
    assert not errors,errors;assert not requests,requests

    return checks
