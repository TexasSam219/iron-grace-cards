# -*- coding: utf-8 -*-
"""
Iron & Grace - 9:16 declaration card renderer.

Matches the existing navy carousel card (sampled from IronAndGrace_Day31_Card1.png):
  background  #1E2D4A with a soft radial lift toward #21304C
  headline    Lora Bold, warm cream #EDE9E1
  kicker      Poppins Medium, letterspaced caps, steel #7A9AB8
  handle      Poppins Medium, letterspaced caps, faded #4A6A88

Output: 1080x1920 PNG, safe for Instagram Stories and Reels.
"""

import os
import math
from PIL import Image, ImageDraw, ImageFont, ImageFilter

# ---------------------------------------------------------------- brand spec

W, H = 1080, 1920

BG_BASE  = (30, 45, 74)     # #1E2D4A
BG_LIFT  = (38, 56, 90)     # glow center, slightly brighter than the base
CREAM    = (237, 233, 225)  # #EDE9E1
STEEL    = (122, 154, 184)  # #7A9AB8
FADED    = (74, 106, 136)   # #4A6A88

FONT_DIR = "/usr/share/fonts/truetype/google-fonts"
LORA     = os.path.join(FONT_DIR, "Lora-Variable.ttf")
POPPINS  = os.path.join(FONT_DIR, "Poppins-Medium.ttf")

# Confirmed against instagram.com/7ironandgrace/ - no underscores.
HANDLE = "@7IRONANDGRACE"

# Instagram overlays UI on the top ~250px and bottom ~350px of a 1920 frame.
SAFE_TOP    = 260
SAFE_BOTTOM = 1560

KICKER_Y  = 300
HANDLE_Y  = 1500
SIDE_PAD  = 110          # text never comes closer than this to either edge

HEADLINE_MAX   = 108     # starting size; shrinks to fit
HEADLINE_MIN   = 62
HEADLINE_LEAD  = 1.22    # line height multiplier


def lora_bold(size):
    f = ImageFont.truetype(LORA, size)
    try:
        f.set_variation_by_axes([700])
    except Exception:
        pass
    return f


def poppins(size):
    return ImageFont.truetype(POPPINS, size)


# ---------------------------------------------------------------- background

def make_background():
    """Navy field with an off-center radial glow, matching the source card."""
    bg = Image.new("RGB", (W, H), BG_BASE)

    # Build the glow small, then blur and upscale - fast and smooth.
    small_w, small_h = 108, 192
    glow = Image.new("L", (small_w, small_h), 0)
    gx, gy = small_w * 0.5, small_h * 0.42   # glow sits slightly above center
    radius = small_w * 0.85
    px = glow.load()
    for y in range(small_h):
        for x in range(small_w):
            d = math.hypot(x - gx, y - gy) / radius
            v = max(0.0, 1.0 - d)
            px[x, y] = int((v ** 2) * 255)
    glow = glow.filter(ImageFilter.GaussianBlur(12)).resize((W, H), Image.LANCZOS)

    lift = Image.new("RGB", (W, H), BG_LIFT)
    return Image.composite(lift, bg, glow)


# ---------------------------------------------------------------- text utils

def tracked_text(draw, text, font, fill, y, tracking):
    """Draw letterspaced caps, centered horizontally."""
    widths = [draw.textlength(ch, font=font) for ch in text]
    total = sum(widths) + tracking * (len(text) - 1)
    x = (W - total) / 2
    for ch, w in zip(text, widths):
        draw.text((x, y), ch, font=font, fill=fill)
        x += w + tracking


def wrap(draw, text, font, max_width):
    words, lines, cur = text.split(), [], ""
    for word in words:
        trial = (cur + " " + word).strip()
        if draw.textlength(trial, font=font) <= max_width or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def fit_headline(draw, text, max_width, max_height):
    """Shrink until the wrapped block fits the available box."""
    for size in range(HEADLINE_MAX, HEADLINE_MIN - 1, -2):
        font = lora_bold(size)
        lines = wrap(draw, text, font, max_width)
        block = len(lines) * size * HEADLINE_LEAD
        if block <= max_height and len(lines) <= 5:
            return font, lines, size
    font = lora_bold(HEADLINE_MIN)
    return font, wrap(draw, text, font, max_width), HEADLINE_MIN


# ---------------------------------------------------------------- the card

def render(declaration, day, theme, out_path):
    img = make_background()
    d = ImageDraw.Draw(img)

    # kicker - DAY 31 | MARRIAGE & INTIMACY
    kf = poppins(26)
    tracked_text(d, f"DAY {day}  |  {theme.upper()}", kf, STEEL, KICKER_Y, 6.5)

    # headline - centered in the space between kicker and handle
    box_top    = KICKER_Y + 160
    box_bottom = HANDLE_Y - 140
    max_width  = W - (SIDE_PAD * 2)

    font, lines, size = fit_headline(d, declaration, max_width, box_bottom - box_top)
    line_h = size * HEADLINE_LEAD
    block_h = len(lines) * line_h
    y = box_top + (box_bottom - box_top - block_h) / 2

    for line in lines:
        lw = d.textlength(line, font=font)
        d.text(((W - lw) / 2, y), line, font=font, fill=CREAM)
        y += line_h

    # handle
    hf = poppins(21)
    tracked_text(d, HANDLE, hf, FADED, HANDLE_Y, 7.0)

    img.save(out_path, "PNG")
    return out_path


if __name__ == "__main__":
    render("This covenant stands.", 32, "Marriage & Intimacy", "preview.png")
    print("wrote preview.png")
