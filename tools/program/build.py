import json,re
S='/tmp/claude-0/-home-claude/a7cc3c50-520b-50ed-aa2f-8be73c2de97a/scratchpad'
ss=json.load(open(f'{S}/pdf/sessions.json'))
JP=re.compile(r'[぀-ヿ一-鿿]')
OVR={ # code: (title, authors)
 'S1-4':('Structural Resolution Redefines the Clinical Interpretation of Intragenic Duplications: Lessons from the DMD Gene','Man Jin Kim, Jee-Soo Lee, Seungbok Lee, Hobin Sung, Seung Won Chae, Sung Im Cho, Sang Bin Hong, Jong Ho Cha, Jee Min Kim, Yeseul Kim, Joowon Jang, Moon-Woo Seong, Jong-Hee Chae'),
 'O2-06':('Deep learning reinterpretation of germline VUS in hereditary cancer syndromes','Mario Bernabeu Aracil, Ana Fernandez Montes, Jesus Garcia Mata, María del Carmen Penín Corderi, Silvia Carles Gonzalez, Jimena Massiel Flores Ñaupari, Nooshin Bayat, Laura Martinez Gomez, Kristina Ibañez, Ander Martinez, Nuria Garcia Santa, Abe Shuya, Sho Takishita, Fuji Masaru, Clara Ruiz Ponte, Serban Georgescu, Raul Valin, Ceres Fernandez Rozadilla'),
 'O34-05':('Automated phenotype-driven prioritization of genomic variants tool in rare diseases tested on inherited heart conditions','Kristina Ibañez, Alejandro Blanco-Verea, Nooshin Bayat, Laura Martinez, Ander Martinez, Sho Takishita, Shuya Abe, Masaru Fuji, Raul Valin, María Brion, Nuria García-Santa'),
 'LS5-1':('Next-Generation Mapping: Unlocking the Architecture of the Human Genome with Electronic Genome Mapping','Alka Chaubey'),
 'O6-03':('Complete Paternal Isodisomy of Chromosome 10 Harboring a Novel ERLIN1 Variant Causing Spastic Paraplegia Type 62',None),
 'O10-02':(None,None),
}
def clean_auth(a):
    a=re.sub(r'\s*\d+(,\d+)*\s*（','（',a)      # 名前 1,2 （Romaji） → 名前（Romaji）
    a=re.sub(r'\s+\d+(,\d+)*\s*(?=,|$)','',a)   # Latin Name 1, → Latin Name,
    a=re.sub(r'\s*,\s*',', ',a).strip(' ,')
    a=a.replace('(cid:8267)','辻')
    return a
def first_author(a):
    p=a.split(', ')[0] if a else ''
    p=re.sub(r'（.*?）','',p).strip()
    return p
def jp_affils(aff):
    # keep JP lines (strip leading index), skip English paren lines; merge continuation
    out=[]
    for l in aff:
        if l.startswith('（') or l.startswith('('): continue
        if re.fullmatch(r'\d+',l): continue
        l=re.sub(r'^\d+\s*','',l)
        if not JP.search(l):
            # English-only affil (foreign) keep
            if out and not out[-1].endswith('）') and re.match(r'^[A-Z]',l) is None: out[-1]+=' '+l; continue
        out.append(l)
    # dedupe preserving order
    seen=[];[seen.append(x) for x in out if x not in seen]
    return seen
def meta(s):
    m={'date':'','time':'','room':'','chairs':[],'sponsor':''}
    for t in s['meta']:
        mm=re.match(r'日\s*時：11月(\d+)日（(.)）\s*(\d+:\d+)[～〜](\d+:\d+)',t)
        if mm: m['date']=f"11/{mm.group(1)}({mm.group(2)})"; m['time']=f"{mm.group(3)}-{mm.group(4)}"; continue
        mm=re.match(r'会\s*場：(.+)',t)
        if mm: m['room']=mm.group(1); continue
        mm=re.match(r'座\s*長：(.+)',t)
        if mm: m['chairs'].append(mm.group(1)); m['_ch']=True; continue
        mm=re.match(r'共\s*催：(.+)',t)
        if mm: m['sponsor']=mm.group(1); m['_ch']=False; continue
        if re.match(r'(Date|Room|Chairs?|Co-hosting)\s*：',t): m['_ch']=False; continue
        if m.get('_ch') and JP.search(t): m['chairs'].append(t)
    m['chairs']='／'.join(re.sub(r'（.*?）','',c).strip() for c in m['chairs'])
    return m
def room_short(r):
    mm=re.match(r'(第\d会場|ポスター会場|ハンズオンセミナー会場)（[^）]*?\s*([^（）\s]+(?:\s[^（）]+)?)）',r)
    if not mm: return r
    name=mm.group(1).replace('ハンズオンセミナー会場','ハンズオン会場'); inner=mm.group(2)
    return f"{name}（{inner}）"
orals=[];posters=[];misc=[]
for s in ss:
    n=s['name']; M=meta(s)
    for it in s['items']:
        code=it['code']; title=it['title']; auth=it['authors']
        if code in OVR:
            t2,a2=OVR[code]; title=t2 or title; auth=a2 if a2 is not None else auth
        if code=='O10-02': title=title+' Dystrophy Type 1'; auth=auth.replace('Dystrophy Type 1 ','')
        auth=clean_auth(auth)
        rec={'code':code,'title':title,'authors':auth,'affils':jp_affils(it['affil']),'session':n,'date':M['date'],'time':M['time'],'room':room_short(M['room']),'chairs':M['chairs'],'sponsor':M['sponsor']}
        if code.startswith('P') and re.match(r'P\d-',code): posters.append(rec)
        elif re.match(r'O\d',code): orals.append(rec)
        else: misc.append(rec)
json.dump({'orals':orals,'posters':posters,'misc':misc},open(f'{S}/pdf/built.json','w'),ensure_ascii=False,indent=1)
print(len(orals),len(posters),len(misc))
print(json.dumps(orals[0],ensure_ascii=False)[:600])
print(json.dumps(posters[5],ensure_ascii=False)[:600])
from collections import Counter
print(Counter((o['date'],o['time'],o['room']) for o in orals).most_common(3))
print(set(p['room'] for p in posters), Counter(p['date'] for p in posters))
