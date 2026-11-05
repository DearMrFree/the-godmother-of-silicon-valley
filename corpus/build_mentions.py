#!/usr/bin/env python3
"""Turn checked pages (harvest/checked_pages.json) into the mentions database.
Counted: pages fetched on the date shown whose own text names Esther Wojcicki or calls her the
"Godmother of Silicon Valley" (in any language), after removing her own
sites and bylines, mirrors, retailers, listing pages, duplicate URLs, identical text and syndicated copies."""
import json,re,urllib.parse,collections,os,csv,html
HERE=os.path.dirname(os.path.abspath(__file__))
rows=json.load(open(os.path.join(HERE,"harvest","checked_pages.json"),encoding="utf8"))
corpus=json.load(open(os.path.join(HERE,"corpus.json"),encoding="utf8"))
OWN=re.compile(r'(parentingchildren\.com|raisesuccessfulpeople\.com|estherwojcicki\.com|gmoonshots|moonshotsineducation|moonshotsedu|woj\.education|wojint\.com|moonshots\.org|journalisticlearning\.org|moonshot\.global|globalmoonshots|woj\.net|theglobalmoonshots|tractlearning|tract\.app|thewojway)',re.I)
JUNK=re.compile(r'(wikiwand|wiki\.krisyotam|ipfs|cavac\.at|everybodywiki|alchetron|infogalactic|justapedia|wikimili|dbpedia|wiki2\.org|wikizero|sensagent|en-academic|crmcloud|primowater|educoast|yespress\.io|hmong\.|wikibrief|alamy|gettyimages|shutterstock|wn\.com|peoplepill|prabook|famousbirthdays|celebsagewiki|wikitree|grokipedia|dptribune|staging\.|wwwstage)',re.I)
SHOP=re.compile(r'(amazon\.|ebay\.|barnesandnoble|walmart|bookshop\.org|abebooks|thriftbooks|alibris|bookdepository|booktopia|waterstones|target\.com|rakuten|kobo\.com|audible\.|scribd|perlego|everand|play\.google|wordery|blackwells|hugendubel|thalia|fnac|lazada|shopee|flipkart|bookbelow|phantombookshop)',re.I)
LIST=re.compile(r'(/tag/|/tags/|/category/|/categories/|/author/|/authors/|/topics?/|/search|[?&]s=|[?&]q=|/page/\d+|/archives?/?$|/feed/?$|/label/|^/esther-wojcicki/?$)',re.I)
# Pages that use the nickname for her without her exact name, each kept after checking the wording around the nickname. Everything else that
# has the nickname but not her name stays out: others have been given it (Elizabeth Holmes, Katia Verresen).
NICK_ONLY=re.compile(r'(x8BmJXx3nIQ|ReRjIwyqO0Q|JWjgiZ_c1s0|8cILOwCWDws|inaugural-gsv-x-penn-state-ai|usglobalnews\.wordpress\.com/2026/04/19|businessinsider\.com/23andme-ceo-anne-wojcicki|KGO_20220202_230000|einfomax\.co\.kr/news/articleView\.html\?idxno=4410788)')
FORTUNEVID=re.compile(r'fortune\.com/(media/(?!dd022e4e)|videos/series/)')
BYLINE=re.compile(r'(^|\b)(i raised (2|two|three|3)|i(’|\')ve been|by esther wojcicki, contributor)',re.I)
OWNCH=re.compile(r'^(esther wojcicki|global moonshots|woj\b|moonshots)',re.I)
host=lambda u:urllib.parse.urlparse(u).netloc.lower().removeprefix('www.').removeprefix('m.')
def norm(u):
    p=urllib.parse.urlparse(u);qs=''
    if 'youtube.com' in p.netloc: qs='v='+urllib.parse.parse_qs(p.query).get('v',[''])[0]
    elif re.search(r'^(p|id|story_id|article_id|i)=',p.query): qs=p.query
    return host(u)+re.sub(r'/(amp|print|index\.html?)/?$','',p.path).rstrip('/').lower()+('?'+qs if qs else '')
by_urls={norm(e['url']) for e in corpus if e['relation']=='by'}
all_urls={norm(e['url']):e['id'] for e in corpus}
drop=collections.Counter();keep={}
for x in rows:
    u=x.get('final') or x['url']
    if not x.get('found') and not (x.get('gm') and NICK_ONLY.search(u)):
        drop['neither name nor nickname for her found, or page could not be read']+=1;continue
    h=host(u);p=urllib.parse.urlparse(u);t=x.get('page_title') or x.get('title') or ''
    if not x.get('strict',True):drop['surname only, could be a daughter']+=1
    elif x.get('teaser'):drop['sidebar or promo link only']+=1
    elif x.get('byline'):drop['her own site or byline']+=1
    elif OWN.search(h) or re.search(r'linkedin\.com/(posts|in|pulse)/esther-?wojcicki',u,re.I) or norm(u) in by_urls or (x['src']!='youtube' and BYLINE.search(t)):drop['her own site or byline']+=1
    elif x['src']=='youtube' and OWNCH.search(x.get('channel') or ''):drop['her own site or byline']+=1
    elif JUNK.search(u):drop['mirror, scrape or stock photo']+=1
    elif SHOP.search(u):drop['retailer']+=1
    elif FORTUNEVID.search(u):drop['sidebar or promo link only']+=1
    elif h.endswith('linkedin.com') and not x.get('gm'):drop['LinkedIn page without the nickname']+=1
    elif LIST.search(p.path+('?'+p.query if p.query else '')):drop['listing page']+=1
    elif norm(u) in keep:drop['same page at another URL']+=1
    else:keep[norm(u)]=x;continue
# syndication: same text, same long title, or same long URL slug on another site. Longest page wins.
seen=set();out=[]
def nt(t):
    t=re.sub(r'\s*[\|\-–—:]\s*[^|\-–—:]{0,40}$','',t or '');return re.sub(r'\W+',' ',t.lower()).strip()
PRI=lambda x:(0 if re.search(r'cnbc\.com|nytimes|apnews|reuters',x.get('final') or x['url']) else 1,-(x.get('words') or 0))
for x in sorted(keep.values(),key=PRI):
    u=x.get('final') or x['url'];keys=[]
    if x['src']=='youtube':
        t=nt(x.get('page_title'))
        if len(t)>20 and t!='esther wojcicki':keys.append('y'+t)
    if x['src'] not in('youtube','itunes'):
        if x.get('hash') and (x.get('words') or 0)>80:keys.append('h'+x['hash'])
        t=nt(x.get('page_title') or x.get('title'))
        if len(t)>35:keys.append('t'+t)
        s=urllib.parse.urlparse(u).path.rstrip('/').split('/')[-1]
        if len(s)>30 and not s.isdigit():keys.append('s'+re.sub(r'\.\w+$','',s))
    if any(k in seen for k in keys):drop['syndicated or identical copy']+=1;continue
    seen.update(keys);out.append(x)
STUDENT=re.compile(r'(palyvoice|thecampanile|verdemagazine|cmagazine|vikingsportsmag|madeleinemag|inklingnews|lasaltolahs|elestoque|thetalon|stanforddaily|dailycal|hwchronicle|palymac|issuu\.com/paly)')
NEWS=re.compile(r'(nytimes|washingtonpost|wsj\.com|forbes|fortune|cnbc|cnn|bbc|npr\.org|pbs\.org|reuters|apnews|bloomberg|businessinsider|time\.com|theguardian|telegraph|independent\.co|thetimes|nzherald|stuff\.co|smh\.com|abc\.net|theglobeandmail|thestar|cbc\.ca|latimes|sfgate|sfchronicle|mercurynews|siliconvalley\.com|paloaltoonline|almanacnews|mv-voice|padailypost|patch\.com|techcrunch|wired|theverge|engadget|zdnet|cnet|observer|qz\.com|vox\.com|theatlantic|newyorker|slate|people\.com|foxnews|nbc|cbs|abc7|ktvu|kqed|timesofindia|indiatimes|hindustantimes|ndtv|economictimes|dailymail|nypost|yahoo|msn\.com|jta\.org|jweekly|forward\.com|timesofisrael|haaretz|edweek|edsurge|the74|chalkbeat|hechinger|edsource|eschoolnews|lavanguardia|elpais|expansion\.mx|gulfnews|astanatimes|inc\.com|fastcompany|entrepreneur|tubefilter|variety|hollywoodreporter)')
def kind(x):
    u=x.get('final') or x['url'];h=host(u);p=u.lower();t=(x.get('page_title') or x.get('title') or '').lower()
    if re.search(r'youtube\.com|vimeo\.com|ted\.com/talks|c-span',h):return 'Video'
    if re.search(r'podcasts\.apple|podchaser|castbox|transistor|buzzsprout|castos|libsyn|podbean|spotify|listennotes|podcast',h+p):return 'Podcast'
    if re.search(r'(^|\.)(linkedin|facebook|instagram|x|twitter|tiktok|threads|reddit)\.(com|net)$',h):return 'Social media'
    if 'wikipedia.org' in h:return 'Encyclopedia'
    if STUDENT.search(p):return 'Student press'
    if re.search(r'review|summary|book/|/books?/|goodreads|kirkus|blinkist|publishersweekly|netgalley',p):return 'Book review or summary'
    if re.search(r'speaker|conference|summit|/event|symposium|sxsw|lecture',p):return 'Event or speaker page'
    if NEWS.search(h) or x['src'] in('gnews','gdelt','bingnews'):return 'News or magazine'
    if re.search(r'\.edu$|\.ac\.|archive\.org|loc\.gov',h):return 'University or library'
    return 'Other web page'
def datef(x):
    for k in('pdate','ydate'):
        if x.get(k):return x[k]
    d=x.get('date') or ''
    m=re.match(r'(\d{4})-?(\d\d)-?(\d\d)',d)
    if m:return '-'.join(m.groups())
    m=re.match(r'\w+, (\d\d) (\w{3}) (\d{4})',d)
    if m:
        mon='Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec'.split().index(m[2])+1;return f'{m[3]}-{mon:02d}-{m[1]}'
    m=re.search(r'/((?:19|20)\d\d)/(\d\d)/(\d\d)/',x.get('final') or x['url'])
    if m:return '-'.join(m.groups())
    m=re.search(r'/((?:19|20)\d\d)/(\d\d)/',x.get('final') or x['url'])
    return '-'.join(m.groups()) if m else ''
BAD=re.compile(r'^(just a moment|access denied|attention required|home|untitled|error|404)',re.I)
M=[]
for x in out:
    u=x.get('final') or x['url'];t=(x.get('page_title') if x['src']=='youtube' else (x.get('title') or x.get('page_title'))) or x.get('page_title') or ''
    t=re.sub(r'\s+',' ',html.unescape(t)).strip()
    if not t or BAD.match(t) or len(t)<12:
        t=x.get('page_title') or urllib.parse.unquote(urllib.parse.urlparse(u).path.rstrip('/').split('/')[-1]).replace('-',' ') or host(u)
        if len(t)<12:t=(host(u)+': '+t).strip(': ')
    site=(x.get('channel')+' on YouTube') if x['src']=='youtube' and x.get('channel') else ((x.get('snip') or 'Apple Podcasts') if x['src']=='itunes' else host(u))
    M.append(dict(title=t[:220],site=site,host=host(u),date=datef(x),kind=kind(x),url=u,found_via=x['src'].split(':')[0],named=x.get('hits') or 0,nickname=bool(x.get('gm')),corpus_id=all_urls.get(norm(u),'')))
M.sort(key=lambda e:(e['date'] or '0000',e['title']),reverse=True)
for n,e in enumerate(sorted(M,key=lambda e:(e['date'] or '9999',e['title'])),1):e['id']=f'MEN-{n:04d}'
summary=dict(checked_on='2026-11-04',candidates=len(rows),counted=len(M),sites=len({e['host'] for e in M}),nickname=sum(e['nickname'] for e in M),excluded=dict(drop.most_common()),kinds=dict(collections.Counter(e['kind'] for e in M).most_common()))
json.dump(dict(summary=summary,mentions=M),open(os.path.join(HERE,'mentions.json'),'w',encoding='utf8'),ensure_ascii=False,indent=0)
with open(os.path.join(HERE,'mentions.csv'),'w',newline='',encoding='utf8') as f:
    w=csv.writer(f);w.writerow('id date kind title site url found_via times_named uses_nickname corpus_id'.split())
    for e in M:w.writerow([e['id'],e['date'],e['kind'],e['title'],e['site'],e['url'],e['found_via'],e['named'],'yes' if e['nickname'] else '',e['corpus_id']])
print(json.dumps(summary,indent=1))
hc=collections.Counter(e['host'] for e in M);print(hc.most_common(15));print(sum(1 for e in M if e['date']),'dated')
