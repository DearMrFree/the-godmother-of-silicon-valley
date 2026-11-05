import json,time,sys
sys.path.insert(0,'.')
import recheck
R={x['url']:x for x in json.load(open('r6.json'))}
todo=[x for x in R.values() if 'youtube.com/watch' in x['url'] and not x.get('ok')]
print(len(todo),flush=True);fail=0
for i,x in enumerate(todo):
    r=recheck.one(x);R[x['url']]=r
    if r.get('ok'):fail=0
    else:
        fail+=1;print('fail',r.get('err2'),flush=True);time.sleep(120 if fail<6 else 300)
        if fail>12:print('giving up');break
    time.sleep(4)
    if i%50==49:json.dump(list(R.values()),open('r6.json','w'),ensure_ascii=False);print(i,sum(1 for y in R.values() if y.get('ok') and 'youtube' in y['url']),flush=True)
json.dump(list(R.values()),open('r6.json','w'),ensure_ascii=False);print('END',sum(1 for x in R.values() if 'youtube.com/watch' in x['url'] and x.get('found_now')),sum(1 for x in R.values() if 'youtube.com/watch' in x['url'] and x['gm']))
