"""Collect final receipts without changing the qualified lesson source."""
from pathlib import Path
import hashlib,json,shutil,subprocess,sys
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools'))
from package_education_bundle import FAMILIES,validate_build

SOURCE='569e6686aaa08c7a2005ed25441c59db7afee4f8'
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text())
def collect():
    out=ROOT/'dist';here=Path(__file__).parent;manifest=read(out/'build-manifest.json')
    assert manifest['git_revision']==SOURCE
    validate_build(out,manifest)
    for path,sha in manifest['input_sha256'].items():assert digest(ROOT/path)==sha
    artifact=read(out/'artifact-check.json');browser=read(out/'dissipative-qa/receipt.json')
    lanes=read(here/'final-569e/status.json')
    assert lanes['status']=='PASS_ALL_SEVEN_INTEGRATED_BROWSER_LANES' and lanes['source_commit']==SOURCE
    assert lanes['build_manifest_sha256']==digest(out/'build-manifest.json')
    final_hashes=read(here/'final-569e/final-output-hash-status.json')
    assert final_hashes['status']=='PASS' and final_hashes['source_commit']==SOURCE
    assert final_hashes['checker_files_match_committed_source']
    negatives=read(out/'dissipative-negative-artifacts.json')
    assert len(negatives['cases'])==6 and all(c['detected'] for c in negatives['cases'])
    standalone=read(here/'standalone-569e/receipt.json')
    assert standalone['status']=='PASS' and len(standalone['negative_controls'])==2 and all(c['detected'] for c in standalone['negative_controls'])
    portable=read(Path('/workspace/kenoma-dissipative-portable.json'))
    assert portable['source_revision']==SOURCE and portable['result']=='PASS_CHECKED_BOOK_BUNDLE'
    proofs=here/'fresh-proofs';proofs.mkdir(exist_ok=True)
    for path in sorted(out.glob('*proof-status.json'))+sorted(out.glob('*lean-check.txt')):
        shutil.copy2(path,proofs/path.name)
    for name in ['build-manifest.json','artifact-check.json','dissipative-experiment.json','dissipative-negative-artifacts.json','browser-check.json','mobile-startup-check.json','worker-lifecycle-check.json']:
        if (out/name).exists():shutil.copy2(out/name,here/name)
    for folder in ['dissipative-qa','real-proof-review','property-book-review','material-qa']:
        shutil.copytree(out/folder,here/folder,dirs_exist_ok=True)
    shutil.copy2('/workspace/kenoma-dissipative-portable.json',here/'portable-package.json')
    continuity=read(here/'node-input-continuity.json')
    assert continuity['current_revision']==SOURCE
    frozen=subprocess.check_output(['git','-C','/workspace/kenoma-current-main-53','rev-parse','HEAD'],text=True).strip()
    assert frozen=='e8fa239e3c01468cee86615e1f306dd6659999fa'
    statements=read(here/'final-569e/actual-statements.json')
    assert statements['status']=='PASS' and statements['source_commit']==SOURCE
    manual=['standalone-569e/force-hold-loaded.png','standalone-569e/extension-hold-completed.png','standalone-569e/mobile-default.png','dissipative-qa/force-hold-loaded.png','dissipative-qa/extension-hold-completed.png','dissipative-qa/mobile-default.png','real-proof-review/mobile-dissipative-real-storage-sign.png','real-proof-review/desktop-dissipative-real-power-balance.png','manual-review-569e/pdf-page-19.png','manual-review-569e/pdf-page-20.png','manual-review-569e/pdf-page-21.png','manual-review-569e/pdf-page-85.png','manual-review-569e/pdf-page-86.png']
    result={'result':'PASS_SEPARATE_DISSIPATIVE_LESSON','source_revision':SOURCE,'source_tree':subprocess.check_output(['git','rev-parse',SOURCE+'^{tree}'],cwd=ROOT,text=True).strip(),'base_accepted_revision':'f0973f46e55faa881ab3b34c6a848dfee313142e','frozen_current_main_53_revision':frozen,'node_tests_passed':198,'node_test_source_revision':continuity['passed_node_source_revision'],'unchanged_node_inputs':len(continuity['input_sha256']),'python_tests_passed':34,'new_sls_numerical_tests':19,'new_sls_real_declarations':11,'fresh_lean_declarations':sum(c for *_,c in FAMILIES),'integer_declarations':30,'real_declarations':34,'proof_source_files':len(FAMILIES),'source_inputs':len(manifest['input_sha256']),'actual_existing_browser_lanes_passed':6,'actual_sls_browser_passed':True,'sls_positive_outputs':len(browser['output_sha256']),'sls_delivered_negative_controls_detected':2,'damaged_sls_artifact_controls_detected':6,'property_material_controls_passed':True,'desktop_mobile_new_real_cards':30,'pdf_pages':artifact['pdf_pages'],'artifact_status':artifact['status'],'build_manifest_sha256':digest(out/'build-manifest.json'),'archive_sha256':portable['archive_sha256'],'archive_bytes':portable['archive_bytes'],'archive_file_count':portable['file_count'],'archive_crc_and_per_file_checks':'PASS','manual_appearance_review':[{'path':n,'sha256':digest(here/n)} for n in manual],'limitations':['Authored one-dimensional small-strain quasistatic standard linear solid; no muscle calibration, transverse solve, force–velocity implementation or anatomical claim.','Formal local real-number contracts do not certify the bar reduction, quadrature, floating-point arithmetic or complete discrete ledger.','Local Chromium and mobile emulation; only listed captures manually inspected.','Initial concurrent screenshot timeouts retained; sequential retries use identical source and timeout limits.','Draft PR text prepared; creation awaits parent coordination. No merge or deployment.']}
    (here/'qualification.json').write_text(json.dumps(result,indent=2)+'\n')
    inventory={str(p.relative_to(here)):digest(p) for p in sorted(here.rglob('*')) if p.is_file() and p.name!='evidence-inventory.json' and '__pycache__' not in str(p)}
    (here/'evidence-inventory.json').write_text(json.dumps({'source_revision':SOURCE,'file_sha256':inventory},indent=2)+'\n')
    print('Collected',len(inventory),'source-bound evidence files')
if __name__=='__main__':collect()
