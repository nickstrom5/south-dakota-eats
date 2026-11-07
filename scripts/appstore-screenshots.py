#!/usr/bin/env python3
"""Build the captioned App Store screenshots from simulator captures (the family's frame, from chi-eats/ios/scripts/appstore-screenshots.py,
by way of mi-eats).

Usage (from sd-eats/): .venv/bin/python scripts/appstore-screenshots.py
Reads playbook/app-store/raw/iphone/*.png (1320x2868, iPhone 17 Pro Max) and playbook/app-store/raw/ipad/*.png (2064x2752, iPad Pro 13"),
made with: OUT=$PWD/playbook/app-store/raw/<iphone|ipad> SLEEP=14 bash scripts/capture-screenshots.sh <udid> <screens>
(the map needs about 20 s on a busy Mac). Writes playbook/app-store/iphone/NN-name.png and .../ipad/NN-name.png at the same sizes.
Each frame: cream behind, a Black Hills pine caption band with white condensed type and a short sun-gold rule (the provisional palette,
as in the app's header), and the real capture below in a rounded frame.
Rules (STATE_EATS_PLAYBOOK.md "Screenshots"): real captures, home screen first, no negative board in any image, map zoomed in to
individual pins; captions make no price claim ("free"), use no third-party marks (say "award winners", not MICHELIN or James Beard)
and no "best".
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
LAKE, SAND, BG, WHITE, INK = (30, 77, 59), (242, 181, 28), (246, 240, 228), (255, 255, 255), (26, 26, 26)   # pine band, sun-gold rule, cream
FONT = "/System/Library/Fonts/Avenir Next Condensed.ttc"   # Heavy face; the app itself uses the system compressed face

IPHONE = [("01-home", "home.png", "South Dakota's food, list by list"),
          ("02-chislic", "chislic.png", "Chislic, checked by hand"),
          ("03-detail", "detail.png", "Guide places, checked by hand"),
          ("04-bison", "bison.png", "Bison and walleye in Rapid City"),
          ("05-map", "map.png", "The map, guide by guide"),
          ("06-honors", "honors.png", "Award winners and semifinalists"),
          ("07-saved", "saved.png", "Save places for the next trip")]
IPAD = [("01-home", "home.png", "South Dakota's food, list by list"),
        ("02-chislic", "chislic.png", "Chislic, checked by hand"),
        ("03-bison", "bison.png", "Bison and walleye in Rapid City"),
        ("04-map", "map.png", "The map, guide by guide"),
        ("05-honors", "honors.png", "Award winners and semifinalists")]
BANNED = ("free", "best", "#1", "top ", "james beard", "michelin", "every")   # "every place" overclaimed: only guide places are hand-checked   # price claims, rankings and others' marks stay out of captions
for _, _, cap in IPHONE + IPAD:
    assert not any(b in cap.lower() for b in BANNED), cap


def font(size):
    for index in (8, 0):                # Heavy, else Bold (upright faces of Avenir Next Condensed)
        try:
            return ImageFont.truetype(FONT, size, index=index)
        except OSError:
            continue
    return ImageFont.load_default()


def fit_lines(d, text, f, width):
    words, lines, cur = text.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if d.textlength(t, font=f) <= width or not cur:
            cur = t
        else:
            lines.append(cur); cur = w
    return lines + [cur]


def frame(src, out, caption, W, H, band, fsize, radius):
    shot = Image.open(src).convert("RGB")
    assert shot.size == (W, H), f"{src}: {shot.size}, expected {(W, H)}"
    canvas = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(canvas)
    d.rectangle([0, 0, W, band], fill=LAKE)
    f = font(fsize)
    lines = fit_lines(d, caption.upper(), f, W * 0.86)
    lh = int(fsize * 1.05)
    y = (band - lh * len(lines)) // 2 - int(fsize * 0.08)
    for line in lines:
        w = d.textlength(line, font=f)
        d.text(((W - w) / 2, y), line, font=f, fill=WHITE)
        y += lh
    d.rectangle([(W - 160) // 2, band - 34, (W + 160) // 2, band - 24], fill=SAND)
    top = band + int(H * 0.035)
    scale = min((H - top - int(H * 0.03)) / shot.height, (W * 0.9) / shot.width)
    sw, sh = int(shot.width * scale), int(shot.height * scale)
    x = (W - sw) // 2
    pad = int(W * 0.012)
    d.rounded_rectangle([x - pad, top - pad, x + sw + pad, top + sh + pad], radius=radius + pad, fill=INK)
    shot = shot.resize((sw, sh), Image.LANCZOS)
    mask = Image.new("L", (sw, sh), 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, sw - 1, sh - 1], radius=radius, fill=255)
    canvas.paste(shot, (x, top), mask)
    out.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(out, optimize=True)
    print("wrote", out.relative_to(ROOT))


for d_ in ("iphone", "ipad"):   # a renamed or dropped shot must not linger in the upload folder
    for old in (ROOT / "playbook/app-store" / d_).glob("*.png"):
        old.unlink()
for name, cap, caption in IPHONE:
    frame(ROOT / "playbook/app-store/raw/iphone" / cap, ROOT / "playbook/app-store/iphone" / f"{name}.png", caption, 1320, 2868, 520, 118, 96)
for name, cap, caption in IPAD:
    frame(ROOT / "playbook/app-store/raw/ipad" / cap, ROOT / "playbook/app-store/ipad" / f"{name}.png", caption, 2064, 2752, 420, 120, 60)
