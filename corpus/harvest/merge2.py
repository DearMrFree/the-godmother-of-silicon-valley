import json,re
import sys;sys.path.insert(0,".");from verify import NAME
SIDE=re.compile(r"Lest auch|Also read|Read more|Read also|Related|Recommended|You may also like|Wybrane dla Ciebie|Polecane|上一则|下一则|延伸阅读|Term Sheet [A-Z][a-z]+ \d+, \d{4} \d+:\d+|Photostories|Trending",re.I)
GMRE=re.compile(r"god\s?mother|Patin|Patentante|chrzestn|madrin|marraine|крестн|крёстн|教母|ゴッドマザー|대모|peetmoeder|vaftiz|đỡ đầu",re.I)
R=json.load(open('r6.json'));out=[]
for x in R:
    ok=x.get('ok');f=x.get('found_now') if ok else x.get('found')
    if 'youtube.com/watch' in x['url'] and not ok:
        import recheck
        tl=x.get('title') or ''
        f=bool(NAME.search(tl));x['gm']=bool(recheck.GM.search(tl));x['sur']=bool(recheck.SUR.search(tl));x['hits']=1 if f else 0;x['words']=len(tl.split());x['gmctx']=tl if x['gm'] else ''
    c=x.get('ctx') or '';m=NAME.search(c)
    near=c[max(0,m.start()-110):m.end()+70] if m else ''
    tt=(x.get('page_title') or '')+' '+(x.get('title') or '')
    g=x.get('gmctx') or '';gm=GMRE.search(g);gnear=g[max(0,gm.start()-90):gm.end()+60] if gm else ''
    side=bool(SIDE.search(gnear)) and not GMRE.search(tt)
    y={k:x.get(k) for k in ('url','final','title','page_title','src','date','snip','channel','ydate','pdate','words','hits','hash','http')}
    y.update(found=bool(f),strict=True,gm=bool(x.get('gm')) and not side and not re.search(r'fairy\s+god',g,re.I),sur=bool(x.get('sur')),gm_only_sidebar=bool(x.get('gm') and side),
      teaser=bool((x.get('hits') or 0)<=2 and 'wojcicki' not in tt.lower() and re.search(r"Meet Esther Wojcicki: This mother|VIDEO\s*\d+:\d+|Don.t miss|Also read|You may also like|Trending|Photostories|Recommended|More from|Read more",near,re.I)),
      byline=bool(re.search(r"\bBy Esther (D\. )?Wojcicki\b",near) and 'how to raise' not in near.lower() and 'moonshots' not in near.lower()))
    out.append(y)
json.dump(out,open("/Users/freedom/Downloads/pf-improvements 2/esther-wojcicki-archive/corpus/harvest/checked_pages.json",'w'),ensure_ascii=False,indent=0)
print(len(out),sum(y['found'] for y in out),sum(y['gm'] for y in out))
