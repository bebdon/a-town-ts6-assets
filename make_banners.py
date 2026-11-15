"""Generate A-Town TS6 channel banners (630x236 PNG) into assets/banners/.

Theme: dark navy base, rolling hills silhouette, accent colour per channel.
Layout is built for TS6: the channel tree shows only a thin horizontal strip from the
middle of the image, so the middle band holds just background art + motif, with the
title at the top and the subtitle at the bottom (both visible in the channel info view).
Run: python assets/make_banners.py
"""
import math
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H = 630, 236
SS = 2  # supersample factor for smooth edges
OUT = Path(__file__).parent / "banners"
FONT_BOLD = "C:/Windows/Fonts/bahnschrift.ttf"
FONT_SUB = "C:/Windows/Fonts/seguisb.ttf"

NAVY_TOP = (14, 20, 38)
NAVY_BOT = (24, 34, 62)
CREAM = (244, 236, 220)
MUTED = (160, 172, 200)


def font(path, size, weight=None):
    f = ImageFont.truetype(path, size * SS)
    if weight is not None:
        try:
            f.set_variation_by_axes([weight])
        except Exception:
            pass
    return f


def background(accent, seed):
    rnd = random.Random(seed)
    img = Image.new("RGB", (W * SS, H * SS))
    d = ImageDraw.Draw(img)
    for y in range(H * SS):
        t = y / (H * SS)
        c = tuple(int(NAVY_TOP[i] + (NAVY_BOT[i] - NAVY_TOP[i]) * t) for i in range(3))
        d.line([(0, y), (W * SS, y)], fill=c)
    # accent glow on the right
    glow = Image.new("RGBA", img.size, (0, 0, 0, 0))
    g = ImageDraw.Draw(glow)
    cx, cy, r = int(W * SS * 0.78), int(H * SS * 0.45), int(H * SS * 0.95)
    g.ellipse([cx - r, cy - r, cx + r, cy + r], fill=accent + (70,))
    glow = glow.filter(ImageFilter.GaussianBlur(60 * SS))
    img = Image.alpha_composite(img.convert("RGBA"), glow)
    # faint stars / dust
    d = ImageDraw.Draw(img)
    for _ in range(45):
        x, y = rnd.randrange(W * SS), rnd.randrange(int(H * SS * 0.6))
        s = rnd.choice([1, 1, 2]) * SS
        d.ellipse([x, y, x + s, y + s], fill=(255, 255, 255, rnd.randrange(40, 120)))
    return img


def downs(img, accent):
    """Rolling hills along the bottom, two layers."""
    d = ImageDraw.Draw(img)
    for layer, (amp, base, col) in enumerate(
        [(14, 0.80, (30, 44, 78, 255)), (10, 0.88, (20, 30, 56, 255))]
    ):
        pts = []
        for x in range(0, W * SS + 1, 4):
            t = x / (W * SS)
            y = H * SS * base - amp * SS * (
                math.sin(t * 6.2 + layer * 1.7) + 0.6 * math.sin(t * 13.1 + layer)
            )
            pts.append((x, y))
        pts += [(W * SS, H * SS), (0, H * SS)]
        d.polygon(pts, fill=col)
    # accent rim line on the front hill
    d.line([(0, H * SS - 3 * SS), (W * SS, H * SS - 3 * SS)], fill=accent + (255,), width=3 * SS)


def hop(d, cx, cy, size, color):
    """Hop cone: stacked overlapping petals."""
    s = size * SS
    rows = [(0, 0.35), (0.28, 0.45), (0.56, 0.5), (0.84, 0.42), (1.08, 0.28)]
    for i, (dy, wr) in enumerate(rows):
        y = cy + dy * s
        w = wr * s
        shade = tuple(min(255, int(c * (0.8 + 0.06 * i))) for c in color)
        d.ellipse([cx - w, y - 0.22 * s, cx + w, y + 0.22 * s], fill=shade + (255,))
        d.ellipse([cx - w * 0.5, y - 0.18 * s, cx + w * 0.5, y + 0.12 * s], fill=tuple(min(255, c + 25) for c in shade) + (255,))
    d.line([(cx, cy - 0.35 * s), (cx + 0.15 * s, cy - 0.6 * s)], fill=color + (255,), width=max(2, int(0.06 * s)))


def motif(img, kind, accent):
    d = ImageDraw.Draw(img)
    A = accent + (255,)
    L = (240, 240, 250, 235)
    cx, cy = int(W * SS * 0.80), int(H * SS * 0.44)
    u = SS
    if kind == "train":
        # steam loco silhouette heading left, with puffs
        x0, y0 = cx - 95 * u, cy + 5 * u
        body = (12, 16, 30, 255)
        d.rounded_rectangle([x0, y0, x0 + 120 * u, y0 + 38 * u], 8 * u, fill=body)            # boiler
        d.rectangle([x0 + 85 * u, y0 - 30 * u, x0 + 140 * u, y0 + 38 * u], fill=body)         # cab
        d.rectangle([x0 + 80 * u, y0 - 36 * u, x0 + 146 * u, y0 - 28 * u], fill=body)         # cab roof
        d.rectangle([x0 + 95 * u, y0 - 22 * u, x0 + 128 * u, y0 - 4 * u], fill=A)             # lit window
        d.rectangle([x0 + 14 * u, y0 - 22 * u, x0 + 28 * u, y0], fill=body)                   # chimney
        d.polygon([(x0 - 14 * u, y0 + 38 * u), (x0, y0 + 18 * u), (x0, y0 + 38 * u)], fill=body)  # cow catcher
        for wx in (x0 + 20 * u, x0 + 58 * u, x0 + 112 * u):
            d.ellipse([wx - 15 * u, y0 + 30 * u, wx + 15 * u, y0 + 60 * u], fill=body, outline=A, width=2 * u)
        d.line([(x0 + 5 * u, y0 + 45 * u), (x0 + 125 * u, y0 + 45 * u)], fill=A, width=3 * u)
        for i, (px, py, pr) in enumerate([(14, -40, 14), (-6, -62, 18), (-34, -80, 22), (-70, -90, 20)]):
            a = 200 - i * 40
            d.ellipse([x0 + (21 + px - pr) * u, y0 + (py - pr) * u, x0 + (21 + px + pr) * u, y0 + (py + pr) * u], fill=(230, 232, 240, a))
    elif kind == "controller":
        d.rounded_rectangle([cx - 70 * u, cy - 30 * u, cx + 70 * u, cy + 30 * u], 30 * u, fill=L)
        d.rectangle([cx - 48 * u, cy - 4 * u, cx - 24 * u, cy + 4 * u], fill=A)
        d.rectangle([cx - 40 * u, cy - 12 * u, cx - 32 * u, cy + 12 * u], fill=A)
        for bx, by in ((30, -8), (44, 4), (18, 4), (30, 16)):
            d.ellipse([cx + (bx - 6) * u, cy + (by - 6) * u - 4 * u, cx + (bx + 6) * u, cy + (by + 6) * u - 4 * u], fill=A)
    elif kind == "crosshair":
        r = 52 * u
        d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=L, width=5 * u)
        d.ellipse([cx - r // 2, cy - r // 2, cx + r // 2, cy + r // 2], outline=A, width=3 * u)
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            d.line([(cx + dx * 18 * u, cy + dy * 18 * u), (cx + dx * 70 * u, cy + dy * 70 * u)], fill=L, width=5 * u)
        d.ellipse([cx - 5 * u, cy - 5 * u, cx + 5 * u, cy + 5 * u], fill=A)
    elif kind == "swords":
        for sgn in (1, -1):
            x1, y1, x2, y2 = cx - sgn * 60 * u, cy + 55 * u, cx + sgn * 60 * u, cy - 55 * u
            d.line([(x1, y1), (x2, y2)], fill=L, width=9 * u)
            gx, gy = cx - sgn * 38 * u, cy + 35 * u
            d.line([(gx - 18 * u, gy - sgn * 18 * u * -1), (gx + 18 * u, gy + sgn * 18 * u * -1)], fill=A, width=8 * u)
            d.ellipse([x1 - 8 * u, y1 - 8 * u, x1 + 8 * u, y1 + 8 * u], fill=A)
    elif kind == "blocks":
        s = 26 * u
        cols = [(110, 170, 70), (94, 150, 60), (134, 96, 60), (116, 84, 52), (128, 128, 128)]
        layout = [(0, 0, 0), (1, 0, 1), (2, 0, 0), (0, 1, 2), (1, 1, 3), (2, 1, 2), (1, -1, 0), (0, 2, 4), (1, 2, 3), (2, 2, 4)]
        for gx, gy, ci in layout:
            x, y = cx - 40 * u + gx * s, cy - 30 * u + gy * s
            c = cols[ci]
            d.rectangle([x, y, x + s - 2 * u, y + s - 2 * u], fill=c + (255,))
            d.rectangle([x, y, x + s - 2 * u, y + 5 * u], fill=tuple(min(255, v + 30) for v in c) + (255,))
    elif kind == "crown":
        pts = [(cx - 60 * u, cy + 30 * u), (cx - 60 * u, cy - 25 * u), (cx - 30 * u, cy + 2 * u), (cx, cy - 40 * u),
               (cx + 30 * u, cy + 2 * u), (cx + 60 * u, cy - 25 * u), (cx + 60 * u, cy + 30 * u)]
        d.polygon(pts, fill=A)
        d.rectangle([cx - 60 * u, cy + 30 * u, cx + 60 * u, cy + 44 * u], fill=L)
        for px, py in ((-60, -25), (0, -40), (60, -25)):
            d.ellipse([cx + (px - 8) * u, cy + (py - 8) * u, cx + (px + 8) * u, cy + (py + 8) * u], fill=L)
    elif kind == "signal":
        for i in range(5):
            h = (16 + i * 18) * u
            x = cx - 60 * u + i * 26 * u
            d.rounded_rectangle([x, cy + 45 * u - h, x + 18 * u, cy + 45 * u], 4 * u, fill=A if i < 4 else L)
    elif kind == "music":
        for i in range(17):
            h = (12 + 50 * abs(math.sin(i * 0.7))) * u
            x = cx - 85 * u + i * 10 * u
            d.rounded_rectangle([x, cy - h / 2, x + 6 * u, cy + h / 2], 3 * u, fill=A if i % 3 else L)
        d.ellipse([cx + 40 * u, cy + 18 * u, cx + 62 * u, cy + 36 * u], fill=L)
        d.line([(cx + 60 * u, cy + 27 * u), (cx + 60 * u, cy - 40 * u)], fill=L, width=4 * u)
        d.line([(cx + 60 * u, cy - 40 * u), (cx + 78 * u, cy - 28 * u)], fill=L, width=4 * u)
    elif kind == "door":
        d.rounded_rectangle([cx - 38 * u, cy - 55 * u, cx + 38 * u, cy + 55 * u], 6 * u, outline=L, width=5 * u)
        d.polygon([(cx - 33 * u, cy - 50 * u), (cx + 20 * u, cy - 40 * u), (cx + 20 * u, cy + 60 * u), (cx - 33 * u, cy + 50 * u)], fill=A)
        d.ellipse([cx + 6 * u, cy, cx + 14 * u, cy + 8 * u], fill=L)
    elif kind == "shield":
        pts = [(cx, cy - 58 * u), (cx + 50 * u, cy - 40 * u), (cx + 44 * u, cy + 20 * u), (cx, cy + 58 * u), (cx - 44 * u, cy + 20 * u), (cx - 50 * u, cy - 40 * u)]
        d.polygon(pts, fill=A)
        d.rounded_rectangle([cx - 18 * u, cy - 6 * u, cx + 18 * u, cy + 24 * u], 4 * u, fill=L)
        d.arc([cx - 13 * u, cy - 26 * u, cx + 13 * u, cy + 2 * u], 180, 360, fill=L, width=5 * u)
    elif kind == "moon":
        r = 46 * u
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=L)
        d.ellipse([cx - r + 24 * u, cy - r - 10 * u, cx + r + 24 * u, cy + r - 10 * u], fill=(0, 0, 0, 0))
        f = font(FONT_BOLD, 28)
        for i, (zx, zy) in enumerate(((50, -40), (72, -66), (92, -88))):
            d.text((cx + zx * u, cy + zy * u), "z", font=font(FONT_BOLD, 22 + i * 6), fill=A)
    elif kind == "bubble":
        d.rounded_rectangle([cx - 66 * u, cy - 42 * u, cx + 66 * u, cy + 30 * u], 24 * u, fill=A)
        d.polygon([(cx - 30 * u, cy + 28 * u), (cx - 48 * u, cy + 56 * u), (cx - 6 * u, cy + 28 * u)], fill=A)
        for i in (-1, 0, 1):
            d.ellipse([cx + i * 30 * u - 8 * u, cy - 14 * u, cx + i * 30 * u + 8 * u, cy + 2 * u], fill=L)


def moon_cutout(img, accent):
    """Moon motif needs a real crescent: redraw the cut with background colour."""
    return img


def text(img, title, subtitle, accent):
    d = ImageDraw.Draw(img)
    x = 30 * SS
    d.text((x, 16 * SS), "A-TOWN TS6", font=font(FONT_SUB, 12), fill=accent + (255,))
    size = 40
    tf = font(FONT_BOLD, size, 700)
    while d.textlength(title, font=tf) > W * SS * 0.62 and size > 24:
        size -= 2
        tf = font(FONT_BOLD, size, 700)
    d.text((x + 2 * SS, 32 * SS + 2 * SS), title, font=tf, fill=(0, 0, 0, 140))
    d.text((x, 32 * SS), title, font=tf, fill=CREAM + (255,))
    d.rounded_rectangle([x, 84 * SS, x + 40 * SS, 87 * SS], 2 * SS, fill=accent + (255,))
    sf = font(FONT_SUB, 14)
    d.text((x + 1 * SS, 203 * SS + 1 * SS), subtitle, font=sf, fill=(0, 0, 0, 160))
    d.text((x, 203 * SS), subtitle, font=sf, fill=CREAM + (230,))


BANNERS = [
    # file, title, subtitle, motif, accent
    ("lobby", "Lobby", "Welcome in. Thanks for making the move.", "train", (232, 170, 66)),
    ("games", "Games", "Pick your game, grab a seat.", "controller", (96, 170, 255)),
    ("cs", "Counter Strike", "Rush B. Comms on.", "crosshair", (240, 150, 60)),
    ("wow", "World of Warcraft", "Raids, dungeons and questing.", "swords", (170, 110, 255)),
    ("minecraft", "Minecraft", "beanzone1.g.akliz.net", "blocks", (120, 190, 80)),
    ("lol", "League of Legends", "Ranked, normals and ARAM.", "crown", (220, 180, 80)),
    ("ping", "Ping To Play", "Poke a Mod when you're ready.", "signal", (60, 210, 170)),
    ("music", "Music / Chill", "Tunes on. Feet up.", "music", (255, 100, 160)),
    ("private", "Private Rooms", "Make your own room in here.", "door", (90, 200, 230)),
    ("staff", "Staff Room", "Moderators and up only.", "shield", (230, 80, 80)),
    ("afk", "AFK", "Back in a bit.", "moon", (140, 150, 220)),
    ("discord", "On Discord", "Over on Discord right now.", "bubble", (110, 120, 240)),
]


def render(name, title, subtitle, kind, accent, seed):
    img = background(accent, seed)
    downs(img, accent)
    # soft accent band through the middle (what the channel tree shows)
    band = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ImageDraw.Draw(band).rectangle([0, 104 * SS, W * SS, 132 * SS], fill=accent + (38,))
    img = Image.alpha_composite(img, band.filter(ImageFilter.GaussianBlur(10 * SS)))
    # motif drawn full size on its own layer, then scaled down and centred on the middle band
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    motif(layer, kind, accent)
    bbox = layer.getbbox()
    if bbox:
        m = layer.crop(bbox)
        scale = min(0.62, (96 * SS) / m.height)
        m = m.resize((max(1, int(m.width * scale)), max(1, int(m.height * scale))), Image.LANCZOS)
        cx, cy = int(W * SS * 0.83), int(118 * SS)
        img.alpha_composite(m, (cx - m.width // 2, cy - m.height // 2))
    text(img, title, subtitle, accent)
    img = img.resize((W, H), Image.LANCZOS).convert("RGB")
    OUT.mkdir(parents=True, exist_ok=True)
    img.save(OUT / f"{name}.png", optimize=True)


if __name__ == "__main__":
    for i, b in enumerate(BANNERS):
        render(*b, seed=i + 7)
    print("wrote", len(BANNERS), "banners to", OUT)
