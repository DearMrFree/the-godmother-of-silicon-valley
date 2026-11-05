import json,time,sys,re
sys.path.insert(0,'.')
import recheck
rows=json.load(open('r6.json'));R={x['url']:x for x in rows}
for u in ['https://youtu.be/8QbWB5lyxtI?si=vc6AaAQ2dkessxLo','https://youtu.be/KRk0GJQMKAg?si=vKXlSR00eZddouJ1','https://youtu.be/p0yiiGxpVaw?si=TRP-vxSuxcNVj9AS','https://www.youtube.com/watch?v=T_1FcKoNE4I']:
    x=dict(R[u]);vid=re.search(r'(?:be/|v=)([\w-]{11})',u).group(1)
    x['url']='https://www.youtube.com/watch?v='+vid
    r=recheck.one(x);r['url']=u;R[u]=r
    print(vid,r.get('ok'),r.get('found_now'),r.get('gm'),r.get('channel'),'|',str(r.get('ctx'))[:200],'|',str(r.get('gmctx'))[:200],flush=True);time.sleep(4)
json.dump(list(R.values()),open('r6.json','w'),ensure_ascii=False)
