import math,json,sys
# right-handed B-DNA, 10.5 bp per turn; colors from the original icon
def svg(Wb,Hb,scale,PH=0.0):
    sw=18.5*scale; A=(Wb-sw)/2; cx=Wb/2; P=190*scale; BP=10.5
    y0=sw/2; y1=Hb-sw/2
    def X(y,off): th=2*math.pi*(y1-y)/P+off+PH; return cx+A*math.cos(th), math.sin(th)
    def segs(off):
        out=[];cur=None;y=y0;st=0.5*scale
        while y<=y1+1e-6:
            x,d=X(y,off); f=d<0
            if cur is None or cur[0]!=f:
                if cur: cur[1].append((x,y))
                cur=(f,[(x,y)]); out.append(cur)
            else: cur[1].append((x,y))
            y+=st
        return out
    back=[];front=[];rungs=[]
    for off in (0,math.pi):
        for f,pts in segs(off):
            if len(pts)<2: continue
            d='M'+' L'.join(f'{x:.2f} {y:.2f}' for x,y in pts)
            (front if f else back).append(d)
    step=P/BP; y=y0+step*0.5
    while y<y1-step*0.2:
        xa,_=X(y,0); xb,_=X(y,math.pi); l,r=sorted((xa,xb))
        if r-l>sw*0.9: rungs.append((l,r,y))
        y+=step
    rh=8*scale
    s=[f"<svg xmlns='http://www.w3.org/2000/svg' width='{Wb}' height='{Hb}' viewBox='0 0 {Wb} {Hb}'>"]
    for l,r,y in rungs: s.append(f"<rect x='{l:.2f}' y='{y-rh/2:.2f}' width='{r-l:.2f}' height='{rh:.2f}' fill='#FFD7E6'/>")
    for d in back: s.append(f"<path d='{d}' fill='none' stroke='#E8AAC0' stroke-width='{sw*0.85:.2f}' stroke-linecap='round'/>")
    for d in front: s.append(f"<path d='{d}' fill='none' stroke='#FFFFFF' stroke-width='{sw:.2f}' stroke-linecap='round'/>")
    s.append('</svg>')
    return ''.join(s), len(rungs), (y1-y0)/P
cfg={ # file: (x0,x1,y0,y1)  helix bbox (inclusive)
 'icon-512.png':(172,340,41,329),'icon-192.png':(64,127,15,123),
 'icon-maskable-512.png':(190,321,88,313),'icon-maskable-192.png':(71,120,33,117)}
out={}
for f,(x0,x1,y0,y1) in cfg.items():
    Wb=x1-x0+1;Hb=y1-y0+1;scale=Wb/169
    sv,n,t=svg(Wb,Hb,scale,float(sys.argv[2]) if len(sys.argv)>2 else 0.0); out[f]=dict(svg=sv,x0=x0,y0=y0,W=Wb,H=Hb)
    print(f,'rungs',n,'turns',round(t,2),'bp/turn',10.5)
json.dump(out,open(sys.argv[1],'w'))
