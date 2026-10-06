"""Fail closed on missing, stale or inconsistent projection qualification."""
from pathlib import Path
import hashlib, json, re, sys
from urllib.parse import urlparse
import fitz
ROOT = Path(__file__).resolve().parents[1]


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def check(out=None):
    out = Path(out) if out else ROOT/'dist'
    read = lambda name: json.loads((out/name).read_text())
    r = read('projection-qa/integration.json')
    assert r['result'] == 'PASS_INTEGRATED_FIXED_FIELD_PROJECTION' and not r['errors']
    for field, path in [('manifest_sha256','build-manifest.json'), ('html_sha256','index.html'), ('lab_sha256','standalone/pressure-projection-lab.html'), ('standalone_receipt_sha256','projection-qa/receipt.json'), ('book_capture_sha256','projection-qa/book-controls.png')]:
        assert r[field] == digest(out/path), 'Stale projection binding: '+path
    lab = read('projection-qa/receipt.json')
    assert lab['result'] == 'PASS_STANDALONE_FIXED_FIELD_PRESSURE_PROJECTION_LAB' and lab['exact_reference_states'] == 5625
    assert not lab['javascript_errors'] and not lab['external_requests']
    for path, value in lab['source_sha256'].items():
        assert digest(out/path) == value == digest(ROOT/path), 'Changed projection source: '+path
    for name, value in lab['evidence_sha256'].items():
        assert digest(out/'projection-qa'/name) == value
    with fitz.open(out/'projection-qa/fixed-field-reference.pdf') as doc:
        glyphs = [s['size'] for pg in doc for b in pg.get_text('dict')['blocks'] for line in b.get('lines',[]) for s in line['spans'] if s['text'].strip()]
        assert min(glyphs)>=10 and min(glyphs)==lab['review_print_qualification']['minimum_actual_pt']
        from check_print_readability import PDFText, svg_label_measurements, portable_links
        labels=[]
        measured=PDFText(doc)
        for index in range(3): labels.extend(svg_label_measurements(measured,out/'projection-qa'/f'review-chart-{index}.svg'))
        assert labels==lab['review_print_qualification']['diagram_labels']
        assert portable_links(doc)==lab['portable_pdf_links']
        for page in doc:
            for link in page.get_links():
                uri = urlparse(link.get('uri',''))
                assert uri.hostname not in {'127.0.0.1','localhost','::1'} and uri.scheme != 'file'
    proof = read('mixed-volume-proof-status.json')
    source = out/'proofs/MixedLogVolume.lean'
    names = re.findall(r'^theorem\s+(\w+)\b', source.read_text(), re.M)
    assert len(names) == len(proof['claims']) == 27
    assert [c['theorem'] for c in proof['claims']] == ['KenomaMixedVolume.'+name for name in names]
    assert digest(source) == proof['source_sha256'] == digest(ROOT/'proofs/MixedLogVolume.lean')
    kernel = read('mixed-volume-kernel/receipt.json')
    assert kernel['result'] == 'PASS_RESEARCH_WEIGHTED_PROJECTION_ALGEBRA' and kernel['source_files_match_commit'] is True
    assert kernel['source_sha256'] == proof['source_sha256']
    assert kernel['source_commit'] == read('build-manifest.json')['git_revision']
    assert set(kernel['theorems']) == {c['theorem'] for c in proof['claims']}
    assert kernel['transcript_sha256'] == digest(out/'mixed-volume-kernel/lean-check.txt')
    assert kernel['olean_sha256'] == digest(out/'mixed-volume-kernel/MixedLogVolume.olean')
    print('PASS source-bound projection artifact')
    return r


if __name__ == '__main__':
    check(sys.argv[1] if len(sys.argv)>1 else None)
