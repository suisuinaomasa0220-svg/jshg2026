import json, numpy as np, sys
sys.path.insert(0,'.')
from concepts import VOCAB, C
from wordllama import WordLlama
from sklearn.manifold import TSNE
from sklearn.decomposition import PCA
from sklearn.cluster import AgglomerativeClustering
tt=[x for x in json.load(open('tt_keep.json')) if x['code']!='CN']
pv=json.load(open('pv_rows.json'))
items=[dict(code=x['code'],t='t',en=x['en'],ja=x['ja']) for x in tt]+[dict(code=x['code'],t='p',en=x['en'],ja=x['ja']) for x in pv]
miss=[i['code'] for i in items if i['code'] not in C]; assert not miss, miss
bad=[(k,w) for k,v in C.items() for w in v.split() if w not in VOCAB]; assert not bad, bad
V=list(VOCAB)
X=np.array([[1.0 if v in C[i['code']].split() else 0 for v in V] for i in items])
idf=np.log((1+len(X))/(1+X.sum(0)))+1; Xc=X*idf; Xc/=np.linalg.norm(Xc,axis=1,keepdims=True)
wl=WordLlama.load(cache_dir='wlcache',disable_download=True)
E=wl.embed([i['en'] for i in items],norm=True)
Z=np.hstack([Xc*1.0, E*0.45])            # topics = main signal, model = secondary
Z/=np.linalg.norm(Z,axis=1,keepdims=True)
ts=TSNE(n_components=2,perplexity=14,metric='cosine',init='pca',random_state=7,max_iter=2500).fit_transform(Z)
pc=PCA(n_components=2,random_state=7).fit_transform(Z)
K=int(sys.argv[1]) if len(sys.argv)>1 else 11
lab=AgglomerativeClustering(n_clusters=K,metric='cosine',linkage='average').fit_predict(Z)
for k in range(K):
    idx=np.where(lab==k)[0]; cnt=X[idx].sum(0); top=[V[j] for j in np.argsort(-cnt)[:4] if cnt[j]>0]
    print(k,len(idx),top,[items[i]['code'] for i in idx][:14])
def nz(a):a=a-a.min(0);return (a/a.max(0)).round(4).tolist()
json.dump(dict(items=items,ts=nz(ts),pc=nz(pc),lab=lab.tolist(),topics={i['code']:C[i['code']].split() for i in items}),open('map_raw.json','w'),ensure_ascii=False)

# ---- final payload for the app
NAMES={0:"疾患モデル・再生・エピゲノム",1:"希少疾患・小児（診断→治療）",2:"集団遺伝・進化・染色体",3:"倫理・遺伝カウンセリング（PGT・SRY）",
4:"多因子疾患・GWAS・AI",5:"がん（遺伝性・腫瘍）・免疫",6:"周産期・栄養",7:"ゲノム医療の実装・制度",8:"循環器・代謝・臨床検査",9:"神経・リピート病",10:"機能ゲノミクス・シングルセル"}
JA={"gwas":"GWAS・多因子","prs":"PRS","popgen":"集団遺伝・進化","funcgen":"機能ゲノミクス","sc":"シングルセル","rna":"RNA・スプライシング","epi":"エピゲノム",
"lr":"ロングリード・構造多型","seqdx":"ゲノム診断","rare":"希少疾患","neuro":"神経・神経筋","neurodev":"神経発達・脳","hcancer":"遺伝性がん","scancer":"腫瘍・体細胞",
"repro":"生殖・PGT","perinatal":"周産期","peds":"小児","cardio":"循環器","metab":"代謝・ミトコンドリア","immuno":"免疫・血液","rx":"治療・創薬","model":"疾患モデル",
"regen":"再生・リプログラミング","ai":"AI・バイオインフォ","elsi":"倫理・法・制度","gc":"遺伝カウンセリング・臨床","lab":"臨床検査","impl":"医療実装・制度","dsd":"性分化・スポーツ",
"repeat":"リピート病","cyto":"染色体・細胞遺伝","env":"遺伝×環境・栄養","biobank":"バイオバンク・コホート","mosaic":"モザイク"}
assert set(NAMES)==set(range(K)) and set(JA)==set(VOCAB)
Sim=Z@Z.T;np.fill_diagonal(Sim,-1)
nb=[[int(j) for j in np.argsort(-Sim[i])[:5]] for i in range(len(items))]
T=nz(ts);P=nz(pc)
out=dict(v=1,clusters=[NAMES[k] for k in range(K)],topics=JA,
 items=[dict(c=it['code'],t=it['t'],k=int(lab[i]),x=T[i][0],y=T[i][1],px=P[i][0],py=P[i][1],tp=C[it['code']].split(),nb=nb[i]) for i,it in enumerate(items)])
json.dump(out,open('mapdata.json','w'),ensure_ascii=False,separators=(',',':'))
print('mapdata.json',len(out['items']),'items', round(len(json.dumps(out,ensure_ascii=False))/1024,1),'KB')
print('example neighbors of S16-1:',[items[j]['code'] for j in nb[[i['code'] for i in items].index('S16-1')]])
print('example neighbors of S2-2:',[items[j]['code'] for j in nb[[i['code'] for i in items].index('S2-2')]])

# ---- 学会の注目度（データから）：トピックごとに「どれだけの量と格で扱われているか」を足し上げ、演題はそのトピックの平均
KW={'招待講演':3.0,'教育講演':3.0,'シンポジウム':2.0,'教育セッション':1.5,'一般口演':1.0,'ポスター':0.5}
kinds={x['code']:x['kind'] for x in tt}
wt=np.array([KW.get(kinds.get(it['code'],'ポスター'),1.0) for it in items])
emph=(X*wt[:,None]).sum(0)                       # トピックごとの扱いの厚さ
att=np.array([emph[X[i]>0].mean() if X[i].sum() else 0 for i in range(len(items))])
rank=att.argsort().argsort()/(len(att)-1)        # 0〜1の順位にそろえる
top=sorted([(V[j],round(float(emph[j]),1)) for j in range(len(V))],key=lambda t:-t[1])
print('emphasis top:',top[:8]); print('emphasis bottom:',top[-6:])
for i,it in enumerate(out['items']): it['att']=round(float(rank[i]),3)
out['emph']={V[j]:round(float(emph[j]),2) for j in range(len(V))}
json.dump(out,open('mapdata.json','w'),ensure_ascii=False,separators=(',',':'))
print('att added; e.g.', [(items[i]['code'],out['items'][i]['att']) for i in [0,10,50,100,140]])
