"""Require the complete source-authored limits paragraph at actual PDF points."""
from pathlib import Path
import hashlib, json, subprocess, sys
import fitz
from check_print_readability import HTMLTree, PDFText

ROOT = Path(__file__).resolve().parents[1]
RENDER_INPUTS = ('tests/projection_integration.py', 'tests/artifacts.py',
                 'tools/check_projection_print_limits.py')


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def limits_text(html):
    tree = HTMLTree(Path(html).read_text())
    details = [n for n in tree.root.nodes() if n.tag == 'details' and
               any(c.tag == 'summary' and c.text().strip() == 'Interpretation and limits'
                   for c in n.nodes())]
    assert len(details) == 1, 'Missing or duplicate projection limits section'
    paragraphs = [n.text().strip() for n in details[0].nodes() if n.tag == 'p']
    assert len(paragraphs) == 1 and paragraphs[0], 'Expected the full authored limits paragraph'
    return paragraphs[0]


def measure(pdf, html):
    with fitz.open(pdf) as document:
        printed = PDFText(document)
        return {
            'heading': printed.target('projection:limits-heading', 'Interpretation and limits'),
            'paragraph': printed.target('projection:complete-limits-paragraph', limits_text(html)),
        }


def check(out=None):
    out = Path(out) if out else ROOT/'dist'
    receipt = json.loads((out/'projection-qa/receipt.json').read_text())
    qualification = receipt['review_print_qualification']
    actual = measure(out/'projection-qa/fixed-field-reference.pdf',
                     out/'standalone/pressure-projection-lab.html')
    assert actual == qualification['interpretation_and_limits'], 'Stale complete-paragraph measurement'
    assert set(qualification['render_input_sha256']) == set(RENDER_INPUTS)
    for relative, expected in qualification['render_input_sha256'].items():
        assert digest(ROOT/relative) == expected, 'Changed review renderer/checker: '+relative
        tracked = subprocess.check_output(['git', 'show',
            qualification['renderer_source_commit']+':education/'+relative], cwd=ROOT)
        assert hashlib.sha256(tracked).hexdigest() == expected, 'Renderer bytes do not match recorded source commit'
    print('PASS complete projection limits paragraph at actual >=10pt, source-bound renderer')
    return actual


if __name__ == '__main__':
    check(sys.argv[1] if len(sys.argv)>1 else None)
