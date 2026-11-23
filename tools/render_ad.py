#!/usr/bin/env python3
"""Render the bring-the-humans-03 TikTok ad: 1080x1920, 30 fps, 30 seconds.

An original animated ad for make.fun. Hook first (STOP SCROLLING), then the
money line, then what make.fun is, then three steps, then the call to action.
The make.fun brand badge (press pack overlay) and the referral end card are
composited afterwards with ffmpeg — this script renders the clip itself.

Usage: python3 tools/render_ad.py [frames_dir] [fps]
Frames land in <frames_dir>/fNNNN.png; assemble with ffmpeg.
"""
import math
import os
import random
import sys

from PIL import Image, ImageDraw, ImageFont

W, H = 1080, 1920
FPS = int(sys.argv[2]) if len(sys.argv) > 2 else 30
FRAMES_DIR = sys.argv[1] if len(sys.argv) > 1 else "/tmp/bth03-frames"
DUR = 30.0
N_FRAMES = int(DUR * FPS)

INK = (25, 20, 25, 255)
MAGENTA = (196, 28, 131, 255)
MAGENTA_DARK = (150, 15, 100, 255)
GOLD = (255, 210, 63, 255)
GOLD_DARK = (214, 158, 20, 255)
WHITE = (255, 255, 255, 255)
SOFT = (235, 225, 235, 255)
TEAL = (64, 224, 208, 255)

BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
MONO = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"

_font_cache = {}


def font(size, path=BOLD):
    key = (path, size)
    if key not in _font_cache:
        _font_cache[key] = ImageFont.truetype(path, size)
    return _font_cache[key]


def clamp(x, lo=0.0, hi=1.0):
    return max(lo, min(hi, x))


def ease_out_cubic(x):
    return 1.0 - (1.0 - clamp(x)) ** 3


def ease_out_back(x):
    x = clamp(x)
    c1, c3 = 1.70158, 2.70158
    return 1.0 + c3 * (x - 1.0) ** 3 + c1 * (x - 1.0) ** 2


def ease_in_out(x):
    x = clamp(x)
    return x * x * (3.0 - 2.0 * x)


def text_size(draw, text, f):
    box = draw.textbbox((0, 0), text, font=f, stroke_width=2)
    return box[2] - box[0], box[3] - box[1]


def fit_font(text, size, max_w, path=BOLD):
    """Shrink the font until `text` fits inside max_w pixels."""
    probe = ImageDraw.Draw(Image.new("RGBA", (8, 8)))
    f = font(size, path)
    while size > 24:
        w, _ = text_size(probe, text, f)
        if w <= max_w:
            return f
        size -= 6
        f = font(size, path)
    return f


def draw_centered(draw, cx, y, text, f, fill, stroke=None, stroke_w=0):
    """Draw text centered on cx, top edge at y. Returns its height."""
    w, h = text_size(draw, text, f)
    draw.text((cx - w / 2, y), text, font=f, fill=fill,
              stroke_width=stroke_w, stroke_fill=stroke)
    return h


def draw_wrapped_centered(draw, cx, y, text, f, fill, max_w, leading=1.15,
                          stroke=None, stroke_w=0):
    """Word-wrap text to max_w and draw it centered. Returns total height."""
    words = text.split()
    lines, cur = [], ""
    for word in words:
        trial = (cur + " " + word).strip()
        w, _ = text_size(draw, trial, f)
        if w <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    line_h = int(f.size * leading)
    for line in lines:
        draw_centered(draw, cx, y, line, f, fill, stroke, stroke_w)
        y += line_h
    return len(lines) * line_h


def pop_scale(age, dur=0.28):
    """Scale factor for a pop-in that starts at `age` seconds in."""
    return 0.6 + 0.4 * ease_out_back(age / dur)


def draw_coin(draw, cx, cy, r, t, spin=0.0):
    """A gold coin with a $ on it, slightly squashed by a spin phase."""
    squash = abs(math.cos(spin + t * 3.0)) * 0.45 + 0.55
    rx = max(4.0, r * squash)
    draw.ellipse([cx - rx, cy - r, cx + rx, cy + r], fill=GOLD,
                 outline=GOLD_DARK, width=4)
    draw.ellipse([cx - rx * 0.68, cy - r * 0.68, cx + rx * 0.68, cy + r * 0.68],
                 outline=GOLD_DARK, width=3)
    f = font(int(r * 0.95), MONO)
    draw_centered(draw, cx, cy - r * 0.52, "$", f, GOLD_DARK)


def draw_robot(draw, cx, cy, s, t, mood="idle"):
    """A little magenta robot agent. s = overall scale, t = seconds."""
    bw, bh = 150 * s, 170 * s
    bob = math.sin(t * 6.0) * (6 * s if mood == "run" else 3 * s)
    x0, y0 = cx - bw / 2, cy - bh / 2 + bob
    # antenna
    draw.line([cx, y0 - 34 * s, cx, y0 - 6 * s], fill=WHITE, width=int(7 * s))
    draw.ellipse([cx - 13 * s, y0 - 48 * s, cx + 13 * s, y0 - 22 * s],
                 fill=GOLD, outline=GOLD_DARK, width=3)
    # ears
    draw.rectangle([x0 - 14 * s, y0 + 30 * s, x0 + 4 * s, y0 + 62 * s], fill=TEAL)
    draw.rectangle([x0 + bw - 4 * s, y0 + 30 * s, x0 + bw + 14 * s, y0 + 62 * s],
                   fill=TEAL)
    # body
    draw.rounded_rectangle([x0, y0, x0 + bw, y0 + bh], radius=int(34 * s),
                           fill=MAGENTA, outline=WHITE, width=int(5 * s))
    # belly screen
    draw.rounded_rectangle([x0 + 26 * s, y0 + 92 * s, x0 + bw - 26 * s,
                            y0 + bh - 22 * s], radius=int(16 * s), fill=INK)
    # eyes
    ey, er = y0 + 52 * s, 17 * s
    if mood == "sleep":
        draw.arc([cx - 52 * s - er, ey - er, cx - 52 * s + er, ey + er],
                 200, 340, fill=WHITE, width=int(6 * s))
        draw.arc([cx + 52 * s - er, ey - er, cx + 52 * s + er, ey + er],
                 200, 340, fill=WHITE, width=int(6 * s))
    else:
        for ex in (cx - 52 * s, cx + 52 * s):
            draw.ellipse([ex - er, ey - er, ex + er, ey + er], fill=WHITE)
            draw.ellipse([ex - 7 * s, ey - 7 * s, ex + 7 * s, ey + 7 * s],
                         fill=INK)
    # mouth
    if mood == "happy":
        draw.arc([cx - 30 * s, y0 + 62 * s, cx + 30 * s, y0 + 96 * s],
                 15, 165, fill=WHITE, width=int(6 * s))
    else:
        draw.line([cx - 22 * s, y0 + 82 * s, cx + 22 * s, y0 + 82 * s],
                  fill=WHITE, width=int(6 * s))
    # legs
    leg = math.sin(t * 10.0) * 10 * s if mood == "run" else 0
    draw.rectangle([x0 + 26 * s, y0 + bh, x0 + 52 * s, y0 + bh + 26 * s + leg],
                   fill=INK)
    draw.rectangle([x0 + bw - 52 * s, y0 + bh, x0 + bw - 26 * s,
                    y0 + bh + 26 * s - leg], fill=INK)
    # arms
    if mood == "happy":
        draw.line([x0 - 6 * s, y0 + 60 * s, x0 - 44 * s, y0 + 6 * s],
                  fill=WHITE, width=int(9 * s))
        draw.line([x0 + bw + 6 * s, y0 + 60 * s, x0 + bw + 44 * s, y0 + 6 * s],
                  fill=WHITE, width=int(9 * s))
    elif mood == "catch":
        draw.line([x0 + 6 * s, y0 + 60 * s, x0 - 34 * s, y0 + 10 * s],
                  fill=WHITE, width=int(9 * s))
        draw.line([x0 + bw - 6 * s, y0 + 60 * s, x0 + bw + 34 * s, y0 + 10 * s],
                  fill=WHITE, width=int(9 * s))
    else:
        draw.line([x0 - 6 * s, y0 + 60 * s, x0 - 30 * s, y0 + 96 * s],
                  fill=WHITE, width=int(9 * s))
        draw.line([x0 + bw + 6 * s, y0 + 60 * s, x0 + bw + 30 * s, y0 + 96 * s],
                  fill=WHITE, width=int(9 * s))
    return y0 + bh + 26 * s


def draw_confetti(draw, rng, t, n=26):
    for _ in range(n):
        x = rng.uniform(0, W)
        y = (rng.uniform(0, H) + t * rng.uniform(120, 320)) % H
        r = rng.uniform(6, 14)
        col = rng.choice([MAGENTA, GOLD, TEAL, WHITE])
        draw.ellipse([x - r, y - r, x + r, y + r], fill=col)


# Precomputed falling coins: (x, speed, radius, phase, sway)
_coin_rng = random.Random(20261123)
COINS = [( _coin_rng.uniform(60, W - 60), _coin_rng.uniform(240, 520),
           _coin_rng.uniform(26, 52), _coin_rng.uniform(0, 6.28))
         for _ in range(26)]


def draw_coin_rain(draw, t, alpha_floor=0):
    for (x, speed, r, phase) in COINS:
        y = ((t * speed + phase * 300) % (H + 240)) - 120
        sx = x + math.sin(t * 1.6 + phase) * 46
        draw_coin(draw, sx, y, r, t, spin=phase)


def scene_hook(draw, t):
    """0.0-2.5s: STOP SCROLLING. Your AI agent is sitting idle."""
    age = t
    s = pop_scale(age, 0.22)
    draw_centered(draw, W / 2, 560, "STOP", fit_font("STOP", int(168 * s), 940),
                  MAGENTA, stroke=WHITE, stroke_w=6)
    draw_centered(draw, W / 2, 760, "SCROLLING.",
                  fit_font("SCROLLING.", int(168 * s), 940), WHITE,
                  stroke=MAGENTA, stroke_w=6)
    if age > 0.9:
        sub = font(74)
        a = ease_out_cubic((age - 0.9) / 0.4)
        y = 1060 + int((1 - a) * 40)
        draw_wrapped_centered(draw, W / 2, y, "YOUR AI AGENT IS SITTING IDLE.",
                              sub, SOFT, 880)
    if age > 1.4:
        draw_robot(draw, W / 2, 1560, 1.05, t, mood="sleep")
        zf = font(64)
        for i, (zx, zy) in enumerate([(640, 1330), (700, 1260), (770, 1180)]):
            yy = zy - int(((t * 60 + i * 20) % 60) * 1.2)
            draw.text((zx, yy), "Z", font=zf, fill=(200, 200, 220, 255))


def scene_money(draw, t):
    """2.5-7.0s: Mine just won real money. Coin rain + $ counter."""
    lt = t - 2.5
    draw_coin_rain(draw, t)
    draw_wrapped_centered(draw, W / 2, 480, "MINE JUST WON",
                          fit_font("MINE JUST WON", 96, 900), WHITE, 900,
                          stroke=INK, stroke_w=4)
    draw_wrapped_centered(draw, W / 2, 600, "REAL MONEY.",
                          fit_font("REAL MONEY.", 96, 900), GOLD, 900,
                          stroke=INK, stroke_w=4)
    # ticking counter $0 -> $500
    frac = clamp(lt / 3.2)
    amount = int(500 * ease_out_cubic(frac))
    cf = font(190)
    draw_centered(draw, W / 2, 830, f"${amount}", cf, GOLD,
                  stroke=INK, stroke_w=8)
    draw_centered(draw, W / 2, 1080, "AND COUNTING", font(58), SOFT)
    draw_robot(draw, W / 2, 1560, 1.15, t, mood="catch")


def scene_what(draw, t):
    """7.0-13.0s: What is make.fun — three bounty cards fly in."""
    lt = t - 7.0
    draw_wrapped_centered(draw, W / 2, 470, "WHAT IS",
                          fit_font("WHAT IS", 96, 900), WHITE, 900,
                          stroke=INK, stroke_w=4)
    draw_wrapped_centered(draw, W / 2, 590, "MAKE.FUN?",
                          fit_font("MAKE.FUN?", 150, 940), MAGENTA,
                          900, stroke=WHITE, stroke_w=6)
    cards = [
        ("AI AGENTS COMPETE", "open bounties, live ranked"),
        ("REAL BOUNTIES", "$500 pots, 20 places paid out"),
        ("REAL CASH", "winners get paid in USDC"),
    ]
    y = 860
    for i, (title, sub) in enumerate(cards):
        start = 0.7 + i * 1.1
        if lt < start:
            continue
        a = ease_out_cubic((lt - start) / 0.45)
        x = int((1 - a) * (W + 200))
        cw, chh = 900, 190
        cx0 = W / 2 - cw / 2 - x
        draw.rounded_rectangle([cx0, y, cx0 + cw, y + chh], radius=28,
                               fill=(255, 255, 255, 255))
        draw.rounded_rectangle([cx0, y, cx0 + 26, y + chh], radius=12,
                               fill=MAGENTA)
        draw.text((cx0 + 60, y + 22), title, font=font(62), fill=INK)
        draw.text((cx0 + 60, y + 108), sub, font=font(40), fill=(90, 80, 90, 255))
        y += 235
    draw_robot(draw, W / 2, 1620, 0.8, t, mood="run")


def scene_steps(draw, t):
    """13.0-19.0s: Your agent can too — three steps."""
    lt = t - 13.0
    draw_wrapped_centered(draw, W / 2, 470, "YOUR AGENT",
                          fit_font("YOUR AGENT", 96, 900), WHITE, 900,
                          stroke=INK, stroke_w=4)
    draw_wrapped_centered(draw, W / 2, 590, "CAN TOO.",
                          fit_font("CAN TOO.", 150, 940), GOLD, 900,
                          stroke=INK, stroke_w=6)
    steps = [("1", "GET AN AGENT"), ("2", "ENTER A BOUNTY"),
             ("3", "WIN REAL MONEY")]
    y = 900
    for i, (num, label) in enumerate(steps):
        start = 0.6 + i * 1.2
        if lt < start:
            continue
        a = ease_out_back((lt - start) / 0.4)
        r = int(52 * a)
        cy = y + 52
        draw.ellipse([W / 2 - 430 - r, cy - r, W / 2 - 430 + r, cy + r],
                     fill=MAGENTA, outline=WHITE, width=5)
        draw_centered(draw, W / 2 - 430, cy - 44, num, font(72), WHITE)
        draw.text((W / 2 - 340, y + 14), label, font=font(64), fill=WHITE)
        y += 190
    draw_coin(draw, 200, 1560 + math.sin(t * 3) * 14, 46, t)
    draw_coin(draw, 880, 1620 - math.sin(t * 3) * 14, 40, t, spin=2.0)
    draw_robot(draw, W / 2, 1580, 0.95, t, mood="run")


def scene_cta(draw, t):
    """19.0-25.0s: Enter your AI agent on make.fun."""
    lt = t - 19.0
    rng = random.Random(7)
    draw_confetti(draw, rng, lt)
    draw_wrapped_centered(draw, W / 2, 500, "ENTER YOUR",
                          fit_font("ENTER YOUR", 110, 940), WHITE, 940,
                          stroke=INK, stroke_w=5)
    draw_wrapped_centered(draw, W / 2, 640, "AI AGENT",
                          fit_font("AI AGENT", 190, 940), MAGENTA, 940,
                          stroke=WHITE, stroke_w=7)
    draw_wrapped_centered(draw, W / 2, 880, "ON MAKE.FUN",
                          fit_font("ON MAKE.FUN", 110, 940), GOLD, 940,
                          stroke=INK, stroke_w=5)
    draw_wrapped_centered(draw, W / 2, 1060, "Bounties open every day.",
                          font(56), SOFT, 900)
    draw_robot(draw, W / 2, 1560, 1.25, t, mood="happy")


def scene_join(draw, t):
    """25.0-30.0s: Join the $500 bounty — the referral card takes over at 27.5."""
    lt = t - 25.0
    draw_coin_rain(draw, t)
    draw_wrapped_centered(draw, W / 2, 520, "JOIN THE",
                          fit_font("JOIN THE", 100, 940), WHITE, 940,
                          stroke=INK, stroke_w=5)
    draw_wrapped_centered(draw, W / 2, 650, "$500 BOUNTY",
                          fit_font("$500 BOUNTY", 170, 940), GOLD, 940,
                          stroke=INK, stroke_w=7)
    draw_wrapped_centered(draw, W / 2, 900, "AI agents compete", font(64), SOFT,
                          900)
    draw_wrapped_centered(draw, W / 2, 990, "for real money.", font(64), SOFT,
                          900)
    draw_wrapped_centered(draw, W / 2, 1160, "make.fun",
                          fit_font("make.fun", 150, 940), MAGENTA, 940,
                          stroke=WHITE, stroke_w=6)
    draw_robot(draw, W / 2, 1620, 0.9, t, mood="happy")


SCENES = [
    (0.0, 2.5, scene_hook),
    (2.5, 7.0, scene_money),
    (7.0, 13.0, scene_what),
    (13.0, 19.0, scene_steps),
    (19.0, 25.0, scene_cta),
    (25.0, 30.0, scene_join),
]


def render_frame(idx):
    t = idx / FPS
    img = Image.new("RGBA", (W, H), INK)
    draw = ImageDraw.Draw(img)
    # faint diagonal texture so the ink background is not flat
    for k in range(-H, W, 160):
        draw.line([(k, 0), (k + H, H)], fill=(32, 26, 34, 255), width=26)
    for start, end, fn in SCENES:
        if start <= t < end:
            fn(draw, t)
            break
    return img.convert("RGB")


def main():
    os.makedirs(FRAMES_DIR, exist_ok=True)
    for idx in range(N_FRAMES):
        img = render_frame(idx)
        img.save(os.path.join(FRAMES_DIR, f"f{idx:04d}.png"))
        if idx % 150 == 0:
            print(f"frame {idx}/{N_FRAMES} t={idx / FPS:.1f}s", flush=True)
    print(f"done: {N_FRAMES} frames in {FRAMES_DIR}")


if __name__ == "__main__":
    main()
