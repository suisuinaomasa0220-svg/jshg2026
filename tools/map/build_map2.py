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
# embed title + first part of abstract for richer signal
E=wl.embed([ (it['en']+'. '+it['txt'].split(' . ',1)[-1])[:600] for it in items],norm=True)
Z=np.hstack([Xc*1.0, E*0.5]); Z/=np.linalg.norm(Z,axis=1,keepdims=True)
K=int(sys.argv[1]) if len(sys.argv)>1 else 12
lab=AgglomerativeClustering(n_clusters=K,metric='cosine',linkage='average').fit_predict(Z)
for k in range(K):
    idx=np.where(lab==k)[0]; cnt=X[idx].sum(0); top=[V[j] for j in np.argsort(-cnt)[:5] if cnt[j]>0]
    print(k,len(idx),top)
np.save('Z.npy',Z); json.dump({'C':{k:v for k,v in C.items()},'lab':lab.tolist()},open('tmp.json','w'),ensure_ascii=False)
