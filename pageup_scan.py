import concurrent.futures as cf, urllib.request, re, time, json, sys
UA={'User-Agent':'DesignRolesAU-prototype/0.1 (job aggregation research; contact via owner)'}
def get(u):
    try:
        r=urllib.request.urlopen(urllib.request.Request(u,headers=UA),timeout=15); return r.status, r.read()
    except Exception as e:
        return getattr(e,'code',0), b''
def probe(i):
    time.sleep(0.25)
    for b in ('cw','ci'):
        s,body=get(f'https://careers.pageuppeople.com/{i}/{b}/en/rss')
        if s==200 and b'<item>' in body:
            s2,h=get(f'https://careers.pageuppeople.com/{i}/{b}/en/listing/')
            m=re.search(rb'<title>(.*?)</title>',h,re.S)
            t=m.group(1).decode('utf8','ignore').strip() if m else ''
            return {'id':i,'brand':b,'items':body.count(b'<item>'),'title':' '.join(t.split())}
    return None
res=[]
with cf.ThreadPoolExecutor(4) as ex:
    for r in ex.map(probe, range(1,1500)):
        if r: res.append(r); print(r, flush=True)
json.dump(res,open('pageup_ids.json','w'),indent=1)
