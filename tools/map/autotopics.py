# Auto-assign standardized topics to each talk from its title + abstract (English).
# Replaces hand-labeling for the ~550 oral/poster talks added 2026-11-09.
import re
from concepts import VOCAB
# keyword patterns per topic id (word-boundary, case-insensitive)
PAT={
 "gwas":r"\bGWAS\b|genome-wide association|complex (trait|disease)|multifactorial|common variant|susceptibility locus|association stud",
 "prs":r"polygenic|\bPRS\b|genetic risk score",
 "popgen":r"population (genetic|structure|histor)|evolution|ancestry|ancient (genom|DNA)|Jomon|founder (effect|allele)|natural selection|haplogroup|balancing selection|trans-species",
 "funcgen":r"functional genomic|gene regulation|regulatory (element|variant|region)|enhancer|promoter|chromatin|\bQTL\b|eQTL|reporter assay|\bTAD\b|cis-regulat|gene expression regulat",
 "sc":r"single-cell|single cell|scRNA|single-nucleus|snRNA-seq|spatial transcriptom",
 "rna":r"\bRNA-seq\b|transcriptom|splic|isoform|RNA sequencing|alternative splicing|long-read RNA|aberrant transcript|exon",
 "epi":r"epigenet|methylat|imprint|m6A|histone|DNA methylation|epimutation|epigenom",
 "lr":r"long-read|nanopore|PacBio|HiFi|structural variant|structural variation|\bSVs?\b|optical genome mapping|electronic genome mapping|T2T",
 "seqdx":r"\bWGS\b|whole-genome sequenc|whole genome sequenc|\bWES\b|whole-exome|exome sequenc|genomic diagnos|genetic diagnos|diagnostic yield|trio (exome|sequenc)|panel test|multigene panel",
 "rare":r"rare disease|rare disorder|undiagnosed|novel .{0,20}variant|new syndrome|ultra-rare|Mendelian disease",
 "neuro":r"\bALS\b|amyotrophic|Parkinson|ataxia|spastic|neuromuscular|neuropathy|myopath|muscular dystrophy|motor neuron|Charcot-Marie-Tooth|neurodegenerat|dystonia|spinal muscular",
 "neurodev":r"neurodevelopment|intellectual disabilit|developmental delay|autism|\bASD\b|schizophren|epilep|brain (development|malformation|organoid)|cortical|encephalo",
 "hcancer":r"hereditary (cancer|breast|tumou?r)|\bHBOC\b|\bBRCA\b|Lynch syndrome|germline (variant|finding|pathogenic)|Li-Fraumeni|cancer predisposition|PALB2|\bMMR\b|cascade testing|RRSO|risk-reducing",
 "scancer":r"\btumou?r\b|somatic (mutation|variant)|carcinoma|\bcancer\b|oncolog|CGP|comprehensive genomic profiling|glioma|leukemia|sarcoma|neoplasm|metasta",
 "repro":r"\bPGT\b|PGT-|preimplantation|embryo|\bIVF\b|assisted reproducti|\bART\b|oocyte|infertil|fertility|blastocyst|sperm",
 "perinatal":r"\bNIPT\b|prenatal|perinatal|fetal|fetus|pregnan|noninvasive prenatal|amniocentesis|antenatal|obstetric|maternal",
 "peds":r"\bpediatric\b|paediatric|infant|neonat|childhood|\bchild\b|congenital|Down syndrome|newborn screening|boy|girl",
 "cardio":r"cardiomyopath|cardiovascular|arrhythmi|aortic|congenital heart|Marfan|Brugada|QT syndrome|atrial fibrillation|channelopath|dilated cardio|hypertrophic cardio",
 "metab":r"metabolic|mitochondri|lipid|hypercholesterol|dyslipidemia|phenylketonuria|\bPKU\b|lysosom|mucopolysacc|inborn error|hyperuricemia|urate|glyco|diabet",
 "immuno":r"immun|hematolog|haematolog|lymphoma|inborn error of immunity|autoimmun|T cell|T-cell|vasculitis|granulomatous|blood cell",
 "rx":r"\btherap|treatment|drug (discovery|target|target)|antisense|oligonucleotide|gene therapy|therapeutic (target|strategy|approach)|repurpos|Mendelian randomi|clinical trial|tofersen|migalastat|semaglutide|pegvaliase|vosoritide|nucleic acid",
 "model":r"mouse model|\bmice\b|iPSC|iPS cell|organoid|zebrafish|knock-?out|knock-?in|disease model|patient-derived|animal model|humanized mouse",
 "regen":r"regenerat|reprogram|induced pluripotent|direct reprogramming|stem cell|differentiation",
 "ai":r"\bAI\b|machine learning|deep learning|\bLLM\b|artificial intelligence|neural network|generative AI|bioinformatic|computational|algorithm|classifier|agent|prediction (model|tool)|in silico",
 "elsi":r"\bethic|\bELSI\b|legal|policy|regulat|consent|privacy|discriminat|data (sharing|governance)|indigenous|sovereignty|social (acceptance|view)|public (view|awareness|attitude)",
 "gc":r"genetic counsel|counseling|counselling|clinical (genetic|practice)|family communication|decision-making|psychosocial|cascade|patient (experience|support)|carrier (testing|screening)",
 "lab":r"clinical (laboratory|testing)|laboratory (testing|medicine)|\bHbA1c\b|endoscop|diagnostic (test|method)|assay (development|for)|validation of",
 "impl":r"implementation|health(care)? (system|service|policy)|insurance|reimburse|medical fee|workflow|real-world|surveillance (program|system)|clinical implementation|nationwide|registr",
 "dsd":r"\bDSD\b|sex development|disorders of sex|\bSRY\b|intersex|sex differentiation|athlete",
 "repeat":r"repeat expansion|CGG repeat|CAG repeat|trinucleotide|tandem repeat|\bRFC1\b|NOTCH2NLC|repeat interruption",
 "cyto":r"chromosom|cytogenet|karyotype|microarray|\bCMA\b|\bCNV\b|copy number|translocation|deletion syndrome|aneuploidy|uniparental disom|\bUPD\b|microdeletion|FISH",
 "env":r"gene-environment|gene–environment|nutrition|diet|epidemiolog|lifestyle|smoking|folate|vitamin|environmental (factor|exposure)|birth (weight|cohort)",
 "biobank":r"biobank|\bcohort\b|\bBBJ\b|BioBank Japan|ToMMo|Tohoku Medical Megabank|database|registry|\bTogoVar\b|population-scale|large-scale .{0,15}(data|resource)",
 "mosaic":r"mosaic|mosaicism|somatic (genetic rescue|mutation.{0,20}normal)|clonal|post-?zygotic",
}
for k in PAT: assert k in VOCAB,k
RE={k:re.compile(v,re.I) for k,v in PAT.items()}
PRIM=["gwas","prs","popgen","funcgen","sc","rna","epi","lr","hcancer","scancer","repro","perinatal","cardio","metab","immuno","neuro","neurodev","repeat","cyto","dsd","mosaic","model","regen","ai","elsi","gc","lab","impl","env","biobank","rx","seqdx","rare","peds"]
def topics(text):
    hit=[k for k in PRIM if RE[k].search(text)]
    # ensure at least one; cap at 5 keep priority order
    if not hit: hit=["rare"]
    return hit[:4]
if __name__=="__main__":
    import json
    tt=json.load(open('tt_keep.json')); pv=json.load(open('pv_rows.json'))
    C={}
    for x in tt+pv:
        C[x['code']]=' '.join(topics((x.get('en','')+' . '+x.get('abs','') )))
    json.dump(C,open('autotopics.json','w'),ensure_ascii=False,indent=0)
    from collections import Counter
    cc=Counter(w for v in C.values() for w in v.split())
    print(len(C),'codes'); print(cc.most_common())
    nt=Counter(len(v.split()) for v in C.values()); print('topics per talk',sorted(nt.items()))
