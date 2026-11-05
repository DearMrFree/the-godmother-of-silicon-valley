import urllib.request,urllib.parse,json,re,time
import xml.etree.ElementTree as ET
BUA={'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126 Safari/537.36','Accept-Language':'en-US'}
def g(u,data=None,h={}):
    return urllib.request.urlopen(urllib.request.Request(u,headers={**BUA,**h},data=data),timeout=30).read().decode('utf8','replace')
raw={}
Qs=['"Marco Troper"','"Marco Troper" Berkeley','"Marco Troper" Wojcicki','"Marco Troper" overdose','"Marco Troper" memorial','"Marco Troper" Cheteni','Susan Wojcicki son died Berkeley','Susan Wojcicki son Marco','"Troper" Wojcicki grandson','Esther Wojcicki grandson Marco','Esther Wojcicki grandson death','Esther Wojcicki Marco drugs']
for q in Qs:
  for hl,gl,ce in [('en-US','US','US:en'),('en-GB','GB','GB:en'),('en-IN','IN','IN:en')]+([('es-419','US','US:es-419'),('pt-BR','BR','BR:pt-419'),('de','DE','DE:de'),('fr','FR','FR:fr'),('it','IT','IT:it'),('pl','PL','PL:pl'),('ja','JP','JP:ja'),('ko','KR','KR:ko'),('zh-TW','TW','TW:zh-Hant'),('he','IL','IL:he'),('ru','RU','RU:ru')] if q=='"Marco Troper"' else []):
    try:
        for it in ET.fromstring(g('https://news.google.com/rss/search?'+urllib.parse.urlencode(dict(q=q,hl=hl,gl=gl,ceid=ce)))).findall('.//item'):
            raw[it.findtext('link')]=(it.findtext('title'),it.findtext('pubDate'),it.findtext('source'))
    except Exception as e:print(q,hl,e)
    time.sleep(1)
  print(q,len(raw),flush=True)
json.dump(raw,open('gn_raw.json','w'))
def dec(l):
    aid=l.split('/articles/')[1].split('?')[0]
    b=g(f'https://news.google.com/rss/articles/{aid}')
    sg=re.search(r'data-n-a-sg="([^"]+)"',b).group(1);ts=re.search(r'data-n-a-ts="([^"]+)"',b).group(1)
    payload=[[["Fbv4je",json.dumps(["garturlreq",[["X","X",["X","X"],None,None,1,1,"US:en",None,1,None,None,None,None,None,0,1],"X","X",1,[1,1,1],1,1,None,0,0,None,0],aid,int(ts),sg]),None,"generic"]]]
    r=g('https://news.google.com/_/DotsSplashUi/data/batchexecute',data=urllib.parse.urlencode({'f.req':json.dumps(payload)}).encode(),h={'Content-Type':'application/x-www-form-urlencoded;charset=UTF-8'})
    return json.loads(json.loads(r.split('\n\n')[1])[0][2])[1]
out={};fails=0
for l,(t,d,s) in raw.items():
    try:out[l]=dict(url=dec(l),title=t,gdate=d,source=s);fails=0
    except Exception as e:
        fails+=1;out[l]=dict(url='',title=t,gdate=d,source=s);print('fail',str(e)[:60],flush=True);time.sleep(5)
        if fails>15:break
    time.sleep(.6)
json.dump(out,open('gn_dec.json','w'),ensure_ascii=False,indent=0)
print('decoded',sum(1 for v in out.values() if v['url']),'of',len(raw))
