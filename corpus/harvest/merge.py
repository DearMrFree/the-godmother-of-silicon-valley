import json,re,glob
NAME=re.compile(r"Esther\s+(?:[A-Z]\.?\s+)?(?:\"Woj\"\s+|Denise\s+|Hochman\s+)?Wojcicki|Wojcicki,\s*Esther|Esther\s+\W*Woj\W*\s+Wojcicki|Эстер\s+Воджицки|Эстер\s+Войджицки|埃丝特.{0,2}沃西基|エスター.{0,2}ウォジスキ|에스더\s*워치츠키|Ester\s+Wojcicki|Esther\s+Wojicki|Esther\s+Wojciki",re.I)
rows={}
for f in sorted(glob.glob('v*.json')):
    if re.match(r'v\d+\.json$',f):
        for x in json.load(open(f)):
            x['strict']=(x['src']=='youtube') or not x.get('ctx') or bool(NAME.search(x['ctx']))
            c=x.get('ctx') or '';m=NAME.search(c)
            near=c[max(0,m.start()-110):m.end()+70] if m else ''
            tt=(x.get('page_title') or '')+' '+(x.get('title') or '')
            x['teaser']=bool((x.get('hits') or 0)<=2 and 'wojcicki' not in tt.lower() and re.search(r"Meet Esther Wojcicki: This mother|VIDEO\s*\d+:\d+|Don.t miss|Also read|You may also like|Trending|Photostories|Recommended|More from|Read more",near,re.I))
            x['byline']=bool(re.search(r"\bBy Esther (D\. )?Wojcicki\b",near) and 'how to raise' not in near.lower() and 'moonshots' not in near.lower())
            x.pop('ctx',None);rows[x['url']]=x
R="/Users/freedom/Downloads/pf-improvements 2/esther-wojcicki-archive/corpus/harvest/checked_pages.json"
json.dump(list(rows.values()),open(R,'w'),ensure_ascii=False,indent=0);print(len(rows))
