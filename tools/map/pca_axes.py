# 全体傾向（PCA）の軸の意味を調べる：各軸のスコアと各トピック（0/1）の相関、説明率、両端の演題例
# 使い方: build_map.py と同じフォルダで  python3 pca_axes.py
import json, numpy as np, sys
sys.path.insert(0,'.')
from concepts import VOCAB, C
from wordllama import WordLlama
from sklearn.decomposition import PCA
tt=[x for x in json.load(open('tt_keep.json')) if x['code']!='CN']
pv=json.load(open('pv_rows.json'))
items=[dict(code=x['code'],ja=x['ja'],en=x['en']) for x in tt+pv]
V=list(VOCAB)
X=np.array([[1.0 if v in C[i['code']].split() else 0 for v in V] for i in items])
idf=np.log((1+len(X))/(1+X.sum(0)))+1; Xc=X*idf; Xc/=np.linalg.norm(Xc,axis=1,keepdims=True)
E=WordLlama.load(cache_dir='wlcache',disable_download=True).embed([i['en'] for i in items],norm=True)
Z=np.hstack([Xc,E*0.45]); Z/=np.linalg.norm(Z,axis=1,keepdims=True)
p=PCA(n_components=2,random_state=7).fit(Z); S=p.transform(Z)
print('説明率',p.explained_variance_ratio_.round(3))
for a in range(2):
    r=sorted((np.corrcoef(S[:,a],X[:,j])[0,1],V[j]) for j in range(len(V)) if X[:,j].sum()>0)
    print(f'PC{a+1} 負側',[(v,round(c,2)) for c,v in r[:6]]); print(f'PC{a+1} 正側',[(v,round(c,2)) for c,v in r[-6:][::-1]])
    o=np.argsort(S[:,a]); print('  負の端',[items[i]['code'] for i in o[:5]],' 正の端',[items[i]['code'] for i in o[-5:]])
# 画面では x=PC1（右が正）、y=PC2（上が正）
