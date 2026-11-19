import math, subprocess, sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter

SRC = "/root/.claude/uploads/b5f8e0aa-889f-5434-9953-73071764a7ad/06225fac-image.jpg"
OUT = sys.argv[1] if len(sys.argv) > 1 else "review.mp4"
W, H, FPS = 1080, 1920, 30
F = "/usr/share/fonts/opentype/tlwg/"
def font(name, size): return ImageFont.truetype(F + name, size, layout_engine=ImageFont.Layout.RAQM)
BOLD = "Kanit" and "Sawasdee-Bold.otf"
HEAD = "Garuda-Bold.otf"

ORANGE = (238, 77, 45); WHITE = (255, 255, 255); YELLOW = (255, 214, 0); DARK = (18, 18, 22)

src = Image.open(SRC).convert("RGB")
product = src.crop((150, 760, 1110, 1630))          # box + size lines
product_tight = src.crop((155, 770, 980, 1445))    # box only

def ease(t): t = max(0, min(1, t)); return 1 - (1 - t) ** 3
def pop(t):  # overshoot scale
    t = max(0, min(1, t)); return 1 + 0.25 * math.sin(t * math.pi) * (1 - t) if t < 1 else 1

def bg(t):
    im = Image.new("RGB", (W, H), DARK)
    d = ImageDraw.Draw(im)
    for y in range(0, H, 8):
        k = y / H
        d.rectangle((0, y, W, y + 8), fill=(int(18 + 30 * k), int(18 + 10 * k), int(22 + 8 * k)))
    # moving glow
    g = Image.new("L", (W, H), 0); gd = ImageDraw.Draw(g)
    cx = W / 2 + 200 * math.sin(t * 0.8); cy = 900 + 100 * math.cos(t * 0.6)
    gd.ellipse((cx - 520, cy - 520, cx + 520, cy + 520), fill=90)
    g = g.filter(ImageFilter.GaussianBlur(160))
    im.paste(Image.new("RGB", (W, H), ORANGE), (0, 0), g)
    return im

def text_center(d, y, s, f, fill=WHITE, stroke=0, sfill=(0, 0, 0)):
    w = d.textlength(s, font=f)
    d.text(((W - w) / 2, y), s, font=f, fill=fill, stroke_width=stroke, stroke_fill=sfill)

def card(im, img, cx, cy, width, alpha=1.0, radius=36):
    r = width / img.width
    p = img.resize((int(img.width * r), int(img.height * r)), Image.LANCZOS)
    m = Image.new("L", p.size, 0)
    ImageDraw.Draw(m).rounded_rectangle((0, 0, p.width, p.height), radius, fill=int(255 * alpha))
    sh = Image.new("L", (p.width + 80, p.height + 80), 0)
    ImageDraw.Draw(sh).rounded_rectangle((40, 50, p.width + 40, p.height + 50), radius, fill=int(140 * alpha))
    sh = sh.filter(ImageFilter.GaussianBlur(25))
    im.paste((0, 0, 0), (int(cx - p.width / 2 - 40), int(cy - p.height / 2 - 40)), sh)
    im.paste(p, (int(cx - p.width / 2), int(cy - p.height / 2)), m)

def pill(d, x, y, s, f, fill=ORANGE, color=WHITE, pad=28):
    w = d.textlength(s, font=f); b = f.getbbox(s)
    h = b[3] - b[1] + pad * 1.4
    d.rounded_rectangle((x, y, x + w + pad * 2, y + h), h / 2, fill=fill)
    d.text((x + pad, y + pad * 0.7 - b[1]), s, font=f, fill=color)
    return w + pad * 2, h

def check(d, x, y, s=54):
    d.ellipse((x, y, x + s, y + s), fill=ORANGE)
    d.line((x + s * .25, y + s * .52, x + s * .43, y + s * .70, x + s * .76, y + s * .32), fill=WHITE, width=8, joint="curve")

def cart(d, x, y, s=1.0, col=WHITE):
    L = lambda pts: [(x + a * s, y + b * s) for a, b in pts]
    d.line(L([(0, 10), (22, 10), (40, 70), (110, 70), (125, 25), (30, 25)]), fill=col, width=int(10 * s), joint="curve")
    for cx in (50, 100): d.ellipse((x + (cx - 9) * s, y + 82 * s, x + (cx + 9) * s, y + 100 * s), fill=col)

fH = font(HEAD, 92); fH2 = font(HEAD, 74); fM = font(HEAD, 60); fS = font(HEAD, 48); fB = font(HEAD, 140)

SCENES = [3.0, 4.0, 5.5, 3.0, 3.5]  # durations
T = sum(SCENES)
starts = [sum(SCENES[:i]) for i in range(len(SCENES))]

def frame(t):
    im = bg(t); d = ImageDraw.Draw(im)
    s = max(i for i in range(len(starts)) if t >= starts[i]); lt = t - starts[s]
    if s == 0:  # HOOK
        z = 1.25 - 0.25 * ease(lt / 3)
        card(im, product_tight, W / 2, 1150, 900 * z)
        d = ImageDraw.Draw(im)
        a = ease(lt / 0.4)
        y0 = 260 - 60 * (1 - a)
        text_center(d, y0, "ถ่ายสินค้าด้วยมือถือ", fH, stroke=6)
        text_center(d, y0 + 130, "ให้ดูแพงเหมือนสตูดิโอ?", fH, fill=YELLOW, stroke=6)
        if lt > 1.2:
            sc = pop((lt - 1.2) / 0.5)
            f = font(HEAD, int(64 * sc))
            text_center(d, 560, "ต้องมีตัวนี้!", f, fill=WHITE, stroke=5, sfill=ORANGE)
    elif s == 1:  # PRODUCT + SPECS
        z = 1.0 + 0.06 * (lt / 4)
        card(im, product, W / 2, 1020, 940 * z)
        d = ImageDraw.Draw(im)
        text_center(d, 200, "ตู้ถ่ายสินค้า ไฟ LED", fH, stroke=6)
        if lt > 0.6:
            a = ease((lt - 0.6) / 0.4)
            f = font(HEAD, 64)
            w = d.textlength("ใหญ่ 80×80×80 ซม.", font=f) + 56
            pill(d, (W - w) / 2, 370 - 30 * (1 - a), "ใหญ่ 80×80×80 ซม.", f)
        if lt > 1.5:
            f = font(HEAD, 58)
            w = d.textlength("ไฟคู่ • แสงสีขาว", font=f) + 56
            pill(d, (W - w) / 2, 1560, "ไฟคู่ • แสงสีขาว", f, fill=YELLOW, color=DARK)
    elif s == 2:  # BENEFITS
        card(im, product_tight, W / 2, 1330, 820)
        d = ImageDraw.Draw(im)
        text_center(d, 170, "ทำไมต้องมี?", fH, fill=YELLOW, stroke=6)
        items = ["ไม่ต้องจัดไฟเอง เปิดปุ๊บสว่างปั๊บ", "พื้นหลังขาว รูปดูโปรเหมือนร้านดัง", "ใบใหญ่ ใส่รองเท้า กระเป๋าได้สบาย", "รูปสวยขึ้น = ขายของได้มากขึ้น"]
        for i, s_ in enumerate(items):
            st = 0.3 + i * 0.9
            if lt > st:
                a = ease((lt - st) / 0.35)
                x = 70 - 120 * (1 - a); y = 360 + i * 135
                d.rounded_rectangle((x - 10, y - 18, x + 950, y + 92), 26, fill=(255, 255, 255, ), outline=None) if False else None
                check(d, x, y + 4, 60)
                d.text((x + 85, y - 6), s_, font=fS, fill=WHITE, stroke_width=4, stroke_fill=(0, 0, 0))
    elif s == 3:  # WHO
        card(im, product_tight, W / 2, 1300, 760)
        d = ImageDraw.Draw(im)
        text_center(d, 200, "เหมาะกับใคร?", fH, stroke=6)
        tags = [("แม่ค้าออนไลน์", ORANGE), ("สายรีวิว / ป้ายยา", (60, 140, 255)), ("ถ่ายของขายในโซเชียล", (30, 170, 110))]
        for i, (s_, c) in enumerate(tags):
            st = 0.2 + i * 0.5
            if lt > st:
                f = font(HEAD, 58); w = d.textlength(s_, font=f) + 56
                a = ease((lt - st) / 0.3)
                pill(d, (W - w) / 2, 360 + i * 120 + 30 * (1 - a), s_, f, fill=c)
    else:  # CTA
        card(im, product_tight, W / 2, 760, 700)
        d = ImageDraw.Draw(im)
        sc = pop(min(1, lt / 0.5))
        f = font(HEAD, int(110 * sc))
        text_center(d, 1170, "กดตะกร้าเลย!", f, fill=YELLOW, stroke=8)
        f2 = font(HEAD, 64)
        w = d.textlength("โปร 12.12 ลดอีก รีบเลย", font=f2) + 56
        pill(d, (W - w) / 2, 1340, "โปร 12.12 ลดอีก รีบเลย", f2)
        # bouncing arrow + cart pointing to bottom-left (Shopee product card)
        b = 22 * abs(math.sin(lt * 6))
        ax, ay = 150, 1560 + b
        cart(d, ax - 20, ay, 1.3, YELLOW)
        d.polygon([(ax + 40, ay + 190), (ax + 5, ay + 145), (ax + 75, ay + 145)], fill=YELLOW)
        d.text((ax + 190, ay + 30), "ลิงก์อยู่ซ้ายล่าง", font=fM, fill=WHITE, stroke_width=5, stroke_fill=(0, 0, 0))
    # top brand bar
    d.text((40, 60), "ของดีตี๋ห่อย", font=fS, fill=(255, 255, 255), stroke_width=3, stroke_fill=ORANGE)
    # progress bar
    d.rectangle((0, H - 10, int(W * t / T), H), fill=ORANGE)
    # fade between scenes
    for st in starts[1:]:
        if abs(t - st) < 0.12:
            k = 1 - abs(t - st) / 0.12
            im = Image.blend(im, Image.new("RGB", (W, H), WHITE), 0.6 * k)
    return im

if __name__ == "__main__":
    if len(sys.argv) > 2:  # preview frames
        for tt in map(float, sys.argv[2:]): frame(tt).save(f"prev_{tt}.jpg", quality=85)
        sys.exit()
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                          "-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo", "-shortest",
                          "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "medium", "-crf", "20", "-c:a", "aac", "-movflags", "+faststart", OUT], stdin=subprocess.PIPE)
    for i in range(int(T * FPS)):
        p.stdin.write(frame(i / FPS).tobytes())
    p.stdin.close(); p.wait()
    print("done", OUT)
