# 地図タブのデータ作成

- `concepts.py`：演題ごとの研究トピック（Claudeが付与、地図の主な信号）
- `build_map.py`：トピック（IDF重み）＋ WordLlama 埋め込み（英語タイトル）を結合 → t-SNE / PCA で2次元化、凝集型クラスタリングで11のまとまり、各演題の近い演題5件
- 出力 `mapdata.json` を page.html の `<script id="mapdata">` に埋め込む
- 抄録公開後は、抄録で作り直す
