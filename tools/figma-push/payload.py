import json,sys,subprocess,os,urllib.parse
from carrier import make
F=os.path.dirname(os.path.abspath(__file__))
FIXED={'ann':1133,'notes':1133}
def run(key):
    d=json.load(open(f'{F}/{key}.json')); S=[]; idx={}
    def walk(n):
        if n.get('t')=='V':
            s=n['svg']
            if s not in idx: idx[s]=len(S); S.append(s)
            n['svg']=idx[s]
        for k in n.get('kids',[]): walk(k)
    walk(d['tree'])
    p={'tree':d['tree'],'S':S}
    if key in FIXED: p['fixedH']=FIXED[key]
    svg,n,k=make(key,p); open(f'{F}/carrier_{key}.svg','w').write(svg)
    # images to disk
    files={}
    for im in d['images']:
        ext=os.path.splitext(urllib.parse.urlparse(im['src']).path)[1] or '.png'
        out=f"{F}/{key}_{im['id']}{ext}"
        if not os.path.exists(out): subprocess.run(['curl','-s','-o',out,im['src']])
        files[im['id']]=out
    for cv in d['canvases']: files[cv['id']]=f"{F}/{key}_{cv['id']}.png"
    json.dump(files,open(f'{F}/{key}_files.json','w'))
    print(key,'json',n,'chunks',k,'svgs',len(S),'images',len(files))
for key in sys.argv[1:]: run(key)
