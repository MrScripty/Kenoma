"""Reviewable property lessons without advertising uncompiled proof claims.

The main book integration waits for the separate fresh real-proof checker.
"""
from pathlib import Path
import hashlib,json,re,shutil,subprocess,sys
from property_labs import block
ROOT=Path(__file__).resolve().parents[1]
def build(destination):
    out=Path(destination).resolve();out.mkdir(parents=True,exist_ok=True)
    chapter=(ROOT/'book/chapters/09a-properties.md').read_text()
    chapter=re.sub(r'\{\{property:(\w+)\}\}',lambda m:block(m[1],True),chapter)
    claims={c['id']:c for c in json.loads((ROOT/'proofs/property-claims.json').read_text())}
    def pending(match):
        c=claims[match[1]]
        return '\n**Proposed exact claim '+match[1]+' (not yet kernel-qualified in this preview):** '+c['claim']+'\n\n**Assumptions:** '+c['assumptions']+'\n\n**Limits:** '+c['limitations']+'\n'
    chapter=re.sub(r'\{\{proof:([\w-]+)\}\}',pending,chapter)
    # The source itself marks proposed declarations as pending; no proof status is inferred.
    source=out/'lessons.md';source.write_text(chapter)
    subprocess.run(['pandoc',str(source),'--standalone','--mathml','--metadata','title=Kenoma property laboratories','--css','assets/style.css','-o',str(out/'index.html')],check=True)
    index=out/'index.html';index.write_text(index.read_text().replace('</body>','<script type="module" src="web/property-labs.mjs"></script></body>'))
    (out/'web').mkdir(exist_ok=True);(out/'assets').mkdir(exist_ok=True)
    for name in ['continuum-properties.mjs','tapered-bar.mjs','property-labs.mjs']:shutil.copy(ROOT/'web'/name,out/'web'/name)
    shutil.copy(ROOT/'web/style.css',out/'assets/style.css')
    subprocess.run(['node','tools/property-experiment.mjs',str(out/'assets'),str(out/'experiment.json')],cwd=ROOT,check=True)
    files=['web/continuum-properties.mjs','web/tapered-bar.mjs','web/property-labs.mjs','web/style.css','tools/property_labs.py','tools/property-experiment.mjs','tools/build_property_preview.py','tools/build_property_mathlib.py','tools/check_property_proofs.py','tests/property_browser.py','tests/continuum_properties.test.mjs','tests/tapered_bar.test.mjs','book/chapters/09a-properties.md','proofs/ContinuumProperties.lean','proofs/property-claims.json','proofs/mathlib-lock.json']
    receipt={'schema':1,'kind':'independent-property-preview','proof_status':'pending fresh kernel check; no checked proof cards','input_sha256':{p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in files},'git_base':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()}
    (out/'preview-manifest.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print('Built three independent property lessons at '+str(out))
if __name__=='__main__':build(sys.argv[1] if len(sys.argv)>1 else ROOT/'dist/property-preview')
