"""Inspect actual standalone PDF fonts, bounds, statement/source coverage and links.

Creates small JPEG85 review captures only after the parent admits rendering.
"""
from pathlib import Path
import argparse,hashlib,json,re
import fitz
from paths import HERE,checked_output,source_hashes

def run(site,output):
    out=checked_output(output);site=site.resolve();pdf=site/'lateral-interface-transfer.pdf'
    manifest=json.loads((site/'build-manifest.json').read_text())
    if manifest['source_sha256']!=source_hashes():raise RuntimeError('PDF/source binding mismatch')
    document=fitz.open(pdf);sizes=[];links=[];text='';captures=[];body_pages=[]
    for i,page in enumerate(document):
        text+=page.get_text();body=[]
        for block in page.get_text('dict')['blocks']:
            for line in block.get('lines',[]):
                for span in line['spans']:
                    if span['text'].strip():
                        sizes.append(span['size']);rect=fitz.Rect(span['bbox'])
                        if span['size']<9.99:raise RuntimeError(f'Sub-10pt actual PDF text on page {i+1}: {span}')
                        if not page.rect.contains(rect):raise RuntimeError(f'Clipped actual PDF text on page {i+1}: {span}')
                        # The footer is checked for point size and bounds above,
                        # then excluded from contiguous appendix code coverage.
                        if rect.y0 < page.rect.height-36:body.append(span['text'])
        for link in page.get_links():
            uri=link.get('uri','')
            if uri and (not uri.startswith(('http://','https://')) or re.search(r'localhost|127\.0\.0\.1|file:|/workspace/',uri)):
                raise RuntimeError('Unportable PDF URI: '+uri)
            links.append({'page':i+1,**{k:v for k,v in link.items() if k in ['uri','page','kind']}})
        body_pages.append('\n'.join(body))
    statements=json.loads((HERE/'claims.json').read_text())
    # Whitespace-insensitive coverage preserves every actual source token after display wrapping.
    compact=lambda s:re.sub(r'\s+','',s)
    start_statements=next(i for i,t in enumerate(body_pages) if 'Appendix: complete Real statements' in t)
    start_source=next(i for i,t in enumerate(body_pages) if 'Appendix: exact Lean source' in t)
    start_audit=next(i for i,t in enumerate(body_pages) if 'Appendix: standalone evidence scope' in t)
    statement_text='\n'.join(body_pages[start_statements:start_source])
    source_text='\n'.join(body_pages[start_source:start_audit])
    for c in statements:
        if compact(c['statement_lean']) not in compact(statement_text):raise RuntimeError('Missing full statement: '+c['theorem'])
    if compact((HERE/'LateralInterfaceTransfer.lean').read_text()) not in compact(source_text):
        raise RuntimeError('Exact complete Lean source is not readable in PDF')
    if not any(link.get('kind')==fitz.LINK_GOTO for link in links):raise RuntimeError('Missing internal source/statement appendix links')
    diagram=document[0]
    if not diagram.get_drawings() or 'Upper guided element' not in diagram.get_text():raise RuntimeError('Missing actual vector diagram')
    # Proof/source spans and vector diagram labels all went through the same actual >=10pt gate.
    for i in [0,start_statements,start_source]:
        name=f'pdf-page-{i+1}.jpg';pix=document[i].get_pixmap(matrix=fitz.Matrix(1.2,1.2));pix.pil_save(out/name,format='JPEG',quality=85)
        captures.append({'file':name,'sha256':hashlib.sha256((out/name).read_bytes()).hexdigest(),'quality':85})
    receipt={'status':'passed','pdf_sha256':hashlib.sha256(pdf.read_bytes()).hexdigest(),'source_sha256':source_hashes(),
      'pages':len(document),'minimum_actual_font_points':min(sizes),'all_text_within_page':True,
      'full_six_statements':True,'exact_full_lean_source':True,'actual_vector_diagram':True,'links':links,
      'captures':captures,'visual_acceptance':'pending independent appearance inspection','scope':'Standalone PDF only; no integrated book/render qualification.'}
    (out/'print-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(f'Actual {len(document)}-page PDF: full statements/source, vector diagram, >=10pt text, bounds and portable links passed.')

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--site',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();run(a.site,a.output)
