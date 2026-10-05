"""Build locked ProofWidgets JS assets from source before mathlib's guarded build.

The upstream mathlib configuration rejects an uncached widget build when loaded
as a dependency. Build its exact package as a standalone root, then re-elaborate
mathlib's unchanged configuration to restore that guard. No proof/check gate or
upstream source is changed, and no binary release cache is downloaded.
"""
from pathlib import Path
import hashlib,json,os,subprocess
ROOT=Path(__file__).resolve().parents[1]
def print_log_tail(path,lines=40,characters=8000):
    path=Path(path)
    text=path.read_text(errors='replace')
    tail='\n'.join(text.splitlines()[-lines:])[-characters:]
    print('PROOF_BUILD_FAILURE_TAIL '+str(path)+'\n'+tail,flush=True)
def bootstrap(mathlib,env):
    mathlib=Path(mathlib);manifest=json.loads((mathlib/'lake-manifest.json').read_text())
    package=next(p for p in manifest['packages'] if p['name']=='proofwidgets')
    source=mathlib/'.lake/packages/proofwidgets'
    def pristine():
        revision=subprocess.check_output(['git','rev-parse','HEAD'],cwd=source,text=True).strip()
        if revision!=package['rev']:raise RuntimeError('ProofWidgets revision differs from pinned mathlib manifest')
        if subprocess.check_output(['git','status','--porcelain'],cwd=source,text=True).strip():raise RuntimeError('Modified ProofWidgets source')
        return revision
    revision=pristine();digest=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
    lock_digest=digest(source/'widget/package-lock.json')
    logs=ROOT/'.tools/property-mathlib-source-logs';logs.mkdir(parents=True,exist_ok=True)
    build_env=env.copy();build_env['npm_config_cache']=str(ROOT/'.tools/proofwidgets-npm-cache')
    log=logs/'proofwidgets-source-assets.txt'
    with log.open('w') as stream:
        result=subprocess.run(['lake','--reconfigure','--no-cache','build','widgetJsAll'],cwd=source,env=build_env,stdout=stream,stderr=subprocess.STDOUT)
    if result.returncode:
        print_log_tail(log)
        raise RuntimeError('ProofWidgets source asset build failed; raw '+str(log))
    pristine()
    if digest(source/'widget/package-lock.json')!=lock_digest:raise RuntimeError('Widget dependency lock changed during source build')
    # Standalone and dependency configurations have different get_config values.
    # Re-elaborate the original mathlib config; its errorOnBuild guard stays active.
    subprocess.run(['lake','--reconfigure','--no-cache','env','lean','--version'],cwd=mathlib,env=env,check=True)
    js=source/'.lake/build/js'
    if not (js/'index.js').is_file() or not (js/'lake.trace').is_file():raise RuntimeError('Missing built widget assets or upstream trace')
    receipt={'schema':1,'result':'PASS_PINNED_PROOFWIDGETS_SOURCE_ASSETS','revision':revision,'package_lock_sha256':lock_digest,'source_sha256':{name:digest(source/name) for name in subprocess.check_output(['git','ls-files','--','widget'],cwd=source,text=True).splitlines()},'asset_sha256':{p.name:digest(p) for p in sorted(js.glob('*')) if p.is_file()},'upstream_source_modified':False,'binary_release_cache_used':False,'scope':'JavaScript dependency assets only; kernel compilation and all numerical/book gates remain separately required'}
    (logs/'proofwidgets-source-assets.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print('PROOFWIDGETS_SOURCE_ASSETS_READY',revision,flush=True)
    return receipt
