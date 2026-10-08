"""Qualify actual printed text, complete checked code and portable PDF links.

This deliberately measures PDF points, not CSS declarations or screenshot pixels.
Whitespace/Unicode presentation normalization permits wrapping, never missing code.
"""
from __future__ import annotations
import argparse
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import unicodedata
from urllib.parse import urlparse
import xml.etree.ElementTree as ET

import fitz

ROOT = Path(__file__).resolve().parents[1]
MINIMUM_PT = 10.0
EXPECTED_CARDS = 109
EXPECTED_SOURCES = 13


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def normalized(text):
    return ''.join(c for c in unicodedata.normalize('NFKC', text)
                   if not c.isspace() and c != '\u00ad')


class Node:
    def __init__(self, tag='', attrs=(), parent=None):
        self.tag, self.attrs, self.parent, self.children = tag, dict(attrs), parent, []

    def text(self):
        return ''.join(c.text() if isinstance(c, Node) else c for c in self.children)

    def nodes(self):
        yield self
        for c in self.children:
            if isinstance(c, Node):
                yield from c.nodes()

    def within(self, tags=(), css_class=None):
        p = self.parent
        while p:
            if p.tag in tags or (css_class and css_class in p.attrs.get('class', '').split()):
                return True
            p = p.parent
        return False


class HTMLTree(HTMLParser):
    VOID = {'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'link', 'meta', 'param', 'source', 'track', 'wbr'}

    def __init__(self, html):
        super().__init__(convert_charrefs=True)
        self.root = self.current = Node()
        self.feed(html)
        self.close()

    def handle_starttag(self, tag, attrs):
        node = Node(tag, attrs, self.current)
        self.current.children.append(node)
        if tag not in self.VOID:
            self.current = node

    def handle_startendtag(self, tag, attrs):
        self.current.children.append(Node(tag, attrs, self.current))

    def handle_endtag(self, tag):
        p = self.current
        while p.parent:
            if p.tag == tag:
                self.current = p.parent
                return
            p = p.parent

    def handle_data(self, text):
        self.current.children.append(text)


class PDFText:
    """A normalized stream with the actual size and position of every glyph."""
    def __init__(self, document):
        self.characters = []
        self.footer_glyphs = 0
        for page_index, page in enumerate(document):
            for block in page.get_text('rawdict')['blocks']:
                for line in block.get('lines', []):
                    text = ''.join(c['c'] for s in line['spans'] for c in s['chars'])
                    # Only the renderer's identified bottom footer is excluded.
                    footer = (line['bbox'][1] > page.rect.height - 40 and
                              (text.startswith('Kenoma · Mechanics of Moving Bodies') or text.strip().isdigit()))
                    for span in line['spans']:
                        for char in span['chars']:
                            if footer:
                                self.footer_glyphs += 1
                                continue
                            for c in normalized(char['c']):
                                self.characters.append({'c': c, 'size': span['size'],
                                    'flags': span['flags'], 'page': page_index + 1,
                                    'bbox': list(char['bbox']), 'page_rect': list(page.rect)})
        self.text = ''.join(c['c'] for c in self.characters)

    def occurrences(self, text, start=0, end=None):
        needle = normalized(text)
        if not needle:
            raise AssertionError('Empty text target')
        end = len(self.text) if end is None else end
        while (pos := self.text.find(needle, start, end)) >= 0:
            yield pos
            start = pos + len(needle)

    def bounded(self, heading, ending):
        for start in self.occurrences(heading):
            stop = self.text.find(normalized(ending), start + len(normalized(heading)))
            if stop >= 0:
                yield start, stop

    def target(self, label, text, start=0, end=None, prose=False, superscript_text=''):
        positions = list(self.occurrences(text, start, end))
        assert positions, f'{label}: missing or truncated printed text'
        pos = positions[0]
        chars = self.characters[pos:pos + len(normalized(text))]
        # Only genuine PDF superscript runs explicitly present as HTML <sup>
        # may use a smaller font. Code never receives this exemption.
        allowed = normalized(superscript_text)
        exempt = []
        checked = []
        for c in chars:
            if prose and c['flags'] & 1 and c['c'] in allowed:
                exempt.append(c)
            else:
                checked.append(c)
            x0, y0, x1, y1 = c['bbox']
            _, _, width, height = c['page_rect']
            assert x0 >= -1 and y0 >= -1 and x1 <= width + 1 and y1 <= height + 1, f'{label}: glyph outside PDF page'
        assert checked, f'{label}: no base-size instructional glyphs'
        minimum = min(c['size'] for c in checked)
        assert minimum >= MINIMUM_PT, f'{label}: {minimum:.6f} pt below {MINIMUM_PT:g} pt'
        return {'label': label, 'minimum_pt': minimum, 'matched_glyphs': len(chars),
                'pages': sorted({c['page'] for c in chars}), 'superscript_glyphs_exempted': len(exempt),
                'text_sha256': hashlib.sha256(normalized(text).encode()).hexdigest()}


def theorem_statement(source, theorem):
    local = theorem.split('.')[-1]
    match = re.search(r'\btheorem\s+' + re.escape(local) + r'\b', source)
    assert match, f'Missing source theorem {theorem}'
    end = source.find(':=', match.end())
    assert end >= 0, f'Missing assignment for {theorem}'
    statement = source[match.start():end].strip()
    assert not re.search(r'\n\s*(?:theorem|def|lemma|namespace|end)\b', statement), f'Crossed source declaration {theorem}'
    return statement


def portable_links(document):
    destinations = document.resolve_names()
    external, internal = set(), set()
    annotations = 0
    for page in document:
        for link in page.get_links():
            annotations += 1
            if link['kind'] == fitz.LINK_URI:
                uri = link['uri']
                parsed = urlparse(uri)
                assert parsed.scheme == 'https' and parsed.hostname not in {'localhost', '127.0.0.1', '::1'}, f'Nonportable PDF link: {uri}'
                external.add(re.sub(r'(https://github.com/MrScripty/Kenoma/blob/)[^/]+/', r'\1<revision>/', uri))
            elif link['kind'] in (fitz.LINK_GOTO, fitz.LINK_NAMED):
                name = link.get('nameddest')
                target = destinations.get(name) if name else link
                assert target and 0 <= target.get('page', -1) < len(document), f'Invalid internal PDF target: {link}'
                # Chromium produces named anchors; unnamed GoTo links are bound
                # to their resolved destination rather than annotation count.
                internal.add(name or f"page:{target['page']}:point:{target.get('to')}")
            else:
                raise AssertionError(f'Unsupported/nonportable PDF link kind: {link}')
    return {'external_targets': sorted(external), 'internal_targets': sorted(internal), 'annotations': annotations}


def svg_label_measurements(pdf, svg_path):
    """Match the entire ordered SVG text inventory as one printed figure.

    Bounding by every supplied label prevents another paragraph/figure from
    concealing an absent or undersized label, including repeated numeric ticks.
    Scientific-notation tick exponents alone receive the recorded math exemption.
    """
    labels = [''.join(n.itertext()).strip() for n in ET.parse(svg_path).getroot().iter()
              if n.tag.rsplit('}', 1)[-1] == 'text']
    assert labels and all(labels), f'Empty SVG label inventory: {svg_path}'
    positions = list(pdf.occurrences(''.join(labels)))
    assert len(positions) == 1, f'{svg_path.name}: missing/duplicated complete printed SVG label inventory'
    cursor = positions[0]
    measurements, errors = [], []
    for index, label in enumerate(labels):
        end = cursor + len(normalized(label))
        scientific = re.fullmatch(r'10([−-]\d+)', normalized(label))
        try:
            measurements.append(pdf.target(f'figure:{svg_path.name}:{index}:{label.strip()}', label,
                cursor, end, prose=bool(scientific), superscript_text=scientific.group(1) if scientific else ''))
        except AssertionError as error:
            errors.append(str(error))
        cursor = end
    assert not errors, '\n'.join(errors)
    return measurements


def qualify(out, baseline_pdf=None):
    out = Path(out)
    html_path, pdf_path = out / 'index.html', out / 'kenoma-mechanics.pdf'
    initial_paths = [html_path, pdf_path, out / 'build-manifest.json', *sorted(out.rglob('*.css'))]
    initial_hashes = {str(p.relative_to(out)): sha(p) for p in initial_paths}
    baseline_hash = sha(baseline_pdf) if baseline_pdf else None
    nodes = list(HTMLTree(html_path.read_text()).root.nodes())
    manifest_path = out / 'build-manifest.json'
    manifest = json.loads(manifest_path.read_text())
    families, claims, bindings = [], {}, {}
    for receipt_name in manifest['proof_families']:
        receipt_path = out / receipt_name
        receipt = json.loads(receipt_path.read_text())
        source_path = out / receipt['source']
        assert sha(source_path) == receipt['source_sha256'], f'Source receipt mismatch: {source_path}'
        source = source_path.read_text()
        families.append((source_path, source))
        bindings[receipt_name] = sha(receipt_path)
        bindings[receipt['source']] = sha(source_path)
        for claim in receipt['claims']:
            assert claim['id'] not in claims, 'Duplicate claim id'
            claims[claim['id']] = (claim, source)
    assert len(families) == EXPECTED_SOURCES and len(claims) == EXPECTED_CARDS, 'Expected the complete 109-card, thirteen-source integration edition'
    cards = [n for n in nodes if 'proof-card' in n.attrs.get('class', '').split()]
    assert len(cards) == EXPECTED_CARDS, 'Wrong printed card inventory'
    measurements, errors, figure_inputs = [], [], {}
    with fitz.open(pdf_path) as document:
        pdf = PDFText(document)
        def measure(label, text, bounds=None, prose=False, node=None):
            try:
                supers = ''.join(n.text() for n in node.nodes() if n.tag == 'sup') if node else ''
                measurements.append(pdf.target(label, text, *(bounds or (0, None)), prose=prose, superscript_text=supers))
            except AssertionError as error:
                errors.append(str(error))
        for card in cards:
            ident = card.attrs['id'].removeprefix('proof-')
            claim, source = claims[ident]
            local_nodes = [n for n in card.nodes() if not n.within(('details',))]
            statement = next(n for n in local_nodes if n.tag == 'pre')
            assert normalized(statement.text()) == normalized(theorem_statement(source, claim['theorem'])), f'HTML/source theorem mismatch: {ident}'
            paragraphs = [n for n in local_nodes if n.tag == 'p']
            fields = {'claim': paragraphs[0]}
            for key, prefix in [('assumptions', 'Assumptions:'), ('limits', 'Limits:'), ('implementation', 'Implementation link:')]:
                fields[key] = next(n for n in paragraphs if n.text().strip().startswith(prefix))
            assert normalized(fields['claim'].text()) == normalized(claim['claim']), f'HTML claim mismatch: {ident}'
            assert normalized(fields['assumptions'].text()) == normalized('Assumptions:' + claim['assumptions']), f'HTML assumptions mismatch: {ident}'
            assert normalized(fields['limits'].text()) == normalized('Limits:' + claim['limitations']), f'HTML limits mismatch: {ident}'
            bounds = next(pdf.bounded('Checked claim · ' + ident, 'Full source · Build receipt · Kernel dependency report'), None)
            if bounds is None:
                errors.append(f'{ident}: missing printed proof card boundary')
                continue
            for key, node in fields.items():
                measure(f'card:{ident}:{key}', node.text(), bounds, True, node)
            measure(f'theorem:{claim["theorem"]}', statement.text(), bounds)
        for source_path, source in families:
            heading = 'Checked source appendix: ' + source_path.stem
            heading_nodes = [n for n in nodes if n.tag == 'h1' and normalized(n.text()) == normalized(heading)]
            assert len(heading_nodes) == 1, f'Missing/duplicate HTML appendix {heading}'
            following = nodes[nodes.index(heading_nodes[0]) + 1:]
            printed_source = next(n for n in following if n.tag == 'pre')
            assert normalized(printed_source.text()) == normalized(source), f'Incomplete HTML appendix: {source_path.name}'
            bounds = next((b for b in pdf.bounded(heading, 'Proof check receipt') if list(pdf.occurrences(source, *b))), None)
            if bounds is None:
                errors.append(f'appendix:{source_path.name}: missing or truncated printed complete source')
            else:
                measure(f'appendix:{source_path.name}', source, bounds)
        # One substantive plain instructional paragraph from every chapter.
        # Avoid hidden lab templates, proof cards and duplicated MathML annotations.
        chapter, selected = None, set()
        for n in nodes:
            if n.tag == 'h1':
                if n.text().strip().startswith('Checked source appendix:'):
                    break
                chapter = n.text().strip()
            if (chapter and chapter not in selected and n.tag == 'p' and len(n.text().strip()) >= 80
                    and not n.within(('details', 'nav', 'aside', 'template', 'script', 'style'))
                    and not any(c.tag in ('math', 'canvas', 'svg') for c in n.nodes())
                    and not n.within(css_class='lab')):
                measure('prose:' + chapter, n.text(), prose=True, node=n)
                selected.add(chapter)
        assert selected, 'No representative instructional prose selected'
        for name in ('dense-qualification.svg', 'dense-envelope.svg', 'nodal-force-components.svg', 'property-serial.svg', 'property-dissipative.svg', 'pressure-projection.svg'):
            paths = list(out.rglob(name))
            assert len(paths) == 1, f'Missing/duplicated delivered figure {name}'
            path = paths[0]
            figure_inputs[str(path.relative_to(out))] = sha(path)
            try:
                measurements.extend(svg_label_measurements(pdf, path))
            except AssertionError as error:
                errors.append(str(error))
        links = portable_links(document)
        if baseline_pdf:
            with fitz.open(baseline_pdf) as baseline:
                original = portable_links(baseline)
            for kind in ('external_targets', 'internal_targets'):
                assert original[kind] == links[kind], f'Changed portable PDF {kind}'
        assert not errors, 'Print readability failed:\n' + '\n'.join(errors)
        pages = len(document)
    for name, digest in {**initial_hashes, **bindings, **figure_inputs}.items():
        assert sha(out / name) == digest, f'Delivered input changed during qualification: {name}'
    if baseline_pdf:
        assert sha(baseline_pdf) == baseline_hash, 'Baseline PDF changed during qualification'
    styles = {name: digest for name, digest in initial_hashes.items() if name.endswith('.css')}
    assert styles, 'No delivered styles to bind'
    source_inputs = {name: sha(ROOT / name) for name in ('tools/check_print_readability.py', 'tests/test_print_readability.py', 'tools/render_pdf.py', 'tools/print_layout.js') if (ROOT / name).is_file()}
    return {'schema': 1, 'status': 'PASS', 'minimum_required_pt': MINIMUM_PT,
            'proof_cards': len(cards), 'theorem_statements': len(cards), 'complete_source_appendices': len(families),
            'instructional_prose_chapters': sorted(selected), 'pages': pages,
            'minimum_measured_pt': min(m['minimum_pt'] for m in measurements),
            'measurements': measurements, 'identified_footer_glyphs_excluded': pdf.footer_glyphs,
            'portable_links': links, 'baseline_pdf_sha256': baseline_hash,
            'pdf_sha256': initial_hashes['kenoma-mechanics.pdf'], 'html_sha256': initial_hashes['index.html'], 'delivered_styles_sha256': styles,
            'build_manifest_sha256': initial_hashes['build-manifest.json'], 'proof_inputs_sha256': bindings, 'dense_figure_inputs_sha256': figure_inputs,
            'instructional_figure_labels': sum(m['label'].startswith('figure:') for m in measurements),
            'dense_figure_labels': sum(m['label'].startswith(('figure:dense-', 'figure:nodal-force-components.svg:')) for m in measurements),
            'serial_figure_labels': sum(m['label'].startswith('figure:property-serial.svg:') for m in measurements),
            'dissipative_figure_labels': sum(m['label'].startswith('figure:property-dissipative.svg:') for m in measurements),
            'checker_sha256': sha(__file__), 'source_inputs_sha256': source_inputs,
            'pdf_render_receipt_sha256': sha(out / 'pdf-render.json') if (out / 'pdf-render.json').is_file() else None,
            'pdf_byte_identity_asserted': False,
            'scope': 'Actual PDF base glyph sizes and complete specified instructional/code text; mathematical HTML superscripts and identified renderer footers excluded only as recorded.'}


def check(out=None):
    """Recompute qualification and validate the existing receipt without rebinding.

    The optional original-baseline hash is established by the explicit CLI run;
    consumers recheck current portable targets and every other generated field.
    """
    out = Path(out or ROOT / 'dist')
    receipt = json.loads((out / 'print-readability-check.json').read_text())
    actual = qualify(out)
    assert set(receipt) == set(actual), 'Print readability receipt schema/key mismatch'
    for key, value in actual.items():
        if key != 'baseline_pdf_sha256':
            assert receipt[key] == value, f'Stale/forged print readability receipt: {key}'
    return receipt


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('dist', nargs='?', type=Path, default=ROOT / 'dist')
    parser.add_argument('--baseline-pdf', type=Path)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    output = args.output or args.dist / 'print-readability-check.json'
    output.unlink(missing_ok=True)
    result = qualify(args.dist, args.baseline_pdf)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2) + '\n')
    print(f'PASS: {result["theorem_statements"]} statements, {result["complete_source_appendices"]} complete sources; minimum {result["minimum_measured_pt"]:.6f} pt')


if __name__ == '__main__':
    main()
