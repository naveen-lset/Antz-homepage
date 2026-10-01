import json,sys,html
def make(key, payload, chunk=40000):
    s=json.dumps(payload,ensure_ascii=False,separators=(',',':'))
    parts=[s[i:i+chunk] for i in range(0,len(s),chunk)]
    texts=[]
    for i,p in enumerate(parts):
        t=f'@@{key}@@{i}@@{len(parts)}@@'+p
        t=html.escape(t,quote=False).replace(' ','&#160;')
        texts.append(f'<text x="0" y="{(i+1)*20}" font-family="Inter" font-size="12">{t}</text>')
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="200" height="{(len(parts)+1)*20}">'+''.join(texts)+'</svg>', len(s), len(parts)
if __name__=='__main__':
    test={'hello':'world  two  spaces & <tags> “quotes” 👋🏻 •','big':'x y '*30000}
    svg,n,k=make('test',test); open('carrier_test.svg','w').write(svg); print(n,k,len(svg))
