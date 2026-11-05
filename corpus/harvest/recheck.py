import json,re,sys,os,glob,html
from concurrent.futures import ThreadPoolExecutor,as_completed
sys.path.insert(0,'.')
import verify
GM=re.compile(r"god\s?mother\s+of\s+(?:the\s+)?(?:modern\s+)?silicon\s+valley|silicon\s+valley(?:'s|’s)?\s+god\s?mother|Patin\s+des\s+Silicon\s+Valley|Patentante\s+des\s+Silicon\s+Valley|matk\w+\s+chrzestn\w+\s+Doliny\s+Krzemowej|madrina\s+(?:de|del|della|di)\s+(?:la\s+)?S[il]+icon\s+Valley|marraine\s+de\s+(?:la\s+)?Silicon\s+Valley|madrinha\s+d[eo]\s+(?:Vale\s+do\s+Silício|Silicon\s+Valley)|кр[её]стн\w+\s+мат\w+\s+Кремниевой\s+долины|硅谷教母|矽谷教母|シリコンバレーのゴッドマザー|실리콘\s?밸리의\s*대모|peetmoeder\s+van\s+Silicon\s+Valley|Silikon\s+Vadisi.{0,6}vaftiz\s+annesi|Mẹ\s+đỡ\s+đầu\s+của\s+Thung\s+lũng\s+Silicon",re.I)
SUR=re.compile(r"Wojcicki|Wojicki|Wojciki|Воджицки|Войджицки|Войцицки|Войжицки|沃西基|沃西奇|ウォジスキ|ウォシッキ|워치츠키|보이치키|Woj\b",re.I)
_text=verify.text
def text2(b,ct):
    t,tx=_text(b,ct);text2.last=None;return t,tx
def one(c):
    # re-run the page text extraction, adding nickname and surname checks
    o=dict(c)
    try:
        st,fu,ct,b=verify.fetch(c['url']);t,tx=verify.text(b,ct)
        if 'youtube.com/watch' in c['url']:
            raw=b.decode('utf8','replace')
            m1=re.search(r'"shortDescription":"((?:[^"\\]|\\.)*)"',raw);ot=re.search(r'<meta name="title" content="([^"]*)"',raw)
            ch=re.search(r'"ownerChannelName":"([^"]*)"',raw);dt=re.search(r'"publishDate":"(\d{4}-\d\d-\d\d)',raw)
            t=html.unescape(ot.group(1)) if ot else t;tx=t+' '+(m1.group(1).replace('\\n',' ') if m1 else '')
            o['channel']=ch.group(1) if ch else '';o['ydate']=dt.group(1) if dt else ''
        import hashlib
        m=verify.NAME.search(tx);g=GM.search(tx);s=SUR.search(tx)
        o.update(http=st,final=fu,ctype=ct.split(';')[0],page_title=t,words=len(tx.split()),hits=len(verify.NAME.findall(tx)),found_now=bool(m),gm=bool(g),sur=bool(s),gmhits=len(GM.findall(tx)),ok=True,pdate=o.get('pdate') or (verify.date(b) if 'pdf' not in ct else ''),hash=hashlib.sha1(re.sub(r'\W+','',tx.lower())[:20000].encode()).hexdigest())
        if m:o['ctx']=tx[max(0,m.start()-300):m.end()+300]
        if g:o['gmctx']=tx[max(0,g.start()-200):g.end()+200]
    except Exception as e:o.update(ok=False,gm=False,sur=False,err2=str(e)[:80])
    return o
inp=[]
if __name__=='__main__':
    C={}
    for f in ('v1.json','v2.json','v4.json','v5.json'):
        for x in json.load(open(f)):C[x['url']]=x
    for x in json.load(open('cands6.json')):C.setdefault(x['url'],{**x,'found':False,'new6':True})
    for u in (open('ws6.txt').read()+open('ws7.txt').read()).split():C.setdefault(u,dict(url=u,title='',src='websearch',date='',snip='',found=False,new6=True))
    out={}
    if os.path.exists('r6.json'):out={x['url']:x for x in json.load(open('r6.json'))}
    todo=[c for u,c in C.items() if u not in out];print('todo',len(todo),flush=True)
    with ThreadPoolExecutor(16) as ex:
        fs=[ex.submit(one,c) for c in todo]
        for i,f in enumerate(as_completed(fs)):
            r=f.result();out[r['url']]=r
            if i%300==299:json.dump(list(out.values()),open('r6.json','w'),ensure_ascii=False);print(i,sum(x['gm'] for x in out.values()),flush=True)
    json.dump(list(out.values()),open('r6.json','w'),ensure_ascii=False);print('done',len(out),'gm',sum(x['gm'] for x in out.values()))
