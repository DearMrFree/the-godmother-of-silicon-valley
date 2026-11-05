import urllib.request,urllib.parse,json,re,time,sys
import xml.etree.ElementTree as ET
BUA={'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126 Safari/537.36','Accept-Language':'en-US'}
def g(u,data=None,h={}):
    return urllib.request.urlopen(urllib.request.Request(u,headers={**BUA,**h},data=data),timeout=30).read().decode('utf8','replace')
raw=json.load(open('gnews_raw.json'))
Q='"Esther Wojcicki"'
for v in []:
    for extra in ('','when:1y'):
      try:
        for it in ET.fromstring(g('https://news.google.com/rss/search?'+urllib.parse.urlencode(dict(q=f'{Q} {v} {extra}'.strip(),hl='en-US',gl='US',ceid='US:en')))).findall('.//item'):
            raw[it.findtext('link')]=(it.findtext('title'),it.findtext('pubDate'),it.findtext('source'))
      except Exception as e:print(v,e)
      time.sleep(1)
for hl,gl,ce in ():
    try:
        for it in ET.fromstring(g('https://news.google.com/rss/search?'+urllib.parse.urlencode(dict(q=Q,hl=hl,gl=gl,ceid=ce)))).findall('.//item'):
            raw[it.findtext('link')]=(it.findtext('title'),it.findtext('pubDate'),it.findtext('source'))
    except Exception as e:print(hl,e)
    time.sleep(1)
json.dump(raw,open('gnews_raw.json','w'));print('raw',len(raw),flush=True)
def dec(l):
    aid=l.split('/articles/')[1].split('?')[0]
    b=g(f'https://news.google.com/rss/articles/{aid}')
    sg=re.search(r'data-n-a-sg="([^"]+)"',b).group(1);ts=re.search(r'data-n-a-ts="([^"]+)"',b).group(1)
    payload=[[["Fbv4je",json.dumps(["garturlreq",[["X","X",["X","X"],None,None,1,1,"US:en",None,1,None,None,None,None,None,0,1],"X","X",1,[1,1,1],1,1,None,0,0,None,0],aid,int(ts),sg]),None,"generic"]]]
    r=g('https://news.google.com/_/DotsSplashUi/data/batchexecute',data=urllib.parse.urlencode({'f.req':json.dumps(payload)}).encode(),h={'Content-Type':'application/x-www-form-urlencoded;charset=UTF-8'})
    j=json.loads(r.split('\n\n')[1])
    return json.loads(j[0][2])[1]
out={}
try:out=json.load(open('gnews_dec.json'))
except Exception:pass
fails=0
for l,(t,d,s) in raw.items():
    if l in out:continue
    try:
        out[l]=dict(url=dec(l),title=t,gdate=d,source=s);fails=0
    except Exception as e:
        fails+=1;print('fail',str(e)[:80],flush=True)
        if fails>10:print('stopping');break
        time.sleep(60)
    time.sleep(3)
    if len(out)%25==0:json.dump(out,open('gnews_dec.json','w'));print(len(out),flush=True)
json.dump(out,open('gnews_dec.json','w'));print('end',len(out))
