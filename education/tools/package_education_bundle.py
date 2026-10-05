"""Package a checked immutable book build; preserve every linked local resource."""
from pathlib import Path
import hashlib,json,re,sys,zipfile
from html.parser import HTMLParser
from urllib.parse import unquote,urlsplit
import fitz
ROOT=Path(__file__).resolve().parents[1]
FAMILIES=[('proof-status.json','Mechanics.lean','claims.json',12),('transfer-proof-status.json','AnatomicalTransfer.lean','anatomical-claims.json',2),('coupled-proof-status.json','CoupledMechanics.lean','coupled-claims.json',7),('arm-proof-status.json','AnatomicalArm.lean','arm-claims.json',4),('property-proof-status.json','ContinuumProperties.lean','property-claims.json',4)]
def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def require(condition,message):
    if not condition:raise RuntimeError(message)
def validate_build(out,manifest):
    require(bool(manifest.get('input_sha256')),'Empty build inputs')
    for relative,value in manifest['input_sha256'].items():
        require(digest(ROOT/relative)==value,'Build input changed: '+relative)
    def local(relative):
        path=(out/relative).resolve()
        require(path.is_relative_to(out.resolve()) and path.is_file(),'Missing/invalid bundle resource: '+relative)
        return path
    def read(relative):return json.loads(local(relative).read_text())
    for name in ['index.html','kenoma-mechanics.md','kenoma-mechanics.pdf','assets/app.js','anatomical-arm/worker.js','coupled-fixture/worker.js']:local(name)
    require(manifest.get('proof_families')==[r[0] for r in FAMILIES],'Unexpected proof families')
    for name,source,claims,count in FAMILIES:
        receipt=read(name);expected=json.loads((ROOT/'proofs'/claims).read_text())
        require(len(expected)==count and len(receipt.get('claims',[]))==count,'Missing expected proof coverage: '+name)
        require(receipt.get('source')=='proofs/'+source,'Wrong proof source identity: '+name)
        require(receipt.get('source_sha256')==digest(ROOT/'proofs'/source),'Wrong proof source hash: '+name)
        require(receipt.get('claims_sha256')==digest(ROOT/'proofs'/claims),'Wrong proof map hash: '+name)
        require(receipt.get('lean_version')==manifest.get('lean'),'Wrong proof toolchain: '+name)
        require(digest(local('proofs/'+source))==receipt['source_sha256'],'Bundled proof source differs: '+source)
        require(digest(local('proofs/'+claims))==receipt['claims_sha256'],'Bundled proof map differs: '+claims)
        for actual,claim in zip(receipt['claims'],expected):
            require(all(actual.get(k)==v for k,v in claim.items()),'Wrong proof identity/statement: '+name)
            require(actual.get('status')=='checked' and isinstance(actual.get('axioms'),list) and set(actual['axioms'])<={'propext','Quot.sound','Classical.choice'},'Unqualified proof: '+name)
    lock=json.loads((ROOT/'proofs/mathlib-lock.json').read_text())
    require(read('property-proof-status.json').get('mathlib')==lock==manifest.get('property_mathlib'),'Wrong pinned mathlib identity')
    require(digest(local('proofs/mathlib-lake-manifest.json'))==lock['manifest_sha256'],'Wrong bundled dependency manifest')
    html=digest(local('index.html'));app=digest(local('assets/app.js'));manifest_hash=digest(local('build-manifest.json'))
    for name in ['browser-check.json','mobile-startup-check.json']:
        receipt=read(name);require(receipt.get('status')=='passed','Missing successful check: '+name)
        require(receipt.get('html_sha256')==html and receipt.get('app_sha256')==app,'Stale checked browser outputs: '+name)
    property_check=read('qa/property-browser-check.json')
    require(property_check.get('result')=='PASS_INTEGRATED_PROPERTY_LABS' and property_check.get('proof_cards')==29,'Missing property/proof browser coverage')
    require(property_check.get('html_sha256')==html and property_check.get('app_sha256')==app and property_check.get('manifest_sha256')==manifest_hash,'Stale property browser outputs')
    render=read('property-book-review/render-receipt.json')
    require(render.get('result')=='PASS_PROPERTY_BOOK_RENDER_CAPTURE' and not render.get('page_errors'),'Missing successful render capture')
    require(render.get('html_sha256')==html and render.get('pdf_sha256')==digest(local('kenoma-mechanics.pdf')) and render.get('build_manifest_sha256')==manifest_hash,'Stale render outputs')
    require(render.get('inspector_sha256')==digest(ROOT/'tools/inspect_property_integration.py'),'Stale render inspector')
    views=render.get('views',[]);require(len(views)==2 and {v.get('name') for v in views}=={'desktop','mobile'} and all(v.get('proofCards')==29 and v.get('horizontalOverflow') is False for v in views),'Missing desktop/mobile render coverage')
    pages=render.get('pdf_pages',[]);require(bool(pages),'Empty rendered PDF coverage')
    for phrase in ['Property lab 1','Property lab 2','Property lab 3']:require(any(phrase in p.get('phrases',[]) for p in pages),'Missing rendered '+phrase)
    expected_images={v+'-'+claim+'.png' for v in ['desktop','mobile'] for claim in ['volume-edge-translation','volume-det-compose','volume-diagonal','volume-isochoric-sqrt']}|{p['image'] for p in pages}
    require(set(render.get('outputs',{}))==expected_images,'Unexpected/missing fresh render outputs')
    for name,value in render['outputs'].items():require(digest(local('property-book-review/'+name))==value,'Changed render image: '+name)
    artifact=read('artifact-check.json');require(artifact.get('status')=='passed' and artifact.get('proof_cards')==29,'Missing successful artifact/proof check')
    with fitz.open(local('kenoma-mechanics.pdf')) as pdf:require(len(pdf)==artifact.get('pdf_pages') and len(pdf)>0,'Incomplete checked PDF')
    class Links(HTMLParser):
        def __init__(self):super().__init__();self.urls=[]
        def handle_starttag(self,tag,attrs):self.urls.extend(value for key,value in attrs if key in ['href','src'] and value)
    def linked(source,value):
        parsed=urlsplit(value)
        if parsed.scheme or parsed.netloc or not parsed.path:return None
        target=(source.parent/unquote(parsed.path)).resolve()
        if target.is_dir():target=target/'index.html'
        require(target.is_relative_to(out.resolve()) and target.is_file(),'Missing linked resource in '+str(source.relative_to(out))+': '+value)
        return target
    # Archived authoring templates are source evidence, not generated pages.
    # Check every generated entry page and follow its complete local link graph.
    queue=[p.resolve() for p in out.rglob('*.html') if p.relative_to(out).parts[0] not in ['web','data','proofs','contributions']];visited=set()
    while queue:
        source=queue.pop()
        if source in visited:continue
        visited.add(source)
        if source.suffix=='.html':
            parser=Links();parser.feed(source.read_text());urls=parser.urls
        elif source.suffix=='.css':urls=re.findall(r'''url\(\s*['"]?([^)'"\s]+)['"]?\s*\)''',source.read_text())
        else:continue
        for value in urls:
            target=linked(source,value)
            if target is not None and target.suffix in ['.html','.css']:queue.append(target)
def package(destination):
    out=ROOT/'dist';manifest=json.loads((out/'build-manifest.json').read_text())
    validate_build(out,manifest)
    target=Path(destination).resolve();target.parent.mkdir(parents=True,exist_ok=True)
    excluded={target,target.with_suffix('.json')}
    files=[p for p in sorted(out.rglob('*')) if p.is_file() and p.resolve() not in excluded and '__pycache__' not in str(p)]
    file_hashes={str(p.relative_to(out)):digest(p) for p in files}
    with zipfile.ZipFile(target,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as archive:
        for source in files:archive.write(source,str(source.relative_to(out)))
    with zipfile.ZipFile(target) as archive:
        if archive.testzip() is not None:raise RuntimeError('Archive CRC check failed')
        if set(archive.namelist())!={str(p.relative_to(out)) for p in files}:raise RuntimeError('Incomplete portable archive')
        for name,value in file_hashes.items():require(hashlib.sha256(archive.read(name)).hexdigest()==value,'Zipped bytes differ from checked bytes: '+name)
    validate_build(out,manifest)
    receipt={'schema':2,'result':'PASS_CHECKED_BOOK_BUNDLE','source_revision':manifest['git_revision'],'build_manifest_sha256':digest(out/'build-manifest.json'),'archive':target.name,'archive_bytes':target.stat().st_size,'archive_sha256':digest(target),'file_count':len(files),'file_sha256':file_hashes,'qualification':'Local coherent book, source-bound proofs, numerical and browser evidence; no hosted publication or biological validation'}
    target.with_suffix('.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps({k:v for k,v in receipt.items() if k!='file_sha256'},indent=2))
if __name__=='__main__':package(sys.argv[1] if len(sys.argv)>1 else ROOT/'dist/kenoma-portable.zip')
