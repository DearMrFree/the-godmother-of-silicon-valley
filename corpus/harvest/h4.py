import urllib.request,urllib.parse,json,re,time,html,threading,ssl,gzip
from concurrent.futures import ThreadPoolExecutor
BUA={'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126 Safari/537.36','Accept-Language':'en-US'}
ctx=ssl.create_default_context();ctx.check_hostname=False;ctx.verify_mode=ssl.CERT_NONE
def g(u,t=25):return urllib.request.urlopen(urllib.request.Request(u,headers=BUA),timeout=t,context=ctx).read(5_000_000).decode('utf8','replace')
v=json.load(open('v1.json'))+json.load(open('v2.json'))
seen={x['url'] for x in v};C={};L=threading.Lock()
def add(u,t,s):
    if u and u.startswith('http') and u not in seen:
        with L:C.setdefault(u,dict(url=u,title=html.unescape(t or ''),src=s,date='',snip=''))
def save(tag):
    with L:json.dump(list(C.values()),open('cands4.json','w'),ensure_ascii=False)
    print(tag,len(C),flush=True)
f=[x for x in v if x['found']]
doms=sorted({urllib.parse.urlparse(x.get('final') or x['url']).netloc for x in f}-{'www.youtube.com','podcasts.apple.com','www.linkedin.com'})
# 1 snowball: links with her name in url or anchor from found pages
pat=re.compile(r'<a\b[^>]*href="(https?://[^"#]+)"[^>]*>(.{0,200}?)</a>',re.S|re.I)
SKIP=re.compile(r'(facebook|twitter|x\.com|instagram|pinterest|youtube\.com/(?!watch)|google\.com/search|amazon\.|wikipedia\.org|linkedin\.com/shareArticle|whatsapp|mailto|reddit\.com/submit)')
def sb(x):
    try:
        b=g(x.get('final') or x['url'])
        for h,a in pat.findall(b):
            at=re.sub('<[^>]+>',' ',a)
            if (re.search(r'wojcicki',h,re.I) or re.search(r'wojcicki',at,re.I)) and not SKIP.search(h) and not re.search(r'susan|anne',h,re.I):
                add(html.unescape(h),at.strip(),'snowball')
    except Exception:pass
web=[x for x in f if x['src'] not in('youtube','itunes','wikipedia') ]
with ThreadPoolExecutor(14) as ex:list(ex.map(sb,web))
save('snowball')
# 2 WP search on all verified domains
def wp(d):
    try:
        for pg in (1,2):
            x=json.loads(g(f'https://{d}/wp-json/wp/v2/search?search=Esther+Wojcicki&per_page=100&page={pg}',15))
            if not isinstance(x,list) or not x:break
            for r in x:add(r.get('url'),r.get('title'),'wp:'+d)
            if len(x)<100:break
    except Exception:pass
with ThreadPoolExecutor(12) as ex:list(ex.map(wp,doms))
save('wp')
# 3 DDG variants, 2 pages
TOPIC='''"Esther Wojcicki" teacher|"Esther Wojcicki" daughters|"Esther Wojcicki" Silicon Valley|"Esther Wojcicki" Larry Page Sergey Brin|"Esther Wojcicki" journalism education association|"Esther Wojcicki" scholastic press|"Esther Wojcicki" newspaper students|"Esther Wojcicki" high school students publication|"Esther Wojcicki" alumni|"Esther Wojcicki" book club|"Esther Wojcicki" parenting book list|best parenting books "Esther Wojcicki"|"Esther Wojcicki" raising children article|"Esther Wojcicki" says|"Esther Wojcicki" told|according to "Esther Wojcicki"|"Esther Wojcicki" advice|"Esther Wojcicki" Fortune|"Esther Wojcicki" Business Insider|"Esther Wojcicki" Inc|"Esther Wojcicki" Fast Company|"Esther Wojcicki" Entrepreneur|"Esther Wojcicki" NPR|"Esther Wojcicki" PBS|"Esther Wojcicki" BBC|"Esther Wojcicki" Telegraph|"Esther Wojcicki" Times UK|"Esther Wojcicki" Washington Post|"Esther Wojcicki" Los Angeles Times|"Esther Wojcicki" San Francisco Chronicle|"Esther Wojcicki" Mercury News|"Esther Wojcicki" Quartz|"Esther Wojcicki" Vox|"Esther Wojcicki" Atlantic|"Esther Wojcicki" New Yorker|"Esther Wojcicki" Wired|"Esther Wojcicki" Vogue|"Esther Wojcicki" Oprah|"Esther Wojcicki" Goop|"Esther Wojcicki" Jewish|"Esther Wojcicki" Forward|"Esther Wojcicki" Times of Israel|"Esther Wojcicki" blog post|"Esther Wojcicki" newsletter substack|"Esther Wojcicki" medium.com|"Esther Wojcicki" school district|"Esther Wojcicki" principal|"Esther Wojcicki" library event|"Esther Wojcicki" author talk|"Esther Wojcicki" university lecture|"Esther Wojcicki" commencement speaker|"Esther Wojcicki" honorary doctorate|"Esther Wojcicki" foundation board|"Esther Wojcicki" advisory board|"Esther Wojcicki" startup advisor|"Esther Wojcicki" press release|"Esther Wojcicki" Tract|"Esther Wojcicki" Pressto|"Esther Wojcicki" MyHero|"Esther Wojcicki" University of the People|"Esther Wojcicki" Kazakhstan|"Esther Wojcicki" Mexico|"Esther Wojcicki" Colombia|"Esther Wojcicki" Italy|"Esther Wojcicki" France|"Esther Wojcicki" UK|"Esther Wojcicki" Australia|"Esther Wojcicki" New Zealand|"Esther Wojcicki" Canada|"Esther Wojcicki" Singapore|"Esther Wojcicki" Philippines|"Esther Wojcicki" Vietnam|"Esther Wojcicki" Turkey|"Esther Wojcicki" Ukraine|"Esther Wojcicki" Nigeria|"Esther Wojcicki" South Africa|"Esther Wojcicki" Saudi|"Esther Wojcicki" Greece|"Esther Wojcicki" Switzerland|"Esther Wojcicki" Madrid|"Esther Wojcicki" hija YouTube madre|"Esther Wojcicki" madre educación|"Esther Wojcicki" Mutter Erziehung|"Esther Wojcicki" mère éducation|"Esther Wojcicki" matka wychowanie|"Esther Wojcicki" mãe educação|"Esther Wojcicki" madre educazione|"Esther Wojcicki" Facebook founder|"Esther Wojcicki" Zuckerberg|"Esther Wojcicki" Larry Ellison|"Esther Wojcicki" Tiger Mom|"Esther Wojcicki" Amy Chua|"Esther Wojcicki" Montessori|"Esther Wojcicki" project based learning|"Esther Wojcicki" 20 percent time|"Esther Wojcicki" student voice|"Esther Wojcicki" media literacy|"Esther Wojcicki" fake news|"Esther Wojcicki" coronavirus remote learning|"Esther Wojcicki" Common Sense Media|"Esther Wojcicki" screen time|"Esther Wojcicki" phones kids|"Esther Wojcicki" college admissions|"Esther Wojcicki" retirement|"Esther Wojcicki" 85|"Esther Wojcicki" aging|"Esther Wojcicki" brother David died|"Esther Wojcicki" immigrant poverty|"Esther Wojcicki" Sierra Madre|"Esther Wojcicki" UC Berkeley alumna|"Esther Wojcicki" Palo Alto school board|"Esther Wojcicki" Paly media arts building|"Esther Wojcicki" Steve Jobs daughter Small Fry|"Esther Wojcicki" Gady Epstein|"Esther Wojcicki" Jennifer Siebel Newsom|"Esther Wojcicki" Reid Hoffman|"Esther Wojcicki" Arianna Huffington|"Esther Wojcicki" Walter Isaacson|"Esther Wojcicki" podcast transcript|"Wojcicki, Esther"|"Esther Wojcicki" bibliography references|"Esther Wojcicki" pdf|"Esther Wojcicki" thesis dissertation|"Esther Wojcicki" Wikipedia biography net worth|"Esther Wojcicki" quote|"Esther Wojcicki" TED|"Esther Wojcicki" book summary|"Esther Wojcicki" audiobook|"Esther Wojcicki" Barnes Noble|"Esther Wojcicki" library catalog|"Esther Wojcicki" Kepler's Books event|"Esther Wojcicki" JCC|"Esther Wojcicki" Commonwealth Club|"Esther Wojcicki" Computer History Museum|"Esther Wojcicki" Google for Education|"Esther Wojcicki" Google Teacher Institute|"Esther Wojcicki" Global Education Conference|"Esther Wojcicki" EdTechTeam|"Esther Wojcicki" Maker Education|"Esther Wojcicki" Teach for America|"Esther Wojcicki" charter school'''.split('|')
empt=0
for q in TOPIC:
    for off in (0,):
        try:
            b=g('https://html.duckduckgo.com/html/?'+urllib.parse.urlencode(dict(q=q)))
            rs=re.findall(r'class="result__a"\s+href="([^"]+)"[^>]*>(.*?)</a>',b,re.S)
            if not rs:empt+=1;print('empty',q,flush=True);time.sleep(45);continue
            for h,t in rs:
                m=re.search(r'uddg=([^&]+)',h);add(urllib.parse.unquote(m.group(1)) if m else h,re.sub('<[^>]+>','',t),'ddg')
        except Exception as e:print(q,str(e)[:60],flush=True);time.sleep(30)
        time.sleep(6)
    save('ddg')
    if empt>12:print('ddg stop');break
save('end')
