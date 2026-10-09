"""Shared HTML closure, numerical comparison and control-audit helpers."""
from html.parser import HTMLParser

class Links(HTMLParser):
    def __init__(self,text):super().__init__();self.urls=[];self.ids=set();self.scripts=[];self.feed(text)
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if 'id' in a:self.ids.add(a['id'])
        for k in ['href','src']:
            if k in a:self.urls.append(a[k])
        if tag=='script':self.scripts.append(a)

def near(a,b,t=1e-9):assert abs(a-b)<=t*max(1,abs(a),abs(b)),(a,b)

def parameter(page,key,value):
    x=page.locator('[data-param="'+key+'"]')
    if x.evaluate('(e)=>e.tagName')=='SELECT':x.select_option(str(value));x.dispatch_event('input')
    else:x.fill(str(value));x.dispatch_event('input')

def minimum(document):
    return min(s['size'] for p in document for b in p.get_text('dict')['blocks'] for l in b.get('lines',[]) for s in l['spans'] if s['text'].strip())
