import json,re,sys
CODEPFX=re.compile(r'^(O\d{1,2}-\d\d|P\d-\d\d-\d\d|BP-\d\d|BO-\d\d|LS\d{1,2}(?:-\d)?)\s+(\S.*)$')
S='/tmp/claude-0/-home-claude/a7cc3c50-520b-50ed-aa2f-8be73c2de97a/scratchpad'
P=json.load(open(f'{S}/pdf/program_lines.json'))
def clean(t):
    t=t.replace('(cid:222)','fi').replace('(cid:116)','–').replace('(cid:223)','fl')
    t=t.replace(' ',' ').replace(' ',' ').replace('　',' ')
    return re.sub(r'\s+',' ',t).strip()
lines=[]
for pi,L in enumerate(P):
    for l in L:
        t=clean(l['t'])
        if not t: continue
        if l['s']<=6.5: continue  # 'English' 'Session' labels
        if re.fullmatch(r'\d{1,3}',t) and l['x']>250: continue  # page number
        m=CODEPFX.match(t)
        if m and l['s']>=8.8 and l['x']<80:
            lines.append(dict(l,t=m.group(1),s=8.0,p=pi+1)); lines.append(dict(l,t=m.group(2),x=127.1,p=pi+1)); continue
        lines.append(dict(l,t=t,p=pi+1))
CODE=re.compile(r'^(IL\d|EL\d?|JHG\d|AL\d|S\d{1,2}-\d|ES\d|BO-\d\d|BP-\d\d|O\d{1,2}-\d\d|P\d-\d\d-\d\d|LS\d{1,2}(-\d)?|SS\d?|SW\d?|スポンサード\d?|ハンズオン\d?|WS\d?)$')
HEAD=re.compile(r'^(招待講演\s*\d|教育講演|JHG Young|受賞講演|シンポジウム\s*\d+|教育セッション\s*\d|ClinicalNotes|大会賞候補|Oral Session\s*\d+|優秀演題賞|Poster Session\s*\d-\d\d|ランチョンセミナー\s*\d+|スイーツセミナー|スポンサードシンポジウム|ハンズオンセミナー|メディカルバイオインフォマティクス)')
sessions=[]; cur=None
i=0
NAME=r"[A-Z][A-Za-z'’\-\.]*(?:\s[A-Z][A-Za-z'’\-\.]*){1,4}"
LATIN_AUTH=re.compile(r"^(?:"+NAME+r"\s*\d*(?:,\d+)*\s*,?\s*)+$")
def is_authors(t):
    if re.search(r'[（(][A-Z][a-z]',t) and re.search(r'[\u3040-\u30ff\u4e00-\u9fff]',t): return True
    if LATIN_AUTH.match(t) and len(t)<160: return True
    return False
while i<len(lines):
    l=lines[i]; t=l['t']
    if l['s']>=9.9 and l['x']<80 and HEAD.match(t):
        # session header, may continue with size-10 lines at x>80 (subtitle) or next size10 line
        name=t; j=i+1
        while j<len(lines) and lines[j]['s']>=9.9 and lines[j]['p']==l['p'] and not HEAD.match(lines[j]['t']) :
            name+=' | '+lines[j]['t']; j+=1
        cur={'name':name,'meta':[],'items':[],'page':l['p']}
        sessions.append(cur); i=j; continue
    if CODE.match(t) and l['s']<=8.6:
        code=t
        # title: previous line if size 9 and close y and x>=120
        title=[]
        k=i-1
        if k>=0 and lines[k]['s']>=8.8 and lines[k]['x']>=120 and abs(lines[k]['y']-l['y'])<4 and lines[k]['p']==l['p']:
            title.append(lines[k]['t'])
            # remove from previous item's trailing? it was consumed into meta maybe; handle below
            if cur and cur['items'] and cur['items'][-1].get('_tail') is not None:
                tail=cur['items'][-1]['_tail']
                if tail and tail[-1] is lines[k]: tail.pop()
            elif cur and cur['meta'] and cur['meta'][-1] is lines[k]:
                cur['meta'].pop()
        j=i+1; authors=[]; affil=[]
        state='title'
        while j<len(lines):
            m=lines[j]
            if CODE.match(m['t']) and m['s']<=8.6: break
            if m['s']>=9.9 and m['x']<80 and HEAD.match(m['t']): break
            # a size-9 line at x>=120 right before a code line belongs to next item
            if j+1<len(lines) and CODE.match(lines[j+1]['t']) and lines[j+1]['s']<=8.6 and abs(lines[j+1]['y']-m['y'])<4 and m['s']>=8.8 and m['x']>=120 and lines[j+1]['p']==m['p']:
                break
            if m['s']<=8.0 or m['x']>=130 and m['s']<8.8:
                state='affil'; affil.append(m['t'])
            elif state=='title' and not is_authors(m['t']):
                title.append(m['t'])
            else:
                if state!='affil': state='authors'; authors.append(m['t'])
                else: affil.append(m['t'])
            j+=1
        it={'code':code,'title':' '.join(title),'authors':' '.join(authors),'affil':affil,'page':l['p']}
        if cur is None: cur={'name':'?','meta':[],'items':[],'page':l['p']}; sessions.append(cur)
        cur['items'].append(it); i=j; continue
    if cur: cur['meta'].append(l)
    i+=1
for s in sessions:
    s['meta']=[m['t'] for m in s['meta']]
    for it in s['items']:
        m=re.match(r'^([^\u3040-\u30ff\u4e00-\u9fff（]+?)\s+(?=[\u3040-\u30ff\u4e00-\u9fff])',it['authors'])
        if m:
            pre=m.group(1).strip()
            if not re.search(r',\s*$',pre) and not re.search(r'\s\d+(,\d+)*\s*$',pre):
                it['title']=(it['title']+' '+pre).strip(); it['authors']=it['authors'][m.end():]
        it['title']=re.sub(r'\s+',' ',it['title'])
json.dump(sessions,open(f'{S}/pdf/sessions.json','w'),ensure_ascii=False,indent=1)
print(len(sessions), sum(len(s['items']) for s in sessions))
for s in sessions: print(s['page'], s['name'][:60], len(s['items']), [it['code'] for it in s['items']][:3])
