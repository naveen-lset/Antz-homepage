import sys,time,json,base64; sys.path.insert(0,'tools')
from cdp import Chrome
F=sys.argv[1]; NAMES=open(F+'/names.json').read() if len(sys.argv)>2 else '{}'
SER=open(F+'/ser.js').read()
def ser(c,root,name):
    c.eval('window.__NAMES='+NAMES+';window.__ELEM='+open(F+"/elem.json").read()+';window.__SKIP="#agentation-root, [class*=styles-module], [data-agentation], .v2ctx-veil, .qa-veil";window.__RASTER=".wsky";'+SER)
    out=json.loads(c.eval(f"JSON.stringify(window.__ser({root},{{name:{json.dumps(name)}}}))"))
    return out
def count(n):
    return 1+sum(count(k) for k in n.get('kids',[]))
def stats(n,acc):
    acc.setdefault(n['n'],0); acc[n['n']]+=1
    for k in n.get('kids',[]): stats(k,acc)
res={}
with Chrome(width=744,height=1133,reduced_motion=True) as c:
    c.goto('http://127.0.0.1:8000/index.html?v=2',settle=3.5)
    H=c.eval('document.documentElement.scrollHeight'); c.set_viewport(744,H); time.sleep(1.5)
    res['home']=ser(c,'document.body','Home')
    for cv in res['home']['canvases']:
        c.eval("(()=>{const s=document.createElement('style');s.id='__hide';s.textContent='main.page, .qa, #agentation-root{visibility:hidden!important}';document.head.append(s)})()"); time.sleep(.4)
        r=cv['rect']; d=c.cmd('Page.captureScreenshot',format='png',captureBeyondViewport=True,clip={'x':r['x'],'y':r['y'],'width':r['w'],'height':r['h'],'scale':2})
        open(f"{F}/home_{cv['id']}.png",'wb').write(base64.b64decode(d['data']))
        c.eval("document.getElementById('__hide').remove()")
    c.set_viewport(744,1133); time.sleep(.5)
    c.goto('http://127.0.0.1:8000/index.html?v=2',settle=3.5)
    c.eval("document.querySelector('.qa-pill').click()"); time.sleep(1)
    res['qa']=ser(c,"document.querySelector('.qa-menu')",'Quick Access Menu')
    c.goto('http://127.0.0.1:8000/index.html?v=2',settle=3.5)
    c.eval("document.querySelector('.adeck__all').click()"); time.sleep(1)
    res['ann']=ser(c,"document.querySelector('.fpage')",'Announcements')
    c.goto('http://127.0.0.1:8000/index.html?v=2',settle=3.5)
    c.eval("document.getElementById('obsViewAll').click()"); time.sleep(1)
    res['notes']=ser(c,"document.querySelector('.fpage')",'Observation Notes')
    print('errors',c.errors())
for k,v in res.items():
    json.dump(v,open(f'{F}/{k}.json','w'))
    acc={}; stats(v['tree'],acc)
    print(k,'nodes',count(v['tree']),'imgs',len(v['images']),'canv',len(v['canvases']),'bytes',len(json.dumps(v)))
    if len(sys.argv)<=2: print(sorted(acc.items(),key=lambda x:-x[1])[:400])
