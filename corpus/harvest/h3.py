import urllib.request,urllib.parse,json,re,time,html,subprocess,threading
from concurrent.futures import ThreadPoolExecutor
BUA={'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126 Safari/537.36','Accept-Language':'en-US'}
def g(u,t=30):return urllib.request.urlopen(urllib.request.Request(u,headers=BUA),timeout=t).read().decode('utf8','replace')
C={};L=threading.Lock()
def add(url,title,src,date='',snip=''):
    if not url or not url.startswith('http'):return
    with L:
        if url not in C:C[url]=dict(url=url,title=html.unescape(title or '').strip(),src=src,date=date,snip=snip)
def save(tag=''):
    with L:json.dump(list(C.values()),open('cands3.json','w'),ensure_ascii=False,indent=0)
    print(tag,'total',len(C),flush=True)
q=urllib.parse.quote('"Esther Wojcicki"')
# --- IA full text and TV
for be in ('fts','tvs','metadata'):
    for p in range(1,5):
        try:
            hs=json.loads(g(f'https://archive.org/services/search/beta/page_production/?user_query={q}&hits_per_page=100&page={p}&service_backend={be}'))['response']['body']['hits']['hits']
        except Exception as e:print('ia',be,e);break
        if not hs:break
        for h in hs:
            f=h.get('fields',{});i=f.get('identifier')
            if i:add('https://archive.org/details/'+i,f.get('title') if isinstance(f.get('title'),str) else '', 'archive.org-'+be,str(f.get('date') or '')[:10])
        time.sleep(1)
save('ia')
# --- WordPress site search across publishers
WP='''paloaltoonline.com almanacnews.com mv-voice.com embarcaderomedia.org thecampanile.org verdemagazine.com palyvoice.com cmagazine.org vikingsportsmag.com madeleinemag.org inklingnews.com lasaltolahs.com elestoque.org thetalonstudentnews.com stanforddaily.com news.stanford.edu ed.stanford.edu alumni.stanford.edu stanfordmag.org dailycal.org news.berkeley.edu kqed.org techcrunch.com fastcompany.com gettingsmart.com eschoolnews.com freetech4teachers.com edtechmagazine.com thejournal.com jweekly.com jta.org forward.com tabletmag.com timesofisrael.com jewishjournal.com jewishchronicle.org jpost.com haaretz.com mercurynews.com siliconvalley.com sfexaminer.com sfgate.com sfstandard.com sanjosespotlight.com padailypost.com localnewsmatters.org edsource.org the74million.org chalkbeat.org hechingerreport.org edweek.org educationnext.org teachthought.com edutopia.org tcea.org iste.org cue.org jeadigitalmedia.org jea.org splc.org poynter.org niemanlab.org cjr.org ajr.org mediashift.org pbs.org pbssocal.org npr.org wnyc.org marketplace.org scpr.org laist.com theatlantic.com newyorker.com slate.com vox.com wired.com theverge.com engadget.com venturebeat.com readwrite.com mashable.com gizmodo.com zdnet.com cnet.com inc.com entrepreneur.com thriveglobal.com goop.com mindbodygreen.com parents.com scarymommy.com motherly.com fatherly.com mother.ly babble.com greatergood.berkeley.edu psychologytoday.com ideas.ted.com blog.ted.com creativecommons.org blog.google blog.youtube edublogs.org medium.com hbr.org knowledge.wharton.upenn.edu gsb.stanford.edu news.harvard.edu gse.harvard.edu commonsensemedia.org commonsense.org newsela.com learningaccelerator.org theguardian.com independent.co.uk telegraph.co.uk thetimes.co.uk mirror.co.uk news.com.au smh.com.au abc.net.au nzherald.co.nz stuff.co.nz theglobeandmail.com thestar.com cbc.ca forbes.com fortune.com bloomberg.com time.com people.com businessinsider.com qz.com axios.com cnbc.com buzzfeednews.com huffpost.com latimes.com observer.com ozy.com sunnyvalesun.com svcn.com svbj.com sfbaytimes.com goldenstate.is calmatters.org capradio.org ktvu.com kron4.com abc7news.com ajc.com tech.co geekwire.com recode.net theinformation.com themarkup.org sparknotes.com dianerehm.org oprahdaily.com oprah.com wbur.org onpoint.org freakonomics.com tim.blog lennyspodcast.com thepodcastparents.com janetlansbury.com regina.org thebump.com workingmother.com fairygodboss.com ellevatenetwork.com leanin.org makers.com mashable.com girlboss.com sheknows.com romper.com bustle.com elitedaily.com refinery29.com marieclaire.com vogue.com glamour.com harpersbazaar.com townandcountrymag.com goodhousekeeping.com rd.com ideas.time.com nextavenue.org aarp.org grandparents.com verywellfamily.com'''.split()
def wp(d):
    n=0
    for base in (f'https://{d}',f'https://www.{d}'):
        try:
            for pg in (1,2,3):
                x=json.loads(g(f'{base}/wp-json/wp/v2/search?search=Esther+Wojcicki&per_page=100&page={pg}',20))
                if not isinstance(x,list) or not x:break
                for r in x:add(r.get('url'),r.get('title'),'wp:'+d);n+=1
                if len(x)<100:break
            if n:break
        except Exception:continue
    # RSS fallback
    if not n:
        for base in (f'https://{d}',f'https://www.{d}'):
            try:
                x=g(f'{base}/?s=%22Esther+Wojcicki%22&feed=rss2',20)
                ls=re.findall(r'<item>.*?<title>(.*?)</title>.*?<link>(.*?)</link>',x,re.S)
                for t,l in ls:add(l.strip(),re.sub(r'<!\[CDATA\[|\]\]>','',t),'wprss:'+d);n+=1
                if n:break
            except Exception:continue
    return d,n
with ThreadPoolExecutor(12) as ex:
    res=list(ex.map(wp,WP))
print([r for r in res if r[1]],flush=True);save('wp')
# --- Wikipedia external links (citations), several articles, polite
for l,ts in {'en':['Esther Wojcicki','Susan Wojcicki','Anne Wojcicki','Stanley Wojcicki','Palo Alto High School','Janet Wojcicki'],'de':['Esther Wojcicki','Susan Wojcicki'],'fr':['Esther Wojcicki'],'es':['Esther Wojcicki','Susan Wojcicki'],'pl':['Esther Wojcicki','Susan Wojcicki','Stanley Wojcicki'],'ru':['Уойджицки, Эстер'],'zh':['埃丝特·沃西基']}.items():
    for t in ts:
        cont=''
        for _ in range(6):
            try:
                d=json.loads(g(f'https://{l}.wikipedia.org/w/api.php?action=query&prop=extlinks&ellimit=500&format=json&titles={urllib.parse.quote(t)}{cont}'))
            except Exception as e:print('wk',t,e);time.sleep(10);break
            for pg in d['query']['pages'].values():
                for e in pg.get('extlinks',[]):
                    u=e.get('*') or e.get('url')
                    if u and 'archive.org' not in u: add(('https:'+u) if u.startswith('//') else u,'', 'wikicite')
            c=d.get('continue',{}).get('eloffset')
            if not c:break
            cont=f'&eloffset={c}';time.sleep(1)
        time.sleep(1.5)
for l in 'de fr es it pt ru zh ja ko ar he pl nl sv tr uk fa id vi cs hu ro fi no da'.split():
    try:
        for h in json.loads(g(f'https://{l}.wikipedia.org/w/api.php?action=query&list=search&srsearch={q}&format=json&srlimit=100'))['query']['search']:
            add(f'https://{l}.wikipedia.org/wiki/'+urllib.parse.quote(h['title'].replace(' ','_')),h['title'],'wikipedia')
    except Exception as e:print('wiki',l,e)
    time.sleep(2)
save('wiki')
# --- YouTube
for term in ['Esther Wojcicki','Esther Wojcicki interview','Esther Wojcicki keynote','Esther Wojcicki TRICK parenting','How to Raise Successful People Esther Wojcicki','Esther Wojcicki journalism Palo Alto','Esther Wojcicki Moonshots in Education','Esther Wojcicki podcast','Esther Wojcicki talk','Woj Esther Wojcicki teacher','Esther Wojcicki Susan Wojcicki mother','Esther Wojcicki AI education','Esther Wojcicki TEDx','Esther Wojcicki panel']:
    try:
        o=subprocess.run(['ytv/bin/yt-dlp','--flat-playlist','-J','--no-warnings',f'ytsearch150:{term}'],capture_output=True,timeout=240).stdout
        for e in json.loads(o).get('entries',[]):
            add('https://www.youtube.com/watch?v='+e['id'],e.get('title'),'youtube','',(e.get('description') or '')[:1500])
    except Exception as ex:print('yt',term,ex)
    save('yt');time.sleep(2)
# --- DDG html with variants
V=['','parenting','TRICK','"How to Raise Successful People"','Palo Alto High School','journalism teacher','"Moonshots in Education"','Google Teacher Academy','Susan Wojcicki mother','Anne Wojcicki mother','Janet Wojcicki','Media Arts Center','Tract','Creative Commons board','blended learning','interview','podcast','keynote speaker','conference','"Godmother of Silicon Valley"','Paly','Stanford','Learning Accelerator','Newsela','book review','Forbes','CNBC','Time magazine','New York Times','Wall Street Journal','Guardian','Globe and Mail','TEDx','Steve Jobs','James Franco','Gady Epstein','Global Moonshots','Holocaust','Poland','Russia','China','India','Germany','Brazil','Israel','Korea','Japan','Spain','Argentina','Dubai','quotes','Goodreads','LinkedIn','Medium','Huffington Post','EdSurge','Edutopia','ISTE','SXSW EDU','Aspen Ideas','Milken','Harvard','UC Berkeley','Sorbonne','Stanley Wojcicki','grandmother','tech moguls','helicopter parent','independence children','ChatGPT AI teens','obituary Susan','Mother\'s Day','school board','award','honorary','commencement','summit','webinar','panel','newspaper','student press','First Amendment','Hazelwood','MIT','Maker Faire','VidCon','Sal Khan','Sergey Brin','Google garage','Marissa Mayer','Lisa Brennan-Jobs','Gavin Newsom','Forbes 50 over 50','Bay Area','California Teacher of the Year','Exploratorium','Cooperative','Reach Capital','edtech','podcast episode','book excerpt','summary','pdf','site:edu','site:org','site:gov']
ok=0
for v in V:
    url='https://html.duckduckgo.com/html/?q='+urllib.parse.quote_plus(('"Esther Wojcicki" '+v).strip())
    try:
        b=g(url)
    except Exception as e:print('ddg',v,e);time.sleep(30);continue
    rs=re.findall(r'class="result__a"\s+href="([^"]+)"[^>]*>(.*?)</a>',b,re.S)
    if not rs:
        print('ddg empty',v,flush=True);time.sleep(30);ok+=1
        if ok>6:print('ddg stopping');break
        continue
    for h,t in rs:
        m=re.search(r'uddg=([^&]+)',h);u=urllib.parse.unquote(m.group(1)) if m else h
        add(u,re.sub('<[^>]+>','',t),'ddg')
    save('ddg');time.sleep(5)
save('end')
