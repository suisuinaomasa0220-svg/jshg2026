"""Plaud カスタム用語集（1行1語）を作る。
参加予定セッション（Drive「2_箱」の30セッション）の演題・抄録から選んだ用語＋演者名。
出力: plaud_vocab_top100.txt（最優先100語）/ plaud_vocab_all.txt（全部・優先順）
"""
import json, re, os
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, '..', '..')
SESS = ("ES1 IL1 IL2 LS1 LS2 LS3 LS4 LS5 O2 S1 S5 AL1 BO ES6 IL3 IL4 LS6 LS7 LS8 LS9 LS10 "
        "O14 O21 ES7 IL5 LS11 LS12 LS13 S12 S16").split()

# A: どのセッションでも出る共通語（最優先100語）
CORE = """
GWAS PRS ポリジェニックリスクスコア VUS ACMG ClinVar ClinGen HPO AlphaMissense AlphaFold
WGS WES エクソーム RNA-seq ロングリードシーケンス ショートリード PacBio HiFi ナノポア Oxford Nanopore
イルミナ NovaSeq DRAGEN T2T GRCh38 パンゲノム ハプロタイプ フェージング SNV SNP
CNV 構造多型 タンデムリピート リピート伸長 VNTR オプティカルゲノムマッピング OGM 電子ゲノムマッピング MLPA FISH
マイクロアレイ セントロメア k-mer スプライシング イントロン 偽エクソン アンチセンスオリゴヌクレオチド ASO N-of-1 バリアント
ミスセンス フレームシフト 機能喪失 生殖細胞系列 体細胞モザイク ヘミ接合 片親性ダイソミー エピゲノム エピシグネチャー インプリンティング
クロマチン メチル化 トランスクリプトーム 空間トランスクリプトミクス シングルセル マルチオミクス プロテオーム メタボローム eQTL バイオバンク
バイオバンク・ジャパン UK Biobank 東北メディカル・メガバンク GeMJ AMED ASHG IRUD HLA CHIP クローン性造血
遺伝子環境相互作用 ミッシングヘリタビリティ 浸透率 CRISPR/Cas9 ノックイン ノックダウン iPS細胞 AAV 酵素補充療法 造血幹細胞移植
新生児スクリーニング NIPT PGT-M PGT-A 遺伝カウンセリング 大規模言語モデル PhenoScore 希少疾患 未診断疾患 古代ゲノム
"""
# B: 特定の演題で出る遺伝子名・疾患名・薬剤名・製品名（1行1語、# は出どころのメモ）
SPECIFIC = """
# IL1-5, AL1
先天性心疾患|エピジェネティック遺伝|トランスポゾン|筋萎縮性側索硬化症|ALS|ロピニロール|ROPALS|SREBP2|コレステロール生合成
RNA修飾|CDKAL1|MELAS|MERRF|メチルアデノシン|RASopathy|ヌーナン症候群|RAS/MAPK
# S1
NKTCL|NK/T細胞リンパ腫|IL18RAP|HLA-DRB1|青海チベット高原|遺伝性痙性対麻痺|SPAST|SPG11|ATL1|KIF1A|REEP1|DMD遺伝子|挿入転座
# S5 / ES6
フェノミクス|ANKRD11|REVEL|PP4|ACMG/AMP
# S12
ATRX|POU3F3|クロマチンアクセシビリティ|SNUPN|脊髄小脳失調症|プルキンエ細胞|スプライソソーム|LRP12|NOTCH2NLC|MAPT|GLA|ファブリー病|スプライススイッチングオリゴヌクレオチド
# S16 / ES7
ALDH2|ADH1B|アセトアルデヒド|ハプログループ|HOR|アルファサテライト|心筋症|ミクログリア|RNF213|もやもや病
# O2
URST1|URST4|NSCLC|KRAS|TP53|PTEN|BRAF|EGFR|オシメルチニブ|RMC-6236|DepMap|CCLE|JuncBASE|YAP1|MEN1|多発性内分泌腫瘍症
# O14
ABCG2|UMOD|ウロモジュリン|SHARPIN|遅発性アルツハイマー病|ナルコレプシー|カタプレキシー|HLA-DQB1|特発性過眠症|HBV|HLA-DPB1|TPSAB1|TPSB2|トリプターゼ|多発性硬化症|PBMC
# O21
CHD8|複雑染色体再構成|Mowat-Wilson症候群|モノソミーレスキュー|イソダイソミー|ブラシュコ線|NF1|神経線維腫症1型|カフェオレ斑|骨系統疾患|ACAN|アグリカン|SOS1|LZTR1|RIT1
# BO
網膜色素変性|EYS|ADGRV1|REEP6|眼咽頭遠位型ミオパチー|OPDM|GIPC1|ポリグリシン|RAN翻訳|セルフリーRNA|早発性膵がん|CUX1|BRCA2
# LS1, LS13
ライソゾーム病|ムコ多糖症II型|MPS II|ハンター症候群|ポンペ病|イデュルスルファーゼ|パビナフスプ アルファ|イズカーゴ|脳室内投与|デルマタン硫酸|血液脳関門
# LS2-5, LS10
MHC|TCR|ウルトラロングリード|カニクイザル|ゲノムアセンブリ|パンゲノムグラフ|XLEAP-SBS|TruPath|Bionano|C9orf72|DMPK|FMR1|FXN
# LS6
フェニルケトン尿症|PKU|フェニルアラニン|ペグバリアーゼ|パリンジック|サプロプテリン|セピアプテリン|BH4
# LS7-9
日本列島人|縄文人|ターゲットキャプチャー|ハッチンソン・ギルフォード|プロジェリア|HGPS|LMNA|プロジェリン|ロナファルニブ|SOD1|トフェルセン|クアルソディ|VALOR試験|ATTRアミロイドーシス
# LS11-12
脊髄性筋萎縮症|SMA|SMN1|SMN2|ヌシネルセン|スピンラザ|リスジプラム|エブリスディ|オナセムノゲン アベパルボベク|ゾルゲンスマ|デュシェンヌ型筋ジストロフィー|エレビジス|デランジストロゲン モキセパルボベク|マイクロジストロフィン|AAVrh74
"""
# 演者以外で登録しておく人名（アプリの「注目の先生」）
EXTRA_NAMES = ["岡田随象", "鎌谷洋一郎", "鈴木絢子", "鈴木穣", "浜田道昭"]

def uniq(xs):
    seen, out = set(), []
    for x in xs:
        x = x.strip()
        if x and x not in seen:
            seen.add(x); out.append(x)
    return out

core = uniq(CORE.split('\n') and re.split(r'[ \n]+(?=\S)', CORE.strip().replace('Oxford Nanopore', 'Oxford_Nanopore').replace('UK Biobank', 'UK_Biobank')))
core = [c.replace('_', ' ') for c in core]
spec = uniq(t for line in SPECIFIC.strip().split('\n') if not line.startswith('#') for t in line.split('|'))
data = json.load(open(os.path.join(ROOT, 'data', 'data.json'), encoding='utf-8'))
names = []
for x in data:
    if x['code'].split('-')[0] in SESS:
        n = re.sub(r'（ほか\d+名）', '', x['speaker']).strip()
        if n: names.append(n if re.search(r'[A-Za-z]', n) else n.replace(' ', '').replace('　', ''))
names = uniq(names + EXTRA_NAMES)
spec = [t for t in spec if t not in core]
allv = uniq(core + spec + names)
assert len(core) == 100, len(core)
open(os.path.join(HERE, 'plaud_vocab_top100.txt'), 'w', encoding='utf-8').write('\n'.join(core) + '\n')
open(os.path.join(HERE, 'plaud_vocab_all.txt'), 'w', encoding='utf-8').write('\n'.join(allv) + '\n')
print('core', len(core), 'specific', len(spec), 'names', len(names), 'total', len(allv))
print('longest:', sorted(allv, key=len)[-5:])
