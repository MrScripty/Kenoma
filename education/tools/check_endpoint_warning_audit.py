"""Strict historical-byte and fresh current-source endpoint audit gates."""
from pathlib import Path
import hashlib,json,sys
ROOT=Path(__file__).resolve().parents[1]
HISTORICAL_RECEIPT_SHA256='7995b4d3a33cd07994c43007a9e4208170e35f5e1d5d14ba93e0c675cf1acdc3'
HISTORICAL_RENDERER='data/property-labs-v1/endpoint-warning-history/web/property-labs.mjs'
HISTORICAL_NUMERICAL='data/property-labs-v1/endpoint-warning-history/web/tapered-bar.mjs'
NUMERICAL_INPUTS={'web/tapered-bar.mjs','web/property-labs.mjs','tests/tapered_bar.test.mjs',
                  'data/property-labs-v1/review/first-preview/web/tapered-bar.mjs',
                  'tools/tapered-bar-current-endpoint-audit.mjs'}
BROWSER_INPUTS={'web/property-labs.mjs','web/tapered-bar.mjs','web/continuum-properties.mjs',
                'tools/property_labs.py','tools/build_property_preview.py','tests/endpoint_warning_audit.py'}

def check(out):
    digest=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
    base=Path(out)/'data/property-labs-v1'
    path=base/'endpoint-warning-audit.json'
    assert digest(path)==HISTORICAL_RECEIPT_SHA256,'Original historical endpoint receipt changed'
    historical=json.loads(path.read_text())
    assert historical['result']=='PASS_PRESERVED_WARNING_FAILURE_AND_ENDPOINT_CORRECTION'
    for relative,expected in historical['sourceHashes'].items():
        archived={'web/property-labs.mjs':HISTORICAL_RENDERER,'web/tapered-bar.mjs':HISTORICAL_NUMERICAL}.get(relative)
        source=ROOT/(archived or relative)
        assert digest(source)==expected,'Historical endpoint input changed: '+relative
        if relative=='web/property-labs.mjs':
            assert digest(Path(out)/HISTORICAL_RENDERER)==expected,'Delivered historical renderer changed'
        if relative=='web/tapered-bar.mjs':
            assert digest(Path(out)/HISTORICAL_NUMERICAL)==expected,'Delivered historical numerical module changed'
    current=json.loads((base/'endpoint-warning-current-audit.json').read_text())
    assert current['result']=='PASS_CURRENT_ENDPOINT_CORRECTION'
    assert current['historicalReceiptSHA256']==HISTORICAL_RECEIPT_SHA256
    assert set(current['sourceHashes'])==NUMERICAL_INPUTS,'Missing current numerical input binding'
    for receipt in [historical,current]:
        assert not receipt['frozen']['smallStrainWarning'] and receipt['corrected']['smallStrainWarning']
        assert abs(receipt['oracleMaximumStrain']-3/55)<1e-15
        assert abs(receipt['corrected']['maximumStrain']-3/55)<1e-15
        assert [r['segments'] for r in receipt['refinements']]==[8,16,64,512]
        assert all(r['smallStrainWarning'] and abs(r['trueMaximumStrain']-3/55)<1e-15 for r in receipt['refinements'])
    browser=json.loads((base/'endpoint-warning-browser-audit.json').read_text())
    assert browser['result']=='PASS_CURRENT_ENDPOINT_RENDERER' and not browser['javascriptErrors']
    assert set(browser['sourceHashes'])==BROWSER_INPUTS,'Missing current browser input binding'
    assert browser['currentNumericalReceiptSHA256']==digest(base/'endpoint-warning-current-audit.json')
    case=browser['counterexample']
    assert case['warningVisible'] and case['midpointMaximumStrain']<.05
    assert abs(case['endpointMaximumStrain']-3/55)<1e-15
    visibility=browser['visibilityEvidence']
    assert visibility['assertion']=='Playwright expect(specific Small-strain scope dd).to_be_visible after scroll_into_view_if_needed'
    screenshot='data/property-labs-v1/endpoint-warning-current-visible.png'
    assert visibility['screenshot']==screenshot
    assert digest(ROOT/screenshot)==visibility['sha256'],'Current endpoint screenshot changed'
    assert digest(Path(out)/screenshot)==visibility['sha256'],'Delivered endpoint screenshot changed'
    for receipt in [current,browser]:
        assert 'web/property-labs.mjs' in receipt['sourceHashes']
        for relative,expected in receipt['sourceHashes'].items():
            assert digest(ROOT/relative)==expected,'Current endpoint input changed: '+relative
    print('PASS_HISTORICAL_AND_CURRENT_ENDPOINT_ARTIFACT_GATE')

if __name__=='__main__':check(Path(sys.argv[1]) if len(sys.argv)>1 else ROOT)
