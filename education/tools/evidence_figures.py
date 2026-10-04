"""Print-sized derivatives of the licensed original data figures; no data edits."""
from pathlib import Path
import hashlib,json,re,xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[1]
NS='http://www.w3.org/2000/svg'
ET.register_namespace('',NS);ET.register_namespace('xlink','http://www.w3.org/1999/xlink')
def tag(name):return '{'+NS+'}'+name
def text(parent,x,y,value,size=18):
    node=ET.SubElement(parent,tag('text'),{'x':str(x),'y':str(y),'style':f'font-size:{size}px;font-family:Arial,sans-serif;fill:#152e41'})
    node.text=value
def generate(out):
    provenance=[]
    for kind in ['bodyparts3d_right_arm','openarm_recorded_trial']:
        source=ROOT/'data/elbow-v1/figures'/f'{kind}.svg';svg=ET.fromstring(source.read_text())
        figure=svg.find(tag('g'));assert figure.attrib['id']=='figure_1'
        if kind=='bodyparts3d_right_arm':
            legend=next(x for x in figure if x.attrib.get('id')=='legend_1')
            labels=[x.text for x in legend.iter(tag('text'))]
            colors=[re.search(r'fill:\s*(#[0-9a-f]+)',x.attrib['style'])[1] for x in legend.iter(tag('path'))]
            assert len(labels)==len(colors)==10
            figure.remove(legend)
            for child in list(figure):
                if child.attrib.get('id','').startswith('text_'):figure.remove(child)
            text(figure,40,32,'A static right arm anatomical reference',22)
            text(figure,40,59,'BodyParts3D 4.0 · original atlas pose · explanatory colors',17)
            for i,(label,color) in enumerate(zip(labels,colors)):
                x=45+(i//5)*345;y=455+(i%5)*29
                ET.SubElement(figure,tag('rect'),{'x':str(x),'y':str(y-14),'width':'20','height':'14','fill':color})
                text(figure,x+30,y,label)
            svg.set('viewBox','0 0 720 600');svg.set('height','600pt')
        else:
            for child in list(figure):
                if child.attrib.get('id') in ['text_28','text_29']:figure.remove(child)
            for node in figure.iter(tag('text')):
                if node.text=='Normalized (1)':
                    node.text='Unit 1';node.set('x','20')
                    node.set('transform',f'rotate(-90 20 {node.attrib["y"]})')
                if node.text and node.text.startswith('OpenArm Multisensor 2.0  |'):
                    node.text='OpenArm 2.0 · participant 2 / trial 1b · 90° hold'
            svg.set('viewBox','0 0 720 430');svg.set('height','430pt')
        # Tick labels and titles retain their original positions; all are at least 18px.
        for node in figure.iter(tag('text')):
            style=node.attrib.get('style','')
            node.set('style',re.sub(r'font-size:\s*([0-9.]+)px',lambda m:f'font-size: {max(18,float(m[1])):g}px',style))
        name='atlas-print.svg' if kind=='bodyparts3d_right_arm' else 'recording-print.svg'
        (out/name).write_bytes(ET.tostring(svg,encoding='utf-8',xml_declaration=True))
        provenance.append({'figure':name,'source':str(source.relative_to(ROOT)),'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
          'license':'CC BY 4.0','changes':'Larger labels, reflowed atlas legend, removed redundant in-image footer; source geometry/trace paths unchanged. Full attribution and caveats remain in adjacent book prose.','minimum_source_font_px':18})
    (out/'evidence-figure-provenance.json').write_text(json.dumps(provenance,indent=2)+'\n')
