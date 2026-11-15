"""Animated (GIF) versions of A-Town TS6 banners, built on make_banners.py.

Each frame keeps the static layout (title top, subtitle bottom, motif in the ~y=105..137
strip the TS6 channel tree shows) and animates only small things: a light sweep through
the middle band, twinkling stars and a per-channel motif animation.
Run: python assets/make_animated.py
"""
import math
import random

from PIL import Image, ImageDraw, ImageFilter

import make_banners as mb

W, H, SS = mb.W, mb.H, mb.SS
FRAMES = 24
MS = 80  # per frame -> ~1.9 s loop


def base(title, subtitle, accent, seed):
    img = mb.background(accent, seed)
    mb.downs(img, accent)
    band = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ImageDraw.Draw(band).rectangle([0, 104 * SS, W * SS, 132 * SS], fill=accent + (38,))
    img = Image.alpha_composite(img, band.filter(ImageFilter.GaussianBlur(10 * SS)))
    mb.text(img, title, subtitle, accent)
    return img


def sweep(f, accent):
    """Soft light band that slides left->right through the tree strip."""
    layer = Image.new("RGBA", (W * SS, H * SS), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    x = int((-0.2 + 1.4 * f / FRAMES) * W * SS)
    d.rectangle([x - 40 * SS, 106 * SS, x + 40 * SS, 136 * SS], fill=tuple(min(255, c + 60) for c in accent) + (60,))
    return layer.filter(ImageFilter.GaussianBlur(18 * SS))


def stars(f, seed):
    rnd = random.Random(seed * 31)
    layer = Image.new("RGBA", (W * SS, H * SS), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    for i in range(10):
        x, y = rnd.randrange(W * SS // 3, W * SS), rnd.randrange(8 * SS, 100 * SS)
        a = max(0.0, math.sin(2 * math.pi * (f / FRAMES + i / 10)))
        r = (1 + 2 * a) * SS
        d.ellipse([x - r, y - r, x + r, y + r], fill=(255, 255, 255, int(200 * a)))
    return layer


def eq_bars(f, accent):
    """Bouncing equaliser at the motif spot, sized for the 24px strip."""
    layer = Image.new("RGBA", (W * SS, H * SS), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    cx, cy = int(W * SS * 0.83), 121 * SS
    n, bw, gap = 13, 3 * SS, 2 * SS
    x0 = cx - (n * (bw + gap)) // 2
    t = 2 * math.pi * f / FRAMES
    for i in range(n):
        h = (5 + 17 * abs(math.sin(t * (1 + i % 3) + i * 0.9))) * SS
        x = x0 + i * (bw + gap)
        col = accent if i % 3 else (240, 240, 250)
        d.rounded_rectangle([x, cy - h / 2, x + bw, cy + h / 2], SS, fill=col + (255,))
    return layer


MOTIFS = {"music": eq_bars}

ANIMATED = [  # file, title, subtitle, motif, accent, seed (matches make_banners order + 7)
    ("music", "Music & Chill", "Tunes on. Feet up. Type !help", "music", (255, 100, 160), 14),
]


def render(name, title, subtitle, kind, accent, seed):
    still = base(title, subtitle, accent, seed)
    frames = []
    for f in range(FRAMES):
        img = still.copy()
        img.alpha_composite(sweep(f, accent))
        img.alpha_composite(stars(f, seed))
        img.alpha_composite(MOTIFS[kind](f, accent))
        frames.append(img.resize((W, H), Image.LANCZOS).convert("RGB"))
    # one shared palette keeps the gradient steady between frames
    pal = frames[0].quantize(colors=255, method=Image.Quantize.MEDIANCUT)
    q = [fr.quantize(palette=pal, dither=Image.Dither.NONE) for fr in frames]
    out = mb.OUT / f"{name}.gif"
    q[0].save(out, save_all=True, append_images=q[1:], duration=MS, loop=0, optimize=True, disposal=1)
    print("wrote", out, out.stat().st_size // 1024, "KB")
    # APNG: clients that can't animate it just show frame 1 like a normal PNG
    apng = mb.OUT / f"{name}_anim.png"
    frames[0].save(apng, save_all=True, append_images=frames[1:], duration=MS, loop=0, optimize=True)
    print("wrote", apng, apng.stat().st_size // 1024, "KB")


if __name__ == "__main__":
    for spec in ANIMATED:
        render(*spec)
