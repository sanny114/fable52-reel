# Fable 5.2 紹介リール（40秒）

9万個の光の粒が、渦・波・設計図・グラフ・文章・絵へと姿を変える40秒のモーショングラフィックス。素材は使わず、映像も音楽もプログラム1本で生成したもの。

- 公開ページ: https://sanny114.github.io/fable52-reel/
- `fable52_reel.mp4` — 本編（1920×1080 / 30fps / 音声つき）
- `src/fable.py` — 映像と音楽のソース（Python。numpy・Pillow・imageio-ffmpeg を使用）

作り直し（`src/` で実行。全体で約3分）:

```
python fable.py frames
python fable.py audio
python fable.py mux fable52_reel.mp4
```

文字の描画にWindows標準のフォント（Noto Sans JP、Bahnschrift）を使っているため、Windowsでの実行を想定。制作: Claude Code（Fable 5.2）。
