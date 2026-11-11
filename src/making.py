# -*- coding: utf-8 -*-
"""Making-of film for the Fable 5.2 reel. Reuses fable.py as a library.
  python making.py prep            -> mosaic.png, env.npy (needs frames/ and audio.wav of the reel)
  python making.py stills 5 10 ... -> stills/
  python making.py frames [procs]  -> frames2/
  python making.py audio           -> audio2.wav
  python making.py mux out.mp4
"""
import sys, os, math, wave, subprocess
import numpy as np
from PIL import Image, ImageDraw
import fable as F

F.captions = lambda t: []
W, H, FPS, N, ZC = F.W, F.H, F.FPS, F.N, F.ZC
DUR = 76.0
HERE = os.path.dirname(os.path.abspath(__file__))
SRC_LINES = 738
CODE_FONT = r"C:\Windows\Fonts\consola.ttf"
WHITE = np.array([0.9, 0.92, 1.0], np.float32)
Z3, OX3, OY3 = 0.8, -230.0, -40.0
XX = np.arange(W, dtype=np.float32)[None, :]

_mc = {}


def mask(text, size, weight, x, y, anchor="mm", path=F.FONT_JP, tracking=0, cache=True):
    key = (text, size, weight, x, y, anchor, path, tracking)
    if cache and key in _mc:
        return _mc[key]
    f = F.font(size, weight, path)
    img = Image.new("L", (W, H), 0)
    d = ImageDraw.Draw(img)
    if tracking == 0:
        d.text((x, y), text, font=f, fill=255, anchor=anchor)
    else:
        ws = [f.getlength(ch) for ch in text]
        tot = sum(ws) + tracking * (len(text) - 1)
        cx = x - tot / 2 if anchor == "mm" else x
        for ch, w in zip(text, ws):
            d.text((cx, y), ch, font=f, fill=255, anchor="lm")
            cx += w + tracking
    m = np.asarray(img, dtype=np.float32) / 255.0
    if cache:
        _mc[key] = m
    return m


def ease(x):
    return float(F.ease_io(np.float32(x)))


def fade(t, a, b, c, d):
    return F.fade(t, a, b, c, d)


# ------------------------------------------------------------ extra shapes
def draw_tools():
    img = Image.new("L", (W, H), 0)
    d = ImageDraw.Draw(img)
    for k in range(4):
        x0 = 150 + k * 420
        d.rounded_rectangle([x0, 300, x0 + 360, 640], radius=24, outline=255, width=3)
    x0 = 150
    d.rectangle([x0 + 40, 335, x0 + 320, 475], outline=255, width=3)
    d.polygon([(x0 + 160, 375), (x0 + 160, 435), (x0 + 212, 405)], fill=255)
    for j, (a, b) in enumerate(((40, 250), (90, 320), (40, 190))):
        d.rectangle([x0 + a, 505 + j * 38, x0 + b, 523 + j * 38], fill=130, outline=255, width=2)
    d.line([(x0 + 215, 495), (x0 + 215, 615)], fill=255, width=3)
    x0 = 570
    pts = [(x0 + 40 + i * 4, 400 - 55 * math.sin(i / 5.5) * math.sin(i / 22.3 * math.pi)) for i in range(71)]
    d.line(pts, fill=255, width=4)
    d.rectangle([x0 + 40, 500, x0 + 320, 600], outline=255, width=3)
    for i in range(1, 7):
        d.line([(x0 + 40 + i * 40, 500), (x0 + 40 + i * 40, 600)], fill=255, width=2)
    for i in (1, 2, 4, 5, 6):
        d.rectangle([x0 + 28 + i * 40, 500, x0 + 52 + i * 40, 555], fill=255)
    x0 = 990
    d.rectangle([x0 + 90, 345, x0 + 320, 510], outline=150, width=2)
    d.rectangle([x0 + 65, 380, x0 + 295, 545], outline=200, width=2)
    d.rectangle([x0 + 40, 415, x0 + 270, 590], fill=0, outline=255, width=3)
    d.polygon([(x0 + 60, 575), (x0 + 150, 480), (x0 + 200, 540), (x0 + 225, 515), (x0 + 255, 575)], outline=255, fill=110)
    d.ellipse([x0 + 205, 440, x0 + 240, 475], fill=255)
    x0 = 1410
    d.rectangle([x0 + 30, 390, x0 + 330, 560], outline=255, width=3)
    for i in range(10):
        for yy in (402, 536):
            d.rectangle([x0 + 44 + i * 29, yy, x0 + 58 + i * 29, yy + 12], fill=255)
    for i in range(1, 3):
        d.line([(x0 + 30 + i * 100, 425), (x0 + 30 + i * 100, 525)], fill=255, width=2)
    for yy in range(350, 600, 22):
        d.line([(x0 + 180, yy), (x0 + 180, yy + 11)], fill=255, width=4)
    a = np.asarray(img, np.float32) / 255.0
    cols = [F.CYAN, F.PINK, F.GOLD, np.array([0.55, 0.62, 1.0], np.float32)]
    col = np.zeros((H, W, 3), np.float32)
    for k in range(4):
        col[:, 0 if k == 0 else 150 + k * 420 - 30:, :] = cols[k]
    return a, col


def draw_code():
    src = open(os.path.join(HERE, "fable.py"), encoding="utf-8").read().splitlines()
    start = next(i for i, l in enumerate(src) if l.startswith("def render("))
    lines = [l.rstrip().expandtabs(4)[:64] for l in src[start:start + 25]]
    img = Image.new("L", (W, H), 0)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([520, 150, 1400, 830], radius=18, outline=255, width=3)
    d.line([(520, 202), (1400, 202)], fill=255, width=2)
    d.text((550, 177), "fable.py", font=F.font(26, 700, F.FONT_EN), fill=255, anchor="lm")
    for i in range(3):
        d.ellipse([1300 + i * 30, 168, 1316 + i * 30, 184], outline=255, width=2)
    f = F.font(22, 400, CODE_FONT)
    col = np.zeros((H, W, 3), np.float32) + F.CYAN
    for i, l in enumerate(lines):
        y = 232 + i * 23.5
        d.text((552, y), l, font=f, fill=255, anchor="lm")
        s = l.strip()
        c = F.GOLD if s.startswith("def ") else (F.WARM if i % 2 else F.CYAN)
        if s.startswith("for ") or s.startswith("if "):
            c = F.PINK
        col[int(y - 12):int(y + 12), 540:1390] = c
    return np.asarray(img, np.float32) / 255.0, col


class X:
    def __init__(self):
        self.S = S = F.Shapes()
        rng = np.random.default_rng(99)
        self.tools = F.sample(*draw_tools(), rng)
        self.card = np.clip(np.floor((self.tools[0][:, 0] * 540 + 960 - 120) / 420), 0, 3).astype(np.float32)
        self.code = F.sample(*draw_code(), rng, 0.01)
        self.rank = rng.permutation(N)
        self.hi = rng.choice(N, 14, replace=False)
        p = os.path.join(HERE, "mosaic.png")
        self.mosaic = Image.open(p).convert("RGB") if os.path.exists(p) else None
        p = os.path.join(HERE, "env.npy")
        self.envmask = np.zeros((H, W), np.float32)
        self.envcol = np.zeros((H, W, 3), np.float32)
        if os.path.exists(p):
            env = np.load(p)
            for c, e in enumerate(env):
                h = int(4 + e * 230)
                self.envmask[540 - h:540 + h, 200 + c] = 1.0 if c % 3 else 0.35
                k = c / len(env)
                self.envcol[:, 200 + c] = F.CYAN * (1 - k) + F.GOLD * k


def morph(S, A, cA, B, cB, u, t, idx=None, p=None):
    sl = slice(None) if idx is None else idx
    r1, r2, r3, sgn = S.r1[sl], S.r2[sl], S.r3[sl], S.sgn[sl]
    if p is None:
        p = F.ease_io((u - 0.35 * r1) / 0.65)
    p = np.asarray(p, np.float32)
    pos = A + (B - A) * p[:, None]
    col = cA + (cB - cA) * p[:, None]
    sw = np.sin(np.pi * p)
    ang = sw * (0.35 + 0.9 * r2) * sgn
    ca, sa = np.cos(ang), np.sin(ang)
    x, y = pos[:, 0].copy(), pos[:, 1].copy()
    pos[:, 0] = x * ca - y * sa
    pos[:, 1] = x * sa + y * ca
    pos[:, 2] -= sw * (r1 - 0.25) * 1.1
    pos += np.sin(r3 + t * 2.0) * (sw * 0.07)[:, None]
    pos += np.sin(r3 + t * 1.6) * 0.0028
    return pos, col


def project(pos, yaw=0.0, zoom=1.0, ox=0.0, oy=0.0):
    c, s = math.cos(yaw), math.sin(yaw)
    x = pos[:, 0] * c + pos[:, 2] * s
    z = -pos[:, 0] * s + pos[:, 2] * c
    sc = ZC / np.maximum(ZC + z, 0.25) * zoom
    return 960 + ox + x * 540 * sc, 540 + oy + pos[:, 1] * 540 * sc, sc


def splat(acc, pos, col, wgt, yaw=0.0, zoom=1.0, ox=0.0, oy=0.0):
    sx, sy, sc = project(pos, yaw, zoom, ox, oy)
    wg = wgt * np.minimum(sc, 3.0) ** 1.5
    x0 = np.floor(sx).astype(np.int64)
    y0 = np.floor(sy).astype(np.int64)
    fx, fy = sx - x0, sy - y0
    for dx, dy, wb in ((0, 0, (1 - fx) * (1 - fy)), (1, 0, fx * (1 - fy)), (0, 1, (1 - fx) * fy), (1, 1, fx * fy)):
        xi, yi = x0 + dx, y0 + dy
        m = (xi >= 0) & (xi < W) & (yi >= 0) & (yi < H)
        idx = yi[m] * W + xi[m]
        ww = (wb * wg)[m]
        for c in range(3):
            acc[c] += np.bincount(idx, weights=ww * col[m, c], minlength=W * H)


def bloom(img):
    P = F.post_consts()
    pad = P["pad"]
    q = img.reshape(H // 4, 4, W // 4, 4, 3).mean(axis=(1, 3))
    qp = np.pad(q, ((pad, pad), (pad, pad), (0, 0)))
    bl = np.empty_like(img)
    for c in range(3):
        b = np.fft.irfft2(np.fft.rfft2(qp[..., c]) * P["tf"], s=qp.shape[:2])[pad:-pad, pad:-pad]
        bl[..., c] = np.asarray(Image.fromarray(b.astype(np.float32), "F").resize((W, H), Image.BICUBIC))
    return np.maximum(bl, 0, out=bl)


def tone(img, bloom_amt, flash, direct=0.85):
    e = img * direct + F.post_consts()["bg"]
    if bloom_amt > 0:
        e = e + bloom(img) * ((1.5 + 1.2 * flash) * bloom_amt)
    return 1 - np.exp(-1.15 * (1 + flash) * e)


def final(out, t, fi, base=None):
    if base is not None:
        out = 1 - (1 - out) * (1 - base)
    out = out * F.post_consts()["vig"]
    g = min(t / 0.4, 1.0) * min(max((DUR - 0.1 - t) / 0.9, 0.0), 1.0)
    out *= g
    out += np.random.default_rng(5000 + fi).normal(0, 0.007, (H, W, 1)).astype(np.float32)
    return (np.clip(out, 0, 1) * 255 + 0.5).astype(np.uint8)


STEPS = [(20.0, "点を置く", "9万個の点を、絵のとおりに置く。"),
         (24.0, "色をのせる", "1粒ずつ、色を決める。"),
         (28.0, "奥行きをつける", "立体の空間に置いて、カメラで写す。"),
         (32.0, "光をにじませる", "明るいところほど、光をにじませる。")]
CARDS = ["映像ソフト", "音楽ソフト", "素材集", "編集ソフト"]
STATS = [(62.0, 324000000, "粒の位置を計算した回数（9万個 × 3回 × 1,200コマ）", 560, 300),
         (63.0, 1200, "描いたコマ数", 1360, 300),
         (64.0, SRC_LINES, "プログラムの行数（1ファイル）", 560, 610),
         (65.0, 0, "使った素材", 1360, 610)]
IMPACTS = {3.5: 0.9, 14.2: 0.5, 20.0: 0.35, 24.0: 0.35, 28.0: 0.35, 32.0: 0.35, 36.0: 0.7, 40.0: 0.35,
           62.0: 0.3, 63.0: 0.3, 64.0: 0.3, 65.0: 0.3, 71.0: 0.9}


def frame(X, t, fi):
    S = X.S
    if t < 3.5:  # fast-forward through the original film
        tt = 6.0 + (t / 3.5) * 23.5
        img = Image.fromarray(F.render(S, tt, fi))
        d = ImageDraw.Draw(img)
        if (t * 3) % 1 < 0.7:
            for k in range(2):
                d.polygon([(1700 + k * 30, 70), (1700 + k * 30, 106), (1728 + k * 30, 88)], fill=(255, 184, 77))
            d.text((1775, 89), "×7", font=F.font(34, 700, F.FONT_EN), fill=(255, 184, 77), anchor="lm")
        a = np.asarray(img, np.float32) * min(t / 0.4, 1.0)
        return a.astype(np.uint8)

    acc = np.zeros((3, W * H), np.float64)
    L = []  # crisp layers (mask, color, amount)
    base = None
    bloom_amt, direct = 1.0, 0.85
    flash = sum(math.exp(-(t - T) * 5.0) * a for T, a in IMPACTS.items() if t >= T)
    yaw0 = 0.11 * math.sin(t * 0.55 + 0.4)
    wipe = None

    # ---------------- particles
    if t < 7.0:
        k = ease((t - 3.6) / 1.2)
        pos, col = S.get("picture", t)
        splat(acc, pos, col, 1.6, 0.11 * math.sin(29.5 * 0.55 + 0.4) * (1 - k), 1 - 0.2 * k, 0, -30 * k)
    elif t < 12.7:
        A, cA = S.get("picture", t)
        B, cB = X.tools
        p = F.ease_io((t - (7.0 + X.card) - 0.3 * S.r1) / 0.9)
        k = ease((t - 7.0) / 1.5)
        for s in range(3):
            ts = t + s / 90
            pos, col = morph(S, A, cA, B, cB, 0, ts, p=F.ease_io((ts - (7.0 + X.card) - 0.3 * S.r1) / 0.9))
            splat(acc, pos, col, (1.6 - 0.3 * k) / 3, 0, 0.8 + 0.2 * k, 0, -30 * (1 - k))
    elif t < 19.9:
        al = 1 - min(max((t - 19.3) / 0.6, 0), 1)
        for s in range(3):
            ts = t + s / 90
            pos, col = morph(S, *X.tools, *X.code, min((ts - 12.7) / 1.6, 1.0), ts)
            splat(acc, pos, col, 1.25 * al / 3, yaw0 * 0.5)
    elif t < 36.3:
        pos, col = S.get("picture", t)
        al = 1 - min(max((t - 35.6) / 0.7, 0), 1)
        yaw = 0.0
        if t < 24:
            vis = X.rank < N * ease((t - 20.2) / 2.6)
            pos, col = pos[vis], np.tile(WHITE, (int(vis.sum()), 1))
            bloom_amt, direct = 0.0, 1.5
        elif t < 28:
            xw = -1.15 + 2.3 * ease((t - 24.3) / 2.2)
            k = np.clip((xw - pos[:, 0]) / 0.08, 0, 1)[:, None]
            col = WHITE * (1 - k) + col * k
            bloom_amt, direct = 0.0, 1.5
        elif t < 32:
            yaw = 0.95 * math.sin(math.pi * min(max((t - 28.3) / 3.2, 0), 1))
            pos = pos + np.sin(S.r3 + t * 1.6) * 0.0028
            bloom_amt, direct = 0.0, 1.5
        else:
            wipe = 250 + 960 * ease((t - 32.4) / 2.4)
        if len(pos):
            splat(acc, pos, col, 1.6 * al, yaw, Z3, OX3, OY3)
    elif 39.5 <= t < 52.0:
        al = min(max((t - 39.5) / 0.8, 0), 1) * (1 - min(max((t - 51.4) / 0.6, 0), 1))
        A, cA = S.get("blueprint", t)
        B, cB = S.get("graph", t)
        u = min(max((t - 42.0) / 7.0, 0), 1)
        g = (1.5 + (1.1 - 1.5) * u) * 0.6
        for s in range(3):
            ts = t + s / 90
            pos, col = morph(S, A, cA, B, cB, min(max((ts - 42.0) / 7.0, 0), 1), ts)
            splat(acc, pos, col, g * al / 3, yaw0)
        a = fade(t, 40.2, 40.8, 50.4, 51.2)
        if a > 0:
            img = Image.new("L", (W, H), 0)
            d = ImageDraw.Draw(img)
            hi = X.hi
            prev = None
            for k in range(54):
                tk = t - k / 30
                pk, _ = morph(S, A[hi], cA[hi], B[hi], cB[hi], min(max((tk - 42.0) / 7.0, 0), 1), tk, idx=hi)
                sx, sy, _ = project(pk, yaw0)
                if prev is not None:
                    v = int(255 * (1 - k / 54) ** 1.6)
                    for j in range(len(hi)):
                        d.line([(prev[0][j], prev[1][j]), (sx[j], sy[j])], fill=v, width=3)
                else:
                    r = 7 + (3 * math.sin(t * 6) if t < 42 else 0)
                    for j in range(len(hi)):
                        d.ellipse([sx[j] - r, sy[j] - r, sx[j] + r, sy[j] + r], fill=255)
                        if t < 42.4:
                            rr = 18 + 5 * math.sin(t * 6)
                            d.ellipse([sx[j] - rr, sy[j] - rr, sx[j] + rr, sy[j] + rr], outline=200, width=2)
                prev = (sx, sy)
            L.append((np.asarray(img, np.float32) / 255.0, F.GOLD, 2.2 * a))
    elif 62.0 <= t < 68.3:
        al = fade(t, 62.0, 63.0, 67.6, 68.3) * 0.3
        pos, col = S.get("halo", t)
        splat(acc, pos, col, 1.3 * al, yaw0)

    # ---------------- crisp layers
    if t < 8.0:
        L.append((mask("MAKING OF  ―  Fable 5.2 紹介リール", 26, 500, 960, 62, tracking=8), F.GOLD, 1.4 * fade(t, 4.4, 5.0, 6.6, 7.0)))
        L.append((mask("この40秒の裏側を、のぞいてみる。", 48, 500, 960, 985, tracking=10), F.WARM, 1.6 * fade(t, 4.5, 5.2, 6.6, 7.0)))
        if 3.5 <= t < 7.0:
            pm = np.zeros((H, W), np.float32)
            pm[44:80, 150:162] = 1
            pm[44:80, 172:184] = 1
            L.append((pm, F.GOLD, 1.8 * fade(t, 3.5, 3.6, 6.6, 7.0)))
    if 7.5 < t < 13.3:
        for k, name in enumerate(CARDS):
            L.append((mask(name, 34, 500, 330 + k * 420, 700, tracking=6), F.WARM, 1.5 * fade(t, 8.0 + k, 8.4 + k, 12.5, 12.9)))
        L.append((mask("これまでの映像づくり", 40, 500, 960, 170, tracking=12), F.GOLD, 1.4 * fade(t, 8.2, 8.8, 12.5, 12.9)))
        L.append((mask("道具も、技も、別々。", 46, 500, 960, 880, tracking=10), F.WARM, 1.6 * fade(t, 11.2, 11.7, 12.5, 12.9)))
    if 14.0 < t < 20.0:
        L.append((mask("今回は、文章1本。", 50, 500, 960, 915, tracking=10), F.WARM, 1.7 * fade(t, 14.4, 14.9, 19.0, 19.5)))
        L.append((mask("プログラム 1ファイル ・ %d行" % SRC_LINES, 26, 500, 960, 990, tracking=8), F.GOLD, 1.4 * fade(t, 15.2, 15.8, 19.0, 19.5)))
    if 20.0 <= t < 36.2:
        ga = fade(t, 20.0, 20.5, 35.5, 36.0)
        L.append((mask("1コマの解剖", 26, 500, 1270, 250, "lm"), F.GOLD, 1.4 * ga))
        for i, (T, name, desc) in enumerate(STEPS):
            cur = T <= t < T + 4
            a = 1.7 if cur else (0.75 if t >= T + 4 else 0.22)
            L.append((mask("%d　%s" % (i + 1, name), 40, 500, 1270, 345 + i * 92, "lm"), F.WARM if not cur else np.array([1.0, 0.85, 0.55], np.float32), a * ga))
            L.append((mask(desc, 34, 400, 730, 905, tracking=6), F.WARM, 1.5 * fade(t, T + 0.2, T + 0.7, T + 3.6, T + 3.95)))
        if t < 24:
            n = int(N * ease((t - 20.2) / 2.6))
            L.append((mask("{:,} 個".format(n), 40, 700, 730, 975, cache=(n == N)), F.GOLD, 1.5 * fade(t, 20.2, 20.5, 23.6, 23.95)))
    if 36.0 <= t < 40.0 and X.mosaic is not None:
        s = 1 + 1.6 * (1 - ease((t - 36.0) / 2.4))
        cw, ch = 1920 / s, 810 / s
        box = (960 - cw / 2, 405 - ch / 2, 960 + cw / 2, 405 + ch / 2)
        m = X.mosaic.resize((1920, 810), Image.BICUBIC, box=box)
        base = np.zeros((H, W, 3), np.float32)
        base[135:945] = np.asarray(m, np.float32) / 255.0 * fade(t, 36.0, 36.6, 39.3, 39.95)
        L.append((mask("これを、1,200枚。", 52, 500, 960, 1008, tracking=10), F.WARM, 1.7 * fade(t, 36.5, 37.0, 39.2, 39.7)))
        L.append((mask("40秒 × 毎秒30コマ", 26, 500, 960, 70, tracking=8), F.GOLD, 1.4 * fade(t, 37.2, 37.7, 39.2, 39.7)))
    if 40.0 < t < 52.0:
        L.append((mask("9万個ぜんぶに、行き先がある。", 42, 500, 960, 960, tracking=8), F.WARM, 1.6 * fade(t, 40.3, 40.9, 43.3, 43.8)))
        L.append((mask("出発を少しずつずらし、渦を巻かせて移動する。", 42, 500, 960, 960, tracking=6), F.WARM, 1.6 * fade(t, 44.0, 44.6, 48.3, 48.8)))
        L.append((mask("だから、切り替えではなく「変身」に見える。", 42, 500, 960, 960, tracking=6), F.WARM, 1.6 * fade(t, 49.1, 49.6, 51.1, 51.6)))
    if 52.0 <= t < 56.2:
        ga = fade(t, 51.9, 52.0, 55.7, 56.1)
        img = Image.new("L", (W, H), 0)
        img2 = Image.new("L", (W, H), 0)
        d, d2 = ImageDraw.Draw(img), ImageDraw.Draw(img2)
        xs = np.arange(0, 1161, 4)
        tot = np.zeros(len(xs))
        for j, (lab, cyc, y0) in enumerate((("ド", 8, 240), ("ミ", 10, 390), ("ソ", 12, 540))):
            r = min(max((t - (52.0 + j)) / 0.8, 0), 1)
            w = np.sin(2 * np.pi * cyc * xs / 1160 - t * 3.0)
            if r > 0:
                n = max(int(len(xs) * r), 2)
                d.line(list(zip(380 + xs[:n], y0 - 52 * w[:n])), fill=255, width=4)
                L.append((mask(lab, 44, 500, 300, y0), F.WARM, 1.5 * ga * r))
                tot += w
        r = min(max((t - 54.6) / 0.8, 0), 1)
        if r > 0:
            n = max(int(len(xs) * r), 2)
            d2.line(list(zip(380 + xs[:n], 810 - 40 * tot[:n])), fill=255, width=5)
            L.append((mask("和音", 40, 500, 300, 810), F.GOLD, 1.5 * ga * r))
            d.line([(380, 665), (1540, 665)], fill=70, width=1)
        L.append((np.asarray(img, np.float32) / 255.0, F.CYAN, 1.7 * ga))
        L.append((np.asarray(img2, np.float32) / 255.0, F.GOLD, 2.1 * ga))
        L.append((mask("音も同じ。単純な波を、", 40, 400, 960, 990, tracking=8), F.WARM, 1.5 * fade(t, 52.3, 52.8, 54.3, 54.6)))
        L.append((mask("重ねると、和音になる。", 40, 400, 960, 990, tracking=8), F.WARM, 1.5 * fade(t, 54.7, 55.1, 55.7, 56.1)))
    if 56.1 <= t < 62.0:
        ga = fade(t, 56.1, 56.3, 61.4, 61.95)
        rx = 200 + 1520 * min(max((t - 56.3) / 3.2, 0), 1)
        L.append((X.envmask * (XX < rx), X.envcol, 1.5 * ga))
        ph = np.zeros((H, W), np.float32)
        ph[280:800, int(rx):int(rx) + 3] = 1
        L.append((ph, F.WARM, 1.8 * ga * (1 if rx < 1719 else 0)))
        L.append((mask("元の動画の音楽　40秒ぶんの波形", 26, 500, 960, 150, tracking=8), F.GOLD, 1.4 * fade(t, 56.6, 57.2, 61.2, 61.8)))
        L.append((mask("ドラムも、残響も、ぜんぶ数式。", 44, 500, 960, 940, tracking=8), F.WARM, 1.6 * fade(t, 57.0, 57.6, 61.2, 61.8)))
    if 62.0 <= t < 68.3:
        ga = fade(t, 61.9, 62.0, 67.7, 68.2)
        for T, val, lab, cx, cy in STATS:
            if t >= T:
                k = ease((t - T) / 0.7)
                v = int(round(val * k))
                a = min((t - T) / 0.25, 1.0) * ga
                L.append((mask("{:,}".format(v), 128, 700, cx, cy, path=F.FONT_EN, cache=(k >= 1)), F.WARM, 1.9 * a))
                L.append((mask(lab, 26, 500, cx, cy + 105, tracking=3), F.GOLD, 1.4 * a))
        L.append((mask("全コマの描画は、このPCで約2分。", 38, 500, 960, 925, tracking=8), F.WARM, 1.6 * fade(t, 66.0, 66.5, 67.6, 68.1)))
    if t >= 68.3:
        _, _, cuts = F.prompt_layout()
        n = int(np.clip((t - 68.5) / 1.8 * len(F.PROMPT), 2, len(F.PROMPT)))
        L.append((F.prompt_mask() * (XX < cuts[n] + 0.5), F.WARM, 1.5))
        if n < len(F.PROMPT) or (t * 2.2) % 1.0 < 0.55:
            cur = np.zeros((H, W), np.float32)
            cur[510:572, int(cuts[n] + 8):int(cuts[n] + 13)] = 1
            L.append((cur, F.GOLD, 2.0))
        if t >= 71.0:
            L.append((mask("頼んだのは、一行。", 76, 700, 960, 720, tracking=12), F.WARM, 2.0 * min((t - 71.0) / 0.2, 1.0)))
        L.append((mask("Fable 5.2", 46, 700, 960, 860, path=F.FONT_EN, tracking=6), F.GOLD, 1.5 * fade(t, 72.6, 73.4, 100, 101)))

    img = acc.T.reshape(H, W, 3).astype(np.float32)
    np.minimum(img, 30.0, out=img)
    txt = np.zeros_like(img)
    for m, c, a in L:
        if a > 0:
            txt += m[..., None] * (np.asarray(c, np.float32) * a)
    if wipe is not None:
        a_ = tone(img + txt, 1.0, flash)
        b_ = tone(img, 0.0, flash, 1.5)
        tb = tone(txt, 1.0, flash)
        b_ = 1 - (1 - b_) * (1 - tb)
        out = np.where(XX[..., None] < wipe, a_, b_)
        if 250 < wipe < 1205:
            out[150:790, int(wipe) - 1:int(wipe) + 2] = (1.0, 0.85, 0.55)
    elif bloom_amt == 0.0:
        out = 1 - (1 - tone(img, 0.0, flash, direct)) * (1 - tone(txt, 1.0, flash))
    else:
        out = tone(img + txt, bloom_amt, flash, direct)
    return final(out, t, fi, base)


_X = None


def _init():
    global _X
    _X = X()


def _job(fi):
    Image.fromarray(frame(_X, fi / FPS, fi)).save(os.path.join(HERE, "frames2", "f_%05d.png" % fi), compress_level=1)
    return fi


# ------------------------------------------------------------ audio
def read_wav(p):
    w = wave.open(p)
    return np.frombuffer(w.readframes(w.getnframes()), "<i2").reshape(-1, 2) / 32768.0


def make_audio(path):
    sr = 44100
    n = int(sr * (DUR + 3))
    rng = np.random.default_rng(8)
    dry, wet, padb, bassb = (np.zeros((n, 2)) for _ in range(4))

    def add(buf, sig, t0, gain=1.0, pan=0.0):
        i = int(t0 * sr)
        sig = sig[: max(n - i, 0)]
        buf[i:i + len(sig), 0] += sig * gain * (1 - max(pan, 0))
        buf[i:i + len(sig), 1] += sig * gain * (1 + min(pan, 0))

    mtof = lambda m: 440.0 * 2 ** ((m - 69) / 12)
    tt = lambda d: np.arange(int(d * sr)) / sr

    def lp(x, k):
        c = np.cumsum(np.concatenate([np.zeros(k), x]))
        return (c[k:] - c[:-k]) / k

    hp = lambda x, k=6: x - lp(x, k)
    noise = lambda d: rng.normal(0, 1, int(d * sr))

    def pluck(f, d, dec, harm=(1, 0.45, 0.2, 0.08)):
        t = tt(d)
        s = sum(a * np.sin(2 * np.pi * f * (k + 1) * t) for k, a in enumerate(harm))
        return s * np.exp(-t / dec) * np.minimum(t / 0.003, 1)

    def padnote(f, d, bright=1.0):
        t = tt(d)
        s = 0
        for det in (0.996, 1.0, 1.004):
            for h in range(1, 8):
                s = s + np.sin(2 * np.pi * f * det * h * t + h * det * 7) / h ** (2.0 - 0.5 * bright)
        return s * np.minimum(t / 0.5, 1) * np.minimum((d - t) / 0.6, 1) / 3

    def kick():
        t = tt(0.4)
        ph = 2 * np.pi * np.cumsum(42 + 120 * np.exp(-t * 38)) / sr
        return np.sin(ph) * np.exp(-t * 7.5) + 0.3 * np.exp(-t * 400) * rng.normal(0, 1, len(t))

    def impact(g):
        t = tt(2.2)
        ph = 2 * np.pi * np.cumsum(38 + 60 * np.exp(-t * 9)) / sr
        s = np.sin(ph) * np.exp(-t * 2.2) * 1.2 + lp(noise(2.2), 24) * np.exp(-t * 3.5) * 1.5
        return s * g, hp(noise(2.2), 3) * np.exp(-t * 2.0) * 0.22 * g

    def riser(d, g):
        u = tt(d) / d
        return (hp(noise(d), 10) * u ** 2.5 * 0.5 + np.sin(2 * np.pi * np.cumsum(180 * 2 ** (u * 3.2)) / sr) * u ** 2 * 0.25) * g

    def click(g=1.0):
        t = tt(0.03)
        return (hp(noise(0.03), 4) * 0.6 + np.sin(2 * np.pi * rng.uniform(1700, 2600) * t)) * np.exp(-t * 220) * g

    # fast-forward of the original soundtrack, then a tape stop
    src = os.path.join(HERE, "audio.wav")
    if os.path.exists(src):
        o = read_wav(src)[int(6 * sr):int(29.5 * sr)]
        idx = (np.arange(int(3.5 * sr)) * (len(o) / (3.5 * sr))).astype(int)
        ffw = o[np.minimum(idx, len(o) - 1)] * 0.4
        e = np.minimum(np.arange(len(ffw)) / (0.3 * sr), 1) * np.minimum((len(ffw) - np.arange(len(ffw))) / (0.05 * sr), 1)
        dry[:len(ffw)] += ffw * e[:, None]
    t = tt(0.7)
    add(dry, np.sin(2 * np.pi * np.cumsum(320 * np.exp(-t * 5) + 30) / sr) * np.exp(-t * 4), 3.5, 0.3)
    for T, g in IMPACTS.items():
        a, b = impact(g)
        add(dry, a, T, 0.55)
        add(wet, a, T, 0.25)
        add(dry, b, T, 0.6)
        add(wet, b, T, 0.6)
    for T, d_, g in ((13.2, 1.0, 0.35), (34.5, 1.5, 0.45), (39.0, 1.0, 0.3), (60.5, 1.5, 0.4)):
        add(dry, riser(d_, g), T)
        add(wet, riser(d_, g * 0.7), T)
    for k, m in enumerate((76, 79, 81, 84)):
        pl = pluck(mtof(m), 0.8, 0.25)
        add(dry, pl, 8.15 + k, 0.10)
        add(wet, pl, 8.15 + k, 0.12)
    for k, m in enumerate((84, 86, 88, 91)):
        pl = pluck(mtof(m), 0.8, 0.3)
        add(dry, pl, 62.0 + k, 0.09)
        add(wet, pl, 62.0 + k, 0.12)
    for tc in np.arange(20.25, 22.8, 0.055):
        add(dry, click(), tc, 0.035 + 0.02 * (tc - 20.25), rng.uniform(-0.5, 0.5))
    for i in range(len(F.PROMPT)):
        tc = 68.5 + i * 1.8 / len(F.PROMPT)
        c = click()
        add(dry, c, tc, 0.12, rng.uniform(-0.4, 0.4))
        add(wet, c, tc, 0.05)
    # three pure tones -> a chord
    for j, m in enumerate((60, 64, 67)):
        d_ = 4.0 - j
        t = tt(d_)
        s = np.sin(2 * np.pi * mtof(m) * t) * np.minimum(t / 0.08, 1) * np.minimum((d_ - t) / 0.35, 1)
        add(dry, s, 52.0 + j, 0.16, (j - 1) * 0.4)
        add(wet, s, 52.0 + j, 0.05)

    Am, Fc, C, G = [57, 60, 64], [53, 57, 60], [48, 55, 64], [55, 59, 62]
    loop = [Am, Fc, C, G]
    kicks = []
    for bi in range(2, 34):
        t0 = bi * 2.0
        if 52.0 <= t0 < 56.0:
            continue
        ch = loop[bi % 4]
        mode = "intro" if t0 < 8 else "light" if t0 < 20 else "full" if t0 < 40 else "half" if t0 < 52 else "full"
        lvl = {"intro": 0.5, "light": 0.7, "full": 1.0, "half": 0.9}[mode]
        for m in ch:
            add(padb, padnote(mtof(m), 2.5, 1.0 if mode == "full" else 0.5), t0 - 0.1, 0.08 * lvl, 0.3 * (m % 3 - 1))
        root = ch[0] - 24 if ch[0] - 24 >= 31 else ch[0] - 12
        if mode == "full":
            for k in range(8):
                add(bassb, np.tanh(pluck(mtof(root), 0.24, 0.16, (1, 0.6, 0.3)) * 2.0), t0 + k * 0.25, 0.24 if k % 2 == 0 else 0.18)
        elif mode != "intro":
            ts_ = tt(2.0)
            add(bassb, np.sin(2 * np.pi * mtof(root) * ts_) * np.minimum(ts_ / 0.1, 1) * np.minimum((2 - ts_) / 0.2, 1), t0, 0.22)
        notes = [ch[0], ch[1], ch[2], ch[0] + 12, ch[1] + 12, ch[2] + 12, ch[0] + 24, ch[2] + 12]
        step = 0.125 if mode == "full" else 0.25 if mode == "light" else 0.5
        for k in range(int(2.0 / step)):
            m = notes[(k * 3 if mode == "full" else k) % len(notes)] + 12
            v = (0.9 if k % 4 == 0 else 0.6) * lvl
            pl = pluck(mtof(m), 0.9, 0.16 if mode == "full" else 0.35, (1, 0.5, 0.3, 0.15) if mode == "full" else (1, 0.3, 0.1))
            add(dry, pl, t0 + k * step, 0.055 * v, 0.6 * (-1) ** k)
            add(wet, pl, t0 + k * step, 0.050 * v, -0.6 * (-1) ** k)
        if mode != "intro":
            for k in range(4):
                if mode == "half" and k % 2:
                    continue
                kicks.append(t0 + k * 0.5)
                add(dry, kick(), t0 + k * 0.5, {"light": 0.36, "full": 0.58, "half": 0.42}[mode])
            for k in range(16):
                if mode == "half" or (mode == "light" and k % 4 != 2):
                    continue
                ts_ = tt(0.06)
                hh = hp(hp(noise(0.06), 3), 3) * np.exp(-ts_ * (60 if k % 4 == 2 else 140))
                add(dry, hh, t0 + k * 0.125, (0.09 if k % 4 == 2 else 0.03 * rng.uniform(0.5, 1.2)) * (0.6 if mode == "light" else 1), 0.25)
            if mode == "full":
                for k in (1, 3):
                    ts_ = tt(0.25)
                    cp = hp(lp(noise(0.25), 3), 30) * np.exp(-ts_ * 22) * (1 + (ts_ < 0.02))
                    add(dry, cp, t0 + k * 0.5, 0.26)
                    add(wet, cp, t0 + k * 0.5, 0.18)
    # ending chord
    for m, g in ((48, 0.10), (55, 0.09), (60, 0.09), (64, 0.09), (67, 0.07), (74, 0.05)):
        add(padb, padnote(mtof(m), 5.5, 1.0), 70.95, g, 0.4 * (m % 3 - 1))
    ts_ = tt(5.0)
    add(bassb, np.sin(2 * np.pi * mtof(36) * ts_) * np.exp(-ts_ / 2.2) * np.minimum(ts_ / 0.02, 1), 71.0, 0.34)
    for k, m in enumerate((72, 76, 79, 84, 88, 91, 96)):
        pl = pluck(mtof(m), 2.0, 0.6, (1, 0.25, 0.4, 0.1))
        add(dry, pl, 71.0 + k * 0.4, 0.05 * (1 - k / 10), 0.5 * (-1) ** k)
        add(wet, pl, 71.0 + k * 0.4, 0.07 * (1 - k / 10), -0.5 * (-1) ** k)
    duck = np.ones(n)
    tfull = np.arange(n) / sr
    for tk in kicks:
        i = int(tk * sr)
        seg = tfull[i:i + int(0.4 * sr)] - tk
        duck[i:i + len(seg)] = np.minimum(duck[i:i + len(seg)], 1 - 0.55 * np.exp(-seg * 9))
    L_ = int(2.8 * sr)
    tr = np.arange(L_) / sr
    nf = 1 << int(np.ceil(np.log2(n + L_)))
    rev = np.zeros((n, 2))
    for c in range(2):
        ir = hp(rng.normal(0, 1, L_) * np.exp(-tr / 0.55), 40)
        rev[:, c] = np.fft.irfft(np.fft.rfft(wet[:, c], nf) * np.fft.rfft(ir, nf), nf)[:n]
    rev /= np.abs(rev).max() + 1e-9
    music = (padb + bassb) * duck[:, None]
    # quiet the band around the pure-tone demo and the typed ending
    gate = np.ones(n)
    for a, b in ((51.6, 56.0), (67.9, 70.95)):
        gate *= 1 - np.clip((tfull - a) / 0.4, 0, 1) * np.clip((b - tfull) / 0.05, 0, 1)
    mix = dry + music * gate[:, None] + rev * 0.42
    mix = mix[: int(DUR * sr)]
    tm_ = np.arange(len(mix)) / sr
    env = np.clip(tm_ / 0.3, 0, 1) * np.clip((DUR - 0.15 - tm_) / 2.4, 0, 1) ** 1.3
    mix = np.tanh(mix * 1.5) * env[:, None]
    mix *= 0.92 / np.abs(mix).max()
    with wave.open(path, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes((mix * 32767).astype("<i2").tobytes())


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "prep":
        mo = Image.new("RGB", (1920, 810))
        for i in range(1200):
            im = Image.open(os.path.join(HERE, "frames", "f_%05d.png" % i))
            mo.paste(im.resize((48, 27), Image.BOX), ((i % 40) * 48, (i // 40) * 27))
        mo.save(os.path.join(HERE, "mosaic.png"))
        a = np.abs(read_wav(os.path.join(HERE, "audio.wav"))).max(axis=1)
        m = len(a) // 1520
        env = a[: m * 1520].reshape(1520, m).max(axis=1)
        np.save(os.path.join(HERE, "env.npy"), env / env.max())
        print("prep ok")
    elif cmd == "stills":
        os.makedirs(os.path.join(HERE, "stills"), exist_ok=True)
        x = X()
        for a in sys.argv[2:]:
            t = float(a)
            Image.fromarray(frame(x, t, int(t * FPS))).save(os.path.join(HERE, "stills", "m_%05.2f.png" % t))
            print("still", t, flush=True)
    elif cmd == "frames":
        from multiprocessing import Pool
        os.makedirs(os.path.join(HERE, "frames2"), exist_ok=True)
        total = int(DUR * FPS)
        with Pool(int(sys.argv[2]) if len(sys.argv) > 2 else 12, initializer=_init) as pool:
            for k, fi in enumerate(pool.imap_unordered(_job, range(total), chunksize=4)):
                if k % 200 == 0:
                    print("frame", k, "/", total, flush=True)
    elif cmd == "audio":
        make_audio(os.path.join(HERE, "audio2.wav"))
        print("audio ok")
    elif cmd == "mux":
        import imageio_ffmpeg
        ff = imageio_ffmpeg.get_ffmpeg_exe()
        subprocess.check_call([ff, "-y", "-loglevel", "error", "-framerate", str(FPS), "-i", os.path.join(HERE, "frames2", "f_%05d.png"),
                               "-i", os.path.join(HERE, "audio2.wav"), "-c:v", "libx264", "-preset", "slow", "-crf", sys.argv[3] if len(sys.argv) > 3 else "20",
                               "-maxrate", sys.argv[4] if len(sys.argv) > 4 else "14M", "-bufsize", "28M", "-pix_fmt", "yuv420p",
                               "-c:a", "aac", "-b:a", "256k", "-movflags", "+faststart", "-shortest", sys.argv[2]])
