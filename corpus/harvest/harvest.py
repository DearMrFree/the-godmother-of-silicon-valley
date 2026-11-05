import urllib.request,urllib.parse,json,re,time,html,sys,datetime
import xml.etree.ElementTree as ET
UA={'User-Agent':'GodmotherArchive/1.0 (research corpus)'}
def g(u,t=40):
    r=urllib.request.urlopen(urllib.request.Request(u,headers=UA),timeout=t);return r.read().decode('utf8','replace')
C={}
def add(url,title,src,date='',snip=''):
    if not url or not url.startswith('http'):return
    if url not in C:C[url]=dict(url=url,title=html.unescape(title or '').strip(),src=src,date=date,snip=snip)
def save():json.dump(list(C.values()),open('cands.json','w'),ensure_ascii=False,indent=0);print('total',len(C),flush=True)
Q='"Esther Wojcicki"';q=urllib.parse.quote(Q)
# GDELT by quarter
y=2017
for yr in range(2017,2027):
  for s,e in (('0101','0331'),('0401','0630'),('0701','0930'),('1001','1231')):
    u=f'https://api.gdeltproject.org/api/v2/doc/doc?query={q}&mode=ArtList&maxrecords=250&format=json&startdatetime={yr}{s}000000&enddatetime={yr}{e}235959'
    try:
        for a in json.loads(g(u)).get('articles',[]):add(a['url'],a['title'],'gdelt',a.get('seendate','')[:8])
    except Exception as ex:print('gdelt',yr,s,ex)
    time.sleep(6)
save()
# Wikipedia many languages
for l in 'en de fr es it pt ru zh ja ko ar he pl nl sv tr uk fa id vi cs hu ro fi no da'.split():
    try:
        d=json.loads(g(f'https://{l}.wikipedia.org/w/api.php?action=query&list=search&srsearch={q}&format=json&srlimit=100'))
        for h in d['query']['search']:add(f'https://{l}.wikipedia.org/wiki/'+urllib.parse.quote(h['title'].replace(' ','_')),h['title'],'wikipedia')
    except Exception as ex:print('wiki',l,ex)
save()
# HN
for p in range(5):
    d=json.loads(g(f'https://hn.algolia.com/api/v1/search?query={q}&hitsPerPage=100&page={p}'))
    for h in d['hits']:add(h.get('url') or f"https://news.ycombinator.com/item?id={h['objectID']}",h.get('title') or h.get('story_title'),'hackernews',(h.get('created_at')or'')[:10])
    if p>=d['nbPages']-1:break
save()
# iTunes
for term in ['Esther Wojcicki','Esther Wojcicki TRICK','Woj Esther Wojcicki','How to Raise Successful People','Esther Wojcicki parenting','Esther Wojcicki education','Esther Wojcicki moonshots']:
    d=json.loads(g('https://itunes.apple.com/search?'+urllib.parse.urlencode(dict(term=term,entity='podcastEpisode',limit=200))))
    for r in d['results']:
        t=(r.get('trackName')or'')+' '+(r.get('description')or'')
        if 'wojcicki' in t.lower():add(r.get('trackViewUrl'),r.get('trackName'),'itunes',(r.get('releaseDate')or'')[:10],(r.get('collectionName')or''))
    time.sleep(3)
save()
# Internet Archive
for p in range(1,8):
    try:
        d=json.loads(g(f'https://archive.org/services/search/beta/page_production/?user_query={q}&hits_per_page=100&page={p}'))
        hs=d['response']['body']['hits']['hits']
        if not hs:break
        for h in hs:
            f=h['fields'];add('https://archive.org/details/'+f['identifier'],f.get('title'),'archive.org',(f.get('date')or'')[:10])
    except Exception as ex:print('ia',ex);break
    time.sleep(1)
save()
# LOC, OpenLibrary inside
try:
    d=json.loads(g(f'https://www.loc.gov/search/?q={urllib.parse.quote(Q)}&fo=json&c=100'))
    for r in d['results']:add(r.get('url') or r.get('id'),r.get('title'),'loc',r.get('date',''))
except Exception as ex:print(ex)
for off in (0,50):
    try:
        d=json.loads(g(f'https://openlibrary.org/search/inside.json?q={q}&limit=50&offset={off}'))
        for h in d['hits']['hits']:
            ed=h.get('edition') or {};k=ed.get('key') or (h.get('fields',{}).get('identifier') and '')
            if k:add('https://openlibrary.org'+k,ed.get('title'),'openlibrary')
    except Exception as ex:print('ol',ex)
save()
# Google News RSS: monthly windows; published date filter
def gn(qq):
    x=g('https://news.google.com/rss/search?'+urllib.parse.urlencode(dict(q=qq,hl='en-US',gl='US',ceid='US:en')))
    return ET.fromstring(x).findall('.//item')
d0=datetime.date(2012,1,1)
gnl={}
while d0<datetime.date(2026,12,1):
    d1=(d0.replace(day=28)+datetime.timedelta(days=5)).replace(day=1)
    if d0.year<2018 and d0.month%3!=1: d0=d1;continue
    e=d1 if d0.year>=2018 else (d0.replace(day=28)+datetime.timedelta(days=65)).replace(day=1)
    try:
        for it in gn(f'{Q} after:{d0} before:{e}'):
            gnl[it.findtext('link')]=(it.findtext('title'),it.findtext('pubDate'),it.findtext('source'))
    except Exception as ex:print('gn',d0,ex);time.sleep(20)
    time.sleep(1.2);d0=d1
json.dump(gnl,open('gnews_raw.json','w'));print('gnews',len(gnl),flush=True)
# Bing RSS, query variants
V=['','parenting','TRICK','How to Raise Successful People','Palo Alto High School','journalism teacher','Moonshots in Education','Google Teacher','Susan Wojcicki mother','Anne Wojcicki mother','Janet Wojcicki','Media Arts Center','Tract app','Creative Commons','blended learning','interview','podcast','keynote','speaker','conference','Godmother of Silicon Valley','Paly','Stanford','Learning Accelerator','Newsela','book review','Forbes','CNBC','Time','New York Times','Wall Street Journal','Guardian','Globe and Mail','Sequoia Union','Palo Alto Online','TEDx','YouTube','Steve Jobs teacher','James Franco teacher','Gady Epstein','Spring Tide','Global Moonshots','MediaWise','Holocaust','Poland','Russia','China','India','Germany','Brazil','Israel','Korea','Japan','Spain','Argentina','Dubai','review','quotes','Goodreads','Amazon','LinkedIn','Wikipedia','Medium','Huffington Post','EdSurge','Edutopia','ISTE','SXSW EDU','Aspen Ideas','Milken','Harvard','UC Berkeley','Sorbonne','Dennis Wojcicki father Stanley','grandmother','tech moguls mother','helicopter parent','free range kids','independence children','teens AI','ChatGPT','YouTube CEO mother','23andMe mother','obituary Susan Wojcicki','lung cancer mom','Mother\'s Day']
for v in V:
  for off in (1,51,101):
    try:
        x=g('https://www.bing.com/search?'+urllib.parse.urlencode(dict(q=(Q+' '+v).strip(),format='rss',count=50,first=off)))
        items=ET.fromstring(x).findall('.//item')
        if not items:break
        for it in items:add(it.findtext('link'),it.findtext('title'),'bing','',it.findtext('description') or '')
    except Exception as ex:print('bing',v,ex);break
    time.sleep(1.5)
  try:
    x=g('https://www.bing.com/news/search?'+urllib.parse.urlencode(dict(q=(Q+' '+v).strip(),format='rss')))
    for it in ET.fromstring(x).findall('.//item'):
        l=it.findtext('link');m=re.search(r'[?&]url=([^&]+)',l or '')
        add(urllib.parse.unquote(m.group(1)) if m else l,it.findtext('title'),'bingnews','',it.findtext('description') or '')
  except Exception as ex:print('bn',v,ex)
  time.sleep(1.5)
  if V.index(v)%10==0:save()
save()
