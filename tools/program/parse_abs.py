import json,re
S='/tmp/claude-0/-home-claude/a7cc3c50-520b-50ed-aa2f-8be73c2de97a/scratchpad'
P=json.load(open(f'{S}/pdf/abs_lines.json'))
JP=re.compile(r'[぀-ヿ一-鿿]')
CODE=re.compile(r'^(IL\d|EL\d?|JHG\d|AL\d|S\d{1,2}-\d|ES\d|BO-\d\d|BP-\d\d|O\d{1,2}-\d\d|P\d-\d\d-\d\d|LS\d{1,2}(?:-\d)?|SS\d?-?\d?|SW\d(?:-\d)?|スポンサード(?:座長-)?\d)(?:\s+(.*))?$')
def clean(t):
    t=t.replace('(cid:222)','fi').replace('(cid:116)','–').replace(' ','').replace(' ',' ').replace('　',' ')
    return re.sub(r'\s+',' ',t).strip()
seq=[]
for pi,L in enumerate(P):
    L=[dict(l,t=clean(l['t'])) for l in L if l['t'].strip()]
    L=[l for l in L if not (re.fullmatch(r'\d{1,3}',l['t']) and 280<l['x']<310 and l['y']<60)]
    twocol=any(l['x']>295 and l['s']>=8.9 and CODE.match(l['t']) for l in L)
    if twocol:
        left=[l for l in L if l['x']<295]; right=[l for l in L if l['x']>=295]
        L=sorted(left,key=lambda l:-l['y'])+sorted(right,key=lambda l:-l['y'])
    else:
        L=sorted(L,key=lambda l:(-l['y'],l['x']))
    for l in L: l['two']=twocol; l['p']=pi+1
    seq+=L
blocks={};cur=None
for l in seq:
    m=CODE.match(l['t'])
    if m and l['s']>=8.9 and l['x']<320:
        cur={'code':m.group(1),'lines':[],'two':l['two'],'p':l['p']}
        if m.group(2): cur['lines'].append(dict(l,t=m.group(2),kind='title'))
        blocks.setdefault(cur['code'],cur); continue
    if cur is None: continue
    if (9.9<=l['s']<=10.5 or l['s']>=14) or re.match(r'^(Date|Room|Chairs?|Co-hosting|日\s*時|会\s*場|座\s*長|共\s*催|ディレクター)\s*[：:]',l['t']): cur=None; continue
    cur['lines'].append(l)
out={}
for code,b in blocks.items():
    body=[]
    for l in b['lines']:
        if l.get('kind')=='title': continue
        t=l['t']
        if b['two']:
            isbody = 7.9<=l['s']<=8.1
        else:
            isbody = l['s']>=8.4 and l['s']<=8.6 and not JP.search(t) and not t.startswith('（') and not re.match(r'^\d+\s',t)
        if isbody: body.append(t)
    # join with hyphen handling
    txt=''
    for t in body:
        if txt.endswith('-') and re.match(r'^[a-z]',t): txt=txt+t
        else: txt=(txt+' '+t).strip()
    code={'SS1-1':'SW1-1','SS1-2':'SW1-2','スポンサード座長-1':'SS-C1','スポンサード座長-2':'SS-C2','スポンサード1':'SS-1','スポンサード2':'SS-2','スポンサード3':'SS-3'}.get(code,code)
    out[code]={'abs':txt,'page':b['p']}
json.dump(out,open(f'{S}/pdf/abstracts.json','w'),ensure_ascii=False,indent=1)
print(len(out))
import collections
print(collections.Counter(re.sub(r'[\d\-]+$','',k)[:2] for k in out))
short=[(k,len(v['abs'])) for k,v in out.items() if len(v['abs'])<300]
print('short',len(short),short[:30])
for k in ['S13-2','O20-03','P1-07-02','IL1','LS4-1','BO-01']:
    if k in out: print(k, out[k]['abs'][:300],'\n')
