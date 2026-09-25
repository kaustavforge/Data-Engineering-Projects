from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter

WIDTH, HEIGHT = 1200, 260
FRAMES = 40
OUTPUT = Path(__file__).with_name("walmart-project-title.gif")
font_path = "C:/Windows/Fonts/seguisb.ttf"
if not Path(font_path).exists():
    font_path = "C:/Windows/Fonts/arialbd.ttf"
title_font = ImageFont.truetype(font_path, 66)
sub_font = ImageFont.truetype(font_path, 15)

navy = (10, 17, 32)
teal = (53, 222, 235)
blue = (100, 150, 255)
white = (245, 249, 255)

def render(frame_index):
    base = Image.new("RGB", (WIDTH, HEIGHT))
    pix = base.load()
    for y in range(HEIGHT):
        for x in range(WIDTH):
            glow = max(0.0, 1 - abs(x - WIDTH * 0.54) / (WIDTH * 0.72))
            pix[x, y] = (
                int(navy[0] + 8 * glow),
                int(navy[1] + 15 * glow),
                int(navy[2] + 31 * glow),
            )

    haze = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    hd = ImageDraw.Draw(haze)
    hd.ellipse((120, -220, 580, 280), fill=(45, 210, 235, 22))
    hd.ellipse((760, -170, 1270, 300), fill=(102, 120, 255, 25))
    haze = haze.filter(ImageFilter.GaussianBlur(65))
    base = Image.alpha_composite(base.convert("RGBA"), haze).convert("RGB")

    # Type the heading on, then hold it while the accent light sweeps below.
    visible = min(len("WALMART PROJECT"), max(1, frame_index // 2 + 1))
    title_text = "WALMART PROJECT"[:visible]
    d = ImageDraw.Draw(base)
    box = d.textbbox((0, 0), title_text, font=title_font)
    text_width = box[2] - box[0]
    x = (WIDTH - text_width) // 2
    y = 62

    mask = Image.new("L", (WIDTH, HEIGHT), 0)
    md = ImageDraw.Draw(mask)
    md.text((x, y), title_text, font=title_font, fill=255)
    gradient = Image.new("RGB", (WIDTH, HEIGHT), navy)
    gp = gradient.load()
    for gx in range(WIDTH):
        t = gx / (WIDTH - 1)
        color = tuple(int(teal[k] * (1 - t) + blue[k] * t) for k in range(3))
        for gy in range(HEIGHT):
            gp[gx, gy] = color
    base.paste(gradient, (0, 0), mask)

    if visible == len("WALMART PROJECT"):
        pulse = 0.5 + 0.5 * __import__("math").sin(frame_index * 0.28)
        line_width = int(280 + 570 * min(1, max(0, (frame_index - 26) / 6)))
        center = WIDTH // 2
        d = ImageDraw.Draw(base)
        d.rounded_rectangle((center-line_width//2, 158, center+line_width//2, 162), radius=2,
                            fill=(int(45+50*pulse), int(190+40*pulse), 255))
        d.text((0, 183), "DATA ENGINEERING  •  LAKEHOUSE  •  ORCHESTRATION",
               font=sub_font, fill=(192, 208, 231), anchor="mt")
        dot_x = 600 - line_width//2 + int(((frame_index - 26) % 12) / 11 * line_width)
        d.ellipse((dot_x-5, 153, dot_x+5, 167), fill=white)

    return base

frames = [render(i) for i in range(FRAMES)]
# A shared palette keeps the looping banner small for a repository README.
palette_source = Image.new("RGB", (600, 130))
palette_source.paste(frames[0].resize((300, 130)), (0, 0))
palette_source.paste(frames[-1].resize((300, 130)), (300, 0))
palette = palette_source.quantize(colors=128)
indexed = [frame.quantize(palette=palette, dither=Image.Dither.NONE) for frame in frames]
indexed[0].save(OUTPUT, save_all=True, append_images=indexed[1:], duration=100, loop=0, optimize=True)
print(f"Created {OUTPUT} ({OUTPUT.stat().st_size:,} bytes)")

