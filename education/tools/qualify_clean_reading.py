#!/usr/bin/env python3
"""Qualify the edited public payload; all review receipts stay private.

Reuses the already reviewed bounded synthetic controller checks. No anatomy,
proof checker, contribution builder, public network request or cap change.
"""
import argparse
from functools import partial
from http.server import SimpleHTTPRequestHandler,ThreadingHTTPServer
import json
from pathlib import Path
import re
import shutil
import subprocess
from threading import Thread
from urllib.parse import urlsplit,unquote

import fitz
from PIL import Image,ImageDraw
from playwright.sync_api import sync_playwright
from clean_reading_edition import scan_public,COORDINATION,PRIVATE,ROOT,REPO,BASE,RESEARCH,LABS,doc,SCOPE,markdown_html,outside,sha,git,write_json
from qualify_research_edition import Links,near,parameter,minimum

def closure(public):
    count=0;findings=[]
    for p in sorted(public.rglob('*')):
        if not p.is_file() or p.suffix not in {'.html','.md'}:continue
        reader=Links(p.read_text() if p.suffix=='.html' else markdown_html(p.read_text()))
        for href in reader.urls:
            u=urlsplit(href)
            if u.scheme:continue
            target=(p.parent/unquote(u.path)).resolve() if u.path else p
            if not target.is_relative_to(public):raise ValueError('Escaping reading payload: '+href)
            if not target.is_file():findings.append((str(p.relative_to(public)),href));continue
            if u.fragment and target.suffix=='.html' and u.fragment not in Links(target.read_text()).ids:findings.append((str(p.relative_to(public)),href))
            count+=1
    if findings:raise ValueError(json.dumps(findings))
    return count

def pdf_links(page):
    companions={
        'preview/nonuniform/nonuniform-volume-lab.html':(BASE,'education/contributions/nonuniform-isochoric-kinematics/index.template.html'),
        'preview/architecture-force/index.html':(BASE,'education/contributions/architecture-force/index.html'),
        'labs/lateral-interface-transfer/index.html':(RESEARCH,'education/contributions/lateral-interface-transfer/index.html'),
        'labs/directional-compression/index.html':(RESEARCH,'education/contributions/directional-compression-lab/app.mjs'),
        'labs/full-face-load-pressure/index.html':(RESEARCH,'education/contributions/full-face-load-pressure/app.mjs')}
    mapping={};sources=[]
    for href in page.locator('a[href]').evaluate_all('(xs)=>xs.map(x=>x.getAttribute("href"))'):
        if href.startswith(('http:','https:','mailto:','#')):continue
        key=href.split('#')[0]
        if key in companions:
            ref,path=companions[key];git('cat-file','-e',ref+':'+path);destination='https://github.com/MrScripty/Kenoma/blob/'+ref+'/'+path;sources.append(destination)
        elif key.startswith('sources/'):
            path='education/'+key.removeprefix('sources/');git('cat-file','-e',RESEARCH+':'+path);destination='https://github.com/MrScripty/Kenoma/blob/'+RESEARCH+'/'+path
        elif key.startswith('preview/proofs/'):
            path='education/'+key.removeprefix('preview/');git('cat-file','-e',BASE+':'+path);destination='https://github.com/MrScripty/Kenoma/blob/'+BASE+'/'+path
        else:destination='#research-edition-scope'
        mapping[href]=destination
    page.evaluate('''(targets)=>{for(const a of document.querySelectorAll('a[href]')){const h=a.getAttribute('href');if(targets[h]){a.setAttribute('href',targets[h]);if(h.includes('nonuniform-volume-lab.html')||h.includes('architecture-force/index.html')||h.startsWith('labs/')&&h.endsWith('index.html'))a.textContent='Companion scientific source';}}}''',mapping)
    return sources

def qualify(manifest,public,private,*,inputs,browser_executable=None):
    m=inputs;public,private=outside(public),outside(private);q=private/'qualification';q.mkdir(exist_ok=False)
    write_json(q/'preflight-public-scan.json',scan_public(public));prefix='/Kenoma/reading-edition/'
    class Mount(SimpleHTTPRequestHandler):
        def log_message(self,*args):pass
        def translate_path(self,path):
            if not path.startswith(prefix):return '/nonexistent-reading-review'
            relative=unquote(urlsplit(path).path[len(prefix):])
            if relative.startswith('qualification/'):
                target=(q/relative.removeprefix('qualification/')).resolve()
                return str(target) if target.is_relative_to(q) else '/nonexistent-reading-review'
            return super().translate_path('/'+path[len(prefix):])
    # Socket/browser failure is reported, never retried with sandbox bypass.
    server=ThreadingHTTPServer(('127.0.0.1',0),partial(Mount,directory=str(public)));Thread(target=server.serve_forever,daemon=True).start();base=f'http://127.0.0.1:{server.server_port}'+prefix;errors=[];requests=[];checks=[];out=public
    try:
        with sync_playwright() as p:
            browser=p.chromium.launch(headless=True,executable_path=browser_executable or shutil.which('chromium'));ctx=browser.new_context(accept_downloads=True);page=ctx.new_page()
            page.on('pageerror',lambda e:errors.append(str(e)));page.on('request',lambda r:requests.append(r.url) if not r.url.startswith(base) and not r.url.startswith('blob:') else None)
            from reading_controls import controls
            checks=controls(browser,ctx,page,base,out,q,errors,requests)
            # PDF is derived only after public cleanup and runtime inventory regeneration.
            static_ctx=browser.new_context(java_script_enabled=False);static=static_ctx.new_page()
            static.goto(base+'additions.html',wait_until='networkidle');static.emulate_media(media='print');static.set_viewport_size({'width':658,'height':1123});companion_sources=pdf_links(static)
            layout=static.evaluate(git('show',BASE+':education/tools/print_layout.js').decode())
            static.pdf(path=str(public/'research-additions.pdf'),format='A4',margin={'top':'16mm','bottom':'16mm','left':'16mm','right':'16mm'},print_background=True,tagged=True,outline=True)
            cover_path=public/'reading-scope-cover.html';cover_path.write_text(doc('Kenoma: edited reading scope',markdown_html(SCOPE)).replace('LOCAL CANDIDATE','READING EDITION · BUNDLED COMPANIONS').replace('qualification.json','edition-status.json'))
            static.goto(base+'reading-scope-cover.html');pdf_links(static);static.pdf(path=str(q/'reading-scope-cover.pdf'),format='A4',margin={'top':'16mm','bottom':'16mm','left':'16mm','right':'16mm'},print_background=True,tagged=True);version=browser.version;browser.close()
    finally:server.shutdown();server.server_close()
    additions=fitz.open(public/'research-additions.pdf');history=fitz.open(public/'historical/kenoma-mechanics-reading.pdf');original=fitz.open(private/'unchanged-historical-original/kenoma-mechanics.pdf');cover=fitz.open(q/'reading-scope-cover.pdf');combined=fitz.open();combined.insert_pdf(cover);combined.insert_pdf(history);combined.insert_pdf(additions)
    combined.set_metadata({'title':'Kenoma: complete edited reading edition','subject':'25 historical chapters and six additions; source-only formal scope; anatomical execution held'});combined.save(public/'kenoma-research-edition.pdf',garbage=4,deflate=True)
    bad=[]
    for n,page in enumerate(additions):
        for b in page.get_text('dict')['blocks']:
            for line in b.get('lines',[]):
                for s in line['spans']:
                    if not s['text'].strip():continue
                    x0,y0,x1,y1=s['bbox']
                    if x0< -1 or y0< -1 or x1>page.rect.width+1 or y1>page.rect.height+1:bad.append({'page':n+1,'text':s['text'],'bbox':s['bbox']})
                    assert '\ufffd' not in s['text']
    assert not bad,bad;assert minimum(additions)>=9.98;assert len(history)==208
    edits=json.loads((private/'historical-pdf-edits.json').read_text());changed={x['original_page']-1 for x in edits}
    for i in range(208):
        if i not in changed:assert history[i].get_text()==original[i].get_text(),i
    for i in [0,100,207]:assert history[i].get_pixmap().samples==original[i].get_pixmap().samples,i
    assert 'This worker verified' not in ''.join(x.get_text() for x in history)
    text=''.join(x.get_text() for x in additions);normalize=lambda x:re.sub(r'\s+','',x)
    for group,name in [('lateral-interface-transfer','LateralInterfaceTransfer.lean'),('directional-compression-lab','AreaLoadContracts.lean')]:assert normalize((ROOT/'contributions'/group/name).read_text()) in normalize(text)
    uris={x.get('uri') for page in additions for x in page.get_links()}
    for source in set(companion_sources):assert source in uris,source
    assert len(set(companion_sources))==5,companion_sources
    for page in combined:
        for link in page.get_links():assert not PRIVATE.search(link.get('uri',''))
    sheets=[]
    for start in range(0,len(additions),16):
        sheet=Image.new('RGB',(1200,1760),'#b6c4bf');draw=ImageDraw.Draw(sheet)
        for i in range(start,min(start+16,len(additions))):
            pix=additions[i].get_pixmap(matrix=fitz.Matrix(.45,.45),alpha=False);im=Image.frombytes('RGB',[pix.width,pix.height],pix.samples);im.thumbnail((282,405));x=((i-start)%4)*300;y=((i-start)//4)*440;sheet.paste(im,(x+9,y+25));draw.text((x+9,y+5),str(i+1),fill='black')
        name=f'addition-pages-{start+1}-{min(start+16,len(additions))}.jpg';sheet.save(q/name,quality=85);sheets.append(name)
    local_links=closure(public);scan=scan_public(public)
    status=json.loads((public/'edition-status.json').read_text());status.update(pdf_pages=len(combined),additions_pdf_pages=len(additions),local_link_checks=local_links,public_payload_scan='PASS',controls_and_no_javascript='PASS',print_checks='PASS',new_lean_sources_complete_in_pdf=True);write_json(public/'edition-status.json',status)
    # Public and private inventories are separate, and regenerated after all edits.
    write_json(public/'reading-manifest.json',{'kind':'EDITED_PUBLIC_READING_PAYLOAD','candidate_commit':m['candidate_commit'],'candidate_tree':m['candidate_tree'],'files':{str(f.relative_to(public)):sha(f.read_bytes()) for f in sorted(public.rglob('*')) if f.is_file() and f.name!='reading-manifest.json'}})
    result={'kind':'PRIVATE_CLEAN_READING_QUALIFICATION','candidate_commit':m['candidate_commit'],'candidate_tree':m['candidate_tree'],'input_manifest_sha256':sha(Path(manifest).read_bytes()),'historical_pdf_original_sha256':sha((private/'unchanged-historical-original/kenoma-mechanics.pdf').read_bytes()),'historical_reading_pdf_sha256':sha((public/'historical/kenoma-mechanics-reading.pdf').read_bytes()),'historical_page_text_unchanged':208-len(changed),'historical_editorial_changes':edits,'pdf_pages':len(combined),'addition_pages':len(additions),'minimum_new_text_pt':minimum(additions),'out_of_page_spans':bad,'companion_source_annotations':sorted(set(companion_sources)),'companions_online':'HOSTED_AVAILABILITY_UNVERIFIED','print_layout':layout,'controls':checks,'browser_version':version,'local_links_checked':local_links,'public_scan':scan,'external_links':('Network reachability UNRUN; own-source Git objects checked' if inputs is not None else 'Prior 104 reachable / 57 tunnel-blocked observations retained; zero new requests'),'agent_visual_review':'UNRUN','human_editorial_review':('UNRUN_INFORMATIONAL' if inputs is not None else 'UNRUN'),'proof_compilation':'UNRUN','anatomical_execution':'HELD_UNRUN','held_campaigns_executed':False,'cap_changes':False,'publication':('NOT_EXECUTED' if inputs is not None else 'NOT_AUTHORIZED'),'addition_review_sheets':sheets}
    write_json(private/'qualification.json',result);print(json.dumps(result))
