from PIL import Image, ImageDraw, ImageFont, ImageFilter
from pathlib import Path
import math

W, H, FRAMES = 1100, 620, 32
out = Path("assets/project-flow.gif")
base = (12, 18, 31)
panel = (23, 34, 54)
white = (242, 247, 255)
muted = (162, 180, 205)
cyan = (65, 211, 255)
green = (91, 226, 170)
orange = (255, 173, 92)
purple = (183, 151, 255)
coral = (255, 113, 103)
blue = (105, 165, 255)

fontfile = "C:/Windows/Fonts/seguisb.ttf"
if not Path(fontfile).exists():
    fontfile = "C:/Windows/Fonts/arialbd.ttf"
font = ImageFont.truetype(fontfile, 15)
small = ImageFont.truetype(fontfile, 11)
title = ImageFont.truetype(fontfile, 25)
bodyfile = "C:/Windows/Fonts/segoeui.ttf"
if not Path(bodyfile).exists():
    bodyfile = "C:/Windows/Fonts/arial.ttf"
body = ImageFont.truetype(bodyfile, 12)

lanes = [
    ("NEON CDC  /  OPERATIONAL DATA TO BRONZE", [
        (34, 176, 274, 246, "NEON RAW + AGENTIC DB", "Walmart tables + SQL chat", green),
        (300, 176, 540, 246, "AIRFLOW PYTHON TASK", "ingest_cdc()", cyan),
        (566, 176, 806, 246, "DATABRICKS JOB", "ingest_walmart", coral),
        (832, 176, 1066, 246, "BRONZE TABLES", "Databricks Delta", blue),
    ]),
    ("S3 REVIEWS  /  EXTERNAL LOCATION TO GOLD", [
        (34, 320, 274, 390, "S3 reviews.csv", "Amazon S3", orange),
        (300, 320, 540, 390, "UNITY CATALOG", "external location", purple),
        (566, 320, 806, 390, "REVIEWS PIPELINE", "started by Airflow Python", coral),
        (832, 320, 1066, 390, "GOLD REVIEWS", "st-walmart.gold.reviews", green),
    ]),
    ("DBT  /  AFTER BOTH AIRFLOW TASKS SUCCEED", [
        (86, 463, 306, 525, "SOURCE FRESHNESS", "dbt checks", cyan),
        (342, 463, 562, 525, "SILVER MODELS", "technical + business", blue),
        (598, 463, 818, 525, "QUALITY CHECKS", "tests + snapshots", orange),
        (854, 463, 1074, 525, "GOLD MODELS", "analytics tables", purple),
    ]),
]

def center(node):
    return ((node[0] + node[2]) // 2, (node[1] + node[3]) // 2)

def make_frame(index):
    im = Image.new("RGB", (W, H))
    px = im.load()
    for y in range(H):
        t = y / H
        c = tuple(round(base[k] * (1-t) + (21, 32, 52)[k] * t) for k in range(3))
        for x in range(W):
            px[x, y] = c
    haze = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    hd = ImageDraw.Draw(haze)
    hd.ellipse((820, -150, 1260, 230), fill=(117, 91, 255, 28))
    hd.ellipse((-220, 350, 350, 730), fill=(40, 191, 255, 20))
    haze = haze.filter(ImageFilter.GaussianBlur(75))
    im = Image.alpha_composite(im.convert("RGBA"), haze).convert("RGB")
    d = ImageDraw.Draw(im)
    d.text((38, 20), "Walmart Data Engineering", font=title, fill=white)
    d.text((40, 55), "Two ingestion paths. One Python-orchestrated analytics workflow.", font=body, fill=muted)

    # Airflow control ribbon
    d.rounded_rectangle((30, 86, 1070, 143), radius=16, fill=(25, 39, 62), outline=(62, 88, 123), width=1)
    d.ellipse((48, 99, 78, 129), fill=(54, 84, 127))
    d.text((57, 104), "A", font=small, fill=white)
    d.text((92, 96), "AIRFLOW DAG", font=small, fill=cyan)
    d.text((92, 116), "Manual trigger  •  ingest_cdc() + run_reviews_pipeline() in parallel  •  then dbt", font=body, fill=white)

    active_colors = [cyan, orange, purple]
    for lane_idx, (label, nodes) in enumerate(lanes):
        y1, y2 = nodes[0][1] - 31, nodes[0][3] + 12
        d.rounded_rectangle((22, y1, 1078, y2), radius=17, fill=(16, 25, 41), outline=(44, 62, 87), width=1)
        d.text((38, y1 + 7), label, font=small, fill=muted)
        pts = [center(n) for n in nodes]
        for j in range(len(nodes) - 1):
            y = pts[j][1]
            x0, x1 = nodes[j][2] + 6, nodes[j + 1][0] - 10
            d.line((x0, y, x1, y), fill=(77, 98, 129), width=3)
            d.polygon([(x1-8, y-5), (x1, y), (x1-8, y+5)], fill=(130, 155, 191))
        for x0, y0, x1, y1, heading, caption, accent in nodes:
            d.rounded_rectangle((x0+3, y0+5, x1+3, y1+5), radius=13, fill=(6, 11, 20))
            d.rounded_rectangle((x0, y0, x1, y1), radius=13, fill=panel, outline=accent, width=2)
            d.rounded_rectangle((x0+2, y0+2, x1-2, y0+7), radius=4, fill=accent)
            bb = d.textbbox((0, 0), heading, font=font)
            d.text((x0+(x1-x0-(bb[2]-bb[0]))/2, y0+20), heading, font=font, fill=white)
            bb = d.textbbox((0, 0), caption, font=body)
            d.text((x0+(x1-x0-(bb[2]-bb[0]))/2, y0+46), caption, font=body, fill=muted)
        prog = ((index / FRAMES) + lane_idx * 0.29) % 1
        p = prog * (len(pts)-1)
        seg = min(int(p), len(pts)-2)
        frac = p - seg
        x = int(pts[seg][0] + (pts[seg+1][0]-pts[seg][0])*frac)
        y = pts[seg][1]
        col = active_colors[lane_idx]
        d.ellipse((x-13, y-13, x+13, y+13), fill=(37, 75, 105))
        d.ellipse((x-7, y-7, x+7, y+7), fill=col)
        d.ellipse((x-3, y-3, x+3, y+3), fill=white)

    d.text((39, 568), "TECH STACK", font=small, fill=muted)
    badges = [("Neon", green), ("Neon MCP", purple), ("Python", cyan), ("Amazon S3", orange),
              ("Databricks", coral), ("Airflow SDK", blue), ("dbt", orange), ("Docker", cyan), ("uv", purple)]
    x = 132
    for label, accent in badges:
        bb = d.textbbox((0, 0), label, font=small)
        width = bb[2] - bb[0] + 29
        d.rounded_rectangle((x, 558, x+width, 586), radius=13, fill=(25, 38, 59), outline=accent, width=1)
        d.ellipse((x+9, 568, x+17, 576), fill=accent)
        d.text((x+23, 564), label, font=small, fill=white)
        x += width + 8
    return im

frames = [make_frame(i) for i in range(FRAMES)]
# Quantize all frames against one shared palette for a compact, smooth GitHub asset.
palette_sheet = Image.new("RGB", (440, 248))
for i in range(8):
    thumb = frames[i * 4].resize((220, 124), Image.Resampling.LANCZOS)
    palette_sheet.paste(thumb, ((i % 2) * 220, (i // 2) * 62))
palette = palette_sheet.quantize(colors=128, method=Image.Quantize.MEDIANCUT)
frames = [frame.quantize(palette=palette, dither=Image.Dither.NONE) for frame in frames]
frames[0].save(out, save_all=True, append_images=frames[1:], duration=110, loop=0, optimize=True)
print(f"Created {out}: {len(frames)} frames, {out.stat().st_size:,} bytes")

