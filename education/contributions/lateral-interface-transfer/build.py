"""Build only this portable standalone site and PDF, with exact source binding.

Requires genuine source-bound audit and kernel receipts. No experiments,
dependency install, integrated book registry or workflow change is performed.
"""
from pathlib import Path
import argparse,hashlib,html,json,re,shutil,subprocess,textwrap,zipfile
from paths import HERE,checked_output,source_hashes
from check_lean import PIN,MANIFEST,THEOREMS

def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def bound_receipts(audit_path,proof_path):
    audit=json.loads(audit_path.read_text());proof=json.loads(proof_path.read_text())
    if audit.get('status')!='passed' or audit.get('case_count')!=24 or audit.get('symbolic_identity_count')!=6:
        raise RuntimeError('Actual bounded 24-case audit required')
    if audit.get('audited_model_sha256')!=digest(HERE/'model.mjs') or audit.get('source_sha256',{}).get('check_algebra.py')!=digest(HERE/'check_algebra.py'):
        raise RuntimeError('Audit/model source binding mismatch')
    if proof.get('status')!='passed' or proof.get('mathlib_commit')!=PIN or proof.get('manifest_sha256')!=MANIFEST or 'version 4.19.0,' not in proof.get('lean_version',''):
        raise RuntimeError('Actual pinned kernel receipt required')
    for name in ['LateralInterfaceTransfer.lean','claims.json','check_lean.py']:
        if proof.get('source_sha256',{}).get(name)!=digest(HERE/name):raise RuntimeError('Proof source binding mismatch: '+name)
    expected=['KenomaLateralTransfer.'+name for name in THEOREMS]
    if [c.get('theorem') for c in proof.get('claims',[])]!=expected or any(c.get('status')!='checked' for c in proof['claims']):
        raise RuntimeError('All six actual kernel claims required')
    transcript=proof_path.with_name('lateral-transfer-lean.txt')
    if not transcript.is_file() or digest(transcript)!=proof.get('transcript_sha256'):
        raise RuntimeError('Actual source-bound kernel transcript required')
    for full in expected:
        m=re.search(rf"'{re.escape(full)}' (?:depends on axioms: \[([^\]]*)\]|does not depend on any axioms)",transcript.read_text())
        if not m or not {x.strip() for x in (m.group(1) or '').split(',') if x.strip()}<={'propext','Quot.sound','Classical.choice'}:
            raise RuntimeError('Missing/unsupported actual kernel dependency record')
    return audit,proof

def replace_block(body,name,text):
    pattern=r'<!-- '+name+r' -->[\s\S]*?<!-- /'+name+r' -->'
    body,count=re.subn(pattern,lambda _:text,body)
    if count!=1:raise RuntimeError('Unique HTML binding marker required: '+name)
    return body

def make_pdf(path,claims,proof,audit):
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,PageBreak,Preformatted,Flowable,KeepTogether
    font_root=Path('/usr/share/fonts/truetype/dejavu')
    for name,file in [('Body','DejaVuSans.ttf'),('Bold','DejaVuSans-Bold.ttf'),('Code','DejaVuSansMono.ttf')]:
        pdfmetrics.registerFont(TTFont(name,str(font_root/file)))
    pdfmetrics.registerFontFamily('Body',normal='Body',bold='Bold',italic='Body',boldItalic='Bold')
    width,height=A4;usable=width-84
    styles={
      'body':ParagraphStyle('body',fontName='Body',fontSize=11,leading=16,spaceAfter=8),
      'title':ParagraphStyle('title',fontName='Bold',fontSize=25,leading=30,spaceAfter=16),
      'h2':ParagraphStyle('h2',fontName='Bold',fontSize=15,leading=20,spaceBefore=16,spaceAfter=9),
      'h3':ParagraphStyle('h3',fontName='Bold',fontSize=12,leading=17,spaceBefore=10,spaceAfter=7),
      'code':ParagraphStyle('code',fontName='Code',fontSize=10,leading=14,spaceBefore=5,spaceAfter=10),
      'caption':ParagraphStyle('caption',fontName='Body',fontSize=10,leading=14,spaceAfter=8),
    }
    def inline(text):
        text=html.escape(text)
        text=re.sub(r'\[([^\]]+)\]\((https?://[^\s)]+)\)',lambda m:'<link href="'+m[2]+'" color="#205849">'+m[1]+'</link>',text)
        text=re.sub(r'\*\*([^*]+)\*\*',r'<b>\1</b>',text)
        text=re.sub(r'`([^`]+)`',r'<font name="Code">\1</font>',text)
        return text
    def code(text):
        # Preserve every source character; display wrapping adds only line breaks.
        lines=[];limit=int(usable/pdfmetrics.stringWidth('M','Code',10))
        for line in text.splitlines():
            if not line:lines.append('');continue
            while len(line)>limit:
                lines.append(line[:limit]);line=line[limit:]
            lines.append(line)
        return Preformatted('\n'.join(lines),styles['code'])
    class Diagram(Flowable):
        def __init__(self):super().__init__();self.width=usable;self.height=190
        def draw(self):
            c=self.canv;left=50;right=usable-65;upper_y=137;lower_y=60;offset=14
            c.setStrokeColor(colors.HexColor('#ba743e'));c.setLineWidth(2)
            c.line(left,upper_y,left+offset,lower_y);c.line(right+offset,upper_y,right+2*offset,lower_y)
            for x,y,w,fill,label in [(left,upper_y,right-left+offset,'#cae3d5','Upper guided element'),(left+offset,lower_y,right-left+offset,'#a7c8df','Lower guided element')]:
                c.setFillColor(colors.HexColor(fill));c.setStrokeColor(colors.HexColor('#47665a'))
                c.roundRect(x,y-13,w,26,5,stroke=1,fill=1)
                c.setFillColor(colors.HexColor('#172b37'));c.setFont('Body',11);c.drawCentredString(x+w/2,y-4,label)
            c.setFont('Body',11);c.setFillColor(colors.HexColor('#172b37'))
            for x,y,label in [(left,upper_y+27,'fixed: 0'),(right+offset,upper_y+27,'free: u'),(left+offset,lower_y-31,'free: v'),(right+2*offset,lower_y-31,'driven: δ')]:
                c.drawCentredString(x,y,label)
            for x,y in [(left,upper_y),(right+offset,upper_y),(left+offset,lower_y),(right+2*offset,lower_y)]:c.circle(x,y,3,fill=1,stroke=0)
            c.setFont('Body',10);c.drawCentredString(usable/2,4,'Schematic guided displacement graph; offsets exaggerated, not to scale.')
    story=[Paragraph('Lateral interface transfer',styles['title']),Paragraph('Standalone passive property lab · original authored macro-element fixture',styles['body']),Diagram(),Spacer(1,9)]
    story.append(Paragraph('Six fresh Real kernel claims at the exact included Lean source. This is standalone algebra, not integrated book or anatomical acceptance.',styles['body']))
    story.append(Paragraph('<link href="#statements" color="#205849">Complete statements</link> · <link href="#source" color="#205849">Exact source</link> · <link href="#audit" color="#205849">Bounded audit scope</link>',styles['body']))
    paragraph=[];code_lines=[]
    def flush():
        if paragraph:story.append(Paragraph(inline(' '.join(paragraph)),styles['body']));paragraph.clear()
        if code_lines:story.append(code('\n'.join(code_lines)));code_lines.clear()
    for line in (HERE/'chapter.md').read_text().splitlines():
        if not line.strip():flush()
        elif line.startswith('    '):
            if paragraph:story.append(Paragraph(inline(' '.join(paragraph)),styles['body']));paragraph.clear()
            code_lines.append(line[4:])
        elif line.startswith('#'):
            flush();level=len(line)-len(line.lstrip('#'));story.append(Paragraph(inline(line.lstrip('#').strip()),styles['h2' if level<3 else 'h3']))
        else:
            if code_lines:story.append(code('\n'.join(code_lines)));code_lines.clear()
            paragraph.append(line)
    flush()
    story.extend([PageBreak(),Paragraph('<a name="statements"/>Appendix: complete Real statements',styles['h2'])])
    for claim in claims:
        story.append(Paragraph(claim['title'],styles['h3']));story.append(code(claim['statement_lean']))
        story.append(Paragraph(inline(claim['limitations']),styles['caption']))
    story.extend([PageBreak(),Paragraph('<a name="source"/>Appendix: exact Lean source',styles['h2']),
      Paragraph('SHA-256: '+digest(HERE/'LateralInterfaceTransfer.lean'),styles['caption']),code((HERE/'LateralInterfaceTransfer.lean').read_text()),
      PageBreak(),Paragraph('<a name="audit"/>Appendix: standalone evidence scope',styles['h2'])])
    for text in [f"Audit: {audit['case_count']} independent rational state comparisons; six symbolic identity groups. No iterative solve or trajectory.",
      'Kernel: '+proof['lean_version']+'; mathlib '+PIN+'. Allowed transitive axioms are separately reported for each of six declarations.',
      'All six claims quantify Real values in this discrete guided model. Differentiation, continuum equilibrium, browser arithmetic, geometry, tissue calibration and biology are separate obligations.',
      'Source-ledger and full source/receipt downloads are bundled as relative files in the portable site. This PDF uses only internal appendix links and primary HTTP references.',
      'The current contribution does not change or qualify the integrated 115-declaration book, anatomy, saved trajectories or held research campaigns.']:
        story.append(Paragraph(inline(text),styles['body']))
    def footer(canvas,doc):
        canvas.setFont('Body',10);canvas.setFillColor(colors.HexColor('#536671'))
        canvas.drawString(42,24,'Kenoma · standalone discrete interface model');canvas.drawRightString(width-42,24,str(doc.page))
    doc=SimpleDocTemplate(str(path),pagesize=A4,rightMargin=42,leftMargin=42,topMargin=38,bottomMargin=42,title='Lateral interface transfer',author='Kenoma')
    doc.build(story,onFirstPage=footer,onLaterPages=footer)

def run(args):
    out=checked_output(args.output);audit,proof=bound_receipts(args.audit.resolve(),args.proof_receipt.resolve())
    claims=json.loads((HERE/'claims.json').read_text())
    for source in HERE.iterdir():
        if source.is_file():shutil.copyfile(source,out/source.name)
    body=(HERE/'index.html').read_text()
    status='Freshly checked: six Real declarations at Lean source SHA-256 '+digest(HERE/'LateralInterfaceTransfer.lean')+'. Standalone discrete algebra only; no certified differentiation, continuum, floating-point, anatomy or biology.'
    body=replace_block(body,'PROOF_STATUS',html.escape(status))
    cards=''.join('<details><summary>'+html.escape(c['title'])+'</summary><pre>'+html.escape(c['statement_lean'])+'</pre><p class="subtle">'+html.escape(c['limitations'])+'</p></details>' for c in claims)
    body=replace_block(body,'STATEMENTS',cards)
    body=replace_block(body,'LEAN_SOURCE','<pre>'+html.escape((HERE/'LateralInterfaceTransfer.lean').read_text())+'</pre>')
    (out/'index.html').write_text(body)
    shutil.copyfile(args.audit,out/'algebra-audit.json');shutil.copyfile(args.proof_receipt,out/'lateral-transfer-proof-status.json')
    shutil.copyfile(args.proof_receipt.with_name('lateral-transfer-lean.txt'),out/'lateral-transfer-lean.txt')
    make_pdf(out/'lateral-interface-transfer.pdf',claims,proof,audit)
    manifest={'status':'built','source_sha256':source_hashes(),'lean_source_sha256':digest(HERE/'LateralInterfaceTransfer.lean'),
      'audit_sha256':digest(args.audit),'proof_receipt_sha256':digest(args.proof_receipt),
      'git_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=HERE,text=True).strip(),
      'book_registered':False,'scope':'Portable standalone contribution only; no whole-book, anatomical or publication qualification.'}
    (out/'build-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    archive=out/'lateral-interface-transfer-portable.zip'
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
        for p in sorted(out.iterdir()):
            if p.is_file() and p!=archive:z.write(p,p.name)
    print('Built source-bound standalone HTML, PDF and portable ZIP outside Git.')

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True)
    p.add_argument('--audit',type=Path,required=True);p.add_argument('--proof-receipt',type=Path,required=True)
    run(p.parse_args())
