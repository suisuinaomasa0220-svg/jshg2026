"""Plaud カスタム用語集（1行1語・英語のみ）を作る。
対象は参加予定セッションのうち英語で発表される演題（IL1-5, S1, S5, S12, S16, O2, BO）と LS5-1。
日本語演題は用語集なしで問題ないため対象外。人名はローマ字。
出力: plaud_vocab_en.txt（優先順：用語 → 人名）
"""
import json, re, os
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, '..', '..')
EN_SESS = "IL1 IL2 IL3 IL4 IL5 S1 S5 S12 S16 O2 BO".split()
EN_TALKS = ["LS5-1"]          # 言語欄が空のランチョンのうち、海外演者のもの

# 1行1語。# は出どころのメモ
TERMS = """
# 共通（略語・製品名・データベース名）
GWAS|PRS|polygenic risk score|VUS|ACMG/AMP|ClinVar|ClinGen|HPO|AlphaMissense|AlphaFold2|REVEL
WGS|WES|RNA-seq|LRS|long-read sequencing|PacBio|HiFi|Oxford Nanopore|NovaSeq|T2T|MLPA
SNV|CNV|eQTL|k-mer|pseudoexon|antisense oligonucleotide|ASO|N-of-1|loss-of-function|hemizygous
epigenome|chromatin accessibility|spatial transcriptomics|multi-omics|metabolome|CRISPR/Cas9|iPSC|LLM
BioBank Japan|UK Biobank|GeMJ|AMED|ASHG|HLA|CHIP|clonal hematopoiesis|G×E|missing heritability
# IL1-5
congenital heart disease|genomic imprinting|ALS|ropinirole|ROPALS|ALSFRS-R|SREBP2|CDKAL1|MELAS|MERRF|N6-methyladenosine
# S1
NKTCL|IL18RAP|HLA-DRB1|Qinghai-Tibet Plateau|hereditary spastic paraplegia|4SMD|Gower distance|SPAST|SPG11|ATL1|KIF1A|REEP1|DMD
# S5
PhenoScore|phenomics|ANKRD11|PP4
# S12
ATRX|POU3F3|SNUPN|spinocerebellar ataxia|Purkinje|spliceosome|LRP12|NOTCH2NLC|MAPT|GLA|Fabry disease|splice-switching oligonucleotide
# S16
ALDH2|ADH1B|acetaldehyde|haplogroup|HOR|alpha satellite|cardiomyopathy|microglia
# O2
URST1|URST4|NSCLC|KRAS|TP53|PTEN|BRAF|EGFR|osimertinib|RMC-6236|DepMap|CCLE|JuncBASE|YAP1|SCRIB|MEN1
# BO
retinitis pigmentosa|EYS|ADGRV1|REEP6|HDLBP|OPDM|oculopharyngodistal myopathy|GIPC1|polyglycine|RAN translation|cell-free RNA|SFTPC|CALML5|EOPC|CUX1|BRCA2
# LS5-1
EGM|electronic genome mapping|OGM|optical genome mapping|C9orf72|DMPK|FMR1|FXN
"""
# プログラムにローマ字がない／誤記のある人の読み
ROMAJI_FIX = {"内藤龍彦": "Tatsuhiko Naito", "平塚真弘": "Masahiro Hiratsuka"}
# 演者・座長以外で登録しておく人名（アプリの「注目の先生」）
EXTRA_NAMES = ["Yukinori Okada", "Yoichiro Kamatani", "Ayako Suzuki", "Yutaka Suzuki", "Michiaki Hamada"]

def uniq(xs):
    seen, out = set(), []
    for x in xs:
        x = x.strip()
        if x and x not in seen:
            seen.add(x); out.append(x)
    return out

data = json.load(open(os.path.join(ROOT, 'data', 'data.json'), encoding='utf-8'))
prog = json.load(open(os.path.join(ROOT, 'tools', 'program', 'program_2026-11-04.json'), encoding='utf-8'))
romaji = {}
for x in prog['orals'] + prog['posters'] + prog['misc'] + data:
    for k, r in re.findall(r"([^,（）]+?)\s*（([A-Za-z][A-Za-z .\-']+)）", x.get('authors') or ''):
        romaji[re.sub(r'\s', '', k)] = r.strip()
romaji.update(ROMAJI_FIX)

speakers, chairs, missing = [], [], []
def add(lst, n):
    n = re.sub(r'（.*?）', '', n).strip()
    if not n: return
    if re.search(r'[A-Za-z]', n): lst.append(n); return
    r = romaji.get(re.sub(r'\s', '', n))
    (lst if r else missing).append(r or n)
for x in data:
    if x['code'].split('-')[0] in EN_SESS or x['code'] in EN_TALKS:
        add(speakers, x['speaker'])
        if x['code'] not in EN_TALKS:
            for c in re.split('[／/]', x['chairs']): add(chairs, c)

terms = uniq(t for line in TERMS.strip().split('\n') if not line.startswith('#') for t in line.split('|'))
names = uniq(speakers + chairs + EXTRA_NAMES)
allv = uniq(terms + names)
open(os.path.join(HERE, 'plaud_vocab_en.txt'), 'w', encoding='utf-8').write('\n'.join(allv) + '\n')
print('terms', len(terms), 'names', len(names), 'total', len(allv), '| ローマ字なしで除外:', missing)
bad = [v for v in allv if re.search(r'[ぁ-んァ-ヶ一-龥]', v)]
print('日本語が残っている行:', bad)
