import urllib.request,urllib.parse,json,re,time,html,subprocess,datetime,threading
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor
BUA={'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126 Safari/537.36','Accept-Language':'en-US'}
def g(u,t=30,data=None,h={}):return urllib.request.urlopen(urllib.request.Request(u,headers={**BUA,**h},data=data),timeout=t).read().decode('utf8','replace')
C={};L=threading.Lock()
def add(u,t,s,d='',sn=''):
    if u and u.startswith('http'):
        with L:C.setdefault(u,dict(url=u,title=html.unescape(t or '').strip(),src=s,date=d,snip=sn))
def save(tag):
    with L:json.dump(list(C.values()),open('cands6.json','w'),ensure_ascii=False)
    print(tag,len(C),flush=True)
EN='"Godmother of Silicon Valley"'
PH=[EN,'"Silicon Valley\'s godmother"','"Silicon Valley godmother"','"godmother of the Silicon Valley"','"Patin des Silicon Valley"','"Patentante des Silicon Valley"','"Matka chrzestna Doliny Krzemowej"','"matką chrzestną Doliny Krzemowej"','"madrina de Silicon Valley"','"madrina del Silicon Valley"','"madrina de Sillicon Valley"','"marraine de la Silicon Valley"','"madrina della Silicon Valley"','"madrinha do Vale do Silício"','"madrinha de Silicon Valley"','"крестная мать Кремниевой долины"','"крёстная мать Кремниевой долины"','"硅谷教母"','"矽谷教母"','"シリコンバレーのゴッドマザー"','"실리콘밸리의 대모"','"Silikon Vadisi\'nin vaftiz annesi"','"Nașa Silicon Valley"','"peetmoeder van Silicon Valley"','"gudmor"  "Silicon Valley"','"Ibu baptis Silicon Valley"','"Mẹ đỡ đầu của Thung lũng Silicon"']
# GDELT quarterly for English phrase, plus 1 pass of others
for yr in range(2017,2027):
  for s,e in (('0101','0630'),('0701','1231')):
    try:
        for a in json.loads(g(f'https://api.gdeltproject.org/api/v2/doc/doc?query={urllib.parse.quote(EN)}&mode=ArtList&maxrecords=250&format=json&startdatetime={yr}{s}000000&enddatetime={yr}{e}235959')).get('articles',[]):add(a['url'],a['title'],'gdelt',a.get('seendate','')[:8])
    except Exception as ex:print('gdelt',ex)
    time.sleep(6)
save('gdelt')
# Google News
raw={}
def gn(q,hl='en-US',gl='US',ce='US:en'):
    for it in ET.fromstring(g('https://news.google.com/rss/search?'+urllib.parse.urlencode(dict(q=q,hl=hl,gl=gl,ceid=ce)))).findall('.//item'):
        raw[it.findtext('link')]=(it.findtext('title'),it.findtext('pubDate'),it.findtext('source'))
d0=datetime.date(2019,1,1)
while d0<datetime.date(2026,12,1):
    d1=(d0.replace(day=28)+datetime.timedelta(days=5)).replace(day=1)
    try:gn(f'{EN} after:{d0} before:{d1}')
    except Exception as ex:print(ex);time.sleep(15)
    time.sleep(1.2);d0=d1
for p in PH:
    for loc in (('en-US','US','US:en'),):
        try:gn(p,*loc)
        except Exception as ex:print(ex)
        time.sleep(1)
for loc,p in ((('de','DE','DE:de'),'"Patin des Silicon Valley"'),(('pl','PL','PL:pl'),'"Doliny Krzemowej" matka chrzestna Wojcicki'),(('es-419','MX','MX:es-419'),'madrina Silicon Valley Wojcicki'),(('es','ES','ES:es'),'madrina Silicon Valley Wojcicki'),(('fr','FR','FR:fr'),'marraine Silicon Valley Wojcicki'),(('it','IT','IT:it'),'madrina Silicon Valley Wojcicki'),(('pt-BR','BR','BR:pt-419'),'madrinha Vale do Silício Wojcicki'),(('ru','RU','RU:ru'),'крестная мать Кремниевой долины Воджицки'),(('zh-TW','TW','TW:zh-Hant'),'矽谷教母'),(('zh-CN','CN','CN:zh-Hans'),'硅谷教母'),(('ja','JP','JP:ja'),'シリコンバレー ゴッドマザー ウォジスキ'),(('ko','KR','KR:ko'),'실리콘밸리 대모 워치츠키'),(('en-GB','GB','GB:en'),EN),(('en-IN','IN','IN:en'),EN),(('en-AU','AU','AU:en'),EN),(('en-CA','CA','CA:en'),EN)):
    try:gn(p,*loc)
    except Exception as ex:print(ex)
    time.sleep(1)
json.dump(raw,open('gnews6_raw.json','w'));print('gn raw',len(raw),flush=True)
def dec(l):
    aid=l.split('/articles/')[1].split('?')[0]
    b=g(f'https://news.google.com/rss/articles/{aid}')
    sg=re.search(r'data-n-a-sg="([^"]+)"',b).group(1);ts=re.search(r'data-n-a-ts="([^"]+)"',b).group(1)
    payload=[[["Fbv4je",json.dumps(["garturlreq",[["X","X",["X","X"],None,None,1,1,"US:en",None,1,None,None,None,None,None,0,1],"X","X",1,[1,1,1],1,1,None,0,0,None,0],aid,int(ts),sg]),None,"generic"]]]
    r=g('https://news.google.com/_/DotsSplashUi/data/batchexecute',data=urllib.parse.urlencode({'f.req':json.dumps(payload)}).encode(),h={'Content-Type':'application/x-www-form-urlencoded;charset=UTF-8'})
    return json.loads(json.loads(r.split('\n\n')[1])[0][2])[1]
prev=json.load(open('gnews_dec.json'))
fails=0
for l,(t,d,s) in raw.items():
    if l in prev:add(prev[l].get('url'),(t or '').rsplit(' - ',1)[0],'gnews',d,s);continue
    try:add(dec(l),(t or '').rsplit(' - ',1)[0],'gnews',d,s);fails=0
    except Exception as ex:
        fails+=1;print('dec',str(ex)[:60],flush=True);time.sleep(40)
        if fails>10:break
    time.sleep(3)
save('gnews')
# iTunes, HN, Wikipedia, IA
for term in ['Godmother of Silicon Valley','Silicon Valley godmother','godmother silicon valley wojcicki']:
    for r in json.loads(g('https://itunes.apple.com/search?'+urllib.parse.urlencode(dict(term=term,entity='podcastEpisode',limit=200))))['results']:
        tx=(r.get('trackName')or'')+' '+(r.get('description')or'')
        if re.search('godmother',tx,re.I):add(r.get('trackViewUrl'),r.get('trackName'),'itunes',(r.get('releaseDate')or'')[:10],r.get('collectionName')or'')
    time.sleep(3)
try:
    for h in json.loads(g(f'https://hn.algolia.com/api/v1/search?query={urllib.parse.quote(EN)}&hitsPerPage=100'))['hits']:add(h.get('url') or f"https://news.ycombinator.com/item?id={h['objectID']}",h.get('title') or h.get('story_title'),'hackernews',(h.get('created_at')or'')[:10])
except Exception as ex:print(ex)
for l in 'en de fr es it pt pl ru zh ja ko'.split():
    try:
        for h in json.loads(g(f'https://{l}.wikipedia.org/w/api.php?action=query&list=search&srsearch={urllib.parse.quote(EN)}&format=json&srlimit=50'))['query']['search']:add(f'https://{l}.wikipedia.org/wiki/'+urllib.parse.quote(h['title'].replace(' ','_')),h['title'],'wikipedia')
    except Exception as ex:print('w',l,str(ex)[:40])
    time.sleep(3)
for be in ('fts','tvs','rcs','metadata'):
    try:
        for p in (1,2,3):
            hs=json.loads(g(f'https://archive.org/services/search/beta/page_production/?user_query={urllib.parse.quote(EN)}&hits_per_page=100&page={p}&service_backend={be}'))['response']['body']['hits']['hits']
            if not hs:break
            for h in hs:
                f=h.get('fields',{})
                if f.get('identifier'):add('https://archive.org/details/'+f['identifier'],f.get('title') if isinstance(f.get('title'),str) else '','archive.org-'+be,str(f.get('date')or'')[:10])
    except Exception as ex:print('ia',be,str(ex)[:50])
save('misc')
# YouTube
for term in ['"Godmother of Silicon Valley"','Godmother of Silicon Valley Esther Wojcicki','Godmother of Silicon Valley interview','Godmother of Silicon Valley podcast','Godmother of Silicon Valley parenting','Godmother of Silicon Valley keynote','Godmother of Silicon Valley AI education','Godmother of Silicon Valley documentary film','Godmother of Silicon Valley trailer','Patin des Silicon Valley','madrina de Silicon Valley','Matka chrzestna Doliny Krzemowej','硅谷教母','实力教母 硅谷 沃西基','крестная мать Кремниевой долины','실리콘밸리의 대모','シリコンバレーのゴッドマザー']:
    try:
        o=subprocess.run(['ytv/bin/yt-dlp','--flat-playlist','-J','--no-warnings',f'ytsearch100:{term}'],capture_output=True,timeout=200).stdout
        for e in json.loads(o).get('entries',[]):add('https://www.youtube.com/watch?v='+e['id'],e.get('title'),'youtube')
    except Exception as ex:print('yt',str(ex)[:50])
    time.sleep(2)
save('yt')
# DDG
Q=[EN]+[f'{EN} {v}' for v in 'Esther Wojcicki|interview|podcast|parenting|book|film|documentary|Poland|keynote|speaker|conference|summit|AI|education|teacher|journalism|Forbes|Fortune|CNBC|Business Insider|Time|Guardian|Times|Substack|Medium|blog|LinkedIn|Facebook|Instagram|Reddit|YouTube|TikTok|X Twitter|university|school|award|festival|press release|Mexico|Spain|Germany|Italy|India|China|Japan|Korea|Brazil|Dubai|Kazakhstan|Turkey|Israel|magazine|newspaper|radio|TV|video|review|opinion'.split('|')]+PH[1:]
empt=0
for q in Q:
    try:
        b=g('https://html.duckduckgo.com/html/?'+urllib.parse.urlencode(dict(q=q)))
        rs=re.findall(r'class="result__a"\s+href="([^"]+)"[^>]*>(.*?)</a>',b,re.S)
        if not rs:empt+=1;time.sleep(60)
        for h,t in rs:
            m=re.search(r'uddg=([^&]+)',h);add(urllib.parse.unquote(m.group(1)) if m else h,re.sub('<[^>]+>','',t),'ddg')
    except Exception as ex:print('ddg',str(ex)[:50]);time.sleep(40)
    if empt>10:print('ddg stop');break
    time.sleep(8)
save('ddg');print('END')
