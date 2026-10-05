"""Package a checked immutable book build; preserve every linked local resource."""
from pathlib import Path
import hashlib,json,sys,zipfile
ROOT=Path(__file__).resolve().parents[1]
def package(destination):
    out=ROOT/'dist';manifest=json.loads((out/'build-manifest.json').read_text())
    for relative,digest in manifest['input_sha256'].items():
        if hashlib.sha256((ROOT/relative).read_bytes()).hexdigest()!=digest:raise RuntimeError('Build input changed: '+relative)
    for name in ['artifact-check.json','browser-check.json','mobile-startup-check.json']:
        if json.loads((out/name).read_text())['status']!='passed':raise RuntimeError('Missing successful check: '+name)
    if json.loads((out/'qa/property-browser-check.json').read_text())['result']!='PASS_INTEGRATED_PROPERTY_LABS':raise RuntimeError('Property interactions not checked')
    for name in manifest['proof_families']:
        if not all(c['status']=='checked' for c in json.loads((out/name).read_text())['claims']):raise RuntimeError('Unqualified proof receipt: '+name)
    target=Path(destination).resolve();target.parent.mkdir(parents=True,exist_ok=True)
    excluded={target,target.with_suffix('.json')}
    files=[p for p in sorted(out.rglob('*')) if p.is_file() and p.resolve() not in excluded and '__pycache__' not in str(p)]
    with zipfile.ZipFile(target,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as archive:
        for source in files:archive.write(source,str(source.relative_to(out)))
    with zipfile.ZipFile(target) as archive:
        if archive.testzip() is not None:raise RuntimeError('Archive CRC check failed')
        if set(archive.namelist())!={str(p.relative_to(out)) for p in files}:raise RuntimeError('Incomplete portable archive')
    receipt={'schema':1,'result':'PASS_CHECKED_BOOK_BUNDLE','source_revision':manifest['git_revision'],'build_manifest_sha256':hashlib.sha256((out/'build-manifest.json').read_bytes()).hexdigest(),'archive':target.name,'archive_bytes':target.stat().st_size,'archive_sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'file_count':len(files),'file_sha256':{str(p.relative_to(out)):hashlib.sha256(p.read_bytes()).hexdigest() for p in files},'qualification':'Local coherent book, source-bound proofs, numerical and browser evidence; no hosted publication or biological validation'}
    target.with_suffix('.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps({k:v for k,v in receipt.items() if k!='file_sha256'},indent=2))
if __name__=='__main__':package(sys.argv[1] if len(sys.argv)>1 else ROOT/'dist/kenoma-portable.zip')
