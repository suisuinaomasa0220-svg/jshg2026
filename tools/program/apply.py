import re,json
S='/tmp/claude-0/-home-claude/a7cc3c50-520b-50ed-aa2f-8be73c2de97a/scratchpad'
P='/home/claude/jshg2026/page.html'
s=open(P).read()
m=re.search(r'(<script type="application/json" id="data">)(.*?)(</script>)',s,re.S)
data=json.loads(m.group(2))
b=json.load(open(f'{S}/pdf/built.json'))
by={d['code']:d for d in data}
def spk(r):
    a=r['authors'].split(', ') if r['authors'] else []
    f=re.sub(r'（.*?）','',a[0]).strip() if a else ''
    return f+(f'（ほか{len(a)-1}名）' if len(a)>1 else '')
def aff(r): return r['affils'][0] if r['affils'] else ''
def strip_num(t): return re.sub(r'^\d+\s*','',t)
out=[]
# --- oral sessions: replace OS items
for d in data:
    if d['kind']=='一般口演':
        n=int(d['code'][2:])
        talks=[r for r in b['orals'] if re.match(rf'O{n}-\d\d$',r['code'])]
        for r in talks:
            out.append({'code':r['code'],'kind':'一般口演','session':f"Oral Session {n}：{d['title']}",'date':d['date'],'time':d['time'],'room':d['room'],'chairs':d['chairs'],'lang':d['lang'],
                        'title':r['title'],'ja':'','speaker':spk(r),'affil':aff(r),'authors':r['authors'],'affils':r['affils']})
        continue
    if d['code']=='AW1':
        for r in b['misc']:
            if r['code'].startswith('BO-'):
                out.append({**d,'code':r['code'],'title':r['title'],'ja':'','speaker':spk(r),'affil':aff(r),'authors':r['authors'],'affils':r['affils']})
        continue
    if d['code']=='AW2':
        for r in b['misc']:
            if r['code'].startswith('JHG'):
                out.append({**d,'code':r['code'],'title':r['title'],'ja':'','speaker':spk(r),'affil':aff(r),'authors':r['authors'],'affils':r['affils']})
        continue
    if d['code']=='AW3':
        for r in b['misc']:
            if re.match(r'AL\d',r['code']):
                out.append({**d,'code':r['code'],'title':r['title'],'ja':'','speaker':spk(r),'affil':aff(r),'authors':r['authors'],'affils':r['affils']})
        continue
    if d['kind']=='ランチョンセミナー':
        n=int(d['code'][2:])
        rs=[r for r in b['misc'] if re.match(rf'LS{n}(-\d)?$',r['code'])]
        sess=next(x for x in rs)['session']
        jt=re.sub(r'^ランチョンセミナー\s*\d+\s*','',sess.split(' | Luncheon')[0]).replace(' | ','')
        spons=d['affil'].replace('共催：','')
        for r in rs:
            out.append({**d,'code':r['code'],'session':f"ランチョンセミナー{n}：{jt}",'title':r['title'],'ja':'','speaker':spk(r),'affil':aff(r),'sponsor':spons,'authors':r['authors'],'affils':r['affils']})
        continue
    if d['code']=='SW1':
        base={**d,'session':'スイーツセミナー：希少疾患診断を加速するナノポアシーケンスの可能性','ja':'','sponsor':'株式会社ジーンベイ'}
        out.append({**base,'code':'SW1-1','title':'Analysis of complex chromosomal structural abnormalities using nanopore long-read sequencing','speaker':'山本 俊至','affil':'東京女子医科大学 遺伝子医学分野／ゲノム診療科'})
        out.append({**base,'code':'SW1-2','title':'Latest Advances in Nanopore Transcriptome Sequencing','speaker':'上村 泰央','affil':'株式会社ジーンベイ'})
        continue
    if d['code'].startswith('SS-'):
        if d['code']=='SS-1':
            sp=[r for r in b['misc'] if r['code'].startswith('スポンサード')]
            # chair lectures
            c1=sp[0]; c2=sp[1]
            base={**d,'session':'スポンサードシンポジウム：AMEDが支援するゲノム・オミックスデータの利活用（共催：AMED）','time':'14:20-15:40','ja':''}
            out.append({**base,'code':'SS-C1','title':c1['title'],'speaker':'小林 憲明','affil':'バイオインダストリー協会'})
            out.append({**base,'code':'SS-C2','title':c2['title']+' Diseases','speaker':'中川 英刀','affil':'理化学研究所 生命医科学研究センター'})
            t1=sp[2]; t2=sp[3]
            out.append({**base,'code':'SS-1','title':t1['title'],'speaker':spk(t1),'affil':aff(t1),'authors':t1['authors'],'affils':t1['affils']})
            out.append({**base,'code':'SS-2','title':t2['title'],'speaker':spk(t2),'affil':aff(t2),'authors':t2['authors'],'affils':t2['affils']})
            out.append({**base,'code':'SS-3','title':'BioBank Japan in CANNDS: Data Utilization, Sustainable Access, and Future Directions through TRE and JAMBO','speaker':'松田 浩一','affil':'東京大学大学院新領域創成科学研究科'})
        continue
    if d['code']=='IL2':
        d=dict(d,title='Epigenetic inheritance – models and mechanisms',ja='エピジェネティック遺伝：モデルとメカニズム')
    if d['code']=='S5-1':
        d=dict(d,title='The ASHG AI Initiative Task Force (tentative)',ja='ASHG AIイニシアチブ・タスクフォース（仮）')
    if d['kind']=='ポスター発表':
        n=sum(1 for r in b['posters'] if r['code'].startswith(d['code'].replace('PD','P')+'-'))
        d=dict(d,title=f"{d['title']}（{n}題）",pcat=d['code'].replace('PD','P'))
    out.append(d)
# fix withdrawn
for d in out:
    if d['title']=='演題取り下げ': d['title']='（演題取り下げ）'; d['speaker']=''; d['affil']=''
from collections import Counter
print(len(data),'->',len(out)); print(Counter(d['kind'] for d in out))
new_json=json.dumps(out,ensure_ascii=False,separators=(', ',': '))
s=s[:m.start(2)]+new_json+s[m.end(2):]
# --- posters
pst=[]
for r in b['posters']:
    cat=re.sub(r'^Poster Session \d-\d\d\s*\|?\s*','',r['session'])
    t=r['title'] if r['title']!='演題取り下げ' else '（演題取り下げ）'
    pst.append({'code':r['code'],'title':t,'ja':'','authors':r['authors'],'affil':'／'.join(r['affils'][:2])+('ほか' if len(r['affils'])>2 else ''),'abs':'','cat':cat})
# BP (poster award) also as posters
for r in b['misc']:
    if r['code'].startswith('BP-'):
        pst.append({'code':r['code'],'title':r['title'],'ja':'','authors':r['authors'],'affil':'／'.join(r['affils'][:2])+('ほか' if len(r['affils'])>2 else ''),'abs':'','cat':'優秀演題賞（ポスター）候補'})
i=s.find('const POSTERS'); j=s.find('];',i)+2
k=s.find('/* ---------- classification rules ---------- */',j)
pjson=json.dumps(pst,ensure_ascii=False,separators=(',',':'))
s=s[:i]+'const POSTERS='+pjson+';\n\n'+s[k:]
# day for BP: 11/20 (P2) → dayOf needs handling
s=s.replace('function dayOf(p,i){const m=String(p.code).match(/^P([123])-/);return m?m[1]:String(i%3+1)}',
            'function dayOf(p,i){const m=String(p.code).match(/^P([123])-/);if(m)return m[1];if(String(p.code).startsWith("BP-"))return "2";return String(i%3+1)}')
# remove mock banner
s=re.sub(r'\s*<div class="mockbanner">.*?</div>','',s,count=1)
open(P,'w').write(s)
print('posters',len(pst), len(s))
