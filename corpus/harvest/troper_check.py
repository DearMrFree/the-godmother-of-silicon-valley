import json,re,sys,time
sys.path.insert(0,'.')
import verify
from concurrent.futures import ThreadPoolExecutor
C={}
for v in json.load(open('gn_dec.json')).values():
    if v['url']:C.setdefault(v['url'],dict(url=v['url'],title=v['title'],src='gnews',gdate=v['gdate'],source=v['source']))
for u in open('web.txt').read().split():C.setdefault(u,dict(url=u,title='',src='web'))
for v in json.load(open('yt_mt.json')).values():
    if re.search(r'troper|marco|son|wojcicki',v['title'],re.I) and re.search(r'susan|troper|marco|esther',v['title'],re.I) and re.search(r'ago',v.get('ago','')) and re.search(r'(2|1) year|month',v.get('ago','')):
        C.setdefault('https://www.youtube.com/watch?v='+v['id'],dict(url='https://www.youtube.com/watch?v='+v['id'],title=v['title'],src='youtube',channel=v['channel']))
print(len(C),flush=True)
MARCO=re.compile(r'Marco\s+Troper|\bTroper\b|Марко\s+Тропер|马可.{0,2}特罗珀|马尔科.{0,2}特罗珀|マルコ.{0,3}トロパー|마르코\s*트로퍼',re.I)
FC=re.compile(r'Cheteni',re.I)
def run(c):
    o=dict(c)
    try:
        st,fu,ct,b=verify.fetch(c['url']);t,tx=verify.text(b,ct)
        if 'youtube.com/watch' in c['url']:
            raw=b.decode('utf8','replace');m=re.search(r'"shortDescription":"((?:[^"\\]|\\.)*)"',raw)
            tx=(json.loads('"'+m[1]+'"') if m else '')+' '+t;d=re.search(r'"publishDate":"([^"]+)"',raw);o['date']=d[1][:10] if d else ''
            ch=re.search(r'"ownerChannelName":"([^"]*)"',raw);o['channel']=ch[1] if ch else o.get('channel','')
        else:o['date']=verify.date(b)
        o.update(ok=True,status=st,final=fu,page_title=t[:300],words=len(tx.split()),marco=len(MARCO.findall(tx+' '+t)),fc=len(FC.findall(tx)),esther=len(verify.NAME.findall(tx)))
        for k,R in (('fcctx',FC),('ectx',verify.NAME)):
            m=R.search(tx);o[k]=tx[max(0,m.start()-250):m.end()+250] if m else ''
    except Exception as e:o.update(ok=False,err=str(e)[:120])
    return o
R=[]
with ThreadPoolExecutor(8) as ex:
    for i,o in enumerate(ex.map(run,C.values())):
        R.append(o)
        if i%25==0:print(i,flush=True)
json.dump(R,open('checked.json','w'),ensure_ascii=False,indent=0)
ok=[r for r in R if r.get('ok')]
print('opened',len(ok),'of',len(R),'| name Marco',sum(1 for r in ok if r['marco']),'| Cheteni',sum(1 for r in ok if r['fc']),'| Esther',sum(1 for r in ok if r['esther']))
