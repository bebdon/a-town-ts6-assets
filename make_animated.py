"""Animated (APNG) versions of the A-Town TS6 banners, built on make_banners.py.

TS6 plays APNG banners on mouse-over and shows frame 1 otherwise (GIFs stay frozen),
so frame 1 is kept identical in feel to the still banner. Each frame keeps the static
layout and animates only small things: a light sweep through the middle band (the strip
the channel tree shows), twinkling stars and a per-channel motif move.
Run: python assets/make_animated.py   -> banners/<name>_anim.png
"""
import math
import random

from PIL import Image, ImageDraw, ImageFilter

import make_banners as mb

W, H, SS = mb.W, mb.H, mb.SS
FRAMES = 24
MS = 80  # per frame -> ~1.9 s loop
CX, CY = int(W * SS * 0.83), 121 * SS  # motif centre, same as the still banners


def base(title, subtitle, accent, seed):
    img = mb.background(accent, seed)
    mb.downs(img, accent)
    band = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ImageDraw.Draw(band).rectangle([0, 104 * SS, W * SS, 132 * SS], fill=accent + (38,))
    img = Image.alpha_composite(img, band.filter(ImageFilter.GaussianBlur(10 * SS)))
    mb.text(img, title, subtitle, accent)
    return img


def blank():
    return Image.new("RGBA", (W * SS, H * SS), (0, 0, 0, 0))


def sweep(t, accent):
    """Soft light band that slides left->right through the tree strip (offscreen at t=0)."""
    layer = blank()
    x = int((-0.25 + 1.5 * t) * W * SS)
    ImageDraw.Draw(layer).rectangle([x - 40 * SS, 106 * SS, x + 40 * SS, 136 * SS],
                                    fill=tuple(min(255, c + 60) for c in accent) + (60,))
    return layer.filter(ImageFilter.GaussianBlur(18 * SS))


def stars(t, seed):
    rnd = random.Random(seed * 31)
    layer = blank()
    d = ImageDraw.Draw(layer)
    for i in range(10):
        x, y = rnd.randrange(W * SS // 3, W * SS), rnd.randrange(8 * SS, 100 * SS)
        a = max(0.0, math.sin(2 * math.pi * (t + i / 10)))
        r = (1 + 2 * a) * SS
        d.ellipse([x - r, y - r, x + r, y + r], fill=(255, 255, 255, int(200 * a)))
    return layer


def static_motif(kind, accent):
    """The still banner's motif, scaled exactly like make_banners.render."""
    layer = blank()
    mb.motif(layer, kind, accent)
    m = layer.crop(layer.getbbox())
    scale = min(0.62, (24 * SS) / m.height, (70 * SS) / m.width)
    return m.resize((max(1, int(m.width * scale)), max(1, int(m.height * scale))), Image.LANCZOS)


def place(m, dx=0, dy=0, scale=1.0, angle=0.0, alpha=1.0):
    if angle:
        m = m.rotate(angle, resample=Image.BICUBIC, expand=True)
    if scale != 1.0:
        m = m.resize((max(1, int(m.width * scale)), max(1, int(m.height * scale))), Image.LANCZOS)
    if alpha < 1.0:
        m = m.copy()
        m.putalpha(m.getchannel("A").point(lambda v: int(v * alpha)))
    layer = blank()
    layer.alpha_composite(m, (int(CX + dx - m.width / 2), int(CY + dy - m.height / 2)))
    return layer


# ---- per-channel motif moves; t runs 0..1, and t=0 looks like the still banner ----

def eq_bars(t, accent, m):
    layer = blank()
    d = ImageDraw.Draw(layer)
    n, bw, gap = 13, 3 * SS, 2 * SS
    x0 = CX - (n * (bw + gap)) // 2
    for i in range(n):
        h = (5 + 17 * abs(math.sin(2 * math.pi * t * (1 + i % 3) + i * 0.9))) * SS
        x = x0 + i * (bw + gap)
        d.rounded_rectangle([x, CY - h / 2, x + bw, CY + h / 2], SS,
                            fill=(accent if i % 3 else (240, 240, 250)) + (255,))
    return layer


def signal_fill(t, accent, m):
    """Bars light up one by one, then reset."""
    layer = blank()
    d = ImageDraw.Draw(layer)
    lit = int(t * 6) if t > 0 else 4
    for i in range(5):
        h = (5 + i * 4.5) * SS
        x = CX - 26 * SS + i * 11 * SS
        on = i < lit
        d.rounded_rectangle([x, CY + 12 * SS - h, x + 8 * SS, CY + 12 * SS], 2 * SS,
                            fill=(accent + (255,)) if on else (240, 240, 250, 90))
    return layer


def moon_z(t, accent, m):
    layer = place(m, dy=1.5 * SS * math.sin(2 * math.pi * t))
    d = ImageDraw.Draw(layer)
    f = mb.font(mb.FONT_BOLD, 9)
    for k in range(3):
        p = (t + k / 3) % 1
        x = CX + (20 + 14 * p) * SS
        y = CY + (6 - 20 * p) * SS
        d.text((x, y), "z", font=f, fill=accent + (int(255 * math.sin(math.pi * p)),))
    return layer


def train(t, accent, m):
    s = math.sin(2 * math.pi * t)
    layer = place(m, dx=4 * SS * s, dy=0.6 * SS * abs(math.sin(4 * math.pi * t)))
    d = ImageDraw.Draw(layer)
    for k in range(3):  # puffs rising from the chimney end (left)
        p = (t + k / 3) % 1
        x = CX - m.width / 2 + 4 * SS * s - 10 * SS * p
        y = CY - m.height / 2 - 10 * SS * p
        r = (2 + 4 * p) * SS
        d.ellipse([x - r, y - r, x + r, y + r], fill=(230, 232, 240, int(180 * (1 - p))))
    return layer


def bob(t, accent, m):
    return place(m, dy=2 * SS * math.sin(2 * math.pi * t))


def pulse(t, accent, m):
    return place(m, scale=1 + 0.12 * math.sin(2 * math.pi * t) ** 2)


def wobble(t, accent, m):
    return place(m, angle=8 * math.sin(2 * math.pi * t))



def blocks_drop(t, accent, m):
    # whole stack hops like a block being placed
    return place(m, dy=-3 * SS * max(0.0, math.sin(4 * math.pi * t)))


def bubble_typing(t, accent, m):
    layer = place(m)
    d = ImageDraw.Draw(layer)
    for i in (-1, 0, 1):  # dots bounce in turn, like someone typing
        dy = -2 * SS * max(0.0, math.sin(2 * math.pi * (t - (i + 1) * 0.15)))
        x = CX + i * 5.5 * SS
        y = CY - 2.5 * SS + dy
        d.ellipse([x - 1.6 * SS, y - 1.6 * SS, x + 1.6 * SS, y + 1.6 * SS], fill=(255, 255, 255, 255))
    return layer


MOVES = {
    "music": eq_bars, "signal": signal_fill, "moon": bob, "train": train,
    "controller": wobble, "crosshair": pulse, "swords": wobble, "blocks": blocks_drop,
    "crown": bob, "door": pulse, "shield": pulse, "bubble": bob,
}


def render(name, title, subtitle, kind, accent, seed):
    still = base(title, subtitle, accent, seed)
    m = static_motif(kind, accent)
    frames = []
    for f in range(FRAMES):
        t = f / FRAMES
        img = still.copy()
        img.alpha_composite(sweep(t, accent))
        img.alpha_composite(stars(t, seed))
        img.alpha_composite(MOVES[kind](t, accent, m))
        frames.append(img.resize((W, H), Image.LANCZOS).convert("RGB"))
    out = mb.OUT / f"{name}_anim.png"
    frames[0].save(out, save_all=True, append_images=frames[1:], duration=MS, loop=0, optimize=True)
    print("wrote", out.name, out.stat().st_size // 1024, "KB")


if __name__ == "__main__":
    for i, b in enumerate(mb.BANNERS):
        render(*b, seed=i + 7)
