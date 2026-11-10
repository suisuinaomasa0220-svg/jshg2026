import math
# B-DNA: right-handed, 10.5 bp per turn. Screen y goes down; theta increases going UP.
CX,R,Y0,Y1,P=62.0,30.0,8.0,252.0,120.0     # P = pixels per full turn (same scale as before)
BP=10.5
def pt(y,off): th=2*math.pi*(Y1-y)/P+off; return CX+R*math.cos(th), math.sin(th)
def strand(off):
    out=[];cur=None;y=Y0
    while y<=Y1+1e-6:
        x,d=pt(y,off); front=d<0
        if cur is None or cur[0]!=front:
            if cur: cur[1].append((x,y))      # close segment at boundary
            cur=(front,[(x,y)]); out.append(cur)
        else: cur[1].append((x,y))
        y+=1.5
    return out
els=[]
for off in (0.0, math.pi):
    for front,pts in strand(off):
        if len(pts)<2: continue
        d='M'+' L'.join(f'{x:.1f} {y:.1f}' for x,y in pts)
        els.append(f"<path d='{d}'"+("" if front else " stroke-width='1.3' opacity='.55'")+"/>")
# base pairs: one rung per base pair, P/10.5 apart, split in the middle like before
step=P/BP; y=Y0+step*0.5; n=0
rungs=[]
while y<Y1:
    xa,_=pt(y,0.0); xb,_=pt(y,math.pi)
    l,r=min(xa,xb),max(xa,xb); mid=(l+r)/2; gap=min(1.6,(r-l)/2)
    if r-l>4:
        rungs.append(f"<line x1='{l:.1f}' y1='{y:.1f}' x2='{mid-gap:.1f}' y2='{y:.1f}' stroke-width='1.6'/>")
        rungs.append(f"<line x1='{mid+gap:.1f}' y1='{y:.1f}' x2='{r:.1f}' y2='{y:.1f}' stroke-width='1.6'/>")
    y+=step; n+=1
back=[e for e in els if "opacity='.55'" in e]; front=[e for e in els if "opacity='.55'" not in e]
group=''.join(back)+''.join(rungs)+''.join(front)
print(f"bp drawn={n}, per turn={P/step:.1f}, turns={(Y1-Y0)/P:.2f}")
open('/tmp/claude-0/-home-claude/a7cc3c50-520b-50ed-aa2f-8be73c2de97a/scratchpad/helix_group.txt','w').write(group)
