#!/usr/bin/env python3
"""Generate raster assets for the Byte TSC landing page.

Run:    python3 scripts/make_raster_assets.py
Needs:  Pillow (pip install pillow)

Outputs:
  assets/favicon-16.png       16x16 favicon (simplified 3-bar mark)
  assets/favicon-32.png       32x32 favicon
  assets/apple-touch-icon.png  180x180 touch icon
  assets/img/og-share.png      1200x630 social share image (language-neutral)
  assets/img/og-share.webp     same image in WebP
"""

import os

from PIL import Image, ImageDraw, ImageFont

NAVY = (16, 48, 92)        # #10305c
NAVY_DEEP = (10, 27, 46)   # #0a1b2e
ICE = (232, 240, 248)      # #e8f0f8
AMBER = (232, 145, 45)     # #e8912d
PAPER = (247, 248, 250)    # #f7f8fa
INK = (16, 26, 38)         # #101a26

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def find_font(size):
    for path in (
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/TTF/DejaVuSans-Bold.ttf",
    ):
        if os.path.exists(path):
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def rounded(draw, box, radius, fill):
    draw.rounded_rectangle(box, radius=radius, fill=fill)


def draw_mark(size, base_color, bar_color, accent_color):
    """Byte TSC symbol: rounded square + 8 vertical bars (a 'byte' as a waveform)."""
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    s = size / 64.0
    rounded(d, (0, 0, size, size), int(14 * s), base_color)
    heights = [8, 14, 22, 30, 22, 14, 18, 10]
    xs = [10, 17, 24, 31, 38, 45, 52, 58.5]
    for i, (x, h) in enumerate(zip(xs, heights)):
        col = accent_color if x * s > 42 * s else bar_color
        bx = x * s
        bw = max(2.0, 4 * s)
        by1 = (32 - h / 2) * s
        by2 = (32 + h / 2) * s
        rounded(d, (bx, by1, bx + bw, by2), int(1.6 * s), col)
    return img


def rounded_px(img, box, radius, fill):
    d = ImageDraw.Draw(img)
    d.rounded_rectangle(box, radius=radius, fill=fill)


def og_share():
    w, h = 1200, 630
    img = Image.new("RGB", (w, h), NAVY_DEEP)
    d = ImageDraw.Draw(img)

    # vertical gradient
    for y in range(h):
        t = y / h
        r = int(NAVY_DEEP[0] + (NAVY[0] - NAVY_DEEP[0]) * t)
        g = int(NAVY_DEEP[1] + (NAVY[1] - NAVY_DEEP[1]) * t)
        b = int(NAVY_DEEP[2] + (NAVY[2] - NAVY_DEEP[2]) * t)
        d.line([(0, y), (w, y)], fill=(r, g, b))

    # subtle broadcast arcs
    for i, (r, alpha) in enumerate([(90, 26), (130, 20), (170, 14), (210, 10)]):
        arc_col = (ICE[0], ICE[1], ICE[2])
        d.arc([850 - r, 315 - r, 850 + r, 315 + r], 200, 340, fill=arc_col, width=3)

    # amber baseline
    d.rectangle([0, h - 10, w, h], fill=AMBER)

    # device silhouette (right)
    dx0, dy0, dx1, dy1 = 795, 215, 955, 385
    rounded_px(img, (dx0, dy0, dx1, dy1), 24, ICE)
    sx0, sy0, sx1, sy1 = 811, 231, 939, 315
    rounded_px(img, (sx0, sy0, sx1, sy1), 10, (18, 56, 110))
    # waveform bars on screen
    bar_h = [12, 22, 20, 28, 42, 20, 32, 12, 22, 18, 24, 18]
    bx = 823
    for bh in bar_h:
        rounded_px(img, (bx, 273 - bh / 2, bx + 7, 273 + bh / 2), 3, ICE)
        bx += 10
    d.rectangle([823, 297, 927, 299], fill=AMBER)
    # speaker dots + LED
    for i, cx in enumerate((823, 851, 879, 907)):
        d.ellipse([cx, 343, cx + 14, 357], fill=(184, 196, 214))
    d.ellipse([895, 200, 909, 214], fill=AMBER)

    # Byte TSC mark (left)
    mark = draw_mark(112, ICE, NAVY_DEEP, AMBER)  # dark mark on dark bg? use ICE base
    img.paste(mark, (96, 92), mark)

    # wordmark: BYTE TSC
    f_big = find_font(64)
    d.text((232, 112), "BYTE TSC", font=f_big, fill=ICE)
    f_small = find_font(30)
    d.text((234, 192), "Quake Byte TSC", font=f_small, fill=(160, 180, 205))
    f_tag = find_font(26)
    d.text((97, 508), "ja · en · pt", font=f_tag, fill=(160, 180, 205))

    img.save(os.path.join(ROOT, "assets", "img", "og-share.png"), optimize=True)
    img.save(os.path.join(ROOT, "assets", "img", "og-share.webp"), "WEBP", quality=90)


def favicon(size):
    s = size / 64.0
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([0, 0, size - 1, size - 1], radius=int(14 * s), fill=NAVY)
    # three bold bars, readable at 16px
    bars = [(22, 10), (31, 14), (40, 8)]  # (x, h)
    for x, bh in bars:
        bx = x * s
        bw = 10 * s
        d.rounded_rectangle(
            [bx, (32 - bh / 2) * s, bx + bw, (32 + bh / 2) * s],
            radius=int(3 * s),
            fill=ICE,
        )
    d.rounded_rectangle(
        [40 * s, 26 * s, 40 * s + 10 * s, 38 * s], radius=int(3 * s), fill=AMBER
    )
    return img


def touch_icon():
    size = 180
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    s = size / 64.0
    d.rounded_rectangle([0, 0, size - 1, size - 1], radius=int(14 * s), fill=NAVY)
    heights = [8, 14, 22, 30, 22, 14, 18, 10]
    xs = [10, 17, 24, 31, 38, 45, 52, 58.5]
    for x, h in zip(xs, heights):
        col = AMBER if x > 42 else ICE
        bx = x * s
        d.rounded_rectangle(
            [bx, (32 - h / 2) * s, bx + 4 * s, (32 + h / 2) * s],
            radius=int(1.6 * s),
            fill=col,
        )
    return img


def main():
    os.makedirs(os.path.join(ROOT, "assets", "img"), exist_ok=True)
    og_share()
    favicon(16).save(os.path.join(ROOT, "assets", "favicon-16.png"), optimize=True)
    favicon(32).save(os.path.join(ROOT, "assets", "favicon-32.png"), optimize=True)
    touch_icon().save(
        os.path.join(ROOT, "assets", "apple-touch-icon.png"), optimize=True
    )
    print("done:", ROOT + "/assets")


if __name__ == "__main__":
    main()