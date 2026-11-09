import sys, json, re
from pdfminer.pdffont import PDFCIDFont
from pdfminer.cmapdb import CMapDB
from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextContainer, LTTextLine, LTChar, LTAnno, LAParams

class GidMap:
    def get_unichr(self, cid):
        if 3 <= cid <= 97: return chr(cid+29)
        raise KeyError(cid)

class Fallback:
    def __init__(self, primary, fb): self.p=primary; self.fb=fb
    def get_unichr(self, cid):
        try:
            if self.p is not None: return self.p.get_unichr(cid)
        except KeyError: pass
        return self.fb.get_unichr(cid)

_orig_init = PDFCIDFont.__init__
def patched_init(self, rsrcmgr, spec, strict=False):
    _orig_init(self, rsrcmgr, spec, strict)
    from pdfminer.pdftypes import resolve1
    ordering=''
    try:
        csi = resolve1(spec.get('CIDSystemInfo'))
        ordering = resolve1(csi['Ordering']).decode()
    except Exception: pass
    fb = CMapDB.get_unicode_map('Adobe-Japan1', False) if 'Japan1' in ordering else GidMap()
    self.unicode_map = Fallback(getattr(self,'unicode_map',None), fb)
PDFCIDFont.__init__ = patched_init

def main(pdf, out, pages=None):
    result=[]
    laparams=LAParams(line_margin=0.3, char_margin=2.0, boxes_flow=None)
    for pno, layout in enumerate(extract_pages(pdf, page_numbers=pages, laparams=laparams)):
        lines=[]
        for el in layout:
            if isinstance(el, LTTextContainer):
                for ln in el:
                    if isinstance(ln, LTTextLine):
                        txt=ln.get_text().rstrip('\n')
                        sizes=[c.size for c in ln if isinstance(c,LTChar)]
                        fonts=[c.fontname for c in ln if isinstance(c,LTChar)]
                        lines.append({'y':round(ln.y1,1),'x':round(ln.x0,1),'s':round(max(sizes),1) if sizes else 0,'f':fonts[0] if fonts else '','t':txt})
        lines.sort(key=lambda l:(-l['y'],l['x']))
        result.append(lines)
        print(pno, len(lines), file=sys.stderr)
    json.dump(result, open(out,'w'), ensure_ascii=False)

if __name__=='__main__':
    pdf,out=sys.argv[1],sys.argv[2]
    pages=[int(x) for x in sys.argv[3].split(',')] if len(sys.argv)>3 else None
    main(pdf,out,pages)
