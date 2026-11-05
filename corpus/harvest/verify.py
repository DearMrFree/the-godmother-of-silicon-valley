import json,re,sys,os,html,hashlib,urllib.request,urllib.parse,subprocess,tempfile,ssl,gzip,time
from concurrent.futures import ThreadPoolExecutor,as_completed
UA={'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126 Safari/537.36','Accept':'text/html,application/xhtml+xml,application/pdf,*/*','Accept-Language':'en-US,en;q=0.8','Accept-Encoding':'gzip'}
NAME=re.compile(r"Esther\s+(?:[A-Z]\.?\s+)?(?:\"Woj\"\s+|Denise\s+|Hochman\s+)?Wojcicki|Wojcicki,\s*Esther|Esther\s+\W*Woj\W*\s+Wojcicki|Эстер\s+Воджицки|Эстер\s+Войджицки|埃丝特.{0,2}沃西基|エスター.{0,2}ウォジスキ|에스더\s*워치츠키|אסתר\s+וויצ'יצקי|Ester\s+Wojcicki|Esther\s+Wojicki|Esther\s+Wojciki",re.I)
ctx=ssl.create_default_context();ctx.check_hostname=False;ctx.verify_mode=ssl.CERT_NONE
def fetch(u):
    r=urllib.request.urlopen(urllib.request.Request(u,headers=UA),timeout=25,context=ctx)
    b=r.read(15_000_000)
    if r.headers.get('Content-Encoding')=='gzip':b=gzip.decompress(b)
    return r.status,r.geturl(),r.headers.get('Content-Type',''),b
def text(b,ct):
    if 'pdf' in ct or b[:4]==b'%PDF':
        with tempfile.NamedTemporaryFile(suffix='.pdf') as f:
            f.write(b);f.flush()
            try:return '',subprocess.run(['pdftotext','-q',f.name,'-'],capture_output=True,timeout=60).stdout.decode('utf8','replace')
            except Exception:return '',''
    s=b.decode('utf8','replace')
    m=re.search(r'<title[^>]*>(.*?)</title>',s,re.S|re.I);t=html.unescape(re.sub(r'\s+',' ',m.group(1))).strip() if m else ''
    metas=' '.join(re.findall(r'<meta[^>]+content="([^"]{0,800})"',s))
    body=re.sub(r'(?is)<(script|style|noscript|svg).*?</\1>',' ',s)
    ld=' '.join(re.findall(r'(?is)<script[^>]+ld\+json[^>]*>(.*?)</script>',s))
    nd=' '.join(re.findall(r'(?is)<script[^>]+__NEXT_DATA__[^>]*>(.*?)</script>',s))
    body=html.unescape(re.sub(r'<[^>]+>',' ',body))
    return t,re.sub(r'\s+',' ',body)+' '+html.unescape(metas)+' '+ld[:200000]+' '+nd[:300000]
def date(b):
    s=b[:300000].decode('utf8','replace')
    for p in (r'article:published_time"\s+content="(\d{4}-\d\d-\d\d)',r'content="(\d{4}-\d\d-\d\d)[^"]*"\s+(?:property|name)="article:published_time',r'"datePublished"\s*:\s*"(\d{4}-\d\d-\d\d)',r'name="(?:date|pubdate|publish-date|DC.date)"\s+content="(\d{4}-\d\d-\d\d)',r'<time[^>]+datetime="(\d{4}-\d\d-\d\d)'):
        m=re.search(p,s)
        if m:return m.group(1)
    return ''
def one(c):
    o=dict(c)
    try:
        st,fu,ct,b=fetch(c['url'])
        t,tx=text(b,ct)
        if 'youtube.com/watch' in c['url']:
            raw=b.decode('utf8','replace')
            m1=re.search(r'"shortDescription":"((?:[^"\\\\]|\\\\.)*)"',raw)
            ot=re.search(r'<meta name="title" content="([^"]*)"',raw)
            ch=re.search(r'"ownerChannelName":"([^"]*)"',raw)
            dt=re.search(r'"publishDate":"(\d{4}-\d\d-\d\d)',raw)
            t=html.unescape(ot.group(1)) if ot else t
            tx=t+' '+(m1.group(1).replace('\\n',' ') if m1 else '')
            o['channel']=ch.group(1) if ch else ''
            o['ydate']=dt.group(1) if dt else ''
        m=NAME.search(tx)
        ws=len(tx.split())
        o.update(http=st,final=fu,ctype=ct.split(';')[0],page_title=t,words=ws,found=bool(m),hits=len(NAME.findall(tx)),hash=hashlib.sha1(re.sub(r'\W+','',tx.lower())[:20000].encode()).hexdigest(),pdate=date(b) if 'pdf' not in ct else '')
        if m:o['ctx']=tx[max(0,m.start()-300):m.end()+300]   # kept locally for classification only
    except urllib.error.HTTPError as e:o.update(http=e.code,found=False,err='http')
    except Exception as e:o.update(http=0,found=False,err=str(e)[:80])
    return o
if __name__=='__main__':
    inp,out=sys.argv[1],sys.argv[2]
    done={}
    if os.path.exists(out):done={x['url']:x for x in json.load(open(out))}
    todo=[c for c in json.load(open(inp)) if c['url'] not in done]
    print('todo',len(todo),flush=True)
    with ThreadPoolExecutor(16) as ex:
        fs=[ex.submit(one,c) for c in todo]
        for i,f in enumerate(as_completed(fs)):
            r=f.result();done[r['url']]=r
            if i%200==199:
                json.dump(list(done.values()),open(out,'w'),ensure_ascii=False);print(i,sum(x['found'] for x in done.values()),flush=True)
    json.dump(list(done.values()),open(out,'w'),ensure_ascii=False)
    print('done',len(done),'found',sum(x['found'] for x in done.values()))
