# プログラムPDF（11/4時点版）の取り込み

- 元: https://www.congre.co.jp/jshg2026/program/files/jshg2026_program_jp_en.pdf
- 手順: extract.py（pdfminer。一部フォントのToUnicode欠落を Adobe-Japan1 / 標準GID順で補完）→ parse_program.py（セッション・演題に分割）→ build.py（整形）→ apply.py（page.html の data / POSTERS に反映）
- program_2026-11-04.json: 整形後データ（orals 210 / posters 338 / misc）。抄録PDFが開封できたら、このファイルの code をキーに abs を足す
- 印の引き継ぎ: 旧記号 OS1→O1、AW1→BO、AW2→JHG、AW3→AL は page.html の MIG() で読み替え
