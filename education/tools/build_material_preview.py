"""Freshly compiled, source-bound material lesson; no whole-book release claim."""
from pathlib import Path
import argparse,hashlib,html,json,re,shutil,subprocess
from check_material_proofs import check
from material_lab import block
ROOT=Path(__file__).resolve().parents[1]

def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def build(destination):
    out=Path(destination).resolve()
    if out.exists():raise FileExistsError('Choose a fresh output directory')
    out.mkdir(parents=True)
    receipt=check(out)
    checked=(ROOT/receipt['source']).read_text()
    claims={c['id']:c for c in receipt['claims']}
    def proof(match,web):
        c=claims[match[1]];name=c['theorem'].split('.')[-1]
        statement=re.search(r'theorem '+re.escape(name)+r'\b(.*?) := by',checked,re.S)
        if not statement:raise RuntimeError('Missing theorem statement')
        stmt='theorem '+name+statement[1]
        meta=f"Lean 4.19.0; bundled Std; exact scaled integers; transitive axioms: {', '.join(c['axioms']) or 'none'}; source SHA-256: {receipt['source_sha256']}"
        fence=chr(96)*3
        if not web:return f"\n**Freshly checked claim {c['id']}:** {c['claim']}\n\n**Assumptions:** {c['assumptions']}\n\n{fence}lean\n{stmt}\n{fence}\n\n**Limits:** {c['limitations']}\n\n{meta}. [Full source]({receipt['source']}); [receipt](material-proof-status.json).\n"
        e=html.escape
        return f'\n<aside class="proof-card" id="proof-{c["id"]}"><h3>Freshly checked claim · {e(c["id"])}</h3><p>{e(c["claim"])}</p><p><strong>Assumptions:</strong> {e(c["assumptions"])}</p><pre><code>{e(stmt)}</code></pre><p><strong>Limits:</strong> {e(c["limitations"])}</p><p class="proof-meta">{e(meta)}</p><p><strong>Implementation:</strong> {e(c["implementation"])}</p><p><a href="{receipt["source"]}">Full source</a> · <a href="material-proof-status.json">Fresh receipt</a> · <a href="material-lean-check.txt">Kernel report</a></p></aside>\n'
    chapter=(ROOT/'book/chapters/09b-material-response.md').read_text()
    # Neighboring chapters are outside this standalone lesson, explicitly linked
    # to the published book. No historical proof cards enter this preview.
    chapter=re.sub(r'\]\(#([^)]*)\)',r'](https://mrscripty.github.io/Kenoma/#\1)',chapter)
    note='Independent material-response review. This lesson and its five Std contracts are executed freshly; this is not a rebuilt or qualified full-book release.'
    fence=chr(96)*3
    appendix='\n\n# Complete checked material source {#material-source-appendix}\n\n'+fence+'lean\n'+checked+'\n'+fence+'\n\n## Fresh proof receipt {#material-proof-receipt}\n\n'+fence+'json\n'+json.dumps(receipt,indent=2)+'\n'+fence+'\n\n## Kernel report {#material-kernel-report}\n\n'+fence+'text\n'+(out/'material-lean-check.txt').read_text()+'\n'+fence+'\n'
    def expand(web):
        text=chapter.replace('{{property:material}}',block(web))
        text=re.sub(r'\{\{proof:([\w-]+)\}\}',lambda m:proof(m,web),text)
        if '{{' in text:raise RuntimeError('Unexpanded directive')
        return '> '+note+'\n\n'+text+appendix
    (out/'material-response.md').write_text(expand(False))
    staging=out/'staging.md';staging.write_text(expand(True))
    template=(ROOT/'web/template.html').read_text().replace('kenoma-mechanics.md','material-response.md').replace('kenoma-mechanics.pdf','material-response.pdf').replace('proof-status.json','material-proof-status.json').replace('experiment.json','material-experiment.json').replace('Markdown book','Markdown lesson').replace('Foundation milestone 1','Independent material review; not a full-book release')
    template_path=out/'preview-template.html';template_path.write_text(template)
    result=subprocess.run(['pandoc',str(staging),'--standalone','--mathml','--toc','--toc-depth=2','--metadata','title=Kenoma material-response review','--metadata','subtitle=Fresh reduced equilibrium, browser controls and narrow Std contracts','--template',str(template_path),'-o',str(out/'index.html')],capture_output=True,text=True,check=True)
    if 'Could not convert TeX math' in result.stderr:raise RuntimeError(result.stderr)
    staging.unlink()
    template_path.unlink()
    rendered=(out/'index.html').read_text()
    rendered=re.sub(r'<math display="block".*?</math>',lambda m:'<div class="equation" tabindex="0" aria-label="Scrollable displayed equation">'+m[0]+'</div>',rendered,flags=re.S)
    (out/'index.html').write_text(rendered)
    (out/'web').mkdir();(out/'proofs').mkdir();(out/'assets').mkdir()
    for name in ['material-response.mjs','material-lab.mjs','tissue.mjs']:shutil.copy(ROOT/'web'/name,out/'web'/name)
    for name in ['MaterialResponse.lean','material-claims.json','lean-toolchain']:shutil.copy(ROOT/'proofs'/name,out/'proofs'/name)
    shutil.copy(ROOT/'web/style.css',out/'assets/style.css')
    subprocess.run([str(ROOT/'node_modules/.bin/esbuild'),str(ROOT/'web/app.mjs'),'--bundle','--minify','--format=esm','--target=es2022',f'--outfile={out/"assets/app.js"}','--legal-comments=external'],check=True)
    shutil.copy(ROOT.parent/'LICENSE',out/'LICENSE')
    (out/'THIRD_PARTY_NOTICES.txt').write_text('Kenoma authored content: Apache-2.0. Three.js 0.180.0 (MIT) in the production app bundle:\n'+(ROOT/'node_modules/three/LICENSE').read_text())
    subprocess.run(['node',str(ROOT/'tools/material-experiment.mjs'),str(out/'assets'),str(out/'material-experiment.json')],cwd=ROOT,check=True)
    files=['book/book.json','book/chapters/00-scope.md','book/chapters/04-research-path.md','book/chapters/09a-properties.md','book/chapters/09b-material-response.md','book/chapters/13-coverage.md',
           'proofs/MaterialResponse.lean','proofs/material-claims.json','proofs/lean-toolchain','web/material-response.mjs','web/material-lab.mjs','web/tissue.mjs','web/style.css','web/app.mjs','web/template.html','package-lock.json',
           'tools/material_lab.py','tools/build_material_preview.py','tools/material-experiment.mjs','tools/check_material_proofs.py','tools/check_material_artifact.py','tools/build.py','tools/property_labs.py','tools/render_pdf.py',
           'tests/material_response.test.mjs','tests/material_browser.py','tests/artifacts.py','tests/property_browser.py']
    manifest={'schema':1,'kind':'fresh-independent-material-review','scope':note,'proof_cards':len(claims),'proof_receipt':'material-proof-status.json',
              'source_base_revision':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
              'worktree_dirty':bool(subprocess.check_output(['git','status','--porcelain'],cwd=ROOT,text=True).strip()),
              'input_sha256':{p:digest(ROOT/p) for p in files},'output_sha256':{p:digest(out/p) for p in ['index.html','material-response.md','material-experiment.json','material-proof-status.json','material-lean-check.txt','assets/property-material.svg','assets/app.js']}}
    (out/'material-preview-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print('Built freshly checked material lesson at '+str(out))

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('out',type=Path);build(parser.parse_args().out)
