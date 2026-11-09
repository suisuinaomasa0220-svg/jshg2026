import json, numpy as np, sys
sys.path.insert(0,'.')
from concepts import VOCAB
from autotopics import topics as auto
from wordllama import WordLlama
from sklearn.manifold import TSNE
from sklearn.decomposition import PCA
from sklearn.cluster import AgglomerativeClustering
tt=json.load(open('tt_keep.json')); pv=json.load(open('pv_rows.json'))
items=[dict(code=x['code'],t='t',kind=x['kind'],en=x['en'],ja=x['ja'],txt=x['en']+' . '+x.get('abs','')) for x in tt]+\
      [dict(code=x['code'],t='p',kind='ポスター',en=x['en'],ja=x['ja'],txt=x['en']+' . '+x.get('abs','')) for x in pv]
C={it['code']:auto(it['txt']) for it in items}
V=list(VOCAB)
X=np.array([[1.0 if v in C[it['code']] else 0 for v in V] for it in items])
idf=np.log((1+len(X))/(1+X.sum(0)))+1; Xc=X*idf; Xc/=np.linalg.norm(Xc,axis=1,keepdims=True)
wl=WordLlama.load(cache_dir='wlcache',disable_download=True)
E=wl.embed([ (it['en']+'. '+it['txt'].split(' . ',1)[-1])[:600] for it in items],norm=True)
Z=np.hstack([Xc*1.0, E*0.5]); Z/=np.linalg.norm(Z,axis=1,keepdims=True)
K=14
lab=AgglomerativeClustering(n_clusters=K,metric='cosine',linkage='average').fit_predict(Z)
ts=TSNE(n_components=2,perplexity=16,metric='cosine',init='pca',random_state=7,max_iter=2500).fit_transform(Z)
pc_model=PCA(n_components=2,random_state=7).fit(Z); pc=pc_model.transform(Z)
def nz(a):a=a-a.min(0);return (a/a.max(0)).round(4).tolist()
NAMES={
 0:"多因子疾患・GWAS・集団遺伝",1:"がん（遺伝性・腫瘍）",2:"機能ゲノミクス・エピゲノム・発生",
 3:"疾患モデル・再生医療",4:"ロングリード・リピート病・神経",5:"臨床遺伝（小児〜成人）診断と治療",
 6:"生殖・周産期・性分化・倫理",7:"臨床検査（遺伝型‐表現型）",8:"AI・機械学習・バリアント解釈",
 9:"希少疾患の診断（症例・AI支援）",10:"RASopathy・神経・循環器モデル",11:"遺伝×環境・代謝・栄養",
 12:"神経・ゲノム解析（混在）",13:"神経発達・染色体・小児診断"}
JA={"gwas":"GWAS・多因子","prs":"PRS","popgen":"集団遺伝・進化","funcgen":"機能ゲノミクス","sc":"シングルセル","rna":"RNA・スプライシング","epi":"エピゲノム",
"lr":"ロングリード・構造多型","seqdx":"ゲノム診断","rare":"希少疾患","neuro":"神経・神経筋","neurodev":"神経発達・脳","hcancer":"遺伝性がん","scancer":"腫瘍・体細胞",
"repro":"生殖・PGT","perinatal":"周産期","peds":"小児","cardio":"循環器","metab":"代謝・ミトコンドリア","immuno":"免疫・血液","rx":"治療・創薬","model":"疾患モデル",
"regen":"再生・リプログラミング","ai":"AI・バイオインフォ","elsi":"倫理・法・制度","gc":"遺伝カウンセリング・臨床","lab":"臨床検査","impl":"医療実装・制度","dsd":"性分化・スポーツ",
"repeat":"リピート病","cyto":"染色体・細胞遺伝","env":"遺伝×環境・栄養","biobank":"バイオバンク・コホート","mosaic":"モザイク"}
assert set(NAMES)==set(range(K)) and set(JA)==set(VOCAB)
Sim=Z@Z.T;np.fill_diagonal(Sim,-1)
nb=[[int(j) for j in np.argsort(-Sim[i])[:5]] for i in range(len(items))]
T=nz(ts);P=nz(pc)
# attention att
KW={'招待講演':3.0,'教育講演':3.0,'受賞・大会賞':2.5,'シンポジウム':2.0,'教育セッション':1.5,'ランチョンセミナー':1.2,'一般口演':1.0,'ポスター':0.5}
wt=np.array([KW.get(it['kind'],1.0) for it in items])
emph=(X*wt[:,None]).sum(0)
att=np.array([emph[X[i]>0].mean() if X[i].sum() else 0 for i in range(len(items))])
rank=att.argsort().argsort()/(len(att)-1)
out=dict(v=2,clusters=[NAMES[k] for k in range(K)],topics=JA,
 items=[dict(c=it['code'],t=it['t'],k=int(lab[i]),x=T[i][0],y=T[i][1],px=P[i][0],py=P[i][1],tp=C[it['code']],nb=nb[i],att=round(float(rank[i]),3)) for i,it in enumerate(items)])
out['emph']={V[j]:round(float(emph[j]),2) for j in range(len(V))}
json.dump(out,open('mapdata.json','w'),ensure_ascii=False,separators=(',',':'))
# PCA axis meaning
ev=pc_model.explained_variance_ratio_
print('PCA explained:',[round(float(x),3) for x in ev],'sum',round(float(ev.sum()),3))
for ax in [0,1]:
    cor=[(V[j],round(float(np.corrcoef(pc[:,ax],X[:,j])[0,1]),2)) for j in range(len(V))]
    cor=[c for c in cor if abs(c[1])>=0.2]; cor.sort(key=lambda c:-c[1])
    print(f'PC{ax+1} +:',cor[:5]); print(f'PC{ax+1} -:',cor[-5:])
print('mapdata.json', len(out['items']),'items', round(len(open("mapdata.json").read())/1024,1),'KB')
from collections import Counter
print(Counter(it['t'] for it in out['items']))
