"""Read-only hash/provenance/receipt checks; does not replay the symbolic audit."""
import hashlib
import json
from pathlib import Path
import subprocess


ROOT=Path(__file__).resolve().parents[2]
PACKET=ROOT/'education/data/anatomical-arm-v1/review/source-unit-calibration'


def main():
    manifest=json.loads((PACKET/'manifest.json').read_text())
    for entry in manifest['files']:
        path=(ROOT/entry['path']).resolve()
        assert path.is_relative_to(ROOT),entry['path']
        data=path.read_bytes()
        assert len(data)==entry['bytes'],entry['path']
        assert hashlib.sha256(data).hexdigest()==entry['sha256'],entry['path']
    def read(name):
        return json.loads((PACKET/name).read_text())
    audit=read('symbolic-unit-audit.json')
    execution=read('symbolic-unit-execution.json')
    assert audit==read('symbolic-unit-audit.raw.log')
    assert audit['result']=='PASS_EXACT_CONDITIONAL_UNIT_AND_TOPOLOGY_AUDIT'
    assert len(audit['passedIdentities'])==12 and len(set(audit['passedIdentities']))==12
    assert len(audit['validDimensions'])==7
    assert len(audit['intendedDimensionRejections'])==4
    assert len(audit['dimensionallyValidMechanicalCounterexamples'])==2
    assert not audit['physicalCalibrationSelected'] and not audit['kineticOrAnatomicalSolveExecuted']
    assert execution['attempt']==1 and execution['exitCode']==0
    assert audit['protocolCommit']==execution['protocolCommit']==manifest['protocolCommit']
    assert audit['sourceSHA256']==execution['sourceSHA256']
    source='education/tools/audit_source_units_and_identifiability.py'
    committed=subprocess.check_output(['git','show',audit['protocolCommit']+':'+source],cwd=ROOT)
    assert hashlib.sha256(committed).hexdigest()==audit['sourceSHA256']
    assert committed==(ROOT/source).read_bytes()
    facts=read('code-unit-facts.json')
    assert len(facts['sourceFiles'])==20
    assert facts['commit']=='8c766dfb308051309193e7290ddd0bac3b726d11'
    assert facts['tree']=='a802ec6f7299d0745dfab1d5b715a3d9b7aa6f20'
    assert not any(facts[k] for k in ('authorCodeExecuted','authorCodeImported','authorCodeCopiesCommitted'))
    assert read('render-visual-inspection-v1.json')['result']=='LAYOUT_FAIL_PRESERVED'
    assert read('render-visual-inspection-v2.json')['result']=='PASS_VISUAL_LAYOUT_V2'
    for name,source in [('render-execution.json','education/tools/render_source_unit_contract.py'),
                        ('render-v2-execution.json','education/tools/render_source_unit_contract_v2.py')]:
        receipt=read(name)
        assert receipt['exitCode']==0 and receipt['attempt']==1
        assert hashlib.sha256((ROOT/source).read_bytes()).hexdigest()==receipt['sourceSHA256']
    v2=read('render-v2-execution.json')
    assert not v2['symbolicAuditReplayed']
    source='education/tools/render_source_unit_contract_v2.py'
    committed=subprocess.check_output(['git','show',v2['precommittedRendererCommit']+':'+source],cwd=ROOT)
    assert hashlib.sha256(committed).hexdigest()==v2['sourceSHA256']
    changes=subprocess.check_output(['git','diff','--name-status',manifest['frozenBase'],'--'],cwd=ROOT,text=True)
    assert all(line.startswith('A\t') for line in changes.splitlines()),changes
    subprocess.run(['git','merge-base','--is-ancestor','08f5f3b7fd4b987d3f049c13fdf4338bfaa2928e','HEAD'],cwd=ROOT,check=True)
    print(json.dumps(dict(result='PASS_READ_ONLY_SOURCE_UNIT_PACKET',hashBindings=len(manifest['files']),
        exactIdentities=12,intendedDimensionRejections=4,mechanicalCounterexamples=2,
        pinnedSourceBlobs=20,symbolicAuditReplayed=False,physicalCalibrationSelected=False,
        kineticOrAnatomicalSolveExecuted=False,frozenCommittedEvidencePreserved=True)))


if __name__=='__main__':
    main()
